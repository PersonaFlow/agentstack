import asyncio
import copy
import uuid
from typing import Any, Literal, Optional, Tuple

import numpy as np
import structlog
from semantic_router.encoders import (
    BaseEncoder,
)
from tqdm import tqdm
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared

from stack.app.schema.rag import (
    BaseDocument,
    BaseDocumentChunk,
    DocumentProcessorConfig,
    ParserConfig,
)
from stack.app.rag.util import (
    get_tiktoken_length,
    check_content_is_useful,
    deduplicate_chunk,
)
from stack.app.rag.splitter import UnstructuredSemanticSplitter
from stack.app.rag.summarizer import completion
from stack.app.vectordbs import get_vector_service
from stack.app.schema.file import FileSchema
from stack.app.core.configuration import get_settings
from stack.app.model.file import File
from stack.app.utils.file_helpers import parse_json_file, parse_csv_file


# TODO: Add similarity score to the BaseDocumentChunk
# TODO: Add relevance score to the BaseDocumentChunk
# TODO: Add created_at date to the BaseDocumentChunk

logger = structlog.get_logger()
settings = get_settings()


def sanitize_metadata(metadata: dict) -> dict:
    def sanitize_value(value):
        if isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, list):
            # Ensure all elements in the list are of type str, int, float, or bool
            # Convert non-compliant elements to str
            return [
                v if isinstance(v, (str, int, float, bool)) else str(v) for v in value
            ]
        elif isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        else:
            return str(value)

    return {key: sanitize_value(value) for key, value in metadata.items()}


class EmbeddingService:
    # Extract out to configuration
    MIN_WORD_COUNT = 10
    MAX_DENSITY_WORD_COUNT = 200
    INFORMATION_DENSITY_RATIO = 0.5

    def __init__(
        self,
        index_name: str,
        encoder: BaseEncoder,
        vector_credentials: dict,
        dimensions: Optional[int],
        files: Optional[list[tuple[FileSchema, bytes]]] = None,
        namespace: Optional[str] = None,
        purpose: Optional[str] = None,
        parser_config: Optional[ParserConfig] = None,
    ):
        self.encoder = encoder
        self.files = files
        self.index_name = index_name
        self.vector_credentials = vector_credentials
        self.dimensions = dimensions
        self.namespace = namespace
        self.purpose = purpose
        self.unstructured_client = UnstructuredClient(
            api_key_auth=settings.UNSTRUCTURED_API_KEY,
            server_url=settings.UNSTRUCTURED_BASE_URL,
        )
        self.parser_config = parser_config or ParserConfig()

    async def generate_chunks(
        self, config: DocumentProcessorConfig
    ) -> list[BaseDocumentChunk]:
        logger.info(f"Generating chunks using method: {config.splitter.name}")
        doc_chunks = []
        for file, file_content in tqdm(self.files, desc="Generating chunks"):
            try:
                chunks = await self._process_file(file, file_content, config)
                filtered_chunks = self._filter_chunks(chunks)
                doc_chunks.extend(filtered_chunks)
            except Exception as e:
                logger.error(f"Error loading chunks for file {file.filename}: {e}")
                raise
        return doc_chunks

    def _filter_chunks(
        self, chunks: list[BaseDocumentChunk]
    ) -> list[BaseDocumentChunk]:
        filtered_chunks = []
        document_content = ""
        for chunk in chunks:
            chunk_content = deduplicate_chunk(chunk.page_content)
            valid, reason = check_content_is_useful(
                chunk_content,
                min_word_count=self.MIN_WORD_COUNT,
                information_density_ratio=self.INFORMATION_DENSITY_RATIO,
                max_density_word_count=self.MAX_DENSITY_WORD_COUNT,
            )
            if not valid:
                logger.debug(f"Filtering out chunk, {reason}, {chunk}")
                continue
            logger.debug(f"Chunk is useful: {chunk}")
            document_content += chunk_content
            filtered_chunks.append(chunk)

        return filtered_chunks if document_content else []

    async def _process_file(
        self, file: FileSchema, file_content: bytes, config: DocumentProcessorConfig
    ) -> list[BaseDocumentChunk]:
        if file.mime_type == "application/json":
            json_data = parse_json_file(file_content)
            return await self._process_structured_data(file, json_data, config)
        elif file.mime_type == "text/csv":
            csv_data = parse_csv_file(file_content)
            return await self._process_structured_data(file, csv_data, config)
        else:
            return await self._process_unstructured_file(file, file_content, config)

    async def _process_structured_data(
        self, file: FileSchema, data: list[dict], config: DocumentProcessorConfig
    ) -> list[BaseDocumentChunk]:
        content_field = self.parser_config.structured_data_content_field
        all_chunks = []

        for item in data:
            if content_field not in item:
                logger.warn(
                    f"Item in file {file.filename} is missing '{content_field}' field. Skipping."
                )
                continue

            item_content = item[content_field]
            item_metadata = {k: v for k, v in item.items() if k != content_field}

            chunks = await self._partition_and_chunk(item_content, config)
            item_chunks = [
                self._create_document_chunk(chunk, file, item_metadata)
                for chunk in chunks
            ]
            all_chunks.extend(item_chunks)

        return all_chunks

    async def _process_unstructured_file(
        self, file: FileSchema, file_content: bytes, config: DocumentProcessorConfig
    ) -> list[BaseDocumentChunk]:
        chunks = await self._partition_and_chunk(file_content, config, file=file)
        return [self._create_document_chunk(chunk, file) for chunk in chunks]

    async def _partition_and_chunk(
        self,
        content: Any,
        config: DocumentProcessorConfig,
        file: Optional[FileSchema] = None,
    ) -> list[dict]:
        if config.splitter.name == "by_title":
            return await self._partition_by_title(content, config, file)
        elif config.splitter.name == "semantic":
            return await self._partition_semantic(content, config, file)
        else:
            raise ValueError(f"Unsupported splitter method: {config.splitter.name}")

    async def _partition_by_title(
        self,
        content: Any,
        config: DocumentProcessorConfig,
        file: Optional[FileSchema] = None,
    ) -> list[dict]:
        chunked_elements = await self._partition_content(
            content, strategy=config.unstructured.partition_strategy, file=file
        )
        return [
            {
                "page_content": element.get("text"),
                "metadata": sanitize_metadata(element.get("metadata")),
            }
            for element in chunked_elements
        ]

    async def _partition_semantic(
        self,
        content: Any,
        config: DocumentProcessorConfig,
        file: Optional[FileSchema] = None,
    ) -> list[dict]:
        elements = await self._partition_content(
            content,
            strategy=config.unstructured.partition_strategy,
            returned_elements_type="original",
            file=file,
        )
        splitter_config = UnstructuredSemanticSplitter(
            encoder=self.encoder,
            window_size=config.splitter.rolling_window_size,
            min_split_tokens=config.splitter.min_tokens,
            max_split_tokens=config.splitter.max_tokens,
        )
        return await splitter_config(elements=elements)

    async def _partition_content(
        self,
        content: Any,
        strategy: str = "auto",
        returned_elements_type: Literal["chunked", "original"] = "chunked",
        file: Optional[FileSchema] = None,
    ) -> list[Any]:
        try:
            files = shared.Files(
                content=content
                if isinstance(content, bytes)
                else content.encode("utf-8"),
                file_name=file.source.split("/")[-1] if file else "content.txt",
            )
            req = shared.PartitionParameters(
                files=files,
                include_page_breaks=True,
                strategy=strategy,
                max_characters=2500 if returned_elements_type == "chunked" else None,
                new_after_n_chars=1000 if returned_elements_type == "chunked" else None,
                chunking_strategy="by_title"
                if returned_elements_type == "chunked"
                else None,
            )

            unstructured_response = self.unstructured_client.general.partition(req)
            if unstructured_response.elements is not None:
                return unstructured_response.elements
        except Exception as e:
            logger.exception(f"Error processing content: {e}")
            raise
        return []

    def _create_document_chunk(
        self, chunk: dict, file: FileSchema, additional_metadata: Optional[dict] = None
    ) -> BaseDocumentChunk:
        metadata = {
            "file_id": str(file.id),
            "purpose": self.purpose,
            "source": file.source,
            "source_type": file.mime_type,
            "token_count": get_tiktoken_length(chunk["page_content"]),
            **(additional_metadata or {}),
            **chunk.get("metadata", {}),
        }
        return BaseDocumentChunk(
            id=str(uuid.uuid4()),
            page_content=chunk["page_content"],
            namespace=str(self.namespace),
            metadata=metadata,
        )

    async def embed_and_upsert(
        self,
        chunks: list[BaseDocumentChunk],
        encoder: BaseEncoder,
        index_name: Optional[str] = None,
        batch_size: int = 100,
    ) -> list[BaseDocumentChunk]:
        pbar = tqdm(total=len(chunks), desc="Generating embeddings")
        queue = asyncio.Queue()

        async def embed_batch(
            chunks_batch: list[BaseDocumentChunk],
        ) -> list[BaseDocumentChunk]:
            try:
                chunk_texts = [
                    chunk.page_content
                    for chunk in chunks_batch
                    if chunk and chunk.page_content
                ]
                if not chunk_texts:
                    logger.warning(f"No content to embed in batch {chunks_batch}")
                    return []
                embeddings = encoder(chunk_texts)
                for chunk, embedding in zip(chunks_batch, embeddings):
                    chunk.dense_embedding = np.array(embedding).tolist()
                pbar.update(len(chunks_batch))
                return chunks_batch
            except Exception as e:
                logger.error(f"Error embedding a batch of documents: {e}")
                raise

        # Create batches of chunks
        chunks_batches = [
            chunks[i : i + batch_size] for i in range(0, len(chunks), batch_size)
        ]

        # Add batches to the queue
        for batch in chunks_batches:
            await queue.put(batch)

        async def process_batches():
            while not queue.empty():
                batch = await queue.get()
                await embed_batch(batch)
                queue.task_done()

        # Process batches concurrently
        tasks = [asyncio.create_task(process_batches()) for _ in range(10)]
        await asyncio.gather(*tasks)

        chunks_with_embeddings = [
            chunk for chunk in chunks if chunk.dense_embedding is not None
        ]
        pbar.close()

        print(f"Attempting to upsert {len(chunks_with_embeddings)} chunks...")
        if not chunks_with_embeddings:
            logger.warn("No chunks to upsert. Aborting operation.")
            return []

        vector_service = get_vector_service(
            index_name=index_name or self.index_name,
            credentials=self.vector_credentials,
            encoder=encoder,
            dimensions=self.dimensions,
        )
        try:
            await vector_service.upsert(chunks=chunks_with_embeddings)
        except Exception as e:
            logger.error(f"Error upserting embeddings: {e}")
            raise

        return chunks_with_embeddings

    async def generate_summary_documents(
        self, documents: list[BaseDocumentChunk]
    ) -> list[BaseDocumentChunk]:
        pbar = tqdm(total=len(documents), desc="Grouping chunks")
        pages: dict[int, BaseDocumentChunk] = {}
        for document in documents:
            page_number = document.metadata.get("page_number", None)
            if page_number not in pages:
                pages[page_number] = copy.deepcopy(document)
            else:
                pages[page_number].page_content += document.page_content
            pbar.update()
        pbar.close()

        async def safe_completion(
            document: BaseDocumentChunk,
        ) -> Optional[BaseDocumentChunk]:
            try:
                document.page_content = await completion(document=document)
                return document
            except Exception as e:
                logger.error(f"Error summarizing document {document.id}: {e}")
                return None

        pbar = tqdm(desc="Summarizing documents")
        summary_documents = []
        for future in asyncio.as_completed(
            [safe_completion(document) for document in pages.values()]
        ):
            document = await future
            if document:
                summary_documents.append(document)
            pbar.update()
        pbar.close()

        return summary_documents

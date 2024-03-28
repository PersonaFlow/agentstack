import asyncio
import aiohttp
import copy
import uuid
from tempfile import NamedTemporaryFile
from typing import Any, Literal, Optional

import numpy as np
import structlog
from semantic_router.encoders import (
    BaseEncoder,
)
from tqdm import tqdm
from unstructured_client import UnstructuredClient
from unstructured_client.models import shared
from unstructured_client.models.errors import SDKError

from app.schema.rag import (
    BaseDocument,
    BaseDocumentChunk,
    IngestFile,
    DocumentProcessorConfig,
)
from app.rag.util import get_tiktoken_length
from app.rag.splitter import UnstructuredSemanticSplitter
from app.rag.summarizer import completion
from app.vectordbs import get_vector_service

from app.core.configuration import get_settings

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
                v if isinstance(v, (str, int, float, bool)) else str(v)
                for v in value
            ]
        elif isinstance(value, dict):
            return {k: sanitize_value(v) for k, v in value.items()}
        else:
            return str(value)

    return {key: sanitize_value(value) for key, value in metadata.items()}
class EmbeddingService:
    def __init__(
        self,
        index_name: str,
        encoder: BaseEncoder,
        vector_credentials: dict,
        dimensions: Optional[int],
        files: Optional[list[IngestFile]] = None,
    ):
        self.encoder = encoder
        self.files = files
        self.index_name = index_name
        self.vector_credentials = vector_credentials
        self.dimensions = dimensions
        self.unstructured_client = UnstructuredClient(
            api_key_auth=settings.UNSTRUCTURED_API_KEY,
            server_url=settings.UNSTRUCTURED_BASE_URL,
        )

    async def _partition_file(
        self,
        file: IngestFile,
        strategy="auto",
        returned_elements_type: Literal["chunked", "original"] = "chunked",
    ) -> list[Any]:
        """
        Process an IngestFile object to partition it based on the specified strategy.
        This method handles both files uploaded directly (with content) and files to be downloaded via URL.

        Args:
            file (IngestFile): The file to be processed.
            strategy (str): The partitioning strategy to use.
            returned_elements_type (Literal["chunked", "original"]): The type of elements to return, either chunked or original.

        Returns:
            list[Any]: A list of partitioned file elements.
        """
        # Check if the file content is directly provided or needs to be downloaded
        if file.content:
            file_content = file.content
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(file.url) as response:
                    if response.status != 200:
                        await logger.error(f"Failed to download file from {file.url}")
                        return []
                    file_content = await response.read()

        # At this point, file_content contains the actual file content,
        # either from a direct upload or downloaded from a URL

        with NamedTemporaryFile(suffix=file.suffix, delete=True) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_file.seek(0)
            file_name = temp_file.name

            files = shared.Files(
                content=file_content,
                file_name=file_name,
            )
            req = shared.PartitionParameters(
                files=files,
                include_page_breaks=True,
                strategy=strategy,
                max_characters=2500 if returned_elements_type == "chunked" else None,
                new_after_n_chars=1000 if returned_elements_type == "chunked" else None,
                chunking_strategy="by_title" if returned_elements_type == "chunked" else None,
            )
            try:
                unstructured_response = self.unstructured_client.general.partition(req)
                if unstructured_response.elements is not None:
                    return unstructured_response.elements
                else:
                    await logger.error(f"Error partitioning file: {unstructured_response}")
                    return []
            except SDKError as e:
                await logger.error(f"Error partitioning file: {e}")
                return []

    def _create_base_document(
        self, document_id: str, file: IngestFile, document_content: str
    ) -> BaseDocument:
        return BaseDocument(
            id=document_id,
            content=document_content,
            doc_url=file.url,
            metadata={
                "source": file.url,
                "source_type": "document",
                "document_type": file.suffix,
            },
        )

    async def generate_chunks(
        self,
        config: DocumentProcessorConfig,
    ) -> list[BaseDocumentChunk]:
        doc_chunks = []
        for file in tqdm(self.files, desc="Generating chunks"):
            await logger.info(f"Splitting method: {str(config.splitter.name)}")
            try:
                chunks = []
                if config.splitter.name == "by_title":
                    chunked_elements = await self._partition_file(
                        file, strategy=config.unstructured.partition_strategy
                    )
                    for element in chunked_elements:
                        chunk_data = {
                            "content": element.get("text"),
                            "metadata": sanitize_metadata(
                                element.get("metadata")
                            ),
                        }
                        chunks.append(chunk_data)
                if config.splitter.name == "semantic":
                    elements = await self._partition_file(
                        file,
                        strategy=config.unstructured.partition_strategy,
                        returned_elements_type="original",
                    )
                    splitter_config = UnstructuredSemanticSplitter(
                        encoder=self.encoder,
                        window_size=config.splitter.rolling_window_size,
                        min_split_tokens=config.splitter.min_tokens,
                        max_split_tokens=config.splitter.max_tokens,
                    )
                    chunks = await splitter_config(elements=elements)

                if not chunks:
                    continue

                document_id = f"doc_{uuid.uuid4()}"
                document_content = "".join(chunk.get("content", "") for chunk in chunks)

                doc_chunks.extend(
                    [
                        BaseDocumentChunk(
                            id=str(uuid.uuid4()),
                            doc_url=file.url,
                            document_id=document_id,
                            content=f"{chunk.get('title', '')}\n{chunk.get('content', '')}"
                            if config.splitter.prefix_title
                            else chunk.get("content", ""),
                            source=file.url,
                            source_type=file.suffix,
                            chunk_index=chunk.get("chunk_index", None),
                            title=chunk.get("title", None),
                            token_count=get_tiktoken_length(chunk.get("content", "")),
                            metadata=sanitize_metadata(chunk.get("metadata", {})),
                        )
                        for chunk in chunks
                    ]
                )

                self._create_base_document(document_id, file, document_content)

            except Exception as e:
                await logger.error(f"Error loading chunks: {e}")
                raise
        return doc_chunks

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
                    chunk.content
                    for chunk in chunks_batch
                    if chunk and chunk.content
                ]
                if not chunk_texts:
                    await logger.warning(f"No content to embed in batch {chunks_batch}")
                    return []
                embeddings = encoder(chunk_texts)
                for chunk, embedding in zip(chunks_batch, embeddings):
                    chunk.dense_embedding = np.array(embedding).tolist()
                pbar.update(len(chunks_batch))
                return chunks_batch
            except Exception as e:
                await logger.error(f"Error embedding a batch of documents: {e}")
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
            await logger.warn("No chunks to upsert. Aborting operation.")
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
            await logger.error(f"Error upserting embeddings: {e}")
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
                pages[page_number].content += document.content
            pbar.update()
        pbar.close()

        async def safe_completion(document: BaseDocumentChunk) -> Optional[BaseDocumentChunk]:
            try:
                document.content = await completion(document=document)
                return document
            except Exception as e:
                await logger.error(f"Error summarizing document {document.id}: {e}")
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

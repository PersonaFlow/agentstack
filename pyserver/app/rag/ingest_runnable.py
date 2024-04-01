"""This module provides document ingestion utilities using langchain runnables."""
from __future__ import annotations
import uuid
import logging
from typing import Any, BinaryIO, List, Optional

from langchain.document_loaders.parsers import BS4HTMLParser, PDFMinerParser
from langchain.document_loaders.parsers.generic import MimeTypeBasedParser
from langchain.document_loaders.parsers.msword import MsWordParser
from langchain.document_loaders.parsers.txt import TextParser
from langchain.text_splitter import TextSplitter
from langchain_community.document_loaders import Blob
from langchain_community.document_loaders.base import BaseBlobParser
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
from langchain_community.document_loaders.blob_loaders import Blob
from langchain_community.vectorstores.qdrant import Qdrant
from qdrant_client.http import models as rest
from langchain_core.runnables import (
    ConfigurableField,
    RunnableConfig,
    RunnableSerializable,
)
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from app.utils.vector_collection import create_assistants_collection
from app.core.configuration import get_settings


HANDLERS = {
#   PDFMinerParser handles parsing of everything in a pdf such as images, tables, etc.
    "application/pdf": PDFMinerParser(),
    "text/plain": TextParser(),
    "text/html": BS4HTMLParser(),
    "application/msword": MsWordParser(),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
        MsWordParser()
    ),
}

SUPPORTED_MIMETYPES = sorted(HANDLERS.keys())


MIMETYPE_BASED_PARSER = MimeTypeBasedParser(
    handlers=HANDLERS,
    fallback_parser=None,
)

settings = get_settings()

# logger = structlog.get_logger()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _guess_mimetype(file_bytes: bytes) -> str:
    """Guess the mime-type of a file."""
    try:
        import magic
    except ImportError as e:
        raise ImportError(
            "magic package not found, please install it with `pip install python-magic`"
        ) from e

    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file_bytes)
    return mime_type


def _convert_ingestion_input_to_blob(data: BinaryIO) -> Blob:
    """Convert ingestion input to blob."""
    file_data = data.read()
    mimetype = _guess_mimetype(file_data)
    file_name = data.name
    return Blob.from_data(
        data=file_data,
        path=file_name,
        mime_type=mimetype,
    )


def _sanitize_document_content(document: Document) -> Document:
    """Sanitize the document."""
    # Without this, PDF ingestion fails with
    # "A string literal cannot contain NUL (0x00) characters".
    document.page_content = document.page_content.replace("\x00", "x")

def _update_document_metadata(document: Document, namespace: str, file_id: Optional[str] = None) -> None:
    """Mutation in place that adds namespace and file_id to the document metadata."""
    try:
        document.metadata["namespace"] = namespace
        document.metadata["file_id"] = file_id if file_id is not None else None
    except Exception as e:
        logger.error(f"Error updating document metadata: {e}")
        raise e

def ingest_blob(
    blob: Blob,
    parser: BaseBlobParser,
    text_splitter: TextSplitter,
    vectorstore: VectorStore,
    namespace: str,
    *,
    batch_size: int = 100,
) -> list[str]:
    docs_to_index = []
    file_ids = []
    try:
        for document in parser.lazy_parse(blob):
            file_id = str(uuid.uuid4())
            file_ids.append(file_id)
            logger.debug(f"Generated file_id: {file_id}")

            docs = text_splitter.split_documents([document])
            logger.debug(f"Split document into {len(docs)} chunks")

            for doc in docs:
                _sanitize_document_content(doc)
                _update_document_metadata(doc, namespace, file_id)
            docs_to_index.extend(docs)

            if len(docs_to_index) >= batch_size:
                logger.debug(f"Adding {len(docs_to_index)} documents to vector store")
                vectorstore.add_documents(docs_to_index)
                docs_to_index = []

        if docs_to_index:
            logger.debug(f"Adding remaining {len(docs_to_index)} documents to vector store")
            vectorstore.add_documents(docs_to_index)
        logger.debug(f"Ingested {len(file_ids)} files")

    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise e

    return file_ids


class IngestRunnable(RunnableSerializable[BinaryIO, list[str]]):
    """Runnable for ingesting files into a vectorstore."""

    text_splitter: TextSplitter
    """Text splitter to use for splitting the text into chunks."""

    assistant_id: Optional[str]
    thread_id: Optional[str]
    """Ingested documents will be associated with assistant_id or thread_id.
       The assistant or thread ID is used as the namespace, and is filtered on at query time.
    """

    class Config:
        arbitrary_types_allowed = True

    @property
    def namespace(self) -> str:
        if (self.assistant_id is None and self.thread_id is None) or (
            self.assistant_id is not None and self.thread_id is not None
        ):
            raise ValueError(
                "Exactly one of assistant_id or thread_id must be provided"
            )
        return self.assistant_id if self.assistant_id is not None else self.thread_id

    @property
    def vectorstore(self) -> VectorStore:
        qdrant_client = QdrantClient(settings.VECTOR_DB_HOST, port = settings.VECTOR_DB_PORT)
        collection_name = settings.VECTOR_DB_COLLECTION_NAME
        vector_size = settings.VECTOR_DB_COLLECTION_SIZE

        if not qdrant_client.collection_exists(collection_name):
            create_assistants_collection(qdrant_client, collection_name, vector_size)

        return Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=OpenAIEmbeddings(),
            vector_name="default"
        )

    class Config:
        arbitrary_types_allowed = True

    def invoke(
        self, input: BinaryIO, config: Optional[RunnableConfig] = None
    ) -> tuple[list[str], list[str]]:
        return self.batch([input], config)

    def batch(
        self,
        inputs: List[BinaryIO],
        config: RunnableConfig | List[RunnableConfig] | None = None,
        *,
        return_exceptions: bool = False,
        **kwargs: Any | None,
    ) -> list[str]:
        """Ingest a batch of files into the vectorstore."""
        file_ids = []
        try:
            for data in inputs:
                blob = _convert_ingestion_input_to_blob(data)
                file_ids.extend(ingest_blob(
                    blob,
                    MIMETYPE_BASED_PARSER,
                    self.text_splitter,
                    self.vectorstore,
                    self.namespace,
                ))
            logger.debug(f"Batch ingested {len(file_ids)} files")
        except Exception as e:
            logger.error(f"Error ingesting batch: {e}")
            raise e
        return file_ids

ingest_runnable = IngestRunnable(
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
).configurable_fields(
    assistant_id=ConfigurableField(
        id="assistant_id",
        annotation=str,
        name="Assistant ID",
    ),
    thread_id=ConfigurableField(
        id="thread_id",
        annotation=str,
        name="Thread ID",
    ),
)

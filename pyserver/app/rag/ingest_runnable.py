"""This module provides document ingestion utilities using langchain
runnables."""
from __future__ import annotations
import logging
from typing import Any, BinaryIO, Optional

from langchain.text_splitter import TextSplitter
from langchain_community.document_loaders import Blob
from langchain_community.document_loaders.base import BaseBlobParser
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
from langchain_community.document_loaders.blob_loaders import Blob
from langchain_community.vectorstores.qdrant import Qdrant
from langchain_core.runnables import (
    ConfigurableField,
    RunnableConfig,
    RunnableSerializable,
)
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from pyserver.app.utils.vector_collection import create_assistants_collection
from pyserver.app.core.configuration import get_settings
from pyserver.app.utils.file_helpers import guess_mime_type, MIMETYPE_BASED_PARSER


# TODO: Make Async

settings = get_settings()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _convert_ingestion_input_to_blob(data: BinaryIO) -> Blob:
    file_data = data.read()
    mimetype = guess_mime_type(file_data)
    # TODO: set file source to data.name - this gets set as the metadata.source field for the doc in the vector db.
    # file_name = data.name if hasattr(data, 'name') else 'unnamed_file'

    return Blob.from_data(
        data=file_data,
        # path=file_name,
        mime_type=mimetype,
    )


def _sanitize_document_content(document: Document) -> Document:
    """Sanitize the document."""
    # Without this, PDF ingestion fails with
    # "A string literal cannot contain NUL (0x00) characters".
    document.page_content = document.page_content.replace("\x00", "x")


def _update_document_metadata(
    document: Document, namespace: str, file_id: Optional[str] = None
) -> None:
    """Mutation in place that adds namespace and file_id to the document
    metadata."""
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
    file_id: str,
    *,
    batch_size: int = 100,
) -> list[str]:
    """Ingest a document into the vectorstore."""
    docs_to_index = []
    ids = []
    try:
        for document in parser.lazy_parse(blob):
            docs = text_splitter.split_documents([document])
            logger.debug(f"Split document into {len(docs)} chunks")
            for doc in docs:
                _sanitize_document_content(doc)
                _update_document_metadata(doc, namespace, file_id)
            docs_to_index.extend(docs)

            if len(docs_to_index) >= batch_size:
                logger.debug(f"Adding {len(docs_to_index)} documents to vector store")
                ids.extend(vectorstore.add_documents(docs_to_index))
                docs_to_index = []

        if docs_to_index:
            logger.debug(
                f"Adding remaining {len(docs_to_index)} documents to vector store"
            )
            ids.extend(vectorstore.add_documents(docs_to_index))

    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        raise e

    return ids


class IngestRunnable(RunnableSerializable[BinaryIO, list[str]]):
    """Runnable for ingesting files into a vectorstore."""

    text_splitter: TextSplitter
    """Text splitter to use for splitting the text into chunks."""

    assistant_id: Optional[str]
    thread_id: Optional[str]
    """Ingested documents will be associated with assistant_id or thread_id.
       The assistant or thread ID is used as the namespace, and is filtered on at query time.
    """

    file_id: Optional[str]
    """The file id of the document to ingest."""

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
        qdrant_client = QdrantClient(
            settings.VECTOR_DB_HOST, port=settings.VECTOR_DB_PORT
        )
        collection_name = settings.VECTOR_DB_COLLECTION_NAME
        vector_size = settings.VECTOR_DB_ENCODER_DIMENSIONS

        if not qdrant_client.collection_exists(collection_name):
            create_assistants_collection(qdrant_client, collection_name, vector_size)

        return Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=OpenAIEmbeddings(),
            vector_name="default",
        )

    class Config:
        arbitrary_types_allowed = True

    def invoke(
        self, input: BinaryIO, config: Optional[RunnableConfig] = None
    ) -> list[str]:
        return self.batch([input], config)

    def batch(
        self,
        inputs: list[BinaryIO],
        config: RunnableConfig | list[RunnableConfig] | None = None,
        *,
        return_exceptions: bool = False,
        **kwargs: Any | None,
    ) -> list[str]:
        """Ingest a batch of files into the vectorstore."""
        ids = []
        try:
            for data in inputs:
                blob = _convert_ingestion_input_to_blob(data)
                ids.extend(
                    ingest_blob(
                        blob,
                        MIMETYPE_BASED_PARSER,
                        self.text_splitter,
                        self.vectorstore,
                        self.namespace,
                        self.file_id,
                    )
                )
        except Exception as e:
            logger.error(f"Error ingesting batch: {e}")
            raise e

        return ids


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
    file_id=ConfigurableField(
        id="file_id",
        annotation=str,
        name="File ID",
    ),
)

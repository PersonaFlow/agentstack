from __future__ import annotations

from typing import Any, BinaryIO, List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
from langchain_community.document_loaders.blob_loaders import Blob
from langchain_community.vectorstores.qdrant import Qdrant
from qdrant_client.http import models as rest
import structlog
from langchain_core.runnables import (
    ConfigurableField,
    RunnableConfig,
    RunnableSerializable,
)
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient

from .ingest import ingest_blob
from .parsing import MIMETYPE_BASED_PARSER
from app.core.configuration import get_settings

settings = get_settings()

logger = structlog.get_logger()

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

qdrant_client = QdrantClient(settings.VECTOR_DB_HOST, port = settings.VECTOR_DB_PORT)

class IngestRunnable(RunnableSerializable[BinaryIO, List[str]]):
    """Runnable for ingesting files into a vectorstore."""

    text_splitter: TextSplitter
    """Text splitter to use for splitting the text into chunks."""

    assistant_id: Optional[str]
    """Ingested documents will be associated with this assistant id.
    The assistant ID is used as the namespace, and is filtered on at query time.
    """

    class Config:
        arbitrary_types_allowed = True

    def _create_vectorstore(self) -> VectorStore:
        index_name = self.assistant_id
        print(f"index_name: {index_name}")
        collections = qdrant_client.get_collections()
        # await logger.info(f"collections: {collections}")
        if index_name not in [c.name for c in collections.collections]:
            # await logger.info(f"No index found, creating collection for assistant: {index_name}")
            qdrant_client.create_collection(
                collection_name=index_name,
                vectors_config={
                    index_name: rest.VectorParams(
                        size=1536, distance=rest.Distance.COSINE
                    )
                },
                optimizers_config=rest.OptimizersConfigDiff(
                    indexing_threshold=0,
                ),
            )
        return Qdrant(
            client=qdrant_client,
            collection_name=index_name,
            embeddings=OpenAIEmbeddings(),
            vector_name=index_name,
        )

    class Config:
        arbitrary_types_allowed = True

    def invoke(
        self, input: BinaryIO, config: Optional[RunnableConfig] = None
    ) -> List[str]:
        return self.batch([input], config)

    def batch(
        self,
        inputs: List[BinaryIO],
        config: RunnableConfig | List[RunnableConfig] | None = None,
        *,
        return_exceptions: bool = False,
        **kwargs: Any | None,
    ) -> List:
        """Ingest a batch of files into the vectorstore."""
        vectorstore = self._create_vectorstore()
        ids = []
        for data in inputs:
            blob = _convert_ingestion_input_to_blob(data)
            ids.extend(
                ingest_blob(
                    blob,
                    MIMETYPE_BASED_PARSER,
                    self.text_splitter,
                    vectorstore,
                    self.assistant_id,
                )
            )
        return ids

ingest_runnable = IngestRunnable(
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200),
).configurable_fields(
    assistant_id=ConfigurableField(
        id="assistant_id",
        annotation=str,
        name="Assistant ID",
    ),
)

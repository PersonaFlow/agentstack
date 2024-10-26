from typing import List, Dict, Any, Optional

from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import (
    CallbackManagerForRetrieverRun,
    AsyncCallbackManagerForRetrieverRun,
)
from langchain_core.documents import Document
from stack.app.schema.rag import QueryRequestPayload, BaseDocumentChunk
from stack.app.rag.query import query_documents
from stack.app.core.configuration import get_settings


settings = get_settings()


class Retriever(BaseRetriever):
    def __init__(
        self,
        tags: Optional[List[str]] = None,
        namespace: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(tags=tags, metadata=metadata)
        metadata = metadata or {}
        if namespace is not None:
            metadata["namespace"] = namespace

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        """Sync implementations for retriever."""
        raise NotImplementedError

    def _chunk_to_document(self, chunk: BaseDocumentChunk) -> Document:
        """Convert a BaseDocumentChunk to a langchain Document."""
        metadata = {"namespace": chunk.namespace, **chunk.metadata}
        return Document(page_content=chunk.page_content, metadata=metadata)

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Async implementations for retriever."""
        payload = QueryRequestPayload(
            input=query,
            namespace=self.metadata.get("namespace"),
            index_name=self.metadata.get(
                "index_name", settings.VECTOR_DB_COLLECTION_NAME
            ),
            vector_database=self.metadata.get("vector_database"),
            encoder=self.metadata.get("encoder"),
            enable_rerank=self.metadata.get("enable_rerank"),
            exclude_fields=self.metadata.get("exclude_fields"),
        )
        chunks = await query_documents(payload)
        return [self._chunk_to_document(chunk) for chunk in chunks]

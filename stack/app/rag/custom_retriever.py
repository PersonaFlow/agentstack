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

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[Document]:
        payload = QueryRequestPayload(
            input=query,
            namespace=self.metadata.get("namespace"),
        )
        chunks = await query_documents(payload)
        return [self._chunk_to_document(chunk) for chunk in chunks]

    def _chunk_to_document(self, chunk: BaseDocumentChunk) -> Document:
        metadata = {
            "source": chunk.source,
            "file_id": chunk.file_id,
            "chunk_index": chunk.chunk_index,
            "namespace": chunk.namespace,
        }
        return Document(page_content=chunk.page_content, metadata=metadata)

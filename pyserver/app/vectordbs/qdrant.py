from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from semantic_router.encoders import BaseEncoder
from tqdm import tqdm
import structlog
from app.schema.rag import DeleteDocumentsResponse, BaseDocumentChunk
from app.vectordbs.base import BaseVectorDatabase
from app.core.configuration import get_settings


MAX_QUERY_TOP_K = 5
settings = get_settings()

logger = structlog.get_logger()

class QdrantService(BaseVectorDatabase):
    def __init__(
        self,
        credentials: dict = settings.VECTOR_DB_CREDENTIALS,
        index_name: str = settings.VECTOR_DB_COLLECTION_NAME,
        dimension: int = settings.VECTOR_DB_ENCODER_DIMENSIONS,
        encoder: Optional[BaseEncoder] = None,
        enable_rerank: bool = False,
    ):
        super().__init__(
            index_name=index_name,
            dimension=dimension,
            credentials=credentials,
            encoder=encoder,
            enable_rerank=enable_rerank,
        )

        self.client = QdrantClient(
            credentials["host"],
            api_key=credentials["api_key"],
            https=False
        )

        collections = self.client.get_collections()
        if index_name not in [c.name for c in collections.collections]:
            self.client.create_collection(
                collection_name=self.index_name,
                vectors_config={
                    "content": rest.VectorParams(
                        size=dimension, distance=rest.Distance.COSINE
                    )
                },
                optimizers_config=rest.OptimizersConfigDiff(
                    indexing_threshold=0,
                ),
            )

    async def upsert(self, chunks: List[BaseDocumentChunk]) -> None:
        points = []
        for chunk in tqdm(chunks, desc="Upserting to Qdrant"):
            points.append(
                rest.PointStruct(
                    id=chunk.id,
                    vector={"content": chunk.dense_embedding},
                    payload={
                        "document_id": chunk.document_id,
                        "content": chunk.content,
                        "doc_url": chunk.doc_url,
                        **(chunk.metadata if chunk.metadata else {}),
                    },
                )
            )

        self.client.upsert(collection_name=self.index_name, wait=True, points=points)
    

    async def query(self, input: str, top_k: int = MAX_QUERY_TOP_K) -> List:
        vectors = await self._generate_vectors(input=input)
        search_result = self.client.search(
            collection_name=self.index_name,
            query_vector=("content", vectors[0]),
            limit=top_k,
            with_payload=True,
        )
        return [
            BaseDocumentChunk(
                id=result.id,
                source_type=result.payload.get("filetype"),
                source=result.payload.get("doc_url"),
                document_id=result.payload.get("document_id"),
                content=result.payload.get("content"),
                doc_url=result.payload.get("doc_url"),
                page_number=result.payload.get("page_number"),
                metadata={**result.payload},
            )
            for result in search_result
        ]

    async def delete(self, file_id: str, assistant_id: Optional[str] = None) -> DeleteDocumentsResponse:

        must_conditions = [
            rest.FieldCondition(key="metadata.file_id", match=rest.MatchValue(value=str(file_id)))
        ]
        if assistant_id:
            must_conditions.append(
                rest.FieldCondition(key="metadata.namespace", match=rest.MatchValue(value=str(assistant_id)))
            )

        common_filter = rest.Filter(must=must_conditions)

        deleted_chunks = self.client.count(
            collection_name=self.index_name,
            count_filter=common_filter,
            exact=True,
        )
        await logger.info(f"Preparing to delete {deleted_chunks.count} chunks")

        self.client.delete(
            collection_name=self.index_name,
            points_selector=rest.FilterSelector(filter=common_filter),
        )

        return DeleteDocumentsResponse(num_deleted_chunks=deleted_chunks.count)

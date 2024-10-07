from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from semantic_router.encoders import BaseEncoder
from tqdm import tqdm
import structlog
from stack.app.schema.rag import DeleteDocumentsResponse, BaseDocumentChunk
from stack.app.vectordbs.base import BaseVectorDatabase
from stack.app.core.configuration import get_settings
from qdrant_client.http import models as qdrant_models


settings = get_settings()

logger = structlog.get_logger()


class QdrantService(BaseVectorDatabase):
    def __init__(
        self,
        credentials: dict = settings.VECTOR_DB_CONFIG,
        index_name: str = settings.VECTOR_DB_COLLECTION_NAME,
        dimension: int = settings.VECTOR_DB_ENCODER_DIMENSIONS,
        encoder: Optional[BaseEncoder] = None,
        enable_rerank: bool = False,
        namespace: Optional[str] = settings.VECTOR_DB_DEFAULT_NAMESPACE,
    ):
        super().__init__(
            index_name=index_name,
            dimension=dimension,
            credentials=credentials,
            encoder=encoder,
            enable_rerank=enable_rerank,
            namespace=namespace,
        )

        self.client = QdrantClient(
            credentials["host"], api_key=credentials["api_key"], https=False
        )

        collections = self.client.get_collections()
        if index_name not in [c.name for c in collections.collections]:
            self.client.create_collection(
                collection_name=self.index_name,
                vectors_config={
                    "page_content": rest.VectorParams(
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
                    vector={"page_content": chunk.dense_embedding},
                    payload={
                        "page_content": chunk.page_content,
                        "namespace": chunk.namespace,
                        "metadata": chunk.metadata
                    },
                )
            )

        self.client.upsert(collection_name=self.index_name, wait=True, points=points)

    async def query(
        self,
        input: str,
        top_k: int = settings.MAX_QUERY_TOP_K,
        namespace: Optional[str] = None,
    ) -> List:
        vectors = await self._generate_vectors(input=input)
        if not namespace:
            namespace = self.namespace

        search_result = self.client.search(
            collection_name=self.index_name,
            query_vector=("page_content", vectors[0]),
            limit=top_k,
            with_payload=True,
            query_filter=qdrant_models.Filter(
                must=[
                    qdrant_models.FieldCondition(
                        key="namespace",
                        match=qdrant_models.MatchValue(
                            value=namespace,
                        ),
                    )
                ]
            ),
        )
        return [
            BaseDocumentChunk(
                id=result.id,
                page_content=result.payload.get("page_content", ""),
                namespace=result.payload.get("namespace"),
                metadata={k: v for k, v in result.payload.items() if k not in ["page_content", "namespace"]}
            )
            for result in search_result
        ]

    async def delete(
        self, file_id: str, assistant_id: Optional[str] = None
    ) -> DeleteDocumentsResponse:
        must_conditions = [
            rest.FieldCondition(
                key="metadata.file_id", match=rest.MatchValue(value=str(file_id))
            )
        ]
        if assistant_id:
            must_conditions.append(
                rest.FieldCondition(
                    key="metadata.namespace",
                    match=rest.MatchValue(value=str(assistant_id)),
                )
            )

        common_filter = rest.Filter(must=must_conditions)

        deleted_chunks = self.client.count(
            collection_name=self.index_name,
            count_filter=common_filter,
            exact=True,
        )
        logger.info(f"Preparing to delete {deleted_chunks.count} chunks")

        self.client.delete(
            collection_name=self.index_name,
            points_selector=rest.FilterSelector(filter=common_filter),
        )

        return DeleteDocumentsResponse(num_deleted_chunks=deleted_chunks.count)

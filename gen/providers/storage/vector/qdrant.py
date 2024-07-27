from typing import Any, Optional, Union, List
from pydantic import Field
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from gen.providers.storage.vector.base_vector_db import BaseVectorDatabase, VectorEntry, VectorSearchResult, DatabaseConfig

class QdrantConfig(DatabaseConfig):
    host: str = Field(..., description="Qdrant server host")
    port: int = Field(6333, description="Qdrant server port")
    api_key: Optional[str] = Field(None, description="API key for Qdrant")
    https: bool = Field(False, description="Whether to use HTTPS")
    collection_name: str = Field(..., description="Name of the Qdrant collection")

    @property
    def supported_providers(self) -> list[str]:
        return ["qdrant"]

    def validate(self) -> None:
        super().validate()
        if not self.host:
            raise ValueError("Qdrant host must be provided")
        if not self.collection_name:
            raise ValueError("Collection name must be provided")

class Qdrant(BaseVectorDatabase):
    def __init__(self, config: QdrantConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.client = QdrantClient(
            host=config.host,
            port=config.port,
            api_key=config.api_key,
            https=config.https
        )
        self.collection_name = config.collection_name

    def _initialize_vector_db(self, dimension: int) -> None:
        collections = self.client.get_collections()
        if self.collection_name not in [c.name for c in collections.collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "page_content": rest.VectorParams(
                        size=dimension, distance=rest.Distance.COSINE
                    )
                },
                optimizers_config=rest.OptimizersConfigDiff(
                    indexing_threshold=0,
                ),
            )

    def copy(self, entry: VectorEntry, commit: bool = True) -> None:
        # In Qdrant, copy is the same as upsert
        self.upsert(entry, commit)

    def upsert(self, entry: VectorEntry, commit: bool = True) -> None:
        point = rest.PointStruct(
            id=str(entry.id),
            vector={"page_content": entry.vector.data},
            payload={
                "document_id": entry.metadata.get("document_id", ""),
                "page_content": entry.metadata.get("page_content", ""),
                "source": entry.metadata.get("source", ""),
                "namespace": entry.metadata.get("namespace", ""),
                "file_id": entry.metadata.get("file_id", ""),
                "chunk_index": entry.metadata.get("chunk_index", ""),
                "metadata": entry.metadata,
            },
        )
        self.client.upsert(collection_name=self.collection_name, wait=commit, points=[point])

    def search(
        self,
        query_vector: list[float],
        filters: dict[str, Union[bool, int, str]] = {},
        limit: int = 10,
        *args,
        **kwargs,
    ) -> list[VectorSearchResult]:
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=("page_content", query_vector),
            limit=limit,
            query_filter=self._build_filter(filters),
            with_payload=True,
        )
        return [
            VectorSearchResult(
                id=result.id,
                score=result.score,
                metadata=result.payload.get("metadata", {})
            )
            for result in search_result
        ]

    # def hybrid_search(
    #     self,
    #     query_text: str,
    #     query_vector: list[float],
    #     limit: int = 10,
    #     filters: Optional[dict[str, Union[bool, int, str]]] = None,
    #     full_text_weight: float = 1.0,
    #     semantic_weight: float = 1.0,
    #     rrf_k: int = 20,
    #     *args,
    #     **kwargs,
    # ) -> list[VectorSearchResult]:
    #     search_result = self.client.search(
    #         collection_name=self.collection_name,
    #         query_vector=("page_content", query_vector),
    #         query_text=query_text,
    #         limit=limit,
    #         query_filter=self._build_filter(filters) if filters else None,
    #         with_payload=True,
    #         score_threshold=None,
    #         hybrid_weights=(full_text_weight, semantic_weight),
    #     )
    #     return [
    #         VectorSearchResult(
    #             id=result.id,
    #             score=result.score,
    #             metadata=result.payload.get("metadata", {})
    #         )
    #         for result in search_result
    #     ]

        # from qdrant_client.http import models as rest

    def hybrid_search(
        self,
        query_text: str,
        query_vector: list[float],
        limit: int = 10,
        filters: Optional[dict[str, Union[bool, int, str]]] = None,
        full_text_weight: float = 1.0,
        semantic_weight: float = 1.0,
        *args,
        **kwargs,
    ) -> list[VectorSearchResult]:
        # NOTE: Qdrant does not support text-based search, will require experimentation on this
        # Combine text search with vector search using Qdrant's filtering
        text_filter = rest.Filter(
            must=[
                rest.FieldCondition(
                    key="page_content",
                    match=rest.MatchText(text=query_text)
                )
            ]
        )

        # Combine with any existing filters
        if filters:
            for key, value in filters.items():
                text_filter.must.append(
                    rest.FieldCondition(
                        key=key,
                        match=rest.MatchValue(value=value)
                    )
                )

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=text_filter,
            limit=limit,
            with_payload=True,
            score_threshold=None,
        )

        # Convert to VectorSearchResult objects
        results = [
            VectorSearchResult(
                id=result.id,
                score=result.score,
                metadata=result.payload or {}
            )
            for result in search_result
        ]

        return results

    def create_index(self, index_type, column_name, index_options):
        # Qdrant automatically creates necessary indexes, so this method might not be needed
        pass

    def delete_by_metadata(
        self,
        metadata_fields: list[str],
        metadata_values: list[Union[bool, int, str]],
    ) -> list[str]:
        filter_conditions = [
            rest.FieldCondition(key=field, match=rest.MatchValue(value=value))
            for field, value in zip(metadata_fields, metadata_values)
        ]
        response = self.client.delete(
            collection_name=self.collection_name,
            points_selector=rest.FilterSelector(filter=rest.Filter(must=filter_conditions)),
        )
        return [str(id) for id in response.result]

    def get_metadatas(
        self,
        metadata_fields: list[str],
        filter_field: Optional[str] = None,
        filter_value: Optional[str] = None,
    ) -> list[str]:
        query_filter = None
        if filter_field and filter_value:
            query_filter = rest.Filter(
                must=[rest.FieldCondition(key=filter_field, match=rest.MatchValue(value=filter_value))]
            )

        response = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=query_filter,
            limit=10000,  # Adjust based on your needs
            with_payload=metadata_fields,
        )

        return [
            {field: point.payload.get(field) for field in metadata_fields}
            for point in response[0]
        ]

    def get_document_chunks(self, document_id: str) -> list[dict]:
        response = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=rest.Filter(
                must=[rest.FieldCondition(key="document_id", match=rest.MatchValue(value=document_id))]
            ),
            with_payload=True,
        )
        return [point.payload for point in response[0]]

    def _build_filter(self, filters: dict[str, Union[bool, int, str]]) -> rest.Filter:
        conditions = [
            rest.FieldCondition(key=key, match=rest.MatchValue(value=value))
            for key, value in filters.items()
        ]
        return rest.Filter(must=conditions) if conditions else None

    async def rerank(
        self, query: str, documents: list[VectorSearchResult], top_n: int = 5
    ) -> list[VectorSearchResult]:
        # Implement reranking logic here if needed
        # For now, just return the input documents
        return documents[:top_n]

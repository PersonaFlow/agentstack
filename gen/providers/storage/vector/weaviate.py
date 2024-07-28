import uuid
from typing import Any, Dict, List, Optional, Union
from weaviate import Client
from weaviate.util import generate_uuid5
from weaviate.exceptions import WeaviateException
from .base_vector_db import BaseVectorDatabase, VectorEntry, VectorSearchResult, DatabaseConfig

class WeaviateConfig(DatabaseConfig):
    host: str
    api_key: Optional[str] = None
    schema: Optional[Dict[str, Any]] = None
    class_name: str = "Vector"

    @property
    def supported_providers(self) -> List[str]:
        return ["weaviate"]

    def validate(self) -> None:
        super().validate()
        if not self.host:
            raise ValueError("Weaviate host must be provided")

class Weaviate(BaseVectorDatabase):
    def __init__(self, config: WeaviateConfig, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.client = Client(
            url=config.host,
            auth_client_secret=config.api_key,
        )
        self.class_name = config.class_name
        self._initialize_vector_db(kwargs.get("dimension", 0))

    def _initialize_vector_db(self, dimension: int) -> None:
        if not self.client.schema.exists(self.class_name):
            class_obj = {
                "class": self.class_name,
                "vectorizer": "none",
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                    },
                    {
                        "name": "metadata",
                        "dataType": ["object"],
                    },
                ],
            }
            self.client.schema.create_class(class_obj)

    def copy(self, entry: VectorEntry, commit: bool = True) -> None:
        self.upsert(entry, commit)

    def upsert(self, entry: VectorEntry, commit: bool = True) -> None:
        try:
            self.client.data_object.create(
                self.class_name,
                {
                    "content": entry.metadata.get("content", ""),
                    "metadata": entry.metadata,
                },
                entry.id,
                vector=entry.vector.data,
            )
        except WeaviateException as e:
            raise ValueError(f"Error upserting to Weaviate: {str(e)}")

    def search(
        self,
        query_vector: List[float],
        filters: Dict[str, Union[bool, int, str]] = {},
        limit: int = 10,
        *args,
        **kwargs,
    ) -> List[VectorSearchResult]:
        try:
            query = (
                self.client.query
                .get(self.class_name, ["content", "metadata"])
                .with_near_vector({
                    "vector": query_vector,
                })
                .with_limit(limit)
            )

            if filters:
                where_filter = self._build_weaviate_filter(filters)
                query = query.with_where(where_filter)

            results = query.do()

            return [
                VectorSearchResult(
                    id=item["_additional"]["id"],
                    score=item["_additional"]["certainty"],
                    metadata=item["metadata"]
                )
                for item in results["data"]["Get"][self.class_name]
            ]
        except WeaviateException as e:
            raise ValueError(f"Error searching Weaviate: {str(e)}")

    def hybrid_search(
        self,
        query_text: str,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Union[bool, int, str]]] = None,
        full_text_weight: float = 1.0,
        semantic_weight: float = 1.0,
        *args,
        **kwargs,
    ) -> List[VectorSearchResult]:
        try:
            query = (
                self.client.query
                .get(self.class_name, ["content", "metadata"])
                .with_hybrid(
                    query=query_text,
                    vector=query_vector,
                    alpha=semantic_weight / (full_text_weight + semantic_weight)
                )
                .with_limit(limit)
            )

            if filters:
                where_filter = self._build_weaviate_filter(filters)
                query = query.with_where(where_filter)

            results = query.do()

            return [
                VectorSearchResult(
                    id=item["_additional"]["id"],
                    score=item["_additional"]["score"],
                    metadata=item["metadata"]
                )
                for item in results["data"]["Get"][self.class_name]
            ]
        except WeaviateException as e:
            raise ValueError(f"Error performing hybrid search in Weaviate: {str(e)}")

    def create_index(self, index_type, column_name, index_options):
        # Weaviate automatically creates and manages indexes
        pass

    def delete_by_metadata(
        self,
        metadata_fields: List[str],
        metadata_values: List[Union[bool, int, str]],
    ) -> List[str]:
        where_filter = {
            "operator": "And",
            "operands": [
                {
                    "path": [field],
                    "operator": "Equal",
                    "valueString": str(value)
                }
                for field, value in zip(metadata_fields, metadata_values)
            ]
        }

        try:
            result = self.client.batch.delete_objects(
                class_name=self.class_name,
                where=where_filter
            )
            return [str(uuid) for uuid in result]
        except WeaviateException as e:
            raise ValueError(f"Error deleting objects from Weaviate: {str(e)}")

    def get_metadatas(
        self,
        metadata_fields: List[str],
        filter_field: Optional[str] = None,
        filter_value: Optional[str] = None,
    ) -> List[str]:
        query = (
            self.client.query
            .get(self.class_name, metadata_fields)
        )

        if filter_field and filter_value:
            query = query.with_where({
                "path": [filter_field],
                "operator": "Equal",
                "valueString": filter_value
            })

        try:
            results = query.do()
            return [
                {field: item.get(field) for field in metadata_fields}
                for item in results["data"]["Get"][self.class_name]
            ]
        except WeaviateException as e:
            raise ValueError(f"Error getting metadata from Weaviate: {str(e)}")

    def get_document_chunks(self, document_id: str) -> List[Dict]:
        query = (
            self.client.query
            .get(self.class_name, ["content", "metadata"])
            .with_where({
                "path": ["metadata", "document_id"],
                "operator": "Equal",
                "valueString": document_id
            })
        )

        try:
            results = query.do()
            return [
                {
                    "content": item["content"],
                    **item["metadata"]
                }
                for item in results["data"]["Get"][self.class_name]
            ]
        except WeaviateException as e:
            raise ValueError(f"Error getting document chunks from Weaviate: {str(e)}")

    def _build_weaviate_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        operands = []
        for key, value in filters.items():
            if isinstance(value, dict):
                operator, val = next(iter(value.items()))
                if operator == "$eq":
                    operands.append({"path": [key], "operator": "Equal", "valueString": str(val)})
                elif operator == "$ne":
                    operands.append({"path": [key], "operator": "NotEqual", "valueString": str(val)})
                elif operator == "$gt":
                    operands.append({"path": [key], "operator": "GreaterThan", "valueNumber": val})
                elif operator == "$gte":
                    operands.append({"path": [key], "operator": "GreaterThanEqual", "valueNumber": val})
                elif operator == "$lt":
                    operands.append({"path": [key], "operator": "LessThan", "valueNumber": val})
                elif operator == "$lte":
                    operands.append({"path": [key], "operator": "LessThanEqual", "valueNumber": val})
                elif operator == "$in":
                    operands.append({"path": [key], "operator": "ContainsAny", "valueString": val})
            else:
                operands.append({"path": [key], "operator": "Equal", "valueString": str(value)})

        return {"operator": "And", "operands": operands}

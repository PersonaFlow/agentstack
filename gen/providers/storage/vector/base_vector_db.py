import uuid
from pydantic import BaseModel
from enum import Enum
from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from uuid import UUID
from gen.providers.base_provider import BaseProvider, ProviderConfig

class VectorType(Enum):
    FIXED = "FIXED"

class VectorSearchResult(BaseModel):
    """Result of a search operation."""

    id: uuid.UUID
    score: float
    metadata: dict[str, Any]

    def __str__(self) -> str:
        return f"VectorSearchResult(id={self.id}, score={self.score}, metadata={self.metadata})"

    def __repr__(self) -> str:
        return f"VectorSearchResult(id={self.id}, score={self.score}, metadata={self.metadata})"

    def dict(self) -> dict:
        return {
            "id": self.id,
            "score": self.score,
            "metadata": self.metadata,
        }


class Vector:
    """A vector with the option to fix the number of elements."""

    def __init__(
        self,
        data: list[float],
        type: VectorType = VectorType.FIXED,
        length: int = -1,
    ):
        self.data = data
        self.type = type
        self.length = length

        if (
            self.type == VectorType.FIXED
            and length > 0
            and len(data) != length
        ):
            raise ValueError(f"Vector must be exactly {length} elements long.")

    def __repr__(self) -> str:
        return (
            f"Vector(data={self.data}, type={self.type}, length={self.length})"
        )

class VectorEntry:
    """A vector entry that can be stored directly in supported vector databases."""

    def __init__(self, id: UUID, vector: Vector, metadata: dict[str, Any]):
        """Create a new VectorEntry object."""
        self.vector = vector
        self.id = id
        self.metadata = metadata

    def to_serializable(self) -> str:
        """Return a serializable representation of the VectorEntry."""
        metadata = self.metadata

        for key in metadata:
            if isinstance(metadata[key], UUID):
                metadata[key] = str(metadata[key])
        return {
            "id": str(self.id),
            "vector": self.vector.data,
            "metadata": metadata,
        }

    def __str__(self) -> str:
        """Return a string representation of the VectorEntry."""
        return f"VectorEntry(id={self.id}, vector={self.vector}, metadata={self.metadata})"

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the VectorEntry."""
        return f"VectorEntry(id={self.id}, vector={self.vector}, metadata={self.metadata})"


class DatabaseConfig(ProviderConfig):
    provider: str

    def __post_init__(self):
        self.validate()
        # Capture additional fields
        for key, value in self.extra_fields.items():
            setattr(self, key, value)

    def validate(self) -> None:
        if self.provider not in self.supported_providers:
            raise ValueError(f"Provider '{self.provider}' is not supported.")

    @property
    def supported_providers(self) -> list[str]:
        return ["qdrant"]

class BaseVectorDatabase(BaseProvider, ABC):

    @abstractmethod
    def _initialize_vector_db(self, dimension: int) -> None:
        pass

    @abstractmethod
    def copy(self, entry: VectorEntry, commit: bool = True) -> None:
        pass

    @abstractmethod
    def upsert(self, entry: VectorEntry, commit: bool = True) -> None:
        pass

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        filters: dict[str, Union[bool, int, str]] = {},
        limit: int = 10,
        *args,
        **kwargs,
    ) -> list[VectorSearchResult]:
        pass

    @abstractmethod
    def hybrid_search(
        self,
        query_text: str,
        query_vector: list[float],
        limit: int = 10,
        filters: Optional[dict[str, Union[bool, int, str]]] = None,
        full_text_weight: float = 1.0,
        semantic_weight: float = 1.0,
        rrf_k: int = 20,
        *args,
        **kwargs,
    ) -> list[VectorSearchResult]:
        pass

    @abstractmethod
    def create_index(self, index_type, column_name, index_options):
        pass

    @abstractmethod
    def delete_by_metadata(
        self,
        metadata_fields: list[str],
        metadata_values: list[Union[bool, int, str]],
    ) -> list[str]:
        pass

    @abstractmethod
    def get_metadatas(
        self,
        metadata_fields: list[str],
        filter_field: Optional[str] = None,
        filter_value: Optional[str] = None,
    ) -> list[str]:
        pass

    def upsert_entries(
        self, entries: list[VectorEntry], commit: bool = True
    ) -> None:
        for entry in entries:
            self.upsert(entry, commit=commit)

    def copy_entries(
        self, entries: list[VectorEntry], commit: bool = True
    ) -> None:
        for entry in entries:
            self.copy(entry, commit=commit)

    @abstractmethod
    def get_document_chunks(self, document_id: str) -> list[dict]:
        pass

    async def rerank(
        self, query: str, documents: list[VectorSearchResult], top_n: int = 5
    ) -> list[VectorSearchResult]:
        return documents

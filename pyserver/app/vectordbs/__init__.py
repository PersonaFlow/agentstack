from typing import Optional

from dotenv import load_dotenv
from semantic_router.encoders import BaseEncoder
from semantic_router.encoders.cohere import CohereEncoder

from app.schema.rag import VectorDatabase
from app.vectordbs.base import BaseVectorDatabase
from app.vectordbs.qdrant import QdrantService

load_dotenv()


def get_vector_service(
    *,
    index_name: str,
    credentials: VectorDatabase,
    encoder: BaseEncoder = CohereEncoder(),
    dimensions: Optional[int] = 384,
    enable_rerank: bool = False,
) -> BaseVectorDatabase:
    services = {
        "qdrant": QdrantService,
        # Add other providers here
    }
    
    service = services.get(credentials.type.value)

    if service is None:
        raise ValueError(f"Unsupported provider: {credentials.type.value}")

    return service(
        index_name=index_name,
        dimension=dimensions,
        credentials=dict(credentials.config),
        encoder=encoder,
        enable_rerank=enable_rerank,
    )

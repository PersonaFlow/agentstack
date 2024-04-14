from typing import Optional
from dotenv import load_dotenv
from semantic_router.encoders import BaseEncoder
from app.schema.rag import VectorDatabase, EncoderConfig, EncoderProvider
from app.vectordbs.base import BaseVectorDatabase
from app.vectordbs.qdrant import QdrantService
from app.core.configuration import get_settings

load_dotenv()
settings = get_settings()

def get_vector_service(
    *,
    index_name: str,
    credentials: VectorDatabase = VectorDatabase(),
    encoder_provider: EncoderProvider = EncoderProvider(settings.VECTOR_DB_ENCODER_NAME),
    encoder: BaseEncoder = None,
    dimensions: int = settings.VECTOR_DB_ENCODER_DIMENSIONS,
    enable_rerank: bool = settings.ENABLE_RERANK_BY_DEFAULT,
) -> BaseVectorDatabase:
    services = {
        "qdrant": QdrantService,
        # Add other providers here
    }

    service = services.get(credentials.type)
    if service is None:
        raise ValueError(f"Unsupported provider: {credentials.type}")

    encoder_config = EncoderConfig.get_encoder_config(encoder_provider)
    if encoder_config is None:
        raise ValueError(f"Unsupported encoder provider: {encoder_provider}")

    if encoder is None:
        encoder_class = encoder_config["class"]
        if not issubclass(encoder_class, BaseEncoder):
            raise ValueError(f"Encoder class {encoder_class} is not a subclass of BaseEncoder")
        encoder: BaseEncoder = encoder_class()

    return service(
        index_name=index_name,
        dimension=dimensions,
        credentials=dict(credentials.config),
        encoder=encoder,
        enable_rerank=enable_rerank,
    )

from typing import Optional
from dotenv import load_dotenv
from semantic_router.encoders import BaseEncoder
from stack.app.schema.rag import (
    VectorDatabase,
    VectorDatabaseType,
    EncoderConfig,
    EncoderProvider,
)
from stack.app.vectordbs.base import BaseVectorDatabase
from stack.app.vectordbs.qdrant import QdrantService
from stack.app.core.configuration import get_settings

load_dotenv()
settings = get_settings()


def get_vector_service(
    *,
    index_name: str = settings.VECTOR_DB_COLLECTION_NAME,
    namespace: Optional[str] = settings.VECTOR_DB_DEFAULT_NAMESPACE,
    credentials: Optional[VectorDatabase] = VectorDatabase(),
    encoder_provider: Optional[EncoderProvider] = EncoderProvider(
        settings.VECTOR_DB_ENCODER_NAME
    ),
    encoder: Optional[BaseEncoder] = None,
    dimensions: Optional[int] = settings.VECTOR_DB_ENCODER_DIMENSIONS,
    enable_rerank: Optional[bool] = settings.ENABLE_RERANK_BY_DEFAULT,
) -> BaseVectorDatabase:
    services = {
        VectorDatabaseType.qdrant: QdrantService,
        # Add other providers here
    }

    vector_db = credentials or VectorDatabase()
    # Convert string to enum if necessary
    db_type = (
        VectorDatabaseType(vector_db.type)
        if isinstance(vector_db.type, str)
        else vector_db.type
    )

    service = services.get(db_type)
    if service is None:
        raise ValueError(f"Unsupported provider: {db_type}")

    encoder_config = EncoderConfig.get_encoder_config(encoder_provider)
    if encoder_config is None:
        raise ValueError(f"Unsupported encoder provider: {encoder_provider}")

    if encoder is None:
        encoder_class = encoder_config["class"]
        if not issubclass(encoder_class, BaseEncoder):
            raise ValueError(
                f"Encoder class {encoder_class} is not a subclass of BaseEncoder"
            )
        encoder: BaseEncoder = encoder_class()

    return service(
        index_name=index_name,
        dimension=dimensions,
        credentials=dict(credentials.config),
        encoder=encoder,
        enable_rerank=enable_rerank,
        namespace=namespace,
    )

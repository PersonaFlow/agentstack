from qdrant_client import QdrantClient
from app.core.configuration import get_settings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.qdrant import Qdrant

settings = get_settings()

qdrant_client = QdrantClient(host=settings.VECTOR_DB_HOST, port=settings.VECTOR_DB_PORT)

qdrant_vstore = Qdrant(
        client = qdrant_client,
        collection_name = settings.VECTOR_DB_COLLECTION_NAME,
        embeddings = OpenAIEmbeddings(),
        vector_name = "default"
    )


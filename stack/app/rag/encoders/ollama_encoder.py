from typing import List

from semantic_router.encoders import BaseEncoder
from langchain_community.embeddings.ollama import OllamaEmbeddings

from stack.app.core.configuration import get_settings

settings = get_settings()


def get_ollama_embeddings():
    return OllamaEmbeddings(
        model=settings.VECTOR_DB_ENCODER_MODEL, base_url=settings.OLLAMA_BASE_URL
    )


class OllamaEncoder(BaseEncoder):
    name = "OllamaEncoder"
    score_threshold = 0.5
    type = "ollama"
    embeddings = get_ollama_embeddings()

    def __call__(self, docs: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(docs)

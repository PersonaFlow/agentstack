from typing import List
from pydantic import Field
from semantic_router.encoders import BaseEncoder
from langchain_community.embeddings import OllamaEmbeddings
from stack.app.core.configuration import get_settings

settings = get_settings()

class OllamaEncoder(BaseEncoder):
    name: str = Field(default="all-minilm")
    score_threshold: float = Field(default=0.5)
    type: str = Field(default="ollama")
    dimensions: int = Field(default=384)
    embeddings: OllamaEmbeddings = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if 'name' in data:
            self.embeddings = OllamaEmbeddings(
                model=self.name,
                base_url=settings.OLLAMA_BASE_URL
            )

    def __call__(self, docs: List[str]) -> List[List[float]]:
        return self.embeddings.embed_documents(docs)


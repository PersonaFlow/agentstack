from abc import ABC, abstractmethod

from semantic_router.encoders import BaseEncoder
from tqdm import tqdm

from stack.app.schema.rag import DeleteDocumentsResponse, BaseDocumentChunk
import structlog
from stack.app.core.configuration import get_settings

logger = structlog.get_logger()

settings = get_settings()


class BaseVectorDatabase(ABC):
    def __init__(
        self,
        index_name: str,
        dimension: int,
        credentials: dict,
        encoder: BaseEncoder,
        enable_rerank: bool,
        namespace: str,
    ):
        self.index_name = index_name
        self.dimension = dimension
        self.credentials = credentials
        self.encoder = encoder
        self.enable_rerank = enable_rerank
        self.namespace = namespace

    @abstractmethod
    async def upsert(self, chunks: list[BaseDocumentChunk]):
        pass

    @abstractmethod
    async def query(self, input: str, top_k: int = 25) -> list[BaseDocumentChunk]:
        pass

    @abstractmethod
    async def delete(
        self, file_id: str, assistant_id: str = None
    ) -> DeleteDocumentsResponse:
        pass

    async def _generate_vectors(self, input: str) -> list[list[float]]:
        return self.encoder([input])

    async def rerank(
        self, query: str, documents: list[BaseDocumentChunk], top_n: int = 5
    ) -> list[BaseDocumentChunk]:
        if not self.enable_rerank:
            return documents

        from cohere import Client

        api_key = settings.COHERE_API_KEY
        if not api_key:
            raise ValueError("API key for Cohere is not present.")
        cohere_client = Client(api_key=api_key)

        # Avoid duplications, TODO: fix ingestion for duplications
        # Deduplicate documents based on content while preserving order
        seen = set()
        deduplicated_documents = [
            doc
            for doc in documents
            if doc.page_content not in seen and not seen.add(doc.page_content)
        ]
        docs_text = list(
            doc.page_content
            for doc in tqdm(
                deduplicated_documents,
                desc=f"Reranking {len(deduplicated_documents)} documents",
            )
        )
        try:
            re_ranked = cohere_client.rerank(
                model="rerank-multilingual-v2.0",
                query=query,
                documents=docs_text,
                top_n=top_n,
            ).results
            results = []
            for r in tqdm(re_ranked, desc="Processing reranked results "):
                doc = deduplicated_documents[r.index]
                results.append(doc)
            return results
        except Exception as e:
            logger.error(f"Error while reranking: {e}")
            raise Exception(f"Error while reranking: {e}")

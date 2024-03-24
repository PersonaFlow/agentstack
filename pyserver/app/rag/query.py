import structlog
from semantic_router.encoders import CohereEncoder
from semantic_router.layer import RouteLayer
from semantic_router.route import Route

from app.schema.rag import BaseDocumentChunk, QueryRequestPayload
from .summarizer import SUMMARY_SUFFIX
from app.vectordbs import BaseVectorDatabase, get_vector_service

from app.core.configuration import get_settings

STRUCTURED_DATA = [
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
    "application/json",
]

logger = structlog.get_logger()
settings = get_settings()

def create_route_layer() -> RouteLayer:
    routes = [
        Route(
            name="summarize",
            utterances=[
                "Summmarize the following",
                "Could you summarize the",
                "Summarize",
                "Provide a summary of",
            ],
            score_threshold=0.5,
        )
    ]
    cohere_api_key = settings.COHERE_API_KEY
    encoder = CohereEncoder(cohere_api_key=cohere_api_key) if cohere_api_key else None
    return RouteLayer(encoder=encoder, routes=routes)


async def get_documents(
    *, vector_service: BaseVectorDatabase, payload: QueryRequestPayload
) -> list[BaseDocumentChunk]:
    chunks = await vector_service.query(input=payload.input, top_k=5)
    if not len(chunks):
        logger.error(f"No documents found for query: {payload.input}")
        return []

    reranked_chunks = []

    reranked_chunks.extend(
        await vector_service.rerank(query=payload.input, documents=chunks)
    )
    return reranked_chunks


async def query(payload: QueryRequestPayload) -> list[BaseDocumentChunk]:
    rl = create_route_layer()
    decision = rl(payload.input).name
    encoder = payload.encoder.get_encoder()

    if decision == "summarize":
        vector_service: BaseVectorDatabase = get_vector_service(
            index_name=f"{payload.index_name}{SUMMARY_SUFFIX}",
            credentials=payload.vector_database,
            encoder=encoder,
        )
        return await get_documents(vector_service=vector_service, payload=payload)

    vector_service: BaseVectorDatabase = get_vector_service(
        index_name=payload.index_name,
        credentials=payload.vector_database,
        encoder=encoder,
    )

    return await get_documents(vector_service=vector_service, payload=payload)

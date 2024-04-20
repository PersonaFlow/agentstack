import structlog
from semantic_router.layer import RouteLayer
from semantic_router.route import Route
from semantic_router.encoders import BaseEncoder

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

def create_route_layer(encoder: BaseEncoder) -> RouteLayer:
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
    return RouteLayer(encoder=encoder, routes=routes)

async def get_documents(
    *, vector_service: BaseVectorDatabase, payload: QueryRequestPayload
) -> list[BaseDocumentChunk]:
    chunks = await vector_service.query(input=payload.input, top_k=5)
    if not len(chunks):
        await logger.info(f"No documents found for query: {payload.input}")
        return []

    if not payload.enable_rerank:
        return chunks

    reranked_chunks = []
    reranked_chunks.extend(
        await vector_service.rerank(query=payload.input, documents=chunks)
    )
    return reranked_chunks


async def query_documents(payload: QueryRequestPayload) -> list[BaseDocumentChunk]:
    encoder = payload.encoder.get_encoder()
    rl = create_route_layer(encoder)
    decision = rl(payload.input).name

    vector_service: BaseVectorDatabase = get_vector_service(
        index_name=f"{payload.index_name}_{SUMMARY_SUFFIX}" if decision == "summarize" else payload.index_name,
        credentials=payload.vector_database,
        encoder=encoder,
        namespace=payload.namespace,
    )
    return await get_documents(vector_service=vector_service, payload=payload)

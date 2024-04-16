
from app.schema.rag import IngestRequestPayload
from app.rag.embedding_service import EmbeddingService
from app.rag.summarizer import SUMMARY_SUFFIX
from app.rag.query import query_documents
from app.core.configuration import get_settings
from app.schema.file import FileSchema
import structlog


logger = structlog.get_logger()
settings = get_settings()


async def get_ingest_tasks_from_config(
    files_to_ingest: list[FileSchema],
    config: IngestRequestPayload,
) -> list:
    vector_db_creds = config.vector_database
    document_processor_config = config.document_processor
    encoder = document_processor_config.encoder.get_encoder()
    collection_name = config.index_name
    namespace = config.namespace if config.namespace else settings.VECTOR_DB_DEFAULT_NAMESPACE

    embedding_service = EmbeddingService(
        encoder=encoder,
        index_name=collection_name,
        vector_credentials=vector_db_creds,
        dimensions=document_processor_config.encoder.dimensions,
        files=files_to_ingest,
        namespace=namespace
    )

    chunks = await embedding_service.generate_chunks(config=document_processor_config)

    summary_documents = None
    if document_processor_config.summarize:
        summary_documents = await embedding_service.generate_summary_documents(documents=chunks)

    tasks = [
        embedding_service.embed_and_upsert(
            chunks=chunks, encoder=encoder, index_name=collection_name
        ),
    ]

    if summary_documents and all(item is not None for item in summary_documents):
        tasks.append(
            embedding_service.embed_and_upsert(
                chunks=summary_documents,
                encoder=encoder,
                index_name=f"{collection_name}_{SUMMARY_SUFFIX}",
            )
        )

    return tasks

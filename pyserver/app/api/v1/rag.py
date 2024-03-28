import orjson
import asyncio
import aiohttp
from fastapi import APIRouter, Form, UploadFile, File
from app.api.annotations import ApiKey
from app.schema.rag import (
  IngestRequestPayload,
  QueryRequestPayload,
  QueryResponsePayload,
  IngestFile,
  DocumentProcessorConfig
)
from app.rag.ingest_runnable import ingest_runnable
from app.rag.embedding_service import EmbeddingService
from app.rag.summarizer import SUMMARY_SUFFIX
from app.rag.query import query as _query
from app.core.configuration import get_settings
from app.schema.rag import VectorDatabase

router = APIRouter()
DEFAULT_TAG = "RAG"

@router.post("/ingest", tags=[DEFAULT_TAG],
             summary="Ingest files to be indexed and queried.",
             description="""
              Upload files for ingesting using the advanced RAG system with unstructured library. <br>
              This API is agnostic of the assistant and includes a /query api to query the indexes. <br>
              Files can either be provided as an array of URLs within the payload or uploaded via multipart form data. <br>
            *Note: the payload string should be an IngestRequestPayload (see app.schema.rag.IngestRequestPayload)*
             """)
async def ingest(
    files: list[UploadFile] = File([], description="List of files to upload."),
    payload: str = Form(..., description="Ingest request payload as JSON string. (see README for example)"),
) -> dict:
    settings = get_settings()

    payload_dict = orjson.loads(payload)
    payload_obj = IngestRequestPayload(**payload_dict)
    vector_db_creds = payload_obj.vector_database if payload_obj.vector_database else VectorDatabase(**settings.VECTOR_DB_CREDENTIALS)

    encoder = payload_obj.document_processor.encoder.get_encoder()
    embedding_service = EmbeddingService(
        encoder=encoder,
        index_name=payload_obj.index_name,
        vector_credentials=vector_db_creds,
        dimensions=payload_obj.document_processor.encoder.dimensions,
    )
    upload_ingest_files = [IngestFile.from_upload_file(file) for file in files]
    url_ingest_files = [IngestFile.from_url(file.url) for file in payload_obj.files] if payload_obj.files else []

    all_ingest_files = url_ingest_files + upload_ingest_files

    chunks, summary_documents = await handle_files(
        embedding_service=embedding_service,
        files=all_ingest_files,
        config=payload_obj.document_processor,
    )
    tasks = [
        embedding_service.embed_and_upsert(
            chunks=chunks, encoder=encoder, index_name=payload_obj.index_name
        ),
    ]
    if summary_documents and all(item is not None for item in summary_documents):
        tasks.append(
            embedding_service.embed_and_upsert(
                chunks=summary_documents,
                encoder=encoder,
                index_name=f"{payload_obj.index_name}{SUMMARY_SUFFIX}",
            )
        )
    await asyncio.gather(*tasks)

    # Optionally notify via webhook if specified
    if payload_obj.webhook_url:
        await notify_webhook(payload_obj)

    return {"success": True, "index_name": payload_obj.index_name}

async def handle_files(
    *,
    embedding_service: EmbeddingService,
    files: list[IngestFile],
    config: DocumentProcessorConfig
) -> tuple[list, list]:
    """Process a mixed list of IngestFile objects for chunking and summarizing."""

    embedding_service.files = files

    chunks = await embedding_service.generate_chunks(config=config)

    if config.summarize:
        summary_documents = await embedding_service.generate_summary_documents(documents=chunks)
        return chunks, summary_documents
    else:
        return chunks, []


async def notify_webhook(payload: IngestRequestPayload):
    if payload.webhook_url:
        async with aiohttp.ClientSession() as session:
            await session.post(
                url=payload.webhook_url,
                json={"index_name": payload.index_name, "status": "completed"},
            )


@router.post("/query", response_model=QueryResponsePayload,
             tags=[DEFAULT_TAG],
             summary="Query documents",
             description="""
              Query ingested documents using advanced RAG system with unstructured library. <br>
             """)
async def query(payload: QueryRequestPayload):
    chunks = await _query(payload=payload)
    response_payload = QueryResponsePayload(success=True, data=chunks)
    response_data = response_payload.model_dump(
        exclude=set(payload.exclude_fields) if payload.exclude_fields else None
    )
    return response_data

@router.post("/assistant/ingest", tags=[DEFAULT_TAG],
             summary="Ingest files for assistant retrieval tool.",
             description="""
             Upload files to the given assistant for ingesting. <br>
             *Config must be a RunnableConfig and include the assistant id.* <br>
             eg. {"configurable":{"assistant_id":"57f9a247-86f3-4d72-8e23-e9b1701dae6c"}}
             """)
async def ingest_files_for_assistant(
    # api_key: ApiKey,
    files: list[UploadFile] = File(..., description="List of files to upload."),
    config: str = Form(..., description="RunnableConfig in JSON format.")

) -> None:
    config = orjson.loads(config)
    return ingest_runnable.batch([file.file for file in files], config)

import uuid
import asyncio
import aiohttp
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.api.annotations import ApiKey
from app.schema.rag import (
  IngestRequestPayload,
  QueryRequestPayload,
  QueryResponsePayload,
)
from app.rag.ingest_runnable import ingest_runnable
from app.rag.embedding_service import EmbeddingService
from app.rag.summarizer import SUMMARY_SUFFIX
from app.rag.query import query as _query
from app.core.configuration import get_settings
from app.schema.rag import VectorDatabase, VectorDatabaseType
from app.repositories.file import FileRepository, get_file_repository
from app.schema.file import FileSchema
import structlog

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()
DEFAULT_TAG = "RAG"


@router.post("/ingest", tags=[DEFAULT_TAG],
             response_model=dict,
             operation_id="ingest_data_from_files",
             summary="Ingest files to be indexed and queried.",
             description="""
              Upload files for ingesting using the advanced RAG system.
             """)
async def ingest(
    api_key: ApiKey,
    payload: IngestRequestPayload,
    file_repository: FileRepository = Depends(get_file_repository)
) -> dict:
    vector_db_creds = payload.vector_database
    document_processor_config = payload.document_processor
    encoder = document_processor_config.encoder.get_encoder()
    collection_name = payload.index_name
    namespace = payload.namespace if payload.namespace else str(uuid.uuid4())
    files_to_ingest = []

    for file_id in payload.files:
        file_model = await file_repository.retrieve_file(file_id)
        file = FileSchema.model_validate(file_model)
        files_to_ingest.append(file)

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

    await asyncio.gather(*tasks)

    # Optionally notify via webhook if specified
    if payload.webhook_url:
        await notify_webhook(payload.webhook_url, collection_name)

    return {"success": True}


async def notify_webhook(webhook_url: str, collection_name: str):
    async with aiohttp.ClientSession() as session:
        await session.post(
            url=webhook_url,
            json={"index_name": collection_name, "status": "completed"},
        )


@router.post("/query",
             response_model=QueryResponsePayload,
             tags=[DEFAULT_TAG],
             operation_id="query_documents",
             summary="Query documents",
             description="""
              Query ingested documents using advanced RAG system with unstructured library. <br>
             """)
async def query(
        api_key: ApiKey,
        payload: QueryRequestPayload
    ):
    chunks = await _query(payload=payload)
    response_payload = QueryResponsePayload(success=True, data=chunks)
    response_data = response_payload.model_dump(
        exclude=set(payload.exclude_fields) if payload.exclude_fields else None
    )
    return response_data



# @router.post("/ingest", tags=[DEFAULT_TAG],
#              operation_id="ingest_data_from_files",
#              summary="Ingest files to be indexed and queried.",
#              description="""
#               Upload files for ingesting using the advanced RAG system with unstructured library. <br>
#               This API is agnostic of the assistant and includes a /query api to query the indexes. <br>
#               Files can either be provided as an array of URLs within the payload or uploaded via multipart form data. <br>
#             *Note: the payload string should be an IngestRequestPayload (see app.schema.rag.IngestRequestPayload)*
#              """)
# async def ingest(
#     api_key: ApiKey,
#     files: list[UploadFile] = File([], description="List of files to upload."),
#     payload: str = Form(..., description="Ingest request payload as JSON string. (see README for example)"),
# ) -> dict:
#     settings = get_settings()

#     payload_dict = orjson.loads(payload)
#     payload_obj = IngestRequestPayload(**payload_dict)
#     vector_db_creds = payload_obj.vector_database if payload_obj.vector_database else VectorDatabase(**settings.VECTOR_DB_CREDENTIALS)

#     encoder = payload_obj.document_processor.encoder.get_encoder()
#     embedding_service = EmbeddingService(
#         encoder=encoder,
#         index_name=payload_obj.index_name,
#         vector_credentials=vector_db_creds,
#         dimensions=payload_obj.document_processor.encoder.dimensions,
#     )
#     upload_ingest_files = [IngestFile.from_upload_file(file) for file in files]
#     url_ingest_files = [IngestFile.from_url(file.url) for file in payload_obj.files] if payload_obj.files else []

#     all_ingest_files = url_ingest_files + upload_ingest_files

#     chunks, summary_documents = await handle_files(
#         embedding_service=embedding_service,
#         files=all_ingest_files,
#         config=payload_obj.document_processor,
#     )
#     tasks = [
#         embedding_service.embed_and_upsert(
#             chunks=chunks, encoder=encoder, index_name=payload_obj.index_name
#         ),
#     ]
#     if summary_documents and all(item is not None for item in summary_documents):
#         tasks.append(
#             embedding_service.embed_and_upsert(
#                 chunks=summary_documents,
#                 encoder=encoder,
#                 index_name=f"{payload_obj.index_name}{SUMMARY_SUFFIX}",
#             )
#         )
#     await asyncio.gather(*tasks)

#     # Optionally notify via webhook if specified
#     if payload_obj.webhook_url:
#         await notify_webhook(payload_obj)

#     return {"success": True, "index_name": payload_obj.index_name}

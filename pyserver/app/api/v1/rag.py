import asyncio
import aiohttp
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from app.api.annotations import ApiKey
from app.schema.rag import (
  IngestRequestPayload,
  QueryRequestPayload,
  QueryResponsePayload,
  ContextType,
)
from app.repositories.assistant import get_assistant_repository, AssistantRepository
from app.rag.ingest_runnable import ingest_runnable
from app.rag.embedding_service import EmbeddingService
from app.rag.summarizer import SUMMARY_SUFFIX
from app.rag.query import query_documents
from app.core.configuration import get_settings
from app.repositories.file import FileRepository, get_file_repository
from app.schema.file import FileSchema
import structlog
from app.rag.custom_retriever import Retriever
from app.rag.ingest import get_ingest_tasks_from_config

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
    file_repository: FileRepository = Depends(get_file_repository),
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
) -> dict:
    files_to_ingest = []
    try:
        for file_id in payload.files:
            file_model = await file_repository.retrieve_file(file_id)
            file = FileSchema.model_validate(file_model)
            files_to_ingest.append(file)

        tasks = await get_ingest_tasks_from_config(files_to_ingest, payload)

        await asyncio.gather(*tasks)

        # TODO: if payload.purpose == ContextType.assistants, update the assistant
            # if payload.purpose == ContextType.assistants:
        #     tasks.append(
        #         assistant_repository.add_files_to_assistant(
        #             payload.namespace,
        #             files_to_ingest
        #         )
        #     )

        if payload.webhook_url:
            await notify_webhook(payload.webhook_url, payload.index_name, payload.namespace, payload.files)

        # TODO: return stats from ingestion
        return {"success": True}
    except Exception as e:
        await logger.exception(f"Error ingesting files: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while ingesting the files.")


async def notify_webhook(webhook_url: str, collection_name: str, namespace: str, file_ids: list[str]):
    async with aiohttp.ClientSession() as session:
        await session.post(
            url=webhook_url,
            json={"index_name": collection_name, "status": "completed", "namespace": namespace, "file_ids": file_ids},
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
    try:
        chunks = await query_documents(payload=payload)
        response_payload = QueryResponsePayload(success=True, data=chunks)
        response_data = response_payload.model_dump(
            exclude=set(payload.exclude_fields) if payload.exclude_fields else None
        )
        return response_data
    except HTTPException as e:
        await logger.exception(f"Error querying vector database: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        await logger.exception(f"Error querying vector database: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Used for testing the custom langchain retriever
@router.post("/query-lc-retriever")
async def query_lc_retriever(
    api_key: ApiKey,
    payload: QueryRequestPayload
):
    metadata: dict = {}
    if payload.namespace:
        metadata["namespace"] = payload.namespace

    retriever = Retriever(
        metadata=metadata,
    )
    documents = await retriever.aget_relevant_documents(query=payload.input)
    return documents



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

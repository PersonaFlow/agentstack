from uuid import UUID, uuid4
from typing import List, Optional
import aiohttp
import asyncio
from redis.asyncio import Redis
from fastapi import APIRouter, Depends, BackgroundTasks, Query
from fastapi.exceptions import HTTPException
from sse_starlette.sse import EventSourceResponse

from stack.app.core.auth.request_validators import AuthenticatedUser
from stack.app.schema.rag import (
    IngestRequestPayload,
    QueryRequestPayload,
    QueryResponsePayload,
)
from stack.app.repositories.assistant import (
    get_assistant_repository,
    AssistantRepository,
)
from stack.app.rag.query import query_documents
from stack.app.core.configuration import get_settings
from stack.app.repositories.file import FileRepository, get_file_repository
from stack.app.schema.file import FileSchema
import structlog
from stack.app.rag.custom_retriever import Retriever

# from stack.app.rag.ingest import get_ingest_tasks_from_config
from stack.app.schema.rag import BaseDocumentChunk
from stack.app.schema.assistant import Assistant
from stack.app.core.datastore import get_redis_connection
from stack.app.rag.embedding_service import EmbeddingService
from stack.app.core.redis import RedisService, get_redis_service
from stack.app.utils.stream import ingest_task_event_generator


logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()
DEFAULT_TAG = "RAG"


async def prepare_files(
    ingestion_id: str,
    payload: IngestRequestPayload,
    file_repository: FileRepository,
    assistant_repository: AssistantRepository,
    redis_service: RedisService,
) -> tuple[Optional[list[tuple[FileSchema, bytes]]], bool]:
    try:
        files_to_ingest = []
        is_assistant = payload.purpose == "assistants"
        if is_assistant:
            assistant = await assistant_repository.retrieve_assistant(
                UUID(payload.namespace)
            )
            if not assistant:
                raise ValueError(f"Assistant with ID {payload.namespace} not found.")
            existing_file_ids: set = set(assistant.file_ids or [])
            new_file_ids = set(str(file_id) for file_id in payload.files) - set(
                existing_file_ids
            )
            if not new_file_ids:
                await redis_service.set_ingestion_status(ingestion_id, "completed")
                await redis_service.push_progress_message(
                    ingestion_id, "No new files to ingest."
                )
                return None, is_assistant
            payload.files = list(new_file_ids)

        total_files = len(payload.files)
        for index, file_id in enumerate(payload.files, start=1):
            await redis_service.push_progress_message(
                ingestion_id, f"Retrieving file {index}/{total_files}"
            )
            file_model = await file_repository.retrieve_file(file_id)
            file = FileSchema.model_validate(file_model)
            file_content = await file_repository.retrieve_file_content(str(file_id))
            files_to_ingest.append((file, file_content))
            await redis_service.push_progress_message(
                ingestion_id, f"Retrieved file {index}/{total_files}: {file.filename}"
            )

        return files_to_ingest, is_assistant
    except Exception as e:
        logger.exception(f"Error in prepare_files: {str(e)}")
        await redis_service.push_progress_message(
            ingestion_id, f"Error preparing files: {str(e)}"
        )
        raise


async def generate_chunks_and_summaries(
    ingestion_id: str,
    embedding_service: EmbeddingService,
    payload: IngestRequestPayload,
    redis_service: RedisService,
) -> tuple[list[BaseDocumentChunk], Optional[list[BaseDocumentChunk]]]:
    try:
        await redis_service.push_progress_message(ingestion_id, "Generating chunks")
        chunks = await embedding_service.generate_chunks(payload.document_processor)
        await redis_service.push_progress_message(
            ingestion_id, f"Generated {len(chunks)} chunks"
        )

        summary_documents = None
        if payload.document_processor and payload.document_processor.summarize:
            await redis_service.push_progress_message(
                ingestion_id, "Generating summaries"
            )
            summary_documents = await embedding_service.generate_summary_documents(
                chunks
            )
            await redis_service.push_progress_message(
                ingestion_id, f"Generated {len(summary_documents)} summaries"
            )

        return chunks, summary_documents
    except Exception as e:
        logger.exception(f"Error in generate_chunks_and_summaries: {str(e)}")
        await redis_service.push_progress_message(
            ingestion_id, f"Error generating chunks and summaries: {str(e)}"
        )
        raise


async def embed_and_upsert(
    ingestion_id: str,
    embedding_service: EmbeddingService,
    payload: IngestRequestPayload,
    chunks: list[BaseDocumentChunk],
    summary_documents: Optional[list[BaseDocumentChunk]],
    redis_service: RedisService,
) -> None:
    try:
        await redis_service.push_progress_message(
            ingestion_id, "Embedding and upserting chunks"
        )
        await embedding_service.embed_and_upsert(
            chunks=chunks,
            encoder=payload.document_processor.encoder.get_encoder()
            if payload.document_processor
            else None,
            index_name=payload.index_name,
            ingestion_id=ingestion_id,
            redis_service=redis_service,
        )
        await redis_service.push_progress_message(
            ingestion_id, "Completed embedding and upserting chunks"
        )

        if summary_documents:
            await redis_service.push_progress_message(
                ingestion_id, "Embedding and upserting summaries"
            )
            await embedding_service.embed_and_upsert(
                chunks=summary_documents,
                encoder=payload.document_processor.encoder.get_encoder(),
                index_name=f"{payload.index_name}_summary",
                ingestion_id=ingestion_id,
                redis_service=redis_service,
            )
            await redis_service.push_progress_message(
                ingestion_id, "Completed embedding and upserting summaries"
            )
    except Exception as e:
        logger.exception(f"Error in embed_and_upsert: {str(e)}")
        await redis_service.push_progress_message(
            ingestion_id, f"Error embedding and upserting: {str(e)}"
        )
        raise


async def update_assistant(
    ingestion_id: str,
    assistant_repository: AssistantRepository,
    assistant: dict,
    payload: IngestRequestPayload,
    redis_service: RedisService,
) -> None:
    try:
        await redis_service.push_progress_message(ingestion_id, "Updating assistant")
        existing_file_ids = set(assistant.get("file_ids", []))
        updated_file_ids = list(existing_file_ids | set(payload.files))
        await assistant_repository.update_assistant(
            assistant.id, {"file_ids": updated_file_ids}
        )
        await redis_service.push_progress_message(ingestion_id, "Assistant updated")
    except Exception as e:
        logger.exception(f"Error in update_assistant: {str(e)}")
        await redis_service.push_progress_message(
            ingestion_id, f"Error updating assistant: {str(e)}"
        )
        raise


async def notify_webhook(
    webhook_url: str, collection_name: str, namespace: str, file_ids: List[str]
) -> None:
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                url=webhook_url,
                json={
                    "index_name": collection_name,
                    "status": "completed",
                    "namespace": namespace,
                    "file_ids": file_ids,
                },
            )
    except Exception as e:
        logger.exception(f"Error in notify_webhook: {str(e)}")
        # We don't re-raise this exception as it's not critical to the ingestion process


async def process_ingestion(
    ingestion_id: str,
    payload: IngestRequestPayload,
    file_repository: FileRepository,
    assistant_repository: AssistantRepository,
    redis_service: RedisService,
) -> None:
    redis = await get_redis_connection()
    try:
        await redis_service.set_ingestion_status(ingestion_id, "started")

        files_to_ingest, is_assistant = await prepare_files(
            ingestion_id, payload, file_repository, assistant_repository, redis_service
        )
        if files_to_ingest is None:
            return

        embedding_service = EmbeddingService(
            index_name=payload.index_name,
            encoder=payload.document_processor.encoder.get_encoder(),
            vector_credentials=payload.vector_database,
            dimensions=payload.document_processor.encoder.dimensions
            if payload.document_processor
            else None,
            files=files_to_ingest,
            namespace=payload.namespace,
            purpose=payload.purpose,
            parser_config=payload.document_processor.parser_config
            if payload.document_processor
            else None,
            ingestion_id=ingestion_id,
            redis_service=redis_service,
        )

        chunks, summary_documents = await generate_chunks_and_summaries(
            ingestion_id, embedding_service, payload, redis_service
        )

        await embed_and_upsert(
            ingestion_id, 
            embedding_service, 
            payload, 
            chunks, 
            summary_documents, 
            redis_service
        )

        if is_assistant:
            assistant = await assistant_repository.retrieve_assistant(payload.namespace)
            await update_assistant(
                ingestion_id, assistant_repository, assistant, payload, redis_service
            )

        if payload.webhook_url:
            await notify_webhook(
                payload.webhook_url,
                payload.index_name,
                payload.namespace,
                payload.files,
            )

        await redis_service.set_ingestion_status(ingestion_id, "completed")
        await redis_service.push_progress_message(
            ingestion_id, "Ingestion process completed successfully"
        )

    except Exception as e:
        logger.exception(f"Error during ingestion process: {str(e)}")
        await redis_service.set_ingestion_status(ingestion_id, "failed")
        await redis_service.push_progress_message(ingestion_id, f"Error: {str(e)}")
    finally:
        await redis.close()


@router.post(
    "/ingest",
    tags=[DEFAULT_TAG],
    response_model=dict,
    operation_id="ingest_data_from_files",
    summary="Ingest files to be indexed and queried.",
    description="Upload files for ingesting using the advanced RAG system.",
)
async def ingest(
    auth: AuthenticatedUser,
    payload: IngestRequestPayload,
    background_tasks: BackgroundTasks,
    file_repository: FileRepository = Depends(get_file_repository),
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
    redis_service: RedisService = Depends(get_redis_service),
) -> dict:
    try:
        ingestion_id = str(uuid4())
        background_tasks.add_task(
            process_ingestion,
            ingestion_id,
            payload,
            file_repository,
            assistant_repository,
            redis_service,
        )
        return {"ingestion_id": ingestion_id, "status": "started"}
    except Exception as e:
        logger.exception(f"Error starting ingestion process: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error starting ingestion process: {str(e)}"
        )


@router.get(
    "/ingest/{ingestion_id}/progress", 
    tags=[DEFAULT_TAG],
    response_class=EventSourceResponse,
    operation_id="ingest_task_progress",
    summary="Get progress and status updates for an ingestion task.",
    description="""
                Streams progress and status updates for an ingestion task 
                using the task_id that was recieved when the /ingest api was called.
                """,
)
async def ingest_progress(
    ingestion_id: str, redis_service: RedisService = Depends(get_redis_service)
):
    return EventSourceResponse(ingest_task_event_generator(ingestion_id, redis_service))


@router.post(
    "/query",
    response_model=QueryResponsePayload,
    tags=[DEFAULT_TAG],
    operation_id="query_documents",
    summary="Query documents",
    description="""
              Query ingested documents using advanced RAG system with unstructured library. <br>
             """,
)
async def query(auth: AuthenticatedUser, payload: QueryRequestPayload):
    try:
        chunks = await query_documents(payload=payload)
        response_payload = QueryResponsePayload(success=True, data=chunks)
        response_data = response_payload.model_dump(
            exclude=set(payload.exclude_fields) if payload.exclude_fields else None
        )
        return response_data
    except HTTPException as e:
        logger.exception(f"Error querying vector database: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        logger.exception(f"Error querying vector database: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Temp -> Used for testing the custom langchain retriever
@router.post("/query-lc-retriever", tags=[DEFAULT_TAG])
async def query_lc_retriever(auth: AuthenticatedUser, payload: QueryRequestPayload):
    metadata: dict = {}
    if payload.namespace:
        metadata["namespace"] = payload.namespace

    retriever = Retriever(
        metadata=metadata,
    )
    documents = await retriever.aget_relevant_documents(query=payload.input)
    return documents

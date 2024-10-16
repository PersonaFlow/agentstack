from uuid import UUID, uuid4
from typing import List, Optional
import aiohttp
import asyncio
from redis.asyncio import Redis
from fastapi import APIRouter, Depends, BackgroundTasks, Query
from fastapi.exceptions import HTTPException
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


logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()
DEFAULT_TAG = "RAG"


async def prepare_files(
    redis: Redis,
    ingestion_id: str,
    payload: IngestRequestPayload,
    file_repository: FileRepository,
    assistant_repository: AssistantRepository,
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
                await redis.set(f"ingestion:{ingestion_id}:status", "completed")
                await redis.set(
                    f"ingestion:{ingestion_id}:message", "No new files to ingest."
                )
                return None, is_assistant
            payload.files = list(new_file_ids)

        total_files = len(payload.files)
        for index, file_id in enumerate(payload.files, start=1):
            await redis.rpush(
                f"ingestion:{ingestion_id}:progress",
                f"Retrieving file {index}/{total_files}",
            )
            file_model = await file_repository.retrieve_file(file_id)
            file = FileSchema.model_validate(file_model)
            file_content = await file_repository.retrieve_file_content(str(file_id))
            files_to_ingest.append((file, file_content))
            await redis.rpush(
                f"ingestion:{ingestion_id}:progress",
                f"Retrieved file {index}/{total_files}: {file.filename}",
            )

        return files_to_ingest, is_assistant
    except Exception as e:
        logger.exception(f"Error in prepare_files: {str(e)}")
        await redis.rpush(
            f"ingestion:{ingestion_id}:progress", f"Error preparing files: {str(e)}"
        )
        raise


async def generate_chunks_and_summaries(
    redis: Redis,
    ingestion_id: str,
    embedding_service: EmbeddingService,
    payload: IngestRequestPayload,
) -> tuple[list[BaseDocumentChunk], list[BaseDocumentChunk] | None]:
    try:
        chunks = await embedding_service.generate_chunks(
            payload.document_processor
        )
        await redis.rpush(
            f"ingestion:{ingestion_id}:progress", f"Generated {len(chunks)} chunks"
        )

        summary_documents = None
        if payload.document_processor and payload.document_processor.summarize:
            await redis.rpush(
                f"ingestion:{ingestion_id}:progress", "Generating summaries"
            )
            summary_documents = await embedding_service.generate_summary_documents(
                chunks
            )
            await redis.rpush(
                f"ingestion:{ingestion_id}:progress",
                f"Generated {len(summary_documents)} summaries",
            )

        return chunks, summary_documents
    except Exception as e:
        logger.exception(f"Error in generate_chunks_and_summaries: {str(e)}")
        await redis.rpush(
            f"ingestion:{ingestion_id}:progress",
            f"Error generating chunks and summaries: {str(e)}",
        )
        raise


async def embed_and_upsert(
    redis: Redis,
    ingestion_id: str,
    embedding_service: EmbeddingService,
    payload: IngestRequestPayload,
    chunks: List[dict],
    summary_documents: Optional[List[dict]],
) -> None:
    try:
        await redis.rpush(
            f"ingestion:{ingestion_id}:progress", "Embedding and upserting documents"
        )
        await embedding_service.embed_and_upsert(
            chunks=chunks,
            encoder=payload.document_processor.encoder.get_encoder() if payload.document_processor else None,
            index_name=payload.index_name,
        )
        await redis.rpush(
            f"ingestion:{ingestion_id}:progress",
            "Completed embedding and upserting chunks",
        )

        if summary_documents:
            await redis.rpush(
                f"ingestion:{ingestion_id}:progress",
                "Embedding and upserting summaries",
            )
            await embedding_service.embed_and_upsert(
                chunks=summary_documents,
                encoder=payload.document_processor.encoder.get_encoder(),
                index_name=f"{payload.index_name}_summary",
            )
            await redis.rpush(
                f"ingestion:{ingestion_id}:progress",
                "Completed embedding and upserting summaries",
            )
    except Exception as e:
        logger.exception(f"Error in embed_and_upsert: {str(e)}")
        await redis.rpush(
            f"ingestion:{ingestion_id}:progress",
            f"Error embedding and upserting: {str(e)}",
        )
        raise


async def update_assistant(
    redis: Redis,
    ingestion_id: str,
    assistant_repository: AssistantRepository,
    assistant: dict,
    payload: IngestRequestPayload,
) -> None:
    try:
        await redis.rpush(f"ingestion:{ingestion_id}:progress", "Updating assistant")
        existing_file_ids = set(assistant.get("file_ids", []))
        updated_file_ids = list(existing_file_ids | set(payload.files))
        await assistant_repository.update_assistant(
            assistant.id, {"file_ids": updated_file_ids}
        )
        await redis.rpush(f"ingestion:{ingestion_id}:progress", "Assistant updated")
    except Exception as e:
        logger.exception(f"Error in update_assistant: {str(e)}")
        await redis.rpush(
            f"ingestion:{ingestion_id}:progress", f"Error updating assistant: {str(e)}"
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
    test_delay: float = 0,
) -> None:
    redis = await get_redis_connection()
    try:
        await redis.set(f"ingestion:{ingestion_id}:status", "started")

        files_to_ingest, is_assistant = await prepare_files(
            redis, ingestion_id, payload, file_repository, assistant_repository
        )
        if files_to_ingest is None:
            return

        embedding_service = EmbeddingService(
            index_name=payload.index_name,
            encoder=payload.document_processor.encoder.get_encoder(),
            vector_credentials=payload.vector_database,
            dimensions=payload.document_processor.encoder.dimensions if payload.document_processor else None,
            files=files_to_ingest,
            namespace=payload.namespace,
            purpose=payload.purpose,
            parser_config=payload.document_processor.parser_config if payload.document_processor else None,
            redis=redis,
            ingestion_id=ingestion_id,
            test_delay=test_delay,
        )

        chunks, summary_documents = await generate_chunks_and_summaries(
            redis, ingestion_id, embedding_service, payload
        )

        await embed_and_upsert(
            redis, ingestion_id, embedding_service, payload, chunks, summary_documents
        )

        if is_assistant:
            assistant = await assistant_repository.retrieve_assistant(payload.namespace)
            await update_assistant(
                redis, ingestion_id, assistant_repository, assistant, payload
            )

        if payload.webhook_url:
            await notify_webhook(
                payload.webhook_url,
                payload.index_name,
                payload.namespace,
                payload.files,
            )

        await redis.set(f"ingestion:{ingestion_id}:status", "completed")
        await redis.rpush(
            f"ingestion:{ingestion_id}:progress",
            "Ingestion process completed successfully",
        )

    except Exception as e:
        logger.exception(f"Error during ingestion process: {str(e)}")
        await redis.set(f"ingestion:{ingestion_id}:status", "failed")
        await redis.rpush(f"ingestion:{ingestion_id}:progress", f"Error: {str(e)}")
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
    test_delay: float = Query(0, description="Introduces a delay in seconds for each step of the ingestion process for testing purposes."),
    file_repository: FileRepository = Depends(get_file_repository),
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
) -> dict:
    try:
        ingestion_id = str(uuid4())
        background_tasks.add_task(
            process_ingestion,
            ingestion_id,
            payload,
            file_repository,
            assistant_repository,
            test_delay,
        )
        return {"ingestion_id": ingestion_id, "status": "started"}
    except Exception as e:
        logger.exception(f"Error starting ingestion process: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error starting ingestion process: {str(e)}"
        )


@router.get("/ingest/{ingestion_id}/progress", tags=[DEFAULT_TAG])
async def ingest_progress(ingestion_id: str):
    from sse_starlette.sse import EventSourceResponse
    
    async def event_generator():
        redis = await get_redis_connection()
        try:
            logger.info(f"Starting event generator for ingestion {ingestion_id}")
            while True:
                # Consume all available messages
                while True:
                    message = await redis.lpop(f"ingestion:{ingestion_id}:progress")
                    if message:
                        logger.debug(f"Received progress message: {message.decode('utf-8')}")
                        yield {"event": "progress", "data": message.decode("utf-8")}
                    else:
                        break  # No more messages available
                
                # Check status after consuming all available messages
                status = await redis.get(f"ingestion:{ingestion_id}:status")
                if status in [b"completed", b"failed"]:
                    logger.info(f"Ingestion {ingestion_id} {status.decode('utf-8')}")
                    yield {"event": "completed", "data": status.decode("utf-8")}
                    break
                
                # Short sleep to prevent tight looping
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.exception(f"Error in event_generator: {str(e)}")
            yield {"event": "error", "data": f"Error: {str(e)}"}
        finally:
            await redis.close()
            logger.info(f"Event generator for ingestion {ingestion_id} finished")

    return EventSourceResponse(event_generator())


# async def handle_assistant_files(
#     payload: IngestRequestPayload, assistant_repository: AssistantRepository
# ) -> tuple[list[str], set[str], Assistant]:
#     assistant = await assistant_repository.retrieve_assistant(payload.namespace)
#     if assistant is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Assistant with ID {payload.namespace} not found.",
#         )

#     existing_file_ids = set(assistant.file_ids or [])
#     new_file_ids = set(str(file_id) for file_id in payload.files) - existing_file_ids

#     if not new_file_ids:
#         raise HTTPException(
#             status_code=status.HTTP_200_OK,
#             detail="No new files to ingest.",
#         )

#     return list(new_file_ids), existing_file_ids, assistant

# @router.post(
#     "/ingest",
#     tags=[DEFAULT_TAG],
#     response_model=dict,
#     operation_id="ingest_data_from_files",
#     summary="Ingest files to be indexed and queried.",
#     description="Upload files for ingesting using the advanced RAG system.",
# )
# async def ingest(
#     auth: AuthenticatedUser,
#     payload: IngestRequestPayload,
#     file_repository: FileRepository = Depends(get_file_repository),
#     assistant_repository: AssistantRepository = Depends(get_assistant_repository),
# ) -> dict:
#     files_to_ingest = []
#     try:
#         is_assistant = payload.purpose == ContextType.assistants
#         existing_file_ids = set()
#         assistant = None

#         if is_assistant:
#             payload.files, existing_file_ids, assistant = await handle_assistant_files(
#                 payload, assistant_repository
#             )

#         for file_id in payload.files:
#             file_model = await file_repository.retrieve_file(file_id)
#             file = FileSchema.model_validate(file_model)
#             file_content = await file_repository.retrieve_file_content(str(file_id))
#             files_to_ingest.append((file, file_content))

#         tasks = await get_ingest_tasks_from_config(files_to_ingest, payload)

#         await asyncio.gather(*tasks)

#         if is_assistant and assistant:
#             updated_file_ids = list(existing_file_ids | set(payload.files))
#             await assistant_repository.update_assistant(
#                 assistant.id, {"file_ids": updated_file_ids}
#             )

#         if payload.webhook_url:
#             await notify_webhook(
#                 payload.webhook_url,
#                 payload.index_name,
#                 payload.namespace,
#                 payload.files,
#             )

#         return {
#             "success": True,
#             "message": f"Ingested {len(files_to_ingest)} new files.",
#         }
#     except HTTPException as he:
#         # Re-raise HTTP exceptions
#         raise he
#     except Exception as e:
#         logger.exception(f"Error ingesting files: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An error occurred while ingesting the files.",
#         )


# async def notify_webhook(
#     webhook_url: str, collection_name: str, namespace: str, file_ids: list[str]
# ):
#     async with aiohttp.ClientSession() as session:
#         await session.post(
#             url=webhook_url,
#             json={
#                 "index_name": collection_name,
#                 "status": "completed",
#                 "namespace": namespace,
#                 "file_ids": file_ids,
#             },
#         )


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

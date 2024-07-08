from uuid import UUID
import asyncio
import aiohttp
from fastapi import APIRouter, Depends, status
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
from stack.app.rag.ingest import get_ingest_tasks_from_config
from stack.app.schema.rag import ContextType
from stack.app.schema.assistant import Assistant


logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()
DEFAULT_TAG = "RAG"


async def handle_assistant_files(
    payload: IngestRequestPayload,
    assistant_repository: AssistantRepository
) -> tuple[list[str], set[str], Assistant]:
    assistant = await assistant_repository.retrieve_assistant(payload.namespace)
    if assistant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assistant with ID {payload.namespace} not found.",
        )

    existing_file_ids = set(assistant.file_ids or [])
    new_file_ids = set(str(file_id) for file_id in payload.files) - existing_file_ids

    if not new_file_ids:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="No new files to ingest.",
        )

    return list(new_file_ids), existing_file_ids, assistant

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
    file_repository: FileRepository = Depends(get_file_repository),
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
) -> dict:
    files_to_ingest = []
    try:
        is_assistant = payload.purpose == ContextType.assistants
        existing_file_ids = set()
        assistant = None

        if is_assistant:
            payload.files, existing_file_ids, assistant = await handle_assistant_files(payload, assistant_repository)

        for file_id in payload.files:
            file_model = await file_repository.retrieve_file(UUID(file_id))
            file = FileSchema.model_validate(file_model)
            files_to_ingest.append(file)

        tasks = await get_ingest_tasks_from_config(files_to_ingest, payload)

        await asyncio.gather(*tasks)

        if is_assistant and assistant:
            updated_file_ids = list(existing_file_ids | set(payload.files))
            await assistant_repository.update_assistant(
                assistant.id, {"file_ids": updated_file_ids}
            )

        if payload.webhook_url:
            await notify_webhook(
                payload.webhook_url,
                payload.index_name,
                payload.namespace,
                payload.files,
            )

        return {"success": True, "message": f"Ingested {len(files_to_ingest)} new files."}
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.exception(f"Error ingesting files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while ingesting the files.",
        )


async def notify_webhook(
    webhook_url: str, collection_name: str, namespace: str, file_ids: list[str]
):
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

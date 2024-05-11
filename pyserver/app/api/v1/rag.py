import asyncio
import aiohttp
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from pyserver.app.api.annotations import ApiKey
from pyserver.app.schema.rag import (
    IngestRequestPayload,
    QueryRequestPayload,
    QueryResponsePayload,
)
from pyserver.app.repositories.assistant import get_assistant_repository, AssistantRepository
from pyserver.app.rag.query import query_documents
from pyserver.app.core.configuration import get_settings
from pyserver.app.repositories.file import FileRepository, get_file_repository
from pyserver.app.schema.file import FileSchema
import structlog
from pyserver.app.rag.custom_retriever import Retriever
from pyserver.app.rag.ingest import get_ingest_tasks_from_config

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()
DEFAULT_TAG = "RAG"


@router.post(
    "/ingest",
    tags=[DEFAULT_TAG],
    response_model=dict,
    operation_id="ingest_data_from_files",
    summary="Ingest files to be indexed and queried.",
    description="""
              Upload files for ingesting using the advanced RAG system.
             """,
)
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
        #         assistant_repository.add_files_to_assistant(
        #             payload.namespace,
        #             files_to_ingest
        #         )

        if payload.webhook_url:
            await notify_webhook(
                payload.webhook_url,
                payload.index_name,
                payload.namespace,
                payload.files,
            )

        # TODO: return stats from ingestion
        return {"success": True}
    except Exception as e:
        await logger.exception(f"Error ingesting files: {str(e)}")
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
async def query(api_key: ApiKey, payload: QueryRequestPayload):
    try:
        chunks = await query_documents(payload=payload)
        response_payload = QueryResponsePayload(success=True, data=chunks)
        response_data = response_payload.model_dump(
            exclude=set(payload.exclude_fields) if payload.exclude_fields else None
        )
        return response_data
    except HTTPException as e:
        await logger.exception(
            f"Error querying vector database: {str(e)}", exc_info=True
        )
        raise e
    except Exception as e:
        await logger.exception(
            f"Error querying vector database: {str(e)}", exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))


# Temp -> Used for testing the custom langchain retriever
@router.post("/query-lc-retriever", tags=[DEFAULT_TAG])
async def query_lc_retriever(api_key: ApiKey, payload: QueryRequestPayload):
    metadata: dict = {}
    if payload.namespace:
        metadata["namespace"] = payload.namespace

    retriever = Retriever(
        metadata=metadata,
    )
    documents = await retriever.aget_relevant_documents(query=payload.input)
    return documents

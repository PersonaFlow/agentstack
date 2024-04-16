
from fastapi import APIRouter, status, HTTPException, Depends
import uuid
import asyncio
from datetime import datetime
from io import BytesIO
import structlog
from app.repositories.assistant import get_assistant_repository, AssistantRepository, UniqueConstraintError
from app.repositories.file import FileRepository, get_file_repository
from app.schema.assistant import (
  CreateAssistantSchema,
  Assistant,
  UpdateAssistantSchema,
  CreateAssistantFileSchema,
  CreateAssistantFileSchemaResponse
)
from app.api.annotations import ApiKey
from app.rag.ingest_runnable import ingest_runnable
from app.core.configuration import get_settings
from app.vectordbs import get_vector_service
from app.schema.file import FileSchema
from typing import Optional
from app.rag.ingest import get_ingest_tasks_from_config
from app.schema.rag import IngestRequestPayload

router = APIRouter()
DEFAULT_TAG = "Assistants"
logger = structlog.get_logger()
settings = get_settings()

@router.post("", tags=[DEFAULT_TAG], response_model=Assistant, status_code=status.HTTP_201_CREATED,
             operation_id="create_assistant",
             summary="Create a new assistant",
             description="Creates a new assistant with the specified details.")
async def create_assistant(
    api_key: ApiKey,
    data: CreateAssistantSchema,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository)
) -> Assistant:
    try:
        assistant = await assistant_repository.create_assistant(data=data.model_dump())
        return assistant
    except UniqueConstraintError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        await logger.exception(f"Error creating assistant: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the assistant.")

@router.get("", tags=[DEFAULT_TAG], response_model=list[Assistant],
            operation_id="retrieve_assistants",
            summary="Retrieve all assistants",
            description="Retrieves a list of all assistants.")
async def retrieve_assistants(
    api_key: ApiKey,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository)
) -> list[Assistant]:
    assistants = await assistant_repository.retrieve_assistants()
    return assistants

@router.get("/{assistant_id}", tags=[DEFAULT_TAG], response_model=Assistant,
            operation_id="retrieve_assistant",
            summary="Retrieve a specific assistant",
            description="Retrieves detailed information about a specific assistant by its ID.")
async def retrieve_assistant(
    api_key: ApiKey,
    assistant_id: uuid.UUID,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository)
) -> Assistant:
    assistant = await assistant_repository.retrieve_assistant(assistant_id=assistant_id)
    if assistant:
        return assistant
    raise HTTPException(status_code=404, detail="Assistant not found")

@router.patch("/{assistant_id}", tags=[DEFAULT_TAG], response_model=Assistant,
              operation_id="update_assistant",
              summary="Update a specific assistant",
              description="Updates the details of a specific assistant by its ID.")
async def update_assistant(
    api_key: ApiKey,
    assistant_id: uuid.UUID,
    data: UpdateAssistantSchema,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository)
) -> Assistant:
    assistant = await assistant_repository.update_assistant(assistant_id=assistant_id, data=data.model_dump())
    if assistant:
        return assistant
    raise HTTPException(status_code=404, detail="Assistant not found")

@router.delete("/{assistant_id}", tags=[DEFAULT_TAG], status_code=status.HTTP_204_NO_CONTENT,
               operation_id="delete_assistant",
               summary="Delete a specific assistant",
               description="Deletes a specific assistant by its ID from the database.")
async def delete_assistant(
    api_key: ApiKey,
    assistant_id: uuid.UUID,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository)
):
    await assistant_repository.delete_assistant(assistant_id=assistant_id)
    return {"detail": "Assistant deleted successfully"}

@router.post("/{assistant_id}/files",
             tags=[DEFAULT_TAG],
             response_model=CreateAssistantFileSchemaResponse,
             operation_id="create_assistant_file",
             summary="Add an uploaded file to an assistant for RAG.",
             description="Convenience method to add an uploaded file to an assistant for RAG ingestion and retrieval",)
async def create_assistant_file(
    api_key: ApiKey,
    assistant_id: uuid.UUID,
    data: CreateAssistantFileSchema,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
    file_repository: FileRepository = Depends(get_file_repository),
) -> CreateAssistantFileSchemaResponse:
    try:
        assistant = await assistant_repository.retrieve_assistant(assistant_id=assistant_id)
        if not assistant:
            logger.exception(f"Assistant not found: {assistant_id}")
            raise HTTPException(status_code=404, detail="Assistant not found")

        # Commenting this out for testing purposes
        # if data.file_id in [f.file_id for f in assistant.file_ids]:
        #     logger.exception(f"File with id: {data.file_id} already added to assistant {assistant_id}")
        #     raise HTTPException(status_code=400, detail="File already added to assistant")

        # Old method - we'll bring this back for the "recursive" implementation
        # file_content = await file_repository.retrieve_file_content(data.file_id)
        # file_content_io = BytesIO(file_content)
        # config = {"configurable": {"assistant_id": str(assistant_id), "file_id": str(data.file_id)}}
        # ids = ingest_runnable.batch([file_content_io], config)
        # if not ids:
        #     await logger.exception(f"Error ingesting file: {data.file_id}")
        #     raise HTTPException(status_code=500, detail="An error occurred while ingesting the file.")

        file_model = await file_repository.retrieve_file(data.file_id)
        files_to_ingest = [FileSchema.model_validate(file_model)]

        config = IngestRequestPayload(
            files=[data.file_id],
            namespace=str(assistant_id),
        )

        tasks = await get_ingest_tasks_from_config(files_to_ingest, config)

        await asyncio.gather(*tasks)

        assistant = await assistant_repository.add_file_to_assistant(assistant_id, data.file_id)

        response_data = CreateAssistantFileSchemaResponse(file_id=str(data.file_id), assistant_id=str(assistant_id))
        return response_data

    except HTTPException as e:
        await logger.exception(f"Error creating assistant file: {str(e)}")
        raise e
    except Exception as e:
        await logger.exception(f"Error adding file to assistant: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while adding the file to the assistant.")

@router.delete("/{assistant_id}/files/{file_id}", tags=[DEFAULT_TAG],
             response_model=Assistant,
             operation_id="delete_assistant_file",
             summary="Remove a file from an assistant",
             description="Removes a file from an assistant by its ID. This also deletes the corresponding documents from the vector store.")
async def delete_assistant_file(
    api_key: ApiKey,
    assistant_id: uuid.UUID,
    file_id: uuid.UUID,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
) -> Assistant:
    try:
        service = get_vector_service()
        # delete the associated vector embeddings
        deleted_chunks = await service.delete(str(file_id), str(assistant_id))
        await logger.info(f"Deleted {deleted_chunks} chunks")
        # Delete the file from the assistant's file_ids
        assistant = await assistant_repository.remove_file_reference_from_assistant(assistant_id, str(file_id))
        return assistant
    except Exception as e:
        await logger.exception(f"Error deleting assistant file: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while deleting the file from the assistant.")


@router.get("/{assistant_id}/files", tags=[DEFAULT_TAG],
            response_model=list[FileSchema],
            operation_id="retrieve_assistant_files",
            summary="Retrieve file information for all files associated with an assistant",
            description="Returns a list of file objects for all files associated with an assistant.")
async def retrieve_assistant_files(
    api_key: ApiKey,
    assistant_id: uuid.UUID,
    limit: int = 20,
    order: str = "desc",
    before: Optional[datetime] = None,
    after: Optional[datetime] = None,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
    files_repository: FileRepository = Depends(get_file_repository),
) -> list[FileSchema]:
    try:
        assistant = await assistant_repository.retrieve_assistant(assistant_id)
        if not assistant:
            raise HTTPException(status_code=404, detail="Assistant not found")
        file_ids = assistant.file_ids or []
        files = await files_repository.retrieve_files_by_ids(
            file_ids=file_ids,
            limit=limit,
            order=order,
            before=before,
            after=after
        )
        return files
    except HTTPException as e:
        raise e
    except Exception as e:
        await logger.exception(f"Error retrieving files for assistant: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the files for the assistant.")


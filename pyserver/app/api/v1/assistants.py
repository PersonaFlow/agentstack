
from fastapi import APIRouter, status, HTTPException, Depends
import uuid
import structlog
from app.repositories.assistant import get_assistant_repository, AssistantRepository, UniqueConstraintError
from app.schema.assistant import CreateAssistantSchema, Assistant, UpdateAssistantSchema
from app.api.annotations import ApiKey

router = APIRouter()
DEFAULT_TAG = "Assistants"
logger = structlog.get_logger()

@router.post("", tags=[DEFAULT_TAG], response_model=Assistant, status_code=status.HTTP_201_CREATED,
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
            summary="Retrieve all assistants",
            description="Retrieves a list of all assistants.")
async def retrieve_assistants(
    api_key: ApiKey,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository)
) -> list[Assistant]:
    assistants = await assistant_repository.retrieve_assistants()
    return assistants

@router.get("/{assistant_id}", tags=[DEFAULT_TAG], response_model=Assistant,
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

# TODO: This needs to be protected such that only a user with admin permissions or the owner of the assistant can delete it.
@router.delete("/{assistant_id}", tags=[DEFAULT_TAG], status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a specific assistant",
               description="Deletes a specific assistant by its ID from the database.")
async def delete_assistant(
    api_key: ApiKey,
    assistant_id: uuid.UUID,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository)
):
    await assistant_repository.delete_assistant(assistant_id=assistant_id)
    return {"detail": "Assistant deleted successfully"}

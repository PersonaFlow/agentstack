from fastapi import APIRouter, status, HTTPException, Depends
from pyserver.app.repositories.message import MessageRepository, get_message_repository
from pyserver.app.schema.message import CreateMessageSchema, Message, UpdateMessageSchema
from pyserver.app.api.annotations import ApiKey

# Initialize the router for messages
router = APIRouter()
DEFAULT_TAG = "Messages"


@router.post(
    "",
    tags=[DEFAULT_TAG],
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_message",
    summary="Create a new message",
    description="Creates a new message within a thread.",
)
async def create_message(
    api_key: ApiKey,
    data: CreateMessageSchema,
    message_repo: MessageRepository = Depends(get_message_repository),
) -> Message:
    if not data.user_id:
        data.user_id = api_key.user_store_id
    message = await message_repo.create_message(data=data.model_dump())
    return message


@router.patch(
    "/{message_id}",
    tags=[DEFAULT_TAG],
    response_model=Message,
    operation_id="update_message",
    summary="Update a specific message",
    description="Updates the details of a specific message by its ID.",
)
async def update_message(
    api_key: ApiKey,
    message_id: str,
    data: UpdateMessageSchema,
    message_repo: MessageRepository = Depends(get_message_repository),
) -> Message:
    message = await message_repo.update_message(
        message_id=message_id, data=data.model_dump()
    )
    if message:
        return message
    raise HTTPException(status_code=404, detail="Message not found")


@router.delete(
    "/{message_id}",
    tags=[DEFAULT_TAG],
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_message",
    summary="Delete a specific message",
    description="Deletes a specific message by its ID from the database.",
)
async def delete_message(
    api_key: ApiKey,
    message_id: str,
    message_repo: MessageRepository = Depends(get_message_repository),
):
    await message_repo.delete_message(message_id=message_id)
    return {"detail": "Message deleted successfully"}

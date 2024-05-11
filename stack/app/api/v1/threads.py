from fastapi import APIRouter, Depends, status
from typing import List
from stack.app.repositories.thread import ThreadRepository, get_thread_repository
from stack.app.repositories.message import MessageRepository, get_message_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.app.repositories.assistant import AssistantRepository, get_assistant_repository
from stack.app.schema.thread import CreateThreadSchema, Thread, UpdateThreadSchema
from stack.app.schema.message import Message
from stack.app.api.annotations import ApiKey
from stack.app.core.exception import NotFoundException

router = APIRouter()
DEFAULT_TAG = "Threads"


@router.post(
    "",
    tags=[DEFAULT_TAG],
    response_model=Thread,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_thread",
    summary="Create a new thread",
    description="Creates a new thread with the provided information. This can optionally be obtained from the api_key. If it is not set in the request, it will attempt to get it from the api_key.",
)
async def create_thread(
    api_key: ApiKey,
    data: CreateThreadSchema,
    thread_repo: ThreadRepository = Depends(get_thread_repository),
    assistant_repo: AssistantRepository = Depends(get_assistant_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> Thread:
    assistant = await assistant_repo.retrieve_assistant(assistant_id=data.assistant_id)
    if not assistant:
        raise NotFoundException(f"Assistant with ID {data.assistant_id} not found")
    user = await user_repo.retrieve_by_user_id(user_id=data.user_id)
    if not user:
        raise NotFoundException(f"User with ID {data.user_id} not found")
    thread = await thread_repo.create_thread(data=data.model_dump())
    return thread


@router.get(
    "",
    tags=[DEFAULT_TAG],
    response_model=List[Thread],
    operation_id="retrieve_all_threads",
    summary="Retrieve all threads",
    description="Retrieves a list of all threads in the database. Should be used as an admin operation only.",
)
async def retrieve_threads(
    api_key: ApiKey, thread_repo: ThreadRepository = Depends(get_thread_repository)
) -> List[Thread]:
    threads = await thread_repo.retrieve_threads()
    return threads


@router.get(
    "/{thread_id}",
    tags=[DEFAULT_TAG],
    response_model=Thread,
    operation_id="retrieve_thread",
    summary="Retrieve a specific thread",
    description="Retrieves detailed information about a thread identified by its ID.",
)
async def retrieve_thread(
    api_key: ApiKey,
    thread_id: str,
    thread_repo: ThreadRepository = Depends(get_thread_repository),
) -> Thread:
    thread = await thread_repo.retrieve_thread(thread_id=thread_id)
    if not thread:
        raise NotFoundException(f"Thread with ID {thread_id} not found")
    return thread


@router.patch(
    "/{thread_id}",
    tags=[DEFAULT_TAG],
    response_model=Thread,
    operation_id="update_thread",
    summary="Update a specific thread",
    description="Updates the information of a thread identified by its ID.",
)
async def update_thread(
    api_key: ApiKey,
    thread_id: str,
    data: UpdateThreadSchema,
    thread_repo: ThreadRepository = Depends(get_thread_repository),
) -> Thread:
    thread = await thread_repo.update_thread(
        thread_id=thread_id, data=data.model_dump()
    )
    if not thread:
        raise NotFoundException(f"Thread with ID {thread_id} not found")
    return thread


@router.delete(
    "/{thread_id}",
    tags=[DEFAULT_TAG],
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_thread",
    summary="Delete a specific thread",
    description="Deletes a thread identified by its ID from the database.",
)
async def delete_thread(
    api_key: ApiKey,
    thread_id: str,
    thread_repo: ThreadRepository = Depends(get_thread_repository),
):
    await thread_repo.delete_thread(thread_id=thread_id)
    return {"detail": "Thread deleted successfully"}


@router.get(
    "/{thread_id}/messages",
    tags=[DEFAULT_TAG],
    response_model=List[Message],
    operation_id="retrieve_messages_for_thread",
    summary="Retrieve all messages by thread id",
    description="Retrieves a list of all messages in a thread identified by its ID.",
)
async def retrieve_messages_by_thread_id(
    api_key: ApiKey,
    thread_id: str,
    message_repo: MessageRepository = Depends(get_message_repository),
) -> List[Message]:
    messages = await message_repo.retrieve_messages_by_thread_id(thread_id=thread_id)
    return messages


@router.get(
    "/{thread_id}/checkpoints",
    tags=[DEFAULT_TAG],
    operation_id="retrieve_checkpoint_messages_for_thread",
    summary="Retrieve checkpoints by thread id",
    description="Retrieves a list of messages in a thread from the checkpoints list identified by its ID.",
)
async def retrieve_checkpoints_by_thread_id(
    api_key: ApiKey,
    thread_id: str,
    thread_repo: ThreadRepository = Depends(get_thread_repository),
):
    checkpoints = await thread_repo.get_thread_checkpoints(thread_id=thread_id)
    return checkpoints

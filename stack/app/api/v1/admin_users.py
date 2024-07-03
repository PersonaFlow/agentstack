from typing import List, Optional, Union
from fastapi import APIRouter, status, Query, Depends, HTTPException
from stack.app.core.auth.request_validators import AuthenticatedUser
from stack.app.core.exception import NotFoundException
from stack.app.schema.thread import Thread, GroupedThreads
from stack.app.schema.user import User, CreateUserSchema, UpdateUserSchema
from stack.app.repositories.thread import ThreadRepository, get_thread_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.app.utils.group_threads import group_threads
from stack.app.repositories.assistant import (
    AssistantRepository,
    get_assistant_repository,
)
from stack.app.schema.assistant import Assistant

router = APIRouter()
DEFAULT_TAG = "Users (Admin)"


@router.post(
    "",
    tags=[DEFAULT_TAG],
    response_model=User,
    operation_id="create_user",
    summary="Create a new user",
    description="""
                POST endpoint at `/users` for creating a new user.
                If `user_id` is not present, the database will auto-generate a new UUID for the field.
                This is intended to allow for internal users to be correlated with external systems while not exposing the internal database record id for the user.
                TODO: Add access control for this endpoint.
            """,
)
async def create_user(
    auth: AuthenticatedUser,
    data: CreateUserSchema,
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    # Check that the user does not exist first
    existing_user = await user_repo.retrieve_by_user_id(user_id=data.user_id)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with user_id: {data.user_id} already exists",
        )
    created_user = await user_repo.create_user(data=data)
    return created_user


@router.get(
    "",
    tags=[DEFAULT_TAG],
    response_model=list[User],
    operation_id="retrieve_all_users",
    summary="List all users ",
    description="""
                GET endpoint at `/users` for listing all users.
                TODO: Add access control for this endpoint.
            """,
)
async def retrieve_users(
    auth: AuthenticatedUser,
    user_repo: UserRepository = Depends(get_user_repository)
) -> List[User]:
    records = await user_repo.retrieve_users()
    return records


@router.get(
    "/{user_id}",
    tags=[DEFAULT_TAG],
    response_model=User,
    operation_id="retrieve_user",
    summary="Retrieve a specific user",
    description="""
        GET endpoint at `/users/{user_id}` for fetching details of a specific user using its user_id.
        USAGE: Admins can use this endpoint to retrieve details of a specific user.
        TODO: Add access control for this endpoint.
        """,
)
async def retrieve_user(
    auth: AuthenticatedUser,
    user_id: Optional[str],
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    record = await user_repo.retrieve_by_user_id(user_id=user_id)
    if not record:
        raise NotFoundException
    return record


@router.patch(
    "/{user_id}",
    tags=[DEFAULT_TAG],
    response_model=User,
    operation_id="update_user",
    summary="Update a specific user ",
    description="""
        PATCH endpoint at `/{user_id}` for updating the details of a specific user.
        USAGE: Admins can use this endpoint to update the details of a specific user.
        TODO: Add access control for this endpoint.
        """,
)
async def update_user(
    auth: AuthenticatedUser,
    user_id: str,
    data: UpdateUserSchema,
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    record = await user_repo.update_by_user_id(user_id=user_id, data=data)
    if not record:
        raise NotFoundException
    return record


@router.delete(
    "/{user_id}",
    tags=[DEFAULT_TAG],
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_user",
    summary="Delete a specific user ",
    description=(
            """
                DELETE endpoint at `/users/{user_id}` for removing a specific user using its `user_id`.
                USAGE: Admins can use this endpoint to delete a specific user.
                TODO: Add access control for this endpoint.
            """
    ),
)
async def delete_user(
    auth: AuthenticatedUser,
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository),
):
    record = await user_repo.delete_by_user_id(user_id=user_id)
    if record:
        return record
    raise NotFoundException


@router.get(
    "/{user_id}/threads",
    tags=[DEFAULT_TAG],
    response_model=Union[List[Thread], GroupedThreads],
    operation_id="retrieve_user_threads",
    summary="Retrieve threads by user ",
    description="""
                GET endpoint at `/users/{user_id}/threads` for fetching all threads associated with a specific user using its id. <br>
                USAGE: Admins can use this endpoint to retrieve all threads associated with a specific user.
                TODO: Add access control for this endpoint.
            """,
)
async def retrieve_user_threads(
    auth: AuthenticatedUser,
    user_id: str,
    thread_repo: ThreadRepository = Depends(get_thread_repository),
    grouped: Optional[bool] = Query(None),
    timezoneOffset: Optional[int] = Query(None),
):
    records = await thread_repo.retrieve_threads_by_user_id(user_id=user_id)
    if not grouped:
        return records
    return group_threads(records, timezoneOffset if timezoneOffset else 0)


@router.get(
    "/threads",
    tags=[DEFAULT_TAG],
    response_model=List[Thread],
    operation_id="retrieve_all_threads",
    summary="Retrieve all threads",
    description="""Retrieves a list of all threads in the database.
                Should be used as an admin operation. <br>
                TODO: Add access control for this endpoint.
                """,
)
async def retrieve_all_threads(
    auth: AuthenticatedUser,
    thread_repo: ThreadRepository = Depends(get_thread_repository)
) -> List[Thread]:
    threads = await thread_repo.retrieve_threads()
    return threads

@router.get(
    "/assistants",
    tags=[DEFAULT_TAG],
    response_model=list[Assistant],
    operation_id="retrieve_user_assistants",
    summary="Retrieve user assistants",
    description="Retrieves a list of the user's assistants.",
)
async def retrieve_user_assistants(
    auth: AuthenticatedUser,
    assistant_repository: AssistantRepository = Depends(get_assistant_repository),
) -> list[Assistant]:
    assistants = await assistant_repository.retrieve_assistants()
    return assistants

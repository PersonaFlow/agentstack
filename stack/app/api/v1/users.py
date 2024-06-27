"""
endpoints/user.py
----------

This module provides the FastAPI endpoints related to user management functionalities like user creation, retrieval, update, and deletion.

"""

from typing import List, Optional, Union
from fastapi import APIRouter, status, Query, Depends
from stack.app.api.annotations import ApiKey
from stack.app.core.exception import NotFoundException
from stack.app.schema.thread import Thread, GroupedThreads
from stack.app.schema.user import User, CreateUserSchema, UpdateUserSchema
from stack.app.repositories.thread import ThreadRepository, get_thread_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.app.utils.group_threads import group_threads

router = APIRouter()
DEFAULT_TAG = "Users"


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
            """,
)
async def create_user(
    api_key: ApiKey,
    data: CreateUserSchema,
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    user = await user_repo.create_user(data=data)
    return user


@router.get(
    "",
    tags=[DEFAULT_TAG],
    response_model=list[User],
    operation_id="retrieve_all_users",
    summary="List all users ",
    description="""
                GET endpoint at `/users` for listing all users.
            """,
)
async def retrieve_users(
    api_key: ApiKey, user_repo: UserRepository = Depends(get_user_repository)
) -> List[User]:
    records = await user_repo.retrieve_users()
    return records


@router.get(
    "/{user_id}",
    tags=[DEFAULT_TAG],
    response_model=User,
    operation_id="retrieve_user",
    summary="Retrieve a specific user ",
    description="GET endpoint at `/users/{user_id}` for fetching details of a specific user using its user_id.",
)
async def retrieve_user(
    api_key: ApiKey,
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
    description="PATCH endpoint at `/{user_id}` for updating the details of a specific user.",
)
async def update_user(
    api_key: ApiKey,
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
                """
    ),
)
async def delete_user(
    api_key: ApiKey,
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
            """,
)
async def retrieve_user_threads(
    api_key: ApiKey,
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
    "/{user_id}/startup",
    tags=[DEFAULT_TAG],
    response_model=User,
    operation_id="startup",
    summary="Create a new local user if it does not exist, then return the startup configuration for the user.",
    description="""
                        Gets the startup configuration for the user. <br>
                        **Important**: Creates the local user with the provided `user_id` if the user has not used the service before. <br>
                        Primary purpose is to establish the user in the local database then return any configuration information to the client.
                     """,
)
async def startup(
    user_id: str, user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    record = await user_repo.retrieve_by_user_id(user_id=user_id)
    if not record:
        create_user = CreateUserSchema(user_id=user_id)
        record = await user_repo.create_user(data=create_user)
    return record

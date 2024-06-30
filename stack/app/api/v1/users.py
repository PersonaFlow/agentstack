from typing import List, Optional, Union
from fastapi import APIRouter, status, Query, Depends, Request
from stack.app.core.auth.request_validators import AuthenticatedUser
from stack.app.core.exception import NotFoundException
from stack.app.schema.thread import Thread, GroupedThreads
from stack.app.schema.user import User, CreateUserSchema, UpdateUserSchema
from stack.app.repositories.thread import ThreadRepository, get_thread_repository
from stack.app.repositories.user import UserRepository, get_user_repository
from stack.app.utils.group_threads import group_threads
from stack.app.core.auth.utils import get_header_user_id
router = APIRouter()
DEFAULT_TAG = "Users"


@router.get(
    "/me",
    tags=[DEFAULT_TAG],
    response_model=User,
    operation_id="retrieve_me",
    summary="Retrieve a specific user ",
    description="""
        GET endpoint to fetch details of the logged-in user.
        USAGE: Admins can use this endpoint to retrieve details of a specific user.
        TODO: Add RBAC for this endpoint.
        """,
)
async def retrieve_me(
    auth: AuthenticatedUser,
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    user_id = get_header_user_id(request)
    record = await user_repo.retrieve_by_user_id(user_id=user_id)
    if not record:
        raise NotFoundException
    return record


@router.patch(
    "/me",
    tags=[DEFAULT_TAG],
    response_model=User,
    operation_id="update_me",
    summary="Update a specific user ",
    description="""
        PATCH endpoint for updating the details of the logged-in user.
        """,
)
async def update_me(
    auth: AuthenticatedUser,
    request: Request,
    data: UpdateUserSchema,
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    user_id = get_header_user_id(request)
    record = await user_repo.update_by_user_id(user_id=user_id, data=data)
    if not record:
        raise NotFoundException
    return record


@router.delete(
    "/me",
    tags=[DEFAULT_TAG],
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_me",
    summary="Delete a specific user ",
    description=(
            """
                DELETE endpoint for removing the logged-in user from the system.
                This will do a cascade delete on all threads and messages, but will not
                effect assistants created by the user.
            """
    ),
)
async def delete_me(
    auth: AuthenticatedUser,
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository),
):
    user_id = get_header_user_id(request)
    record = await user_repo.delete_by_user_id(user_id=user_id)
    if record:
        return record
    raise NotFoundException


@router.get(
    "/me/threads",
    tags=[DEFAULT_TAG],
    response_model=Union[List[Thread], GroupedThreads],
    operation_id="retrieve_threads",
    summary="Retrieve threads by user ",
    description="""
                GET endpoint for fetching all threads associated with the logged-in user.
            """,
)
async def retrieve_my_threads(
    auth: AuthenticatedUser,
    request: Request,
    thread_repo: ThreadRepository = Depends(get_thread_repository),
    grouped: Optional[bool] = Query(None),
    timezoneOffset: Optional[int] = Query(None),
):
    user_id = get_header_user_id(request)
    records = await thread_repo.retrieve_threads_by_user_id(user_id=user_id)
    if not grouped:
        return records
    return group_threads(records, timezoneOffset if timezoneOffset else 0)


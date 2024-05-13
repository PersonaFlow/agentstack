"""
repositories/user.py
----------

This module provides a repository class, `UserRepository`, specifically tailored for operations related to the User model. It extends the base repository, making use of its generic methods while also adding more domain-specific methods related to users.

Classes:
-------
- `UserRepository`: A repository class tailored for the User model.
    - `create_user`: Creates a new user in the database.
    - `_get_retrieve_query`: A private method to construct the default query for user retrieval.
    - `retrieve_users`: Fetches all users.
    - `retrieve_user`: Fetches a single user by user_id.
    - `retrieve_by_user_id`: Retrieves a user based on their user_id.
    - `update_user`: Updates an existing user.
    - `update_by_user_id`: Updates a user based on their user_id.
    - `delete_user`: Removes a user from the database.
    - `delete_by_user_id`: Removes a user based on their user_id.

Key Functionalities:
-------------------
- **Async Operations**: All methods are asynchronous for efficient, non-blocking operations.
- **Domain-Specific Methods**: While many methods utilize the base repository's functions, methods like `retrieve_by_user_id` are tailored specifically for user-related operations.
- **Exception handling and logging**: All methods are wrapped in try-except blocks to handle exceptions and log errors.

Notes:
-----
1. Transactions are encapsulated within methods, ensuring atomicity. For example, after creating or updating a user, the changes are committed to the database within the same method.
2. The use of Pydantic models (`CreateUserSchema` and `UpdateUserSchema`) for data validation and serialization ensures data integrity.
3. It's essential to ensure proper error handling in all methods, especially when interfacing with the database, to maintain data consistency and reliability.

"""
import uuid
from sqlalchemy import select
from stack.app.model.user import User
from stack.app.repositories.base import BaseRepository
from stack.app.schema.user import CreateUserSchema, UpdateUserSchema
import structlog
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from stack.app.core.datastore import get_postgresql_session_provider
from typing import Optional, Any

logger = structlog.get_logger()


def get_user_repository(
    session: AsyncSession = Depends(get_postgresql_session_provider),
):
    return UserRepository(postgresql_session=session)


class UserRepository(BaseRepository):
    def __init__(self, postgresql_session):
        self.postgresql_session = postgresql_session

    async def create_user(self, data: CreateUserSchema):
        """Creates a new user in the database."""
        try:
            values = data.model_dump()
            user = await self.create(model=User, values=values)
            await self.postgresql_session.commit()
            return user
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(
                f"Failed to create user due to a database error: {str(e)}",
                exc_info=True,
                user_data=data.json(),
            )
            raise HTTPException(status_code=400, detail="Failed to create user.") from e

    @staticmethod
    def _get_retrieve_query():
        """A private method to construct the default query for user
        retrieval."""
        return select(
            User.id,
            User.user_id,
            User.username,
            User.password,
            User.email,
            User.first_name,
            User.last_name,
            User.kwargs,
            User.created_at,
            User.updated_at,
        )

    async def retrieve_users(
        self, filters: Optional[dict[str, Any]] = None
    ) -> list[User]:
        """Fetches all users."""
        try:
            records = await self.retrieve_all(model=User, filters=filters)
            return records
        except SQLAlchemyError as e:
            await logger.exception(
                f"Failed to retrieve users due to a database error: {str(e)}",
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail="Failed to retrieve users.")

    async def retrieve_user(self, object_id: uuid.UUID):
        """Fetches a single user by UUID."""
        try:
            query = self._get_retrieve_query()
            record = await self.retrieve_one(query=query, object_id=object_id)
            return record
        except SQLAlchemyError as e:
            await logger.exception(
                f"Failed to retrieve user due to a database error: {str(e)}",
                exc_info=True,
                object_id=object_id,
            )
            raise HTTPException(status_code=500, detail="Failed to retrieve user.")

    async def retrieve_by_user_id(self, user_id: str):
        """Retrieves a user based on their user_id."""
        try:
            query = self._get_retrieve_query().where(User.user_id == user_id)
            result = await self.postgresql_session.execute(query)
            record = result.fetchone()
            return record
        except SQLAlchemyError as e:
            await logger.exception(
                "Failed to retrieve user by user_id due to a database error",
                exc_info=True,
                object_id=user_id,
            )
            raise HTTPException(
                status_code=500, detail="Failed to retrieve user by user_id."
            )

    async def update_user(self, object_id: uuid.UUID, data: UpdateUserSchema):
        """Updates an existing user based on its UUID."""
        try:
            values = data.model_dump()
            user = await self.update(model=User, values=values, object_id=object_id)
            await self.postgresql_session.commit()
            return user
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(
                "Failed to update user due to a database error",
                exc_info=True,
                object_id=object_id,
                user_data=data.model_dump_json(),
            )
            raise HTTPException(status_code=400, detail="Failed to update user.")

    async def update_by_user_id(self, user_id: str, data: UpdateUserSchema):
        """Updates an existing user based on their user_id."""
        try:
            values = data.model_dump()
            updated_user = await self.update_by_field(
                model=User, values=values, field=User.user_id, field_value=str(user_id)
            )
            await self.postgresql_session.commit()
            return updated_user
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(
                "Failed to update user by user_id due to a database error",
                exc_info=True,
                object_id=user_id,
                user_data=data.model_dump_json(),
            )
            raise HTTPException(
                status_code=400, detail="Failed to update user by user_id."
            )

    async def delete_user(self, object_id: uuid.UUID):
        """Removes a user from the database."""
        try:
            user = await self.delete(model=User, object_id=object_id)
            await self.postgresql_session.commit()
            return user
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(
                "Failed to delete user due to a database error",
                exc_info=True,
                object_id=object_id,
            )
            raise HTTPException(status_code=400, detail="Failed to delete user.")

    async def delete_by_user_id(self, user_id: str):
        """Removes a user from the database based on their user_id."""
        try:
            user = await self.delete_by_field(
                model=User, field=User.user_id, field_value=user_id
            )
            await self.postgresql_session.commit()
            return user
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(
                "Failed to delete user by user_id due to a database error",
                exc_info=True,
                object_id=user_id,
            )
            raise HTTPException(
                status_code=400, detail="Failed to delete user by user_id."
            )

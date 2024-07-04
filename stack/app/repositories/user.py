import uuid
import bcrypt
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy import select
from stack.app.model.user import User
from stack.app.repositories.base import BaseRepository
from stack.app.schema.user import CreateUserSchema, UpdateUserSchema
from stack.app.utils.exceptions import UniqueConstraintViolationError
import structlog
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from stack.app.core.datastore import get_postgresql_session_provider
from typing import Optional, Any, Union


logger = structlog.get_logger()


def get_user_repository(
    session: AsyncSession = Depends(get_postgresql_session_provider),
):
    return UserRepository(postgresql_session=session)

class UserRepository(BaseRepository):
    def __init__(self, postgresql_session):
        self.postgresql_session = postgresql_session

    def hash_and_salt_password(plain_text_password: str) -> bytes:
        """
        Hashes a given plain-text password with a randomly generated salt.

        Args:
            plain_text_password (str): Password to hash.

        Returns:
            bytes: Hashed password
        """
        return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt())


    def _prepare_user_data(self, data: Union[CreateUserSchema, UpdateUserSchema]) -> dict:
        """
        Prepare user data for database operations, handling password hashing.

        Args:
            data (Union[CreateUserSchema, UpdateUserSchema]): User data.

        Returns:
            dict: Prepared user data with hashed password if applicable.
        """
        values = data.model_dump(exclude={"password"})
        if data.password:
            values["hashed_password"] = self.hash_and_salt_password(data.password)
        return values


    async def create_user(self, data: CreateUserSchema):
        """Creates a new user in the database."""
        try:
            values = self._prepare_user_data(data)
            user = await self.create(model=User, values=values)
            await self.postgresql_session.commit()
            return user
        except IntegrityError as e:
            await self.postgresql_session.rollback()
            error_msg = str(e.orig)
            if "ix_personaflow_users_email" in error_msg:
                raise UniqueConstraintViolationError("Email")
            elif "ix_personaflow_users_username" in error_msg:
                raise UniqueConstraintViolationError("Username")
            elif "ix_personaflow_users_user_id" in error_msg:
                raise UniqueConstraintViolationError("User ID")
            else:
                logger.exception(
                    f"Failed to create user due to a database error: {error_msg}",
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
            User.hashed_password,
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
            logger.exception(
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
            logger.exception(
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
            logger.exception(
                "Failed to retrieve user by user_id due to a database error",
                exc_info=True,
                object_id=user_id,
            )
            raise HTTPException(
                status_code=500, detail="Failed to retrieve user by user_id."
            )


    async def retrieve_user_by_email(self, email: str):
        """Retrieves a user based on their email."""
        try:
            query = self._get_retrieve_query().where(User.email == email)
            result = await self.postgresql_session.execute(query)
            record = result.fetchone()
            return record
        except SQLAlchemyError as e:
            logger.exception(
                "Failed to retrieve user by email due to a database error",
                exc_info=True,
                object_id=email,
            )
            raise HTTPException(
                status_code=500, detail="Failed to retrieve user by email."
            )


    async def update_user(self, object_id: uuid.UUID, data: UpdateUserSchema):
        """Updates an existing user based on its UUID."""
        try:
            values = self._prepare_user_data(data)
            user = await self.update(model=User, values=values, object_id=object_id)
            await self.postgresql_session.commit()
            return user
        except IntegrityError as e:
            await self.postgresql_session.rollback()
            error_msg = str(e.orig)
            if "ix_personaflow_users_email" in error_msg:
                raise UniqueConstraintViolationError("Email")
            elif "ix_personaflow_users_username" in error_msg:
                raise UniqueConstraintViolationError("Username")
            elif "ix_personaflow_users_user_id" in error_msg:
                raise UniqueConstraintViolationError("User ID")
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                "Failed to update user due to a database error",
                exc_info=True,
                object_id=object_id,
                user_data=data.model_dump_json(),
            )
            raise HTTPException(status_code=400, detail="Failed to update user.")


    async def update_by_user_id(self, user_id: str, data: UpdateUserSchema):
        """Updates an existing user based on their user_id."""
        try:
            values = self._prepare_user_data(data)
            updated_user = await self.update_by_field(
                model=User, values=values, field=User.user_id, field_value=str(user_id)
            )
            await self.postgresql_session.commit()
            return updated_user
        except IntegrityError as e:
            await self.postgresql_session.rollback()
            error_msg = str(e.orig)
            if "ix_personaflow_users_email" in error_msg:
                raise UniqueConstraintViolationError("Email")
            elif "ix_personaflow_users_username" in error_msg:
                raise UniqueConstraintViolationError("Username")
            elif "ix_personaflow_users_user_id" in error_msg:
                raise UniqueConstraintViolationError("User ID")
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                "Failed to update user by user_id due to a database error",
                exc_info=True,
                object_id=user_id,
                user_data=data.model_dump_json(),
            )
            raise HTTPException(
                status_code=400, detail="Failed to update user by user_id."
            )


    async def delete_user(self, user_id: str):
        """Removes a user from the database."""
        try:
            user = await self.delete(model=User, object_id=user_id)
            await self.postgresql_session.commit()
            return user
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                "Failed to delete user due to a database error",
                exc_info=True,
                object_id=user_id,
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
            logger.exception(
                "Failed to delete user by user_id due to a database error",
                exc_info=True,
                object_id=user_id,
            )
            raise HTTPException(
                status_code=400, detail="Failed to delete user by user_id."
            )


    async def get_or_create_user(self, token_user: dict[str, str]):
        """
        Gets or creates a user when authenticating them.

        Args:
            token_user (dict): Dictionary of user


        Returns:
            User: User object
        """
        email = token_user.get("email")
        # fullname = token_user.get("name")
        user = self.retrieve_one(User.email == email)

        # Create User if DNE
        if not user:
            db_user = CreateUserSchema(email=email)
            user = self.create_user(db_user)

        return user

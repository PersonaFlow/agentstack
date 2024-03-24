"""
repositories/assistant.py
----------

This module provides a repository class, `AssistantRepository`, specifically tailored for operations related to the Assistant model. It extends the base repository, leveraging its generic methods while also adding more domain-specific methods related to assistants.

Classes:
-------
- `AssistantRepository`: A repository class tailored for the Assistant model.
    - `create_assistant`: Creates a new assistant in the database.
    - `_get_retrieve_query`: A private method to construct the default query for assistant retrieval.
    - `retrieve_assistants`: Fetches all assistants.
    - `retrieve_assistant`: Fetches a single assistant by ID.
    - `update_assistant`: Updates an existing assistant.
    - `delete_assistant`: Removes an assistant from the database.

Key Functionalities:
-------------------
- **Async Operations**: All methods are asynchronous for efficient, non-blocking operations.
- **Domain-Specific Methods**: Methods are tailored specifically for assistant-related operations.
- **Exception handling and logging**: All methods are wrapped in try-except blocks to handle exceptions and log errors, ensuring reliability and ease of debugging.

"""
import uuid
from sqlalchemy import select
from app.models.assistant import Assistant
from app.repositories.base import BaseRepository
import structlog
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.datastore import get_postgresql_session_provider
from typing import Optional, Any


logger = structlog.get_logger()

class UniqueConstraintError(Exception):
    """Exception raised for unique constraint violations in the assistant repository."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

def get_assistant_repository(session: AsyncSession = Depends(get_postgresql_session_provider)):
    return AssistantRepository(postgresql_session=session)

class AssistantRepository(BaseRepository):

    def __init__(self, postgresql_session):
        self.postgresql_session = postgresql_session

    async def create_assistant(self, data: dict) -> Assistant:
        """Creates a new assistant in the database."""
        try:
            assistant = await self.create(model=Assistant, values=data)
            await self.postgresql_session.commit()
            return assistant
        except IntegrityError as e:
            await self.postgresql_session.rollback()
            # check for unique constraint violation specifically
            if 'unique constraint "assistants_name_unique"' in str(e.orig):
                await logger.exception(f"Unique constraint violation while creating assistant: An assistant with the same name already exists.", exc_info=True, assistant_data=data)
                raise UniqueConstraintError("An assistant with the same name already exists.") from e
            else:
                await logger.exception(f"Failed to create assistant due to a database error.", exc_info=True, assistant_data=data)
                raise
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(f"Failed to create assistant due to a database error.", exc_info=True, assistant_data=data)
            # Raising a general exception, could be converted to a more specific type if needed
            raise HTTPException(status_code=400, detail=f"Failed to create assistant.") from e

    @staticmethod
    def _get_retrieve_query() -> select:
        """A private method to construct the default query for assistant retrieval."""
        return select(Assistant.id,
                      Assistant.user_id,
                      Assistant.name,
                      Assistant.config,
                      Assistant.public,
                      Assistant.created_at,
                      Assistant.updated_at
                    )

    async def retrieve_assistants(self, filters: Optional[dict[str, Any]] = None) -> list[Assistant]:
        """Fetches all assistants."""
        try:
            query = self._get_retrieve_query()
            records = await self.retrieve_all(model=Assistant, filters=filters)
            return records
        except SQLAlchemyError as e:
            await logger.exception(f"Failed to retrieve assistants due to a database error.", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to retrieve assistants.")

    async def retrieve_assistant(self, assistant_id: uuid.UUID) -> Assistant:
        """Fetches a single assistant by ID."""
        try:
            query = self._get_retrieve_query()
            record = await self.retrieve_one(query=query, object_id=assistant_id)
            return record
        except SQLAlchemyError as e:
            await logger.exception(f"Failed to retrieve assistant due to a database error.", exc_info=True, assistant_id=assistant_id)
            raise HTTPException(status_code=500, detail="Failed to retrieve assistant.")

    async def update_assistant(self, assistant_id: uuid.UUID, data: dict) -> Assistant:
        """Updates an existing assistant."""
        try:
            # Filter out keys with None values to allow for partial updates
            filtered_data = {k: v for k, v in data.items() if v is not None}
            assistant = await self.update(model=Assistant, values=filtered_data, object_id=assistant_id)
            await self.postgresql_session.commit()
            return assistant
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(f"Failed to update assistant due to a database error.", exc_info=True, assistant_id=assistant_id, assistant_data=data)
            raise HTTPException(status_code=400, detail="Failed to update assistant.")

    async def delete_assistant(self, assistant_id: uuid.UUID) -> Assistant:
        """Removes an assistant from the database."""
        try:
            assistant = await self.delete(model=Assistant, object_id=assistant_id)
            await self.postgresql_session.commit()
            return assistant
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(f"Failed to delete assistant due to a database error: ", exc_info=True, assistant_id=assistant_id)
            raise HTTPException(status_code=400, detail="Failed to delete assistant.")

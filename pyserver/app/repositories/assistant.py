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
            raise HTTPException(status_code=400, detail=f"Failed to create assistant.") from e

    @staticmethod
    def _get_retrieve_query() -> select:
        """A private method to construct the default query for assistant retrieval."""
        return select(Assistant.id,
                      Assistant.user_id,
                      Assistant.name,
                      Assistant.config,
                      Assistant.kwargs,
                      Assistant.file_ids,
                      Assistant.public,
                      Assistant.created_at,
                      Assistant.updated_at
                    )

    async def retrieve_assistants(self, filters: Optional[dict[str, Any]] = None) -> list[Assistant]:
        """Fetches all assistants."""
        try:
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

    async def add_file_to_assistant(self, assistant_id: uuid.UUID, file_id: str) -> Assistant:
        try:
            assistant = await self.retrieve_assistant(assistant_id)
            if assistant:
                updated_file_ids = assistant.file_ids or []
                updated_file_ids.append(file_id)
                updated_data = {"file_ids": updated_file_ids}
                updated_assistant = await self.update_assistant(assistant_id, updated_data)
                return updated_assistant
            else:
                raise HTTPException(status_code=404, detail="Assistant not found")
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(f"Failed to add file to assistant due to a database error.", exc_info=True, assistant_id=assistant_id, file_id=file_id)
            raise HTTPException(status_code=500, detail="Failed to add file to assistant.")

    async def remove_file_reference_from_assistant(self, assistant_id: uuid.UUID, file_id: str) -> Assistant:
        try:
            assistant = await self.retrieve_assistant(assistant_id)
            if assistant:
                updated_file_ids = assistant.file_ids or []
                if file_id in updated_file_ids:
                    updated_file_ids.remove(file_id)
                    updated_data = {"file_ids": updated_file_ids}
                    updated_assistant = await self.update_assistant(assistant_id, updated_data)
                    return updated_assistant
                else:
                    raise HTTPException(status_code=404, detail="File not found")
            else:
                raise HTTPException(status_code=404, detail="Assistant not found")
        except SQLAlchemyError as e:
                await self.postgresql_session.rollback()
                await logger.exception(f"Failed to remove file from assistant due to a database error.", exc_info=True, assistant_id=assistant_id, file_id=file_id)
                raise HTTPException(status_code=500, detail="Failed to remove file from assistant.")

    async def remove_all_file_references(self, file_id: uuid.UUID) -> list[dict[str, Any]]:
        """Removes the file_id from all assistants that reference it. Returns a list of the id and name of the assistants that were updated."""
        updated_assistants = []
        try:
            filters = {
                "file_ids": {"contains": [str(file_id)]}
            }
            assistants = await self.retrieve_assistants(filters=filters)
            for assistant in assistants:
                updated_file_ids = assistant.file_ids
                updated_file_ids.remove(str(file_id))
                updated_data = {"file_ids": updated_file_ids}
                updated_assistant = await self.update_assistant(assistant.id, updated_data)
                assistant_id = updated_assistant.id
                assistant_name = updated_assistant.name
                updated_assistants.append({"id": assistant_id, "name": assistant_name})
            return updated_assistants
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(f"Failed to remove file references from assistants due to a database error.", exc_info=True, file_id=file_id)
            raise HTTPException(status_code=500, detail="Failed to remove file references from assistants.")

"""
repositories/message.py
----------

This module provides a repository class, `MessageRepository`, specifically tailored for operations related to the Message model. It extends the base repository, utilizing its generic methods while adding domain-specific methods for message handling.

Classes:
-------
- `MessageRepository`: A repository class tailored for the Message model.
    - `create_message`: Creates a new message in the database.
    - `_get_retrieve_query`: A private method to construct the default query for message retrieval.
    - `retrieve_by_thread_id`: Retrieves messages based on their thread_id.
    - `update_message`: Updates an existing message.
    - `delete_message`: Removes a message from the database.

Key Functionalities:
-------------------
- **Async Operations**: All methods are asynchronous, allowing for efficient, non-blocking database operations.
- **Domain-Specific Methods**: Tailored methods for message operations, such as retrieval by thread_id, are provided for specific use cases.
- **Exception Handling and Logging**: Methods include try-except blocks to handle and log exceptions, ensuring the stability and debuggability of message operations.

"""

from sqlalchemy import select
from stack.app.model.message import Message
from stack.app.repositories.base import BaseRepository
import structlog
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from stack.app.core.datastore import get_postgresql_session_provider
from typing import List

logger = structlog.get_logger()


def get_message_repository(
    session: AsyncSession = Depends(get_postgresql_session_provider),
):
    return MessageRepository(postgresql_session=session)


class MessageRepository(BaseRepository):
    def __init__(self, postgresql_session):
        self.postgresql_session = postgresql_session

    async def create_message(self, data: dict):
        """Creates a new message in the database."""
        try:
            message = await self.create(model=Message, values=data)
            await self.postgresql_session.commit()
            return message
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                "Failed to create message due to a database error",
                exc_info=True,
                message_data=data,
            )
            raise HTTPException(
                status_code=400, detail="Failed to create message."
            ) from e

    @staticmethod
    def _get_retrieve_query():
        """Constructs the default query for message retrieval."""
        return select(
            Message.id,
            Message.thread_id,
            Message.user_id,
            Message.assistant_id,
            Message.content,
            Message.role,
            Message.kwargs,
            Message.example,
            Message.created_at,
            Message.updated_at,
        )

    async def retrieve_messages_by_thread_id(self, thread_id: str) -> List[Message]:
        """Retrieves messages based on their thread_id."""
        try:
            query = self._get_retrieve_query().where(Message.thread_id == thread_id)
            result = await self.postgresql_session.execute(query)
            records = result.fetchall()
            return records
        except SQLAlchemyError as e:
            logger.exception(
                "Failed to retrieve messages by thread_id due to a database error",
                exc_info=True,
                thread_id=thread_id,
            )
            raise HTTPException(
                status_code=500, detail="Failed to retrieve messages by thread_id."
            )

    async def update_message(self, message_id: str, data: dict) -> Message:
        """Updates an existing message."""
        try:
            message = await self.update(
                model=Message, values=data, object_id=message_id
            )
            await self.postgresql_session.commit()
            return message
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                "Failed to update message due to a database error",
                exc_info=True,
                message_id=message_id,
                message_data=data,
            )
            raise HTTPException(status_code=400, detail="Failed to update message.")

    async def delete_message(self, message_id: str) -> Message:
        """Removes a message from the database."""
        try:
            message = await self.delete(model=Message, object_id=message_id)
            await self.postgresql_session.commit()
            return message
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                "Failed to delete message due to a database error",
                exc_info=True,
                message_id=message_id,
            )
            raise HTTPException(status_code=400, detail="Failed to delete message.")

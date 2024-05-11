from sqlalchemy import select
from pyserver.app.core import logger
from app.models.thread import Thread
from app.repositories.base import BaseRepository
import structlog
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.datastore import get_postgresql_session_provider
from typing import Optional, Any
from langchain_core.messages import message_chunk_to_message

from app.agents import AgentType, get_agent_executor

from langgraph.channels.base import ChannelsManager
from langgraph.checkpoint.base import empty_checkpoint
from langgraph.pregel import _prepare_next_tasks


MESSAGES_CHANNEL_NAME = "__root__"

logger = structlog.get_logger()


def get_thread_repository(
    session: AsyncSession = Depends(get_postgresql_session_provider),
):
    return ThreadRepository(postgresql_session=session)


class ThreadRepository(BaseRepository):
    def __init__(self, postgresql_session):
        self.postgresql_session = postgresql_session

    async def create_thread(self, data: dict) -> Thread:
        """Creates a new thread in the database."""
        try:
            thread = await self.create(model=Thread, values=data)
            await self.postgresql_session.commit()
            return thread
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(
                "Failed to create thread due to a database error",
                exc_info=True,
                thread_data=data,
            )
            raise HTTPException(
                status_code=400, detail="Failed to create thread."
            ) from e

    @staticmethod
    def _get_retrieve_query() -> select:
        """A private method to construct the default query for thread
        retrieval."""
        return select(
            Thread.id,
            Thread.user_id,
            Thread.assistant_id,
            Thread.name,
            Thread.kwargs,
            Thread.created_at,
            Thread.updated_at,
        )

    async def retrieve_threads(
        self, filters: Optional[dict[str, Any]] = None
    ) -> list[Thread]:
        """Fetches all threads."""
        try:
            query = self._get_retrieve_query()
            records = await self.retrieve_all(model=Thread, filters=filters)
            return records
        except SQLAlchemyError as e:
            await logger.exception(
                "Failed to retrieve threads due to a database error", exc_info=True
            )
            raise HTTPException(status_code=500, detail="Failed to retrieve threads.")

    async def retrieve_thread(self, thread_id) -> Thread:
        """Fetches a single thread by ID."""
        try:
            query = self._get_retrieve_query()
            record = await self.retrieve_one(query=query, object_id=thread_id)
            return record
        except SQLAlchemyError as e:
            await logger.exception(
                "Failed to retrieve thread due to a database error",
                exc_info=True,
                thread_id=thread_id,
            )
            raise HTTPException(status_code=500, detail="Failed to retrieve thread.")

    async def retrieve_by_thread_id(self, thread_id) -> Thread:
        """Retrieves a thread based on its thread_id."""
        try:
            query = self._get_retrieve_query().where(Thread.id == thread_id)
            result = await self.postgresql_session.execute(query)
            record = result.fetchone()
            return record
        except SQLAlchemyError as e:
            await logger.exception(
                "Failed to retrieve thread by thread_id due to a database error",
                exc_info=True,
                thread_id=thread_id,
            )
            raise HTTPException(
                status_code=500, detail="Failed to retrieve thread by thread_id."
            )

    async def update_thread(self, thread_id: str, data: dict) -> Thread:
        """Updates an existing thread."""
        try:
            thread = await self.update(model=Thread, values=data, object_id=thread_id)
            await self.postgresql_session.commit()
            return thread
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(
                "Failed to update thread due to a database error",
                exc_info=True,
                thread_id=thread_id,
                thread_data=data,
            )
            raise HTTPException(status_code=400, detail="Failed to update thread.")

    async def delete_thread(self, thread_id: str) -> Thread:
        """Removes a thread from the database."""
        try:
            thread = await self.delete(model=Thread, object_id=thread_id)
            await self.postgresql_session.commit()
            return thread
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            await logger.exception(
                "Failed to delete thread due to a database error",
                exc_info=True,
                thread_id=thread_id,
            )
            raise HTTPException(status_code=400, detail="Failed to delete thread.")

    async def retrieve_threads_by_user_id(self, user_id: str) -> List[Thread]:
        """Retrieves all threads associated with a specific user_id."""
        try:
            query = self._get_retrieve_query().where(Thread.user_id == user_id)
            result = await self.postgresql_session.execute(query)
            records = result.fetchall()
            return records
        except SQLAlchemyError as e:
            await logger.exception(
                "Failed to retrieve threads for user_id due to a database error",
                exc_info=True,
                user_id=user_id,
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve threads for the specified user.",
            )

    async def get_thread_checkpoints(self, thread_id: str):
        """Get all checkpoint messages for a thread."""
        config = {"configurable": {"thread_id": thread_id}}
        app = get_agent_executor([], AgentType.GPT_35_TURBO, "", False)
        checkpoint = await app.checkpointer.aget(config) or empty_checkpoint()
        with ChannelsManager(app.channels, checkpoint) as channels:
            return {
                "messages": [
                    message_chunk_to_message(msg)
                    for msg in channels[MESSAGES_CHANNEL_NAME].get()
                ],
                "resumeable": bool(
                    _prepare_next_tasks(checkpoint, app.nodes, channels)
                ),
            }

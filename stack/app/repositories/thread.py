from sqlalchemy import select
from stack.app.core import logger
from stack.app.model.thread import Thread
from stack.app.repositories.base import BaseRepository
import structlog
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from stack.app.core.datastore import get_postgresql_session_provider
from typing import Optional, Any
from typing import Any, Dict, Mapping, Optional, Sequence, Union
from langchain_core.runnables import RunnableConfig
from stack.app.schema.assistant import Assistant
from stack.app.agents.configurable_agent import agent
from langchain_core.messages import AnyMessage


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
            logger.exception(
                f"Failed to create thread due to a database error: {e}",
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
            logger.exception(
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
            logger.exception(
                "Failed to retrieve thread due to a database error",
                exc_info=True,
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
            logger.exception(
                "Failed to retrieve thread by thread_id due to a database error",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500, detail="Failed to retrieve thread by thread_id."
            )

    async def update_thread(self, thread_id: str, data: dict) -> Thread:
        """Updates an existing thread."""
        try:
            filtered_data = {k: v for k, v in data.items() if v is not None}
            thread = await self.update(model=Thread, values=filtered_data, object_id=thread_id)
            await self.postgresql_session.commit()
            return thread
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                "Failed to update thread due to a database error",
                exc_info=True,
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
            logger.exception(
                "Failed to delete thread due to a database error",
                exc_info=True,
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
            logger.exception(
                "Failed to retrieve threads for user_id due to a database error",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve threads for the specified user.",
            )


    async def get_thread_state(self, thread_id: str, assistant: Assistant):
        """Get the state of a thread."""
        try:
            state = await agent.aget_state(
                {
                    "configurable": {
                        **assistant.config["configurable"],
                        "thread_id": thread_id,
                        "assistant_id": assistant.id,
                    }
                }
            )
            return {
                "values": state.values,
                "next": state.next,
            }
        except TypeError as e:
            logger.exception(f"Type Error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve thread state.",
            )
        except SQLAlchemyError as e:
            logger.exception(
                f"Failed to retrieve checkpoints due to a database error: {e}",
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve threads for the specified user.",
            )
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve thread state .",
            )


    async def update_thread_state(
        config: RunnableConfig,
        values: Union[Sequence[AnyMessage], dict[str, Any]],
        *,
        assistant: Assistant,
    ):
        """Add state to a thread."""
        await agent.aupdate_state(
            {
                "configurable": {
                    **assistant.config["configurable"],
                    **config["configurable"],
                    "assistant_id": assistant.id,
                }
            },
            values,
        )


    async def get_thread_history(*, thread_id: str, assistant: Assistant):
        """Get the history of a thread."""
        return [
            {
                "values": c.values,
                "next": c.next,
                "config": c.config,
                "parent": c.parent_config,
            }
            async for c in agent.aget_state_history(
                {
                    "configurable": {
                        **assistant.config["configurable"],
                        "thread_id": thread_id,
                        "assistant_id": assistant.id,
                    }
                }
            )
        ]

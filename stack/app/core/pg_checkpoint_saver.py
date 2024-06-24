import pickle
import uuid
from datetime import datetime, timezone
from typing import Optional, Any, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.future import select
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointAt,
    CheckpointThreadTs,
    CheckpointTuple,
    SerializerProtocol,
)
from stack.app.model.checkpoint import PostgresCheckpoint
from pydantic import Field
from langchain.schema.runnable.utils import ConfigurableFieldSpec
from stack.app.core.configuration import get_settings

Base = declarative_base()


class PgCheckpointSaver(BaseCheckpointSaver):
    engine: Any = Field(...)
    async_session_factory: Any = Field(...)
    serde: SerializerProtocol = Field(default_factory=pickle)

    def __init__(
        self,
        engine: Any,
        async_session_factory: Any,
        at: Optional[CheckpointAt] = None,
        serde: Optional[SerializerProtocol] = None,
    ) -> None:
        self.engine = engine
        self.async_session_factory = async_session_factory
        self.serde = serde or self.serde
        super().__init__(at=at, serde=self.serde)

    class Config:
        arbitrary_types_allowed = True

    @property
    def config_specs(self) -> list[ConfigurableFieldSpec]:
        return [
            ConfigurableFieldSpec(
                id="thread_id",
                annotation=Optional[str],
                name="Thread ID",
                description=None,
                default=None,
                is_shared=True,
            ),
            CheckpointThreadTs,
        ]

    @classmethod
    async def from_conn_string(cls, db_url: str):
        async_engine = create_async_engine(db_url, echo=True)
        async_session_factory = sessionmaker(
            async_engine, expire_on_commit=False, class_=AsyncSession
        )
        return cls(async_engine, async_session_factory)

    async def setup(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get(self, config: RunnableConfig):
        raise NotImplementedError("Synchronous 'get' method is not implemented.")

    def put(self, config: RunnableConfig, checkpoint: Checkpoint):
        raise NotImplementedError("Synchronous 'put' method is not implemented.")

    async def aget(self, config: RunnableConfig) -> Optional[Checkpoint]:
        if checkpoint_tuple := await self.aget_tuple(config):
            return checkpoint_tuple.checkpoint
        return None

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        thread_id = uuid.UUID(config["configurable"]["thread_id"])
        thread_ts = config["configurable"].get("thread_ts")

        await self.setup()
        async with self.async_session_factory() as session:
            query = select(PostgresCheckpoint).filter_by(thread_id=thread_id)

            if thread_ts:
                query = query.filter_by(thread_ts=datetime.fromisoformat(thread_ts))
            else:
                query = query.order_by(PostgresCheckpoint.thread_ts.desc())

            query = query.limit(1)

            result = await session.execute(query)
            record = result.scalars().first()

            if record:
                checkpoint = self.serde.loads(record.checkpoint)
                return CheckpointTuple(
                    config=config,
                    checkpoint=checkpoint,
                    parent_config={
                        "configurable": {
                            "thread_id": thread_id,
                            "thread_ts": record.parent_ts.isoformat()
                            if record.parent_ts
                            else None,
                        }
                    }
                    if record.parent_ts
                    else None,
                )
        return None

    async def alist(self, config: RunnableConfig) -> AsyncIterator[CheckpointTuple]:
        thread_id = uuid.UUID(config["configurable"]["thread_id"])

        await self.setup()
        async with self.async_session_factory() as session:
            query = (
                select(PostgresCheckpoint)
                .filter(PostgresCheckpoint.thread_id == thread_id)
                .order_by(PostgresCheckpoint.thread_ts.desc())
            )

            result = await session.execute(query)
            records = result.scalars().all()

            for record in records:
                checkpoint = self.serde.loads(record.checkpoint)
                yield CheckpointTuple(
                    config={
                        "configurable": {
                            "thread_id": str(record.thread_id),
                            "thread_ts": record.thread_ts.isoformat(),
                        }
                    },
                    checkpoint=checkpoint,
                    parent_config={
                        "configurable": {
                            "thread_id": str(record.thread_id),
                            "thread_ts": record.parent_ts.isoformat()
                            if record.parent_ts
                            else None,
                        }
                    }
                    if record.parent_ts
                    else None,
                )

    async def aput(self, config: RunnableConfig, checkpoint: Checkpoint) -> None:
        await self.setup()
        async with self.async_session_factory() as session:
            serialized_checkpoint = self.serde.dumps(checkpoint)
            thread_id = config["configurable"]["thread_id"]
            thread_ts = datetime.fromisoformat(checkpoint["ts"])
            result = await session.execute(
                select(PostgresCheckpoint).filter_by(
                    thread_id=thread_id, thread_ts=thread_ts
                )
            )
            record = result.scalars().first()
            if record:
                record.checkpoint = serialized_checkpoint
                record.updated_at = datetime.now(timezone.utc)
            else:
                new_record = PostgresCheckpoint(
                    thread_id=thread_id,
                    thread_ts=thread_ts,
                    checkpoint=serialized_checkpoint,
                    parent_ts=datetime.fromisoformat(checkpoint.get("parent_ts"))
                    if checkpoint.get("parent_ts")
                    else None,
                )
                session.add(new_record)

            await session.commit()

        return {
            "configurable": {
                "thread_id": thread_id,
                "thread_ts": checkpoint["ts"],
            }
        }


def get_pg_checkpoint_saver(
    serde: SerializerProtocol = pickle, at: CheckpointAt = CheckpointAt.END_OF_STEP
) -> PgCheckpointSaver:
    settings = get_settings()
    engine = create_async_engine(settings.INTERNAL_DATABASE_URI)
    async_session_factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    return PgCheckpointSaver(
        engine=engine, async_session_factory=async_session_factory, serde=serde, at=at
    )

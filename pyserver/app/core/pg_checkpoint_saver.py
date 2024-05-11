import pickle
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
    CheckpointTuple,
    SerializerProtocol,
)
from pyserver.app.models.checkpoint import PostgresCheckpoint
from pydantic import Field
from langchain.schema.runnable.utils import ConfigurableFieldSpec
from pyserver.app.core.configuration import get_settings

Base = declarative_base()


class PgCheckpointSaver(BaseCheckpointSaver):
    engine: Any = Field(...)
    async_session_factory: Any = Field(...)
    serde: SerializerProtocol = Field(default_factory=pickle)

    def __init__(
        self,
        engine: Any,
        async_session_factory: Any,
        at: CheckpointAt = CheckpointAt.END_OF_STEP,
        serde: Optional[SerializerProtocol] = None,
    ):
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
                id="user_id",
                annotation=str,
                name="User ID",
                description=None,
                default="",
                is_shared=True,
            ),
            ConfigurableFieldSpec(
                id="thread_id",
                annotation=str,
                name="Thread ID",
                description=None,
                default="",
                is_shared=True,
            ),
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
        await self.setup()
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(PostgresCheckpoint).filter_by(
                    user_id=config["configurable"]["user_id"],
                    thread_id=config["configurable"]["thread_id"],
                )
            )

            record = result.scalars().first()
            if record:
                return self.serde.loads(record.checkpoint)

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        await self.setup()
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(PostgresCheckpoint)
                .filter_by(
                    user_id=config["configurable"]["user_id"],
                    thread_id=config["configurable"]["thread_id"],
                )
                .order_by(PostgresCheckpoint.updated_at.desc())
            )
            record = result.scalars().first()
            if record:
                return CheckpointTuple(
                    config=config, checkpoint=self.serde.loads(record.checkpoint)
                )

    async def alist(self, config: RunnableConfig) -> AsyncIterator[CheckpointTuple]:
        await self.setup()
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(PostgresCheckpoint)
                .filter_by(
                    user_id=config["configurable"]["user_id"],
                    thread_id=config["configurable"]["thread_id"],
                )
                .order_by(PostgresCheckpoint.updated_at.desc())
            )
            records = result.scalars().all()
            for record in records:
                yield CheckpointTuple(
                    config=config, checkpoint=self.serde.loads(record.checkpoint)
                )

    async def aput(self, config: RunnableConfig, checkpoint: Checkpoint) -> None:
        # TODO: At some point in the pipeline this gets called with None config
        # Maybe langgraph bug, but need to make sure all expected checkpoints are being saved
        if not config:
            return
        await self.setup()
        async with self.async_session_factory() as session:
            serialized_checkpoint = self.serde.dumps(checkpoint)
            result = await session.execute(
                select(PostgresCheckpoint).filter_by(
                    user_id=config["configurable"]["user_id"],
                    thread_id=config["configurable"]["thread_id"],
                )
            )
            record = result.scalars().first()
            if record:
                record.checkpoint = serialized_checkpoint
            else:
                new_record = PostgresCheckpoint(
                    user_id=config["configurable"]["user_id"],
                    thread_id=config["configurable"]["thread_id"],
                    checkpoint=serialized_checkpoint,
                )
                session.add(new_record)
            await session.commit()


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

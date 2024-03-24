from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
import pickle
from typing import Optional
from langchain.schema.runnable.utils import ConfigurableFieldSpec
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint
from langgraph.checkpoint import CheckpointAt
from app.models.checkpoint import PostgresCheckpoint
from pydantic import Field
from typing import Any
from app.core.configuration import get_settings


Base = declarative_base()

class PgCheckpointSaver(BaseCheckpointSaver):
    engine: AsyncEngine = Field(...)
    async_session_factory: Any = Field(...)

    def __init__(self, engine: AsyncEngine, async_session_factory: Any, at: CheckpointAt = CheckpointAt.END_OF_STEP):
        super().__init__(at=at)
        self.engine = engine
        self.async_session_factory = async_session_factory

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
                default=None,
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
        return cls(async_engine)

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
                    thread_id=config["configurable"]["thread_id"]
                )
            )
            record = result.scalars().first()
            if record:
                return pickle.loads(record.checkpoint)

    async def aput(self, config: RunnableConfig, checkpoint: Checkpoint) -> None:
        await self.setup()
        async with self.async_session_factory() as session:
            result = await session.execute(
                select(PostgresCheckpoint).filter_by(
                    user_id=config["configurable"]["user_id"],
                    thread_id=config["configurable"]["thread_id"]
                )
            )
            record = result.scalars().first()
            serialized_checkpoint = pickle.dumps(checkpoint)
            if record:
                record.checkpoint = serialized_checkpoint
            else:
                new_record = PostgresCheckpoint(
                    user_id=config["configurable"]["user_id"],
                    thread_id=config["configurable"]["thread_id"],
                    checkpoint=serialized_checkpoint
                )
                session.add(new_record)
            await session.commit()


def get_pg_checkpoint_saver(at: CheckpointAt = CheckpointAt.END_OF_STEP) -> PgCheckpointSaver:
    settings = get_settings()
    engine = create_async_engine(settings.INTERNAL_DATABASE_URI)
    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    return PgCheckpointSaver(engine, async_session_factory, at)

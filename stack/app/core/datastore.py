import structlog
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from redis.asyncio import Redis
from sqlalchemy.orm import sessionmaker
from stack.app.core.configuration import Settings, get_settings
from typing import AsyncGenerator, Annotated, Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Optional
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

logger = structlog.get_logger()
settings = get_settings()

_checkpointer: Optional[AsyncPostgresSaver] = None
# checkpointer used by langgraph for saving messages
def get_checkpointer() -> AsyncPostgresSaver:
    if _checkpointer is None:
        logger.error("Attempting to access uninitialized checkpointer")
        raise RuntimeError("Checkpointer not initialized. Ensure application startup has completed.")
    return _checkpointer

async def initialize_checkpointer() -> None:
    global _checkpointer
    if _checkpointer is not None:
        logger.info("Checkpointer already initialized")
        return
        
    conn_string = (
        f"postgresql://{settings.INTERNAL_DATABASE_USER}:{settings.INTERNAL_DATABASE_PASSWORD}"
        f"@{settings.INTERNAL_DATABASE_HOST}:{settings.INTERNAL_DATABASE_PORT}"
        f"/{settings.INTERNAL_DATABASE_DATABASE}"
        f"?options=-c%20search_path%3D{settings.INTERNAL_DATABASE_SCHEMA}"
    )
    
    try:
        logger.info("Creating checkpointer instance...")
        async with AsyncPostgresSaver.from_conn_string(conn_string) as saver:
            _checkpointer = saver
            await _checkpointer.setup()
            logger.info("Completed checkpointer setup")
    except Exception as e:
        logger.error(f"Failed to initialize checkpointer: {str(e)}", exc_info=True)
        raise

async def get_postgresql_session_provider(
    settings: Settings = Depends(get_settings),
) -> AsyncGenerator[AsyncSession, None]:
    async_engine = create_async_engine(settings.INTERNAL_DATABASE_URI, echo=True)
    async_session_factory = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session


def get_session() -> Generator[Session, Any, None]:
    engine = create_engine(settings.INTERNAL_DATABASE_URI)
    with Session(engine) as session:
        yield session


async def get_redis_connection():
    return Redis.from_url("redis://localhost:6379")

# datastore.py
import structlog
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker
from redis.asyncio import Redis
from typing import Generator, Any, AsyncIterator, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from stack.app.core.configuration import Settings, get_settings

logger = structlog.get_logger()
settings = get_settings()

# Global variables for database connections
_async_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None
_checkpointer: Optional[AsyncPostgresSaver] = None

async def initialize_db() -> None:
    """Initialize database engine and session maker.
    
    This should be called once at application startup.
    """
    global _async_engine, _async_session_maker
    
    if _async_engine is not None:
        logger.info("Database already initialized")
        return

    _async_engine = create_async_engine(
        settings.INTERNAL_DATABASE_URI,
        # echo=settings.ENVIRONMENT != "PRODUCTION",  # Enable SQL logging in non-prod
        echo=False,
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )
    
    _async_session_maker = async_sessionmaker(
        _async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    logger.info("Database engine and session maker initialized")

async def cleanup_db() -> None:
    """Cleanup database resources.
    
    This should be called when the application shuts down.
    """
    global _async_engine
    if _async_engine is not None:
        await _async_engine.dispose()
        _async_engine = None
        logger.info("Database engine disposed")

async def get_postgresql_session() -> AsyncIterator[AsyncSession]:
    """Get a database session.
    
    This is used as a FastAPI dependency to get a database session for each request.
    """
    if _async_session_maker is None:
        raise RuntimeError("Database not initialized. Ensure application startup has completed.")
        
    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_postgresql_session_provider(
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_postgresql_session),
) -> AsyncSession:
    """Dependency provider for database sessions."""
    return session

def get_session() -> Generator[Session, Any, None]:
    """Get a synchronous database session.
    
    This is used for migrations and other sync operations.
    """
    engine = create_engine(settings.INTERNAL_DATABASE_URI)
    with Session(engine) as session:
        yield session

async def get_redis_connection():
    """Get a Redis connection."""
    return Redis.from_url("redis://localhost:6379")

async def initialize_checkpointer() -> None:
    """Initialize the global checkpointer instance.
    
    This creates a connection pool for the checkpointer that will be used
    throughout the application lifecycle. The pool will be closed when the
    application shuts down.
    """
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
        # Create a connection pool that will be managed by the checkpointer
        pool = AsyncConnectionPool(
            conn_string,
            min_size=1,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0}
        )
        
        # Create the checkpointer with the pool
        _checkpointer = AsyncPostgresSaver(pool)
        
        # Set up the database tables
        await _checkpointer.setup()
        logger.info("Completed checkpointer setup")
    except Exception as e:
        logger.error(f"Failed to initialize checkpointer: {str(e)}", exc_info=True)
        if '_checkpointer' in globals() and hasattr(_checkpointer, 'conn'):
            await _checkpointer.conn.close()
        _checkpointer = None
        raise

def get_checkpointer() -> AsyncPostgresSaver:
    """Get the global checkpointer instance.
    
    Returns:
        AsyncPostgresSaver: The global checkpointer instance.
        
    Raises:
        RuntimeError: If the checkpointer hasn't been initialized.
    """
    if _checkpointer is None:
        logger.error("Attempting to access uninitialized checkpointer")
        raise RuntimeError("Checkpointer not initialized. Ensure application startup has completed.")
    return _checkpointer
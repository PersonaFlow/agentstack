import asyncio
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from stack.app.core.configuration import get_settings

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def test_db_connection():
    from sqlalchemy.sql import text
    from dotenv import load_dotenv
    env_path = ".env"
    load_dotenv(env_path)
    settings = get_settings()

    # Creating an async engine
    engine = create_async_engine(settings.INTERNAL_DATABASE_URI, echo=True)

    # Creating a session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Using the session to execute a query
    async with async_session() as session:
        # Simple query to test the connection
        result = await session.execute(text("SELECT 1"))
        print("Query result:", result.scalar())

    # Closing the engine
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_db_connection())

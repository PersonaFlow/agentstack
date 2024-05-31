import asyncio
import os
import subprocess
import logging
import asyncpg
import pytest

from stack.app.main import app
from stack.app.core.lifespan import lifespan, get_pg_pool

from stack.app.core.configuration import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

TEST_DB = "test_stack"

async def _get_admin_conn() -> asyncpg.Connection:
    return await asyncpg.connect(
        user=settings.INTERNAL_DATABASE_USER,
        password=settings.INTERNAL_DATABASE_PASSWORD,
        host=settings.INTERNAL_DATABASE_HOST,
        port=settings.INTERNAL_DATABASE_PORT,
        database="postgres",
    )

async def _get_test_conn() -> asyncpg.Connection:
    return await asyncpg.connect(
        user=settings.INTERNAL_DATABASE_USER,
        password=settings.INTERNAL_DATABASE_PASSWORD,
        host=settings.INTERNAL_DATABASE_HOST,
        port=settings.INTERNAL_DATABASE_PORT,
        database=TEST_DB,
    )


async def _create_test_db() -> None:
    """Check if the test database exists and create it if it doesn't."""
    logger.debug("Creating test database...")
    conn = await _get_admin_conn()
    exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname=$1", TEST_DB)
    if not exists:
        await conn.execute(f'CREATE DATABASE "{TEST_DB}"')
    await conn.close()

async def _create_personaflow_schema() -> None:
    logger.debug("Creating personaflow schema...")
    test_conn = await _get_test_conn()
    await test_conn.execute(f'CREATE SCHEMA IF NOT EXISTS personaflow')
    await test_conn.close()

# async def _drop_test_db() -> None:
#     """Check if the test database exists and if so, drop it."""
#     conn = await _get_admin_conn()
#     exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname=$1", TEST_DB)
#     if exists:
#         await conn.execute(f'DROP DATABASE "{TEST_DB}" WITH (FORCE)')
#     await conn.close()

async def _drop_test_db() -> None:
    logger.debug("Dropping test database if it exists...")
    admin_conn = await _get_admin_conn()
    exists = await admin_conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname=$1", TEST_DB)
    if exists:
        await admin_conn.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{TEST_DB}' AND pid <> pg_backend_pid();
        """)
        await admin_conn.execute(f'DROP DATABASE "{TEST_DB}"')
    await admin_conn.close()

def _migrate_test_db() -> None:
    logger.debug("Migrating test database...")
    os.environ['TEST_DATABASE_URI'] = f'postgres://postgres:postgres@{settings.INTERNAL_DATABASE_HOST}:{settings.INTERNAL_DATABASE_PORT}/{TEST_DB}'
    result = subprocess.run(["alembic", "upgrade", "head"], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Alembic migration failed: {result.stdout}\n{result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, result.args)


    # subprocess.run(["alembic", "upgrade", "head"], check=True)


@pytest.fixture(scope="session")
async def pool():
    await _drop_test_db()  # In case previous test session was abruptly terminated
    await _create_test_db()
    await _create_personaflow_schema()
    _migrate_test_db()
    async with lifespan(app):
        yield get_pg_pool()
    await _drop_test_db()


@pytest.fixture(scope="function", autouse=True)
async def clear_test_db(pool):
    """Truncate all tables before each test."""
    async with pool.acquire() as conn:
        query = """
        DO
        $$
        DECLARE
        r RECORD;
        BEGIN
        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'personaflow') LOOP
            EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' CASCADE;';
        END LOOP;
        END
        $$;
        """
        await conn.execute(query)


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

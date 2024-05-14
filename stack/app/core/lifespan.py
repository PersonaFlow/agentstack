import os
from contextlib import asynccontextmanager

import asyncpg
import orjson
import structlog
from fastapi import FastAPI
from stack.app.core.configuration import get_settings

_pg_pool = None

settings = get_settings()

def get_pg_pool() -> asyncpg.pool.Pool:
    return _pg_pool


async def _init_connection(conn) -> None:
    await conn.set_type_codec(
        "json",
        encoder=lambda v: orjson.dumps(v).decode(),
        decoder=orjson.loads,
        schema="pg_catalog",
    )
    await conn.set_type_codec(
        "jsonb",
        encoder=lambda v: orjson.dumps(v).decode(),
        decoder=orjson.loads,
        schema="pg_catalog",
    )
    await conn.set_type_codec(
        "uuid", encoder=lambda v: str(v), decoder=lambda v: v, schema="pg_catalog"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.render_to_log_kwargs,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    global _pg_pool

    _pg_pool = await asyncpg.create_pool(
        database=settings.INTERNAL_DATABASE_DATABASE,
        user=settings.INTERNAL_DATABASE_USER,
        password=settings.INTERNAL_DATABASE_PASSWORD,
        host=settings.INTERNAL_DATABASE_HOST,
        port=settings.INTERNAL_DATABASE_PORT,
        init=_init_connection,
    )
    yield
    await _pg_pool.close()
    _pg_pool = None

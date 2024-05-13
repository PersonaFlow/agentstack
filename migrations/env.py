# migrations/env.py
# -----------------
# This script sets up the environment for Alembic migrations. It provides both offline and online
# migration paths, ensuring smooth interaction with the application's database schema. The code
# dynamically imports all models, sets up logging, and defines the migration behavior based on
# the context provided by Alembic.

# Necessary imports for asynchronous operations, importing modules, and logging.
import asyncio
import importlib
import pkgutil
from logging.config import fileConfig

# SQLAlchemy and Alembic specific imports for migrations.
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Importing application-specific configurations.
from stack.app.core.configuration import settings

# Fetching the Alembic configuration object to access values from the .ini file.
config = context.config

# Setup Python logging based on the configuration file.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Setting the metadata for the database tables.
from stack.app.model.base import Base

target_metadata = Base.metadata

# Dynamically importing all models.
from stack.app import model

for _, module_name, is_package in pkgutil.iter_modules(model.__path__):
    if not is_package:
        importlib.import_module(f".{module_name}", model.__name__)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    In this mode, an actual database connection is not established.
    """
    url = settings.INTERNAL_DATABASE_URI
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        version_table_schema=settings.INTERNAL_DATABASE_SCHEMA,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Helper function to run migrations with a given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=settings.INTERNAL_DATABASE_SCHEMA,
    )
    with context.begin_transaction():
        context.run_migrations()


async def create_schema_if_not_exists(engine):
    """Asynchronously create the schema if it does not already exist."""
    async with engine.begin() as conn:
        await conn.execute(
            text(f"CREATE SCHEMA IF NOT EXISTS {settings.INTERNAL_DATABASE_SCHEMA}")
        )


async def run_async_migrations() -> None:
    """Create an asynchronous engine and associate a connection with the
    migration context."""
    payload = config.get_section(config.config_ini_section, {})
    payload["sqlalchemy.url"] = settings.INTERNAL_DATABASE_URI
    connectable = async_engine_from_config(
        payload,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    await create_schema_if_not_exists(connectable)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode, establishing a real connection to the
    database."""
    asyncio.run(run_async_migrations())


# Determine the migration mode (offline/online) and run migrations accordingly.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

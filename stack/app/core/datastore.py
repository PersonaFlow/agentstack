"""
core/datastore.py
----------

This module provides utility functions and dependencies to manage the retrieval and lifecycle of the PostgreSQL session for the FastAPI application.
It integrates with the application configuration settings to fetch or create a new database session as required.


 """

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from stack.app.core.configuration import Settings, get_settings
from typing import AsyncGenerator, Annotated, Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


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
    engine = create_engine(Settings.INTERNAL_DATABASE_URI)
    with Session(engine) as session:
        yield session

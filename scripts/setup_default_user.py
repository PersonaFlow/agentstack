# scripts/setup_default_user.py

import asyncio
import os
import sys

# Add the 'stack' directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all models to ensure they're registered with SQLAlchemy
from stack.app.model.user import User
from stack.app.model.thread import Thread
from stack.app.model.assistant import Assistant
from stack.app.model.file import File
from stack.app.model.message import Message
from stack.app.model.checkpoint import PostgresCheckpoint

from stack.app.core.configuration import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

async def insert_default_user():
    engine = create_async_engine(settings.INTERNAL_DATABASE_URI)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    default_user_id = settings.DEFAULT_USER_ID

    async with async_session() as session:
        # Check if the default user already exists
        query = select(User).where(User.user_id == default_user_id)
        result = await session.execute(query)
        default_user = result.scalar_one_or_none()

        if default_user is None:
            # Create the default user
            default_user = User(user_id=default_user_id, username=f"Default User ({default_user_id})")
            session.add(default_user)
            await session.commit()
            print(f"Default user with ID '{default_user_id}' inserted successfully.")
        else:
            print(f"Default user with ID '{default_user_id}' already exists.")


if __name__ == "__main__":
    asyncio.run(insert_default_user())

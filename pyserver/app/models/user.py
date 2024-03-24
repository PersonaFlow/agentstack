"""
models/user.py
----------

This module provides an ORM model for managing user data within the application. By keeping a record of registered users, the system can authenticate, authorize, and track user activities, ensuring data integrity and security.

Dependencies:
------------
- `uuid`: Module from the standard library for generating and managing UUID values.
- `sqlalchemy`: SQLAlchemy is a SQL toolkit and Object-Relational Mapping (ORM) library for Python.
- `app.models.base`: Base class and utilities for defining ORM models in this application.

Classes:
-------
- `User`: An ORM model representing a registered user in the application.
    - `id`: A unique identifier for the user. It's a UUID type and is automatically generated by the database.
    - `user_id`: identifier for the user, used for correlating local user with external systems.
    - (Optional) `email`: The email address associated with the user's account. It's a string type and is expected to be unique across the userbase
    - (Optional) `first_name`: The first name of the user.
    - (Optional) `last_name`: The last name of the user.
    - (Optional) `username`: The username chosen by the user. It's a string type and is expected to be unique across the userbase.
    - (Optional) `password`: The hashed password associated with the user's account.
    - (Optional) `additional_kwargs`: Additional metadata associated with the user.

Note:
-----
This module assumes that passwords are hashed before being stored in the database.

"""

from datetime import datetime
import uuid
from sqlalchemy import String, text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.configuration import settings
from app.models.base import Base
from sqlalchemy import event

from app.models.base import Base
from app.models.util import generate_unique_identifier


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {"schema": settings.INTERNAL_DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="A unique identifier for the user. It's a UUID type and is automatically generated by the database."
    )
    user_id: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        unique=True,
        index=True,
        comment="A unique identifier for the user, used for tracking and referencing purposes so as to not expose the internal db user ID and allow for correlating the user with external systems."
    )
    username: Mapped[str] = mapped_column(
        String(),
        nullable=True,
        comment="The username chosen by the user. It's a string type and is expected to be unique across the userbase."
    )
    password: Mapped[str] = mapped_column(
        String(),
        nullable=True,
        comment="The hashed password associated with the user's account."
    )
    email: Mapped[str] = mapped_column(
        String(),
        nullable=True,
        comment="The email address associated with the user's account. It's a string type and is expected to be unique across the userbase."
    )
    first_name: Mapped[str] = mapped_column(
        String(),
        nullable=True,
        comment="The first name of the user."
    )
    last_name: Mapped[str] = mapped_column(
        String(),
        nullable=True,
        comment="The last name of the user."
    )
    additional_kwargs: Mapped[JSONB] = mapped_column(
        JSONB(),
        nullable=True,
        comment="Additional metadata associated with the user."
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Created date"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last updated date"
    )

@event.listens_for(User, 'before_insert')
def receive_before_insert(mapper, connection, target):
    """Listen for the 'before_insert' event and set the 'user_id' field if not provided."""
    if not target.user_id:
        target.user_id = generate_unique_identifier()

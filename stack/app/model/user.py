from datetime import datetime
import uuid
from sqlalchemy import String, text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from stack.app.core.configuration import settings
from stack.app.model.base import Base
from sqlalchemy import event

from stack.app.model.base import Base
from stack.app.model.util import generate_unique_identifier


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": settings.INTERNAL_DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="A unique identifier for the user. It's a UUID type and is automatically generated by the database.",
    )
    user_id: Mapped[str] = mapped_column(
        String(), # string since organization may want to use their own user id
        nullable=False,
        unique=True,
        index=True,
        comment="A unique identifier for the user, used for tracking and referencing purposes so as to not expose the internal db user ID and allow for correlating the user with external systems.",
    )
    username: Mapped[str] = mapped_column(
        String(),
        nullable=True,
        comment="The username chosen by the user. It's a string type and is expected to be unique across the userbase.",
    )
    password: Mapped[str] = mapped_column(
        String(),
        nullable=True,
        comment="The hashed password associated with the user's account. *NOTE: This is a convenience placeholder field*.",
    )
    email: Mapped[str] = mapped_column(
        String(),
        nullable=True,
        comment="The email address associated with the user's account. It's a string type and is expected to be unique across the userbase.",
    )
    first_name: Mapped[str] = mapped_column(
        String(), nullable=True, comment="The first name of the user."
    )
    last_name: Mapped[str] = mapped_column(
        String(), nullable=True, comment="The last name of the user."
    )
    kwargs: Mapped[JSONB] = mapped_column(
        JSONB(),
        nullable=True,
        comment="Additional key-value data to be associated with the user.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="Created date",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last updated date",
    )

    thread = relationship(
        "Thread",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    checkpoint = relationship(
        "PostgresCheckpoint",
        back_populates="user"
    )

    # don't cascade assistants when user is deleted
    assistant = relationship(
        "Assistant",
        back_populates="user"
    )

    file = relationship(
        "File",
        back_populates="user"
    )

    message = relationship(
        "Message",
        back_populates="user"
    )

@event.listens_for(User, "before_insert")
def receive_before_insert(mapper, connection, target):
    """Listen for the 'before_insert' event and set the 'user_id' field if not
    provided."""
    if not target.user_id:
        target.user_id = generate_unique_identifier()

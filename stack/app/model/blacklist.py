import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column
from stack.app.core.configuration import settings
from stack.app.model.base import Base
from sqlalchemy import DateTime, LargeBinary, String, text, ForeignKey


class Blacklist(Base):
    """
    Table that contains the list of JWT access tokens that are blacklisted during logout.
    """

    __tablename__ = "blacklist"
    __table_args__ = {"schema": settings.INTERNAL_DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="A unique identifier for the checkpoint. It's a UUID type and is automatically generated by the database.",
    )
    token_id: Mapped[str] = mapped_column(
        String(),
        index=True,
        comment="The ID of the token to be blacklisted.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="The timestamp when the token was blacklisted.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="The timestamp when the token was last updated.",
    )
from datetime import datetime
import uuid
from sqlalchemy import String, text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.configuration import settings
from app.models.base import Base

class File(Base):
    __tablename__ = 'files'
    __table_args__ = {"schema": settings.INTERNAL_DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="A unique identifier for the file. It's a UUID type and is automatically generated by the database."
    )
    user_id: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        index=True,
        comment="The ID of the user who created the file."
    )
    filename: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        comment="The name of the file."
    )
    purpose: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        comment="The purpose of the file - either thread, assistants, or personas."
    )
    mime_type: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        comment="The mime type of the file."
    )
    bytes: Mapped[str] = mapped_column(
        Integer(),
        nullable=False,
        comment="The bytes of the file. (Added automatically when file is uploaded)"
    )
    kwargs: Mapped[JSONB] = mapped_column(
        JSONB(),
        nullable=True,
        comment="Any additional information to be included for the file."
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

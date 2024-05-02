from datetime import datetime
import uuid
from sqlalchemy import String, Boolean, text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.configuration import settings
from app.models.base import Base

class Assistant(Base):
    __tablename__ = 'assistants'
    __table_args__ = {"schema": settings.INTERNAL_DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="A unique identifier for the assistant. It's a UUID type and is automatically generated by the database."
    )
    user_id: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        index=True,
        comment="The ID of the user who created the assistant."
    )
    name: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        comment="The name of the assistant."
    )
    config: Mapped[JSONB] = mapped_column(
        JSONB(),
        nullable=False,
        comment="The assistant config, containing specific configuration parameters."
    )
    public: Mapped[bool] = mapped_column(
        Boolean(),
        default=False,
        comment="Whether or not the assistant is public."
    )
    file_ids: Mapped[ARRAY] = mapped_column(
        ARRAY(String()),
        nullable=True,
        comment="A list of files to be associated with this assistant for use with Retrieval."
    )
    kwargs: Mapped[JSONB] = mapped_column(
        JSONB(),
        nullable=True,
        comment="The assistant metadata, containing any additional information about the assistant."
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


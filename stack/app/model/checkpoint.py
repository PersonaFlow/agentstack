from datetime import datetime
import uuid
from sqlalchemy import DateTime, LargeBinary, String, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from stack.app.core.configuration import settings
from stack.app.model.base import Base


class PostgresCheckpoint(Base):
    __tablename__ = "checkpoints"
    __table_args__ = {"schema": settings.INTERNAL_DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        server_default=text("gen_random_uuid()"),
        comment="A unique identifier for the checkpoint. It's a UUID type and is automatically generated by the database.",
    )
    user_id: Mapped[str] = mapped_column(
        String(),
        ForeignKey(f"{settings.INTERNAL_DATABASE_SCHEMA}.users.user_id"),
        nullable=True,
        comment="The ID of the user to whom the checkpoint belongs.",
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(f"{settings.INTERNAL_DATABASE_SCHEMA}.threads.id"),
        nullable=False,
        primary_key=True,
        comment="The ID of the thread to which the checkpoint belongs.",
    )
    thread_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
        nullable=False,
        comment="The timestamp of the checkpoint within the thread.",
    )
    parent_ts: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="The timestamp of the parent checkpoint, if any.",
    )
    checkpoint: Mapped[LargeBinary] = mapped_column(
        LargeBinary(), nullable=False, comment="The serialized checkpoint data."
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        comment="The timestamp when the checkpoint was created.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="The timestamp when the checkpoint was last updated.",
    )

    thread = relationship("Thread", back_populates="checkpoint")

    user = relationship("User", back_populates="checkpoint")

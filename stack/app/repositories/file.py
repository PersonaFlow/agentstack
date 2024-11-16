import uuid
import os
from datetime import datetime
from sqlalchemy import select
from stack.app.model.file import File
from stack.app.repositories.base import BaseRepository
import structlog
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from stack.app.core.datastore import get_postgresql_session_provider
from typing import Optional, Any
from stack.app.core.configuration import settings
from stack.app.utils.file_helpers import guess_file_extension, guess_mime_type
from fastapi import Response

logger = structlog.get_logger()


def get_file_repository(
    session: AsyncSession = Depends(get_postgresql_session_provider),
):
    return FileRepository(postgresql_session=session)


class FileRepository(BaseRepository):
    def __init__(self, postgresql_session):
        self.postgresql_session = postgresql_session

    async def create_file(self, data: dict, file_content: bytes) -> File:
        try:
            original_filename = data.get("filename")
            if not original_filename:
                raise ValueError("Filename is required")

            # Guess the mime type using the original filename
            mime_type = guess_mime_type(original_filename, file_content)

            # Get the file extension from the original filename
            _, file_extension = os.path.splitext(original_filename)
            if not file_extension:
                file_extension = (
                    f".{guess_file_extension(original_filename, file_content)}"
                )

            data["mime_type"] = mime_type

            file_id = uuid.uuid4()
            # Create the new filename using the UUID and original extension
            new_filename = f"{file_id}{file_extension}"
            file_path = os.path.join(settings.FILE_DATA_DIRECTORY, new_filename)
            data["id"] = file_id
            data["source"] = file_path

            # Create the file record in the database
            file = await self.create(model=File, values=data)
            await self.postgresql_session.commit()

            # Create the file data directory if it doesn't exist
            os.makedirs(settings.FILE_DATA_DIRECTORY, exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(file_content)

            return file

        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                f"Failed to create file due to a database error: {e}.",
                exc_info=True,
                file_data=data,
            )
            raise HTTPException(
                status_code=400, detail=f"Failed to create file: {e}."
            ) from e
        except ValueError as e:
            logger.exception(
                f"Failed to create file due to a value error: {e}.",
                exc_info=True,
                file_data=data,
            )
            raise HTTPException(status_code=400, detail=str(e)) from e

    @staticmethod
    def _get_retrieve_query() -> select:
        """A private method to construct the default query for file
        retrieval."""
        return select(
            File.id,
            File.user_id,
            File.filename,
            File.purpose,
            File.kwargs,
            File.mime_type,
            File.source,
            File.bytes,
            File.created_at,
            File.updated_at,
        )

    async def retrieve_files(
        self, user_id: str, purpose: Optional[str] = None
    ) -> list[File]:
        """Fetches all files for a user, optionally filtered by purpose."""
        try:
            filters = {"user_id": user_id}
            if purpose:
                filters["purpose"] = purpose
            records = await self.retrieve_all(model=File, filters=filters)
            return records
        except SQLAlchemyError as e:
            logger.exception(
                f"Failed to retrieve files due to a database error.",
                exc_info=True,
                user_id=user_id,
                purpose=purpose,
            )
            raise HTTPException(status_code=500, detail="Failed to retrieve files.")

    async def retrieve_file(self, file_id: uuid.UUID) -> File:
        """Fetches a single file by ID."""
        try:
            query = self._get_retrieve_query()
            record = await self.retrieve_one(query=query, object_id=file_id)
            return record
        except SQLAlchemyError as e:
            logger.exception(
                f"Failed to retrieve file due to a database error.",
                exc_info=True,
                file_id=file_id,
            )
            raise HTTPException(status_code=500, detail="Failed to retrieve file.")

    async def delete_file(self, file_id: uuid.UUID) -> File:
        """Removes a file from the database and deletes the file content from
        the local file system."""
        try:
            file = await self.delete(model=File, object_id=file_id)
            await self.postgresql_session.commit()

            return file
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                f"Failed to delete file due to a database error: {e}", exc_info=True
            )
            raise HTTPException(status_code=400, detail=f"Failed to delete file.")

    async def retrieve_file_content(self, file_id: str) -> Any:
        """Fetches the content of a file by ID from the local file system."""
        try:
            file = await self.retrieve_file(file_id)
            if not file:
                logger.exception(f"File: {file_id} not found.")
                raise HTTPException(status_code=404, detail="File not found.")
            file_path = file.source
            logger.info(
                f"Reading content for file {file_id} from local file system. File path: {file_path}"
            )
            with open(file_path, "rb") as f:
                file_content = f.read()
            return file_content

        except FileNotFoundError as e:
            logger.exception(
                f"Failed to retrieve file content from local file system.",
                exc_info=True,
                file_id=file_id,
            )
            raise HTTPException(status_code=404, detail="File content not found.")
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                f"Failed to delete file due to a database error: ", exc_info=True
            )
            raise HTTPException(status_code=400, detail="Failed to delete file.")

    async def retrieve_file_content_as_response(self, file_id: str) -> Response:
        """Retrieves the file content as a downloadable response."""
        file = await self.retrieve_file(file_id)
        file_content = await self.retrieve_file_content(file_id)
        file_extension = guess_file_extension(file.mime_type)
        headers = {
            "Content-Disposition": f'attachment; filename="{file.filename}.{file_extension}"'
        }

        return Response(
            content=file_content, media_type=file.mime_type, headers=headers
        )

    async def retrieve_files_by_ids(
        self,
        file_ids: list[uuid.UUID],
        limit: int = 100,
        order: str = "desc",
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
    ) -> list[File]:
        try:
            query = select(File).where(File.id.in_(file_ids))

            if before:
                query = query.filter(File.created_at < before)
            if after:
                query = query.filter(File.created_at > after)

            if order == "asc":
                query = query.order_by(File.created_at.asc())
            else:
                query = query.order_by(File.created_at.desc())

            query = query.limit(limit)

            result = await self.postgresql_session.execute(query)
            records = result.scalars().all()
            return records
        except SQLAlchemyError as e:
            logger.exception(
                f"Failed to retrieve files due to a database error.", exc_info=True
            )
            raise HTTPException(status_code=500, detail="Failed to retrieve files.")

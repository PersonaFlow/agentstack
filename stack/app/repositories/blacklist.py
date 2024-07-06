from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from stack.app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from stack.app.core.datastore import get_postgresql_session_provider
from stack.app.model.blacklist import Blacklist
import structlog

logger = structlog.get_logger()


async def get_blacklist_repository(
    session: AsyncSession = Depends(get_postgresql_session_provider),
):
    return BlacklistRepository(postgresql_session=session)


class BlacklistRepository(BaseRepository):
    def __init__(self, postgresql_session):
        self.postgresql_session = postgresql_session

    @staticmethod
    def _get_retrieve_query() -> select:
        """A private method to construct the default query for retrieval."""
        return select(
            Blacklist.id,
            Blacklist.token_id,
            Blacklist.created_at,
            Blacklist.updated_at,
        )

    async def create_blacklist(self, data: Blacklist) -> Blacklist:
        """Creates a new blacklist in the database."""
        try:
            blacklist = await self.create(model=Blacklist, values=data)
            await self.postgresql_session.commit()
            return blacklist
        except SQLAlchemyError as e:
            await self.postgresql_session.rollback()
            logger.exception(
                f"Failed to create blacklist due to a database error.", exc_info=True
            )
            raise HTTPException(
                status_code=400, detail=f"Failed to create blacklist."
            ) from e

    async def retrieve_blacklist(self, token_id: str) -> Blacklist:
        """Retrieves a blacklist from the database by token_id."""
        try:
            query = self._get_retrieve_query()
            blacklist = await self.retrieve_one(query=query, object_id=token_id)
            # return db.query(Blacklist).filter(Blacklist.token_id == token_id).first()
            return blacklist
        except SQLAlchemyError as e:
            logger.exception(
                f"Failed to retrieve blacklist due to a database error.", exc_info=True
            )
            raise HTTPException(
                status_code=400, detail=f"Failed to retrieve blacklist."
            ) from e

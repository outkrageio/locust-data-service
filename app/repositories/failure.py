from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.failure import Failure
from app.repositories.base import BaseRepository


class FailureRepository(BaseRepository[Failure]):
    """Repository for Failure model with specialized queries."""

    def __init__(self, session: AsyncSession):
        super().__init__(Failure, session)

    async def get_by_test_run(self, test_run_id: UUID, skip: int = 0, limit: int = 100) -> list[Failure]:
        result = await self.session.execute(
            select(Failure)
            .where(Failure.test_run_id == test_run_id)
            .order_by(Failure.occurrences.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

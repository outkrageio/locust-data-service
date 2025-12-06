from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stats_snapshot import StatsSnapshot
from app.repositories.base import BaseRepository


class StatsSnapshotRepository(BaseRepository[StatsSnapshot]):
    """Repository for StatsSnapshot model with specialized queries."""

    def __init__(self, session: AsyncSession):
        super().__init__(StatsSnapshot, session)

    async def get_by_test_run(
        self,
        test_run_id: UUID,
        skip: int = 0,
        limit: int = 1000
    ) -> List[StatsSnapshot]:
        result = await self.session.execute(
            select(StatsSnapshot)
            .where(StatsSnapshot.test_run_id == test_run_id)
            .order_by(StatsSnapshot.timestamp)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

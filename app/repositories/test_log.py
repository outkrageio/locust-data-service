from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_log import TestLog
from app.repositories.base import BaseRepository


class TestLogRepository(BaseRepository[TestLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(TestLog, session)

    async def get_by_test_run(
        self, test_run_id: UUID, level: str | None = None, skip: int = 0, limit: int = 1000
    ) -> list[TestLog]:
        query = select(TestLog).where(TestLog.test_run_id == test_run_id)

        if level:
            query = query.where(TestLog.level == level)

        query = query.order_by(TestLog.timestamp).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def bulk_create(self, logs: list[dict[str, Any]]) -> None:
        instances = [TestLog(**log) for log in logs]
        self.session.add_all(instances)
        await self.session.commit()

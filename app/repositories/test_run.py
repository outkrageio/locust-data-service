from datetime import datetime
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_run import TestRun
from app.repositories.base import BaseRepository


class TestRunRepository(BaseRepository[TestRun]):
    """Repository for TestRun model with specialized queries."""

    def __init__(self, session: AsyncSession):
        super().__init__(TestRun, session)

    async def get_by_project(
        self,
        project: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestRun]:
        result = await self.session.execute(
            select(TestRun)
            .where(TestRun.project == project)
            .order_by(TestRun.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_project_and_test_name(
        self,
        project: str,
        test_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestRun]:
        result = await self.session.execute(
            select(TestRun)
            .where(and_(
                TestRun.project == project,
                TestRun.test_name == test_name
            ))
            .order_by(TestRun.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestRun]:
        result = await self.session.execute(
            select(TestRun)
            .where(TestRun.status == status)
            .order_by(TestRun.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestRun]:
        result = await self.session.execute(
            select(TestRun)
            .where(and_(
                TestRun.start_time >= start_date,
                TestRun.start_time <= end_date
            ))
            .order_by(TestRun.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request_log import RequestLog
from app.repositories.base import BaseRepository


class RequestLogRepository(BaseRepository[RequestLog]):
    """Repository for RequestLog model with specialized queries."""

    def __init__(self, session: AsyncSession):
        super().__init__(RequestLog, session)

    async def get_by_test_run(
        self,
        test_run_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequestLog]:
        result = await self.session.execute(
            select(RequestLog)
            .where(RequestLog.test_run_id == test_run_id)
            .order_by(RequestLog.start_time)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_failed_requests(
        self,
        test_run_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequestLog]:
        result = await self.session.execute(
            select(RequestLog)
            .where(and_(
                RequestLog.test_run_id == test_run_id,
                RequestLog.success == False
            ))
            .order_by(RequestLog.start_time)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def bulk_create(self, requests: List[Dict[str, Any]]) -> None:
        instances = [RequestLog(**req) for req in requests]
        self.session.add_all(instances)
        await self.session.commit()

    async def get_stats_by_test_run(self, test_run_id: UUID) -> Dict[str, Any]:
        """Get aggregated statistics for a test run."""
        result = await self.session.execute(
            select(
                func.count(RequestLog.id).label("total_requests"),
                func.count().filter(RequestLog.success == False).label("failure_count"),
                func.avg(RequestLog.response_time).label("avg_response_time"),
                func.min(RequestLog.response_time).label("min_response_time"),
                func.max(RequestLog.response_time).label("max_response_time"),
            )
            .where(RequestLog.test_run_id == test_run_id)
        )
        row = result.one()

        return {
            "total_requests": row.total_requests or 0,
            "failure_count": row.failure_count or 0,
            "failure_rate": (row.failure_count / row.total_requests * 100) if row.total_requests else 0,
            "avg_response_time": float(row.avg_response_time) if row.avg_response_time else 0,
            "min_response_time": float(row.min_response_time) if row.min_response_time else 0,
            "max_response_time": float(row.max_response_time) if row.max_response_time else 0,
        }

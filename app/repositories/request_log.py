from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.request_log import RequestLog
from app.repositories.base import BaseRepository


class RequestLogRepository(BaseRepository[RequestLog]):
    """Repository for RequestLog model with specialized queries."""

    def __init__(self, session: AsyncSession):
        super().__init__(RequestLog, session)

    async def get_by_test_run(self, test_run_id: UUID, skip: int = 0, limit: int = 100) -> list[RequestLog]:
        result = await self.session.execute(
            select(RequestLog)
            .where(RequestLog.test_run_id == test_run_id)
            .order_by(RequestLog.start_time)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_failed_requests(self, test_run_id: UUID, skip: int = 0, limit: int = 100) -> list[RequestLog]:
        result = await self.session.execute(
            select(RequestLog)
            .where(and_(RequestLog.test_run_id == test_run_id, ~RequestLog.success))
            .order_by(RequestLog.start_time)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def bulk_create(self, requests: list[dict[str, Any]]) -> None:
        instances = [RequestLog(**req) for req in requests]
        self.session.add_all(instances)
        await self.session.commit()

    async def get_stats_by_test_run(self, test_run_id: UUID) -> dict[str, Any]:
        """Get aggregated statistics for a test run."""
        result = await self.session.execute(
            select(
                func.count(RequestLog.id).label("total_requests"),
                func.count().filter(~RequestLog.success).label("failure_count"),
                func.avg(RequestLog.response_time).label("avg_response_time"),
                func.min(RequestLog.response_time).label("min_response_time"),
                func.max(RequestLog.response_time).label("max_response_time"),
            ).where(RequestLog.test_run_id == test_run_id)
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

    async def get_stats_by_endpoint(self, test_run_id: UUID) -> list[dict[str, Any]]:
        """Get aggregated statistics grouped by endpoint."""
        result = await self.session.execute(
            select(
                RequestLog.name.label("endpoint"),
                RequestLog.request_type.label("method"),
                func.count(RequestLog.id).label("total_requests"),
                func.count().filter(~RequestLog.success).label("failure_count"),
                func.avg(RequestLog.response_time).label("avg_response_time"),
                func.min(RequestLog.response_time).label("min_response_time"),
                func.max(RequestLog.response_time).label("max_response_time"),
                func.stddev_pop(RequestLog.response_time).label("std_dev_response_time"),
            )
            .where(RequestLog.test_run_id == test_run_id)
            .group_by(RequestLog.name, RequestLog.request_type)
            .order_by(RequestLog.name)
        )

        stats = []
        for row in result:
            total = row.total_requests or 0
            failures = row.failure_count or 0
            stats.append(
                {
                    "endpoint": row.endpoint,
                    "method": row.method,
                    "total_requests": total,
                    "failure_count": failures,
                    "failure_rate": (failures / total * 100) if total else 0,
                    "avg_response_time": float(row.avg_response_time) if row.avg_response_time else 0,
                    "min_response_time": float(row.min_response_time) if row.min_response_time else 0,
                    "max_response_time": float(row.max_response_time) if row.max_response_time else 0,
                    "std_dev_response_time": float(row.std_dev_response_time) if row.std_dev_response_time else 0,
                }
            )

        return stats

    async def get_bandwidth_stats(self, test_run_id: UUID) -> dict[str, Any]:
        """Get bandwidth and data transfer statistics for a test run."""
        result = await self.session.execute(
            select(
                func.sum(RequestLog.response_length).label("total_bytes"),
                func.avg(RequestLog.response_length).label("avg_bytes_per_request"),
                func.count(RequestLog.id).label("total_requests"),
            ).where(RequestLog.test_run_id == test_run_id)
        )
        row = result.one()

        total_bytes = row.total_bytes or 0
        total_requests = row.total_requests or 0

        return {
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 * 1024), 2) if total_bytes else 0,
            "total_gb": round(total_bytes / (1024 * 1024 * 1024), 4) if total_bytes else 0,
            "avg_bytes_per_request": float(row.avg_bytes_per_request) if row.avg_bytes_per_request else 0,
            "total_requests": total_requests,
        }

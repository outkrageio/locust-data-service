"""Pydantic schemas for API contracts."""

from app.schemas.failure import (
    FailureBase,
    FailureCreate,
    FailureResponse,
)
from app.schemas.request_log import (
    RequestLogBase,
    RequestLogBatchCreate,
    RequestLogCreate,
    RequestLogResponse,
    RequestStatsResponse,
)
from app.schemas.stats_snapshot import (
    StatsSnapshotBase,
    StatsSnapshotCreate,
    StatsSnapshotResponse,
)
from app.schemas.test_run import (
    TestRunBase,
    TestRunCreate,
    TestRunResponse,
    TestRunUpdate,
)

__all__ = [
    # Test Run schemas
    "TestRunBase",
    "TestRunCreate",
    "TestRunUpdate",
    "TestRunResponse",
    # Request Log schemas
    "RequestLogBase",
    "RequestLogCreate",
    "RequestLogBatchCreate",
    "RequestLogResponse",
    "RequestStatsResponse",
    # Failure schemas
    "FailureBase",
    "FailureCreate",
    "FailureResponse",
    # Stats Snapshot schemas
    "StatsSnapshotBase",
    "StatsSnapshotCreate",
    "StatsSnapshotResponse",
]

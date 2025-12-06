"""Pydantic schemas for API contracts."""
from app.schemas.test_run import (
    TestRunBase,
    TestRunCreate,
    TestRunUpdate,
    TestRunResponse,
    TestRunListResponse,
)
from app.schemas.request_log import (
    RequestLogBase,
    RequestLogCreate,
    RequestLogBatchCreate,
    RequestLogResponse,
    RequestLogListResponse,
    RequestStatsResponse,
)
from app.schemas.failure import (
    FailureBase,
    FailureCreate,
    FailureResponse,
    FailureListResponse,
)
from app.schemas.stats_snapshot import (
    StatsSnapshotBase,
    StatsSnapshotCreate,
    StatsSnapshotResponse,
    StatsSnapshotListResponse,
)

__all__ = [
    # Test Run schemas
    "TestRunBase",
    "TestRunCreate",
    "TestRunUpdate",
    "TestRunResponse",
    "TestRunListResponse",
    # Request Log schemas
    "RequestLogBase",
    "RequestLogCreate",
    "RequestLogBatchCreate",
    "RequestLogResponse",
    "RequestLogListResponse",
    "RequestStatsResponse",
    # Failure schemas
    "FailureBase",
    "FailureCreate",
    "FailureResponse",
    "FailureListResponse",
    # Stats Snapshot schemas
    "StatsSnapshotBase",
    "StatsSnapshotCreate",
    "StatsSnapshotResponse",
    "StatsSnapshotListResponse",
]

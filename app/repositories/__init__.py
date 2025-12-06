"""Repositories for data access."""
from app.repositories.base import BaseRepository
from app.repositories.test_run import TestRunRepository
from app.repositories.request_log import RequestLogRepository
from app.repositories.failure import FailureRepository
from app.repositories.stats_snapshot import StatsSnapshotRepository

__all__ = [
    "BaseRepository",
    "TestRunRepository",
    "RequestLogRepository",
    "FailureRepository",
    "StatsSnapshotRepository",
]

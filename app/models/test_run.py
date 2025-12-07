from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.failure import Failure
    from app.models.request_log import RequestLog
    from app.models.stats_snapshot import StatsSnapshot
    from app.models.test_log import TestLog


class TestRun(Base, UUIDMixin, TimestampMixin):
    """Model for storing Locust test run information."""

    __tablename__ = "test_runs"

    project: Mapped[str] = mapped_column(String(255), nullable=False)
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    user_count: Mapped[int] = mapped_column(Integer, nullable=False)
    spawn_rate: Mapped[float] = mapped_column(Float, nullable=False)
    host: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="running")
    test_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    request_logs: Mapped[list[RequestLog]] = relationship(
        "RequestLog", back_populates="test_run", cascade="all, delete-orphan"
    )
    failures: Mapped[list[Failure]] = relationship("Failure", back_populates="test_run", cascade="all, delete-orphan")
    stats_snapshots: Mapped[list[StatsSnapshot]] = relationship(
        "StatsSnapshot", back_populates="test_run", cascade="all, delete-orphan"
    )
    logs: Mapped[list[TestLog]] = relationship("TestLog", back_populates="test_run", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_test_runs_project_name", "project", "test_name"),
        Index("idx_test_runs_start_time", "start_time"),
        Index("idx_test_runs_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<TestRun(id={self.id}, project={self.project}, test_name={self.test_name}, status={self.status})>"

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.test_run import TestRun


class StatsSnapshot(Base, UUIDMixin, TimestampMixin):
    """Model for storing periodic aggregated statistics during Locust tests."""

    __tablename__ = "stats_snapshots"

    test_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_response_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    median_response_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    min_response_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_response_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    percentile_95: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    percentile_99: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    requests_per_second: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_user_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    test_run: Mapped[TestRun] = relationship("TestRun", back_populates="stats_snapshots")

    __table_args__ = (Index("idx_stats_snapshots_test_run_timestamp", "test_run_id", "timestamp"),)

    def __repr__(self) -> str:
        return f"<StatsSnapshot(id={self.id}, timestamp={self.timestamp}, total_requests={self.total_requests})>"

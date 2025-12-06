from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.test_run import TestRun


class Failure(Base, UUIDMixin, TimestampMixin):
    """Model for tracking aggregated failures during Locust tests."""

    __tablename__ = "failures"

    test_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False
    )
    request_type: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    error_message: Mapped[str] = mapped_column(String(2048), nullable=False)
    occurrences: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    first_occurrence: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_occurrence: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    test_run: Mapped[TestRun] = relationship("TestRun", back_populates="failures")

    __table_args__ = (Index("idx_failures_test_run", "test_run_id"),)

    def __repr__(self) -> str:
        return f"<Failure(id={self.id}, request_type={self.request_type}, name={self.name}, occurrences={self.occurrences})>"

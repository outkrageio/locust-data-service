from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.test_run import TestRun


class RequestLog(Base, UUIDMixin, TimestampMixin):
    """Model for storing individual request logs from Locust tests."""

    __tablename__ = "request_logs"

    test_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("test_runs.id", ondelete="CASCADE"), nullable=False
    )
    request_type: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    response_time: Mapped[float] = mapped_column(Float, nullable=False)
    response_length: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    exception: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    context: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    test_run: Mapped[TestRun] = relationship("TestRun", back_populates="request_logs")

    __table_args__ = (
        Index("idx_request_logs_test_run_time", "test_run_id", "start_time"),
        Index("idx_request_logs_success", "success"),
    )

    def __repr__(self) -> str:
        return f"<RequestLog(id={self.id}, request_type={self.request_type}, name={self.name}, success={self.success})>"

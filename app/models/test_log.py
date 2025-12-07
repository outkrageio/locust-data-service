from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.test_run import TestRun


class TestLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "test_logs"

    test_run_id: Mapped[UUID] = mapped_column(ForeignKey("test_runs.id", ondelete="CASCADE"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    level: Mapped[str] = mapped_column(String(10), index=True)
    logger: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    exception: Mapped[str | None] = mapped_column(Text, nullable=True)

    test_run: Mapped["TestRun"] = relationship(back_populates="logs")

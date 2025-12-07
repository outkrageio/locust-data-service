from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TestLogBase(BaseModel):
    timestamp: datetime
    level: str = Field(..., max_length=10)
    logger: str = Field(..., max_length=255)
    message: str
    exception: str | None = None


class TestLogCreate(TestLogBase):
    test_run_id: UUID


class TestLogBatchCreate(BaseModel):
    logs: list[TestLogCreate]


class TestLogResponse(TestLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    test_run_id: UUID
    created_at: datetime
    updated_at: datetime

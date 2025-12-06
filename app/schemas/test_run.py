from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TestRunBase(BaseModel):
    project: str = Field(..., max_length=255)
    test_name: str = Field(..., max_length=255)
    user_count: int = Field(..., ge=0)
    spawn_rate: float = Field(..., ge=0)
    host: str = Field(..., max_length=512)
    test_metadata: dict | None = None


class TestRunCreate(TestRunBase):
    start_time: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="running", max_length=50)


class TestRunUpdate(BaseModel):
    status: str | None = Field(None, max_length=50)
    end_time: datetime | None = None
    test_metadata: dict | None = None


class TestRunResponse(TestRunBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    start_time: datetime
    end_time: datetime | None
    status: str
    created_at: datetime
    updated_at: datetime

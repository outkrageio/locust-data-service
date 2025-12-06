from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class TestRunBase(BaseModel):
    project: str = Field(..., max_length=255)
    test_name: str = Field(..., max_length=255)
    user_count: int = Field(..., ge=0)
    spawn_rate: float = Field(..., ge=0)
    host: str = Field(..., max_length=512)
    test_metadata: Optional[dict] = None


class TestRunCreate(TestRunBase):
    start_time: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="running", max_length=50)


class TestRunUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)
    end_time: Optional[datetime] = None
    test_metadata: Optional[dict] = None


class TestRunResponse(TestRunBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: datetime

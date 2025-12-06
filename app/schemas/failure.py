from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FailureBase(BaseModel):
    request_type: str = Field(..., max_length=10)
    name: str = Field(..., max_length=512)
    error_message: str = Field(..., max_length=2048)


class FailureCreate(FailureBase):
    test_run_id: UUID
    occurrences: int = Field(default=1, ge=1)
    first_occurrence: datetime = Field(default_factory=datetime.utcnow)
    last_occurrence: datetime = Field(default_factory=datetime.utcnow)


class FailureResponse(FailureBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    test_run_id: UUID
    occurrences: int
    first_occurrence: datetime
    last_occurrence: datetime
    created_at: datetime
    updated_at: datetime

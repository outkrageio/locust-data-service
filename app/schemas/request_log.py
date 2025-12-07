from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RequestLogBase(BaseModel):
    request_type: str = Field(..., max_length=10)
    name: str = Field(..., max_length=512)
    url: str = Field(..., max_length=2048)
    response_time: float = Field(..., ge=0)
    response_length: int = Field(..., ge=0)
    success: bool
    exception: str | None = Field(None, max_length=2048)
    user_id: str | None = Field(None, max_length=255)
    context: dict | None = None


class RequestLogCreate(RequestLogBase):
    test_run_id: UUID
    start_time: datetime = Field(default_factory=datetime.utcnow)


class RequestLogBatchCreate(BaseModel):
    requests: list[RequestLogCreate]


class RequestLogResponse(RequestLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    test_run_id: UUID
    start_time: datetime
    created_at: datetime
    updated_at: datetime


class RequestStatsResponse(BaseModel):
    total_requests: int
    failure_count: int
    failure_rate: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float


class EndpointStatsResponse(BaseModel):
    endpoint: str
    method: str
    total_requests: int
    failure_count: int
    failure_rate: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    std_dev_response_time: float

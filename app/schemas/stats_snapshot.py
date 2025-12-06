from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class StatsSnapshotBase(BaseModel):
    total_requests: int = Field(default=0, ge=0)
    failure_count: int = Field(default=0, ge=0)
    failure_rate: float = Field(default=0.0, ge=0, le=100)
    avg_response_time: float = Field(default=0.0, ge=0)
    median_response_time: float = Field(default=0.0, ge=0)
    min_response_time: float = Field(default=0.0, ge=0)
    max_response_time: float = Field(default=0.0, ge=0)
    percentile_95: float = Field(default=0.0, ge=0)
    percentile_99: float = Field(default=0.0, ge=0)
    requests_per_second: float = Field(default=0.0, ge=0)
    current_user_count: int = Field(default=0, ge=0)


class StatsSnapshotCreate(StatsSnapshotBase):
    test_run_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatsSnapshotResponse(StatsSnapshotBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    test_run_id: UUID
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

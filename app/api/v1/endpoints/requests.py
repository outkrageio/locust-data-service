from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.repositories.request_log import RequestLogRepository
from app.schemas.request_log import (
    RequestLogBatchCreate,
    RequestLogCreate,
    RequestLogResponse,
    RequestStatsResponse,
)

router = APIRouter()


@router.post("", response_model=RequestLogResponse, status_code=201)
async def create_request_log(request_log: RequestLogCreate, db: AsyncSession = Depends(get_db)):
    repo = RequestLogRepository(db)
    created = await repo.create(**request_log.model_dump())
    return created


@router.post("/batch", status_code=201)
async def create_request_logs_batch(batch: RequestLogBatchCreate, db: AsyncSession = Depends(get_db)):
    """Create multiple request logs in a single batch."""
    repo = RequestLogRepository(db)
    requests_data = [req.model_dump() for req in batch.requests]
    await repo.bulk_create(requests_data)

    return {"message": f"Successfully created {len(batch.requests)} request logs", "count": len(batch.requests)}


@router.get("", response_model=list[RequestLogResponse])
async def list_request_logs(
    test_run_id: UUID = Query(...),
    failed_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    """List request logs for a specific test run."""
    repo = RequestLogRepository(db)

    if failed_only:
        items = await repo.get_failed_requests(test_run_id, skip, limit)
    else:
        items = await repo.get_by_test_run(test_run_id, skip, limit)

    return items


@router.get("/{request_log_id}", response_model=RequestLogResponse)
async def get_request_log(request_log_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = RequestLogRepository(db)
    request_log = await repo.get_by_id(request_log_id)
    if not request_log:
        raise HTTPException(status_code=404, detail="Request log not found")
    return request_log


@router.get("/stats/{test_run_id}", response_model=RequestStatsResponse)
async def get_request_stats(test_run_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get aggregated statistics for a test run's requests."""
    repo = RequestLogRepository(db)
    stats = await repo.get_stats_by_test_run(test_run_id)
    return stats

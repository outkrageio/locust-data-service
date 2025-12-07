from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.repositories.test_log import TestLogRepository
from app.schemas.test_log import TestLogBatchCreate, TestLogCreate, TestLogResponse

router = APIRouter()


@router.post("/batch", status_code=201)
async def create_logs_batch(batch: TestLogBatchCreate, db: AsyncSession = Depends(get_db)):
    """Bulk create test logs."""
    repo = TestLogRepository(db)
    logs_data = [log.model_dump() for log in batch.logs]
    await repo.bulk_create(logs_data)
    return {"created": len(batch.logs)}


@router.post("", response_model=TestLogResponse, status_code=201)
async def create_log(log: TestLogCreate, db: AsyncSession = Depends(get_db)):
    """Create a single test log."""
    repo = TestLogRepository(db)
    created = await repo.create(**log.model_dump())
    return created


@router.get("", response_model=list[TestLogResponse])
async def list_logs(
    test_run_id: UUID = Query(...),
    level: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db),
):
    """List logs for a test run with optional level filtering."""
    repo = TestLogRepository(db)
    logs = await repo.get_by_test_run(test_run_id, level=level, skip=skip, limit=limit)
    return logs

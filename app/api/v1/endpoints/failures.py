from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.repositories.failure import FailureRepository
from app.schemas.failure import (
    FailureCreate,
    FailureResponse,
)

router = APIRouter()


@router.post("", response_model=FailureResponse, status_code=201)
async def create_failure(
    failure: FailureCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = FailureRepository(db)
    created = await repo.create(**failure.model_dump())
    return created


@router.get("", response_model=list[FailureResponse])
async def list_failures(
    test_run_id: UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List failures for a specific test run, ordered by occurrence count."""
    repo = FailureRepository(db)
    items = await repo.get_by_test_run(test_run_id, skip, limit)
    return items


@router.get("/{failure_id}", response_model=FailureResponse)
async def get_failure(
    failure_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = FailureRepository(db)
    failure = await repo.get_by_id(failure_id)
    if not failure:
        raise HTTPException(status_code=404, detail="Failure not found")
    return failure

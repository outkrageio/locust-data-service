from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.repositories.test_run import TestRunRepository
from app.schemas.test_run import (
    TestRunCreate,
    TestRunUpdate,
    TestRunResponse,
)

router = APIRouter()


@router.post("", response_model=TestRunResponse, status_code=201)
async def create_test_run(
    test_run: TestRunCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = TestRunRepository(db)
    created = await repo.create(**test_run.model_dump())
    return created


@router.get("/{test_run_id}", response_model=TestRunResponse)
async def get_test_run(
    test_run_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = TestRunRepository(db)
    test_run = await repo.get_by_id(test_run_id)
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    return test_run


@router.get("", response_model=list[TestRunResponse])
async def list_test_runs(
    project: Optional[str] = Query(None),
    test_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List test runs with optional filters."""
    repo = TestRunRepository(db)

    if project and test_name:
        items = await repo.get_by_project_and_test_name(project, test_name, skip, limit)
    elif project:
        items = await repo.get_by_project(project, skip, limit)
    elif status:
        items = await repo.get_by_status(status, skip, limit)
    elif start_date and end_date:
        items = await repo.get_by_date_range(start_date, end_date, skip, limit)
    else:
        items = await repo.get_all(skip, limit)

    return items


@router.patch("/{test_run_id}", response_model=TestRunResponse)
async def update_test_run(
    test_run_id: UUID,
    test_run_update: TestRunUpdate,
    db: AsyncSession = Depends(get_db)
):
    repo = TestRunRepository(db)
    update_data = test_run_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = await repo.update(test_run_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Test run not found")

    return updated


@router.delete("/{test_run_id}", status_code=204)
async def delete_test_run(
    test_run_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = TestRunRepository(db)
    deleted = await repo.delete(test_run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Test run not found")

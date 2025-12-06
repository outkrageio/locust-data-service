from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.repositories.stats_snapshot import StatsSnapshotRepository
from app.schemas.stats_snapshot import (
    StatsSnapshotCreate,
    StatsSnapshotResponse,
)

router = APIRouter()


@router.post("", response_model=StatsSnapshotResponse, status_code=201)
async def create_stats_snapshot(
    stats: StatsSnapshotCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = StatsSnapshotRepository(db)
    created = await repo.create(**stats.model_dump())
    return created


@router.get("", response_model=list[StatsSnapshotResponse])
async def list_stats_snapshots(
    test_run_id: UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """List stats snapshots for a specific test run, ordered by timestamp."""
    repo = StatsSnapshotRepository(db)
    items = await repo.get_by_test_run(test_run_id, skip, limit)
    return items


@router.get("/{stats_id}", response_model=StatsSnapshotResponse)
async def get_stats_snapshot(
    stats_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    repo = StatsSnapshotRepository(db)
    stats = await repo.get_by_id(stats_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Stats snapshot not found")
    return stats

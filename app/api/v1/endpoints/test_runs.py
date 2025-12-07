import csv
import io
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.repositories.failure import FailureRepository
from app.repositories.request_log import RequestLogRepository
from app.repositories.stats_snapshot import StatsSnapshotRepository
from app.repositories.test_run import TestRunRepository
from app.schemas.test_run import (
    TestRunCreate,
    TestRunResponse,
    TestRunUpdate,
)

router = APIRouter()


@router.post("", response_model=TestRunResponse, status_code=201)
async def create_test_run(test_run: TestRunCreate, db: AsyncSession = Depends(get_db)):
    repo = TestRunRepository(db)
    created = await repo.create(**test_run.model_dump())
    return created


@router.get("/{test_run_id}", response_model=TestRunResponse)
async def get_test_run(test_run_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = TestRunRepository(db)
    test_run = await repo.get_by_id(test_run_id)
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    return test_run


@router.get("", response_model=list[TestRunResponse])
async def list_test_runs(
    project: str | None = Query(None),
    test_name: str | None = Query(None),
    status: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
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
async def update_test_run(test_run_id: UUID, test_run_update: TestRunUpdate, db: AsyncSession = Depends(get_db)):
    repo = TestRunRepository(db)
    update_data = test_run_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    updated = await repo.update(test_run_id, **update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Test run not found")

    return updated


@router.delete("/{test_run_id}", status_code=204)
async def delete_test_run(test_run_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = TestRunRepository(db)
    deleted = await repo.delete(test_run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Test run not found")


@router.get("/{test_run_id}/report")
async def download_report(
    test_run_id: UUID,
    format: str = Query("json", regex="^(json|csv)$"),
    db: AsyncSession = Depends(get_db),
):
    """Generate and download a comprehensive report for a test run."""
    test_run_repo = TestRunRepository(db)
    stats_repo = StatsSnapshotRepository(db)
    request_repo = RequestLogRepository(db)
    failure_repo = FailureRepository(db)

    test_run = await test_run_repo.get_by_id(test_run_id)
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")

    stats = await stats_repo.get_by_test_run(test_run_id, skip=0, limit=10000)
    request_stats = await request_repo.get_stats_by_test_run(test_run_id)
    endpoint_stats = await request_repo.get_stats_by_endpoint(test_run_id)
    failures = await failure_repo.get_by_test_run(test_run_id, skip=0, limit=10000)

    report_data = {
        "test_run": {
            "id": str(test_run.id),
            "project": test_run.project,
            "test_name": test_run.test_name,
            "start_time": test_run.start_time.isoformat(),
            "end_time": test_run.end_time.isoformat() if test_run.end_time else None,
            "user_count": test_run.user_count,
            "spawn_rate": test_run.spawn_rate,
            "host": test_run.host,
            "status": test_run.status,
            "test_metadata": test_run.test_metadata,
        },
        "aggregate_stats": request_stats,
        "endpoint_stats": endpoint_stats,
        "failures": [
            {
                "request_type": f.request_type,
                "name": f.name,
                "error_message": f.error_message,
                "occurrences": f.occurrences,
                "first_occurrence": f.first_occurrence.isoformat(),
                "last_occurrence": f.last_occurrence.isoformat(),
            }
            for f in failures
        ],
        "stats_timeline": [
            {
                "timestamp": s.timestamp.isoformat(),
                "total_requests": s.total_requests,
                "failure_count": s.failure_count,
                "failure_rate": s.failure_rate,
                "avg_response_time": s.avg_response_time,
                "median_response_time": s.median_response_time,
                "percentile_95": s.percentile_95,
                "percentile_99": s.percentile_99,
                "requests_per_second": s.requests_per_second,
                "current_user_count": s.current_user_count,
            }
            for s in stats
        ],
    }

    if format == "json":
        import json

        filename = (
            f"test_run_{test_run.project}_{test_run.test_name}_{test_run.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        )
        json_str = json.dumps(report_data, indent=2)
        return StreamingResponse(
            io.BytesIO(json_str.encode()),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    else:
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["Test Run Report"])
        writer.writerow([])
        writer.writerow(["Test Run Information"])
        writer.writerow(["Field", "Value"])
        test_run_data = cast(dict[str, Any], report_data["test_run"])
        for key, value in test_run_data.items():
            writer.writerow([key, value])

        writer.writerow([])
        writer.writerow(["Aggregate Statistics"])
        writer.writerow(["Metric", "Value"])
        aggregate_stats = cast(dict[str, Any], report_data["aggregate_stats"])
        for key, value in aggregate_stats.items():
            writer.writerow([key, value])

        writer.writerow([])
        writer.writerow(["Per-Endpoint Statistics"])
        if endpoint_stats:
            headers = list(endpoint_stats[0].keys())
            writer.writerow(headers)
            for stat in endpoint_stats:
                writer.writerow([stat[h] for h in headers])

        writer.writerow([])
        writer.writerow(["Failures"])
        failures_data = cast(list[dict[str, Any]], report_data["failures"])
        if failures_data:
            writer.writerow(
                ["Request Type", "Name", "Error Message", "Occurrences", "First Occurrence", "Last Occurrence"]
            )
            for failure in failures_data:
                writer.writerow(
                    [
                        failure["request_type"],
                        failure["name"],
                        failure["error_message"],
                        failure["occurrences"],
                        failure["first_occurrence"],
                        failure["last_occurrence"],
                    ]
                )

        writer.writerow([])
        writer.writerow(["Stats Timeline"])
        stats_timeline = cast(list[dict[str, Any]], report_data["stats_timeline"])
        if stats_timeline:
            headers = list(stats_timeline[0].keys())
            writer.writerow(headers)
            for stat in stats_timeline:
                writer.writerow([stat[h] for h in headers])

        filename = (
            f"test_run_{test_run.project}_{test_run.test_name}_{test_run.start_time.strftime('%Y%m%d_%H%M%S')}.csv"
        )
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

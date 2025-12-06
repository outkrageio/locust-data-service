"""API v1 router aggregator."""
from fastapi import APIRouter

from app.api.v1.endpoints import health, test_runs, requests, failures, stats

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(test_runs.router, prefix="/test-runs", tags=["test-runs"])
api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
api_router.include_router(failures.router, prefix="/failures", tags=["failures"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

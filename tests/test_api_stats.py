"""Tests for stats snapshot API endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_stats_snapshot(client: AsyncClient, test_run_data, stats_snapshot_data):
    """Test creating a stats snapshot."""
    # Create a test run first
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create a stats snapshot
    stats = {**stats_snapshot_data, "test_run_id": test_run_id}
    response = await client.post("/api/v1/stats", json=stats)
    assert response.status_code == 201
    data = response.json()
    assert data["test_run_id"] == test_run_id
    assert data["total_requests"] == stats_snapshot_data["total_requests"]
    assert data["failure_count"] == stats_snapshot_data["failure_count"]
    assert data["avg_response_time"] == stats_snapshot_data["avg_response_time"]


@pytest.mark.asyncio
async def test_list_stats_snapshots(client: AsyncClient, test_run_data, stats_snapshot_data):
    """Test listing stats snapshots for a test run."""
    # Create a test run
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create multiple stats snapshots
    for i in range(5):
        await client.post(
            "/api/v1/stats", json={**stats_snapshot_data, "test_run_id": test_run_id, "total_requests": (i + 1) * 100}
        )

    # List stats snapshots
    response = await client.get(f"/api/v1/stats?test_run_id={test_run_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    # Should be ordered by timestamp
    assert data["items"][0]["total_requests"] <= data["items"][-1]["total_requests"]


@pytest.mark.asyncio
async def test_get_stats_snapshot(client: AsyncClient, test_run_data, stats_snapshot_data):
    """Test retrieving a specific stats snapshot."""
    # Create a test run and stats snapshot
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    create_response = await client.post("/api/v1/stats", json={**stats_snapshot_data, "test_run_id": test_run_id})
    stats_id = create_response.json()["id"]

    # Get the stats snapshot
    response = await client.get(f"/api/v1/stats/{stats_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == stats_id


@pytest.mark.asyncio
async def test_get_stats_snapshot_not_found(client: AsyncClient):
    """Test retrieving a non-existent stats snapshot."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/v1/stats/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pagination_stats(client: AsyncClient, test_run_data, stats_snapshot_data):
    """Test pagination of stats snapshots."""
    # Create a test run
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create 10 stats snapshots
    for _ in range(10):
        await client.post("/api/v1/stats", json={**stats_snapshot_data, "test_run_id": test_run_id})

    # Get first 5
    response = await client.get(f"/api/v1/stats?test_run_id={test_run_id}&skip=0&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["skip"] == 0
    assert data["limit"] == 5

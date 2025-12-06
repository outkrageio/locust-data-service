"""Tests for test run API endpoints."""
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_test_run(client: AsyncClient, test_run_data):
    """Test creating a new test run."""
    response = await client.post("/api/v1/test-runs", json=test_run_data)
    assert response.status_code == 201
    data = response.json()
    assert data["project"] == test_run_data["project"]
    assert data["test_name"] == test_run_data["test_name"]
    assert data["user_count"] == test_run_data["user_count"]
    assert data["status"] == "running"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_test_run(client: AsyncClient, test_run_data):
    """Test retrieving a test run by ID."""
    # Create a test run first
    create_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = create_response.json()["id"]

    # Get the test run
    response = await client.get(f"/api/v1/test-runs/{test_run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_run_id
    assert data["project"] == test_run_data["project"]


@pytest.mark.asyncio
async def test_get_test_run_not_found(client: AsyncClient):
    """Test retrieving a non-existent test run."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/v1/test-runs/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_test_runs(client: AsyncClient, test_run_data):
    """Test listing test runs."""
    # Create multiple test runs
    await client.post("/api/v1/test-runs", json=test_run_data)
    await client.post("/api/v1/test-runs", json={**test_run_data, "test_name": "load-test-2"})

    # List all test runs
    response = await client.get("/api/v1/test-runs")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["skip"] == 0
    assert data["limit"] == 100


@pytest.mark.asyncio
async def test_list_test_runs_filter_by_project(client: AsyncClient, test_run_data):
    """Test filtering test runs by project."""
    # Create test runs for different projects
    await client.post("/api/v1/test-runs", json=test_run_data)
    await client.post("/api/v1/test-runs", json={**test_run_data, "project": "other-project"})

    # Filter by project
    response = await client.get(f"/api/v1/test-runs?project={test_run_data['project']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["project"] == test_run_data["project"]


@pytest.mark.asyncio
async def test_list_test_runs_filter_by_status(client: AsyncClient, test_run_data):
    """Test filtering test runs by status."""
    # Create a test run
    create_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = create_response.json()["id"]

    # Update status to completed
    await client.patch(f"/api/v1/test-runs/{test_run_id}", json={"status": "completed"})

    # Create another running test run
    await client.post("/api/v1/test-runs", json={**test_run_data, "test_name": "load-test-2"})

    # Filter by status
    response = await client.get("/api/v1/test-runs?status=completed")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "completed"


@pytest.mark.asyncio
async def test_update_test_run(client: AsyncClient, test_run_data):
    """Test updating a test run."""
    # Create a test run
    create_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = create_response.json()["id"]

    # Update the test run
    update_data = {
        "status": "completed",
        "end_time": datetime.utcnow().isoformat()
    }
    response = await client.patch(f"/api/v1/test-runs/{test_run_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["end_time"] is not None


@pytest.mark.asyncio
async def test_update_test_run_not_found(client: AsyncClient):
    """Test updating a non-existent test run."""
    fake_id = str(uuid4())
    response = await client.patch(f"/api/v1/test-runs/{fake_id}", json={"status": "completed"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_test_run(client: AsyncClient, test_run_data):
    """Test deleting a test run."""
    # Create a test run
    create_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = create_response.json()["id"]

    # Delete the test run
    response = await client.delete(f"/api/v1/test-runs/{test_run_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = await client.get(f"/api/v1/test-runs/{test_run_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_test_run_not_found(client: AsyncClient):
    """Test deleting a non-existent test run."""
    fake_id = str(uuid4())
    response = await client.delete(f"/api/v1/test-runs/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, test_run_data):
    """Test pagination of test runs."""
    # Create 5 test runs
    for i in range(5):
        await client.post("/api/v1/test-runs", json={**test_run_data, "test_name": f"test-{i}"})

    # Get first 2
    response = await client.get("/api/v1/test-runs?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["skip"] == 0
    assert data["limit"] == 2

    # Get next 2
    response = await client.get("/api/v1/test-runs?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2

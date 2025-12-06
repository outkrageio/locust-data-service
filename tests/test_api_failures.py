"""Tests for failure API endpoints."""
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_failure(client: AsyncClient, test_run_data, failure_data):
    """Test creating a failure record."""
    # Create a test run first
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create a failure
    failure = {**failure_data, "test_run_id": test_run_id}
    response = await client.post("/api/v1/failures", json=failure)
    assert response.status_code == 201
    data = response.json()
    assert data["test_run_id"] == test_run_id
    assert data["request_type"] == failure_data["request_type"]
    assert data["error_message"] == failure_data["error_message"]
    assert data["occurrences"] == failure_data["occurrences"]


@pytest.mark.asyncio
async def test_list_failures(client: AsyncClient, test_run_data, failure_data):
    """Test listing failures for a test run."""
    # Create a test run and failures
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create multiple failures
    for i in range(3):
        await client.post("/api/v1/failures", json={
            **failure_data,
            "test_run_id": test_run_id,
            "error_message": f"Error {i}",
            "occurrences": i + 1
        })

    # List failures
    response = await client.get(f"/api/v1/failures?test_run_id={test_run_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    # Should be ordered by occurrences descending
    assert data["items"][0]["occurrences"] >= data["items"][1]["occurrences"]


@pytest.mark.asyncio
async def test_get_failure(client: AsyncClient, test_run_data, failure_data):
    """Test retrieving a specific failure."""
    # Create a test run and failure
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    create_response = await client.post("/api/v1/failures", json={
        **failure_data,
        "test_run_id": test_run_id
    })
    failure_id = create_response.json()["id"]

    # Get the failure
    response = await client.get(f"/api/v1/failures/{failure_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == failure_id


@pytest.mark.asyncio
async def test_get_failure_not_found(client: AsyncClient):
    """Test retrieving a non-existent failure."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/v1/failures/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pagination_failures(client: AsyncClient, test_run_data, failure_data):
    """Test pagination of failures."""
    # Create a test run
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create 5 failures
    for i in range(5):
        await client.post("/api/v1/failures", json={
            **failure_data,
            "test_run_id": test_run_id,
            "error_message": f"Error {i}"
        })

    # Get first 2
    response = await client.get(f"/api/v1/failures?test_run_id={test_run_id}&skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2

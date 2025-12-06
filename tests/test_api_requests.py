"""Tests for request log API endpoints."""
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_request_log(client: AsyncClient, test_run_data, request_log_data):
    """Test creating a single request log."""
    # Create a test run first
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create a request log
    request_data = {**request_log_data, "test_run_id": test_run_id}
    response = await client.post("/api/v1/requests", json=request_data)
    assert response.status_code == 201
    data = response.json()
    assert data["test_run_id"] == test_run_id
    assert data["request_type"] == request_log_data["request_type"]
    assert data["name"] == request_log_data["name"]
    assert data["success"] == request_log_data["success"]


@pytest.mark.asyncio
async def test_create_request_logs_batch(client: AsyncClient, test_run_data, request_log_data):
    """Test batch creating request logs."""
    # Create a test run first
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create batch of request logs
    batch_data = {
        "requests": [
            {**request_log_data, "test_run_id": test_run_id, "name": f"/api/endpoint-{i}"}
            for i in range(10)
        ]
    }
    response = await client.post("/api/v1/requests/batch", json=batch_data)
    assert response.status_code == 201
    data = response.json()
    assert data["count"] == 10
    assert "Successfully created" in data["message"]


@pytest.mark.asyncio
async def test_list_request_logs(client: AsyncClient, test_run_data, request_log_data):
    """Test listing request logs for a test run."""
    # Create a test run and request logs
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create multiple request logs
    for i in range(3):
        await client.post("/api/v1/requests", json={
            **request_log_data,
            "test_run_id": test_run_id,
            "name": f"/api/endpoint-{i}"
        })

    # List request logs
    response = await client.get(f"/api/v1/requests?test_run_id={test_run_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_list_failed_requests(client: AsyncClient, test_run_data, request_log_data):
    """Test listing only failed request logs."""
    # Create a test run
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create successful and failed requests
    await client.post("/api/v1/requests", json={
        **request_log_data,
        "test_run_id": test_run_id,
        "success": True
    })
    await client.post("/api/v1/requests", json={
        **request_log_data,
        "test_run_id": test_run_id,
        "success": False,
        "exception": "Connection timeout"
    })

    # List failed requests only
    response = await client.get(f"/api/v1/requests?test_run_id={test_run_id}&failed_only=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["success"] is False


@pytest.mark.asyncio
async def test_get_request_log(client: AsyncClient, test_run_data, request_log_data):
    """Test retrieving a specific request log."""
    # Create a test run and request log
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    create_response = await client.post("/api/v1/requests", json={
        **request_log_data,
        "test_run_id": test_run_id
    })
    request_log_id = create_response.json()["id"]

    # Get the request log
    response = await client.get(f"/api/v1/requests/{request_log_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == request_log_id


@pytest.mark.asyncio
async def test_get_request_log_not_found(client: AsyncClient):
    """Test retrieving a non-existent request log."""
    fake_id = str(uuid4())
    response = await client.get(f"/api/v1/requests/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_request_stats(client: AsyncClient, test_run_data, request_log_data):
    """Test getting aggregated request statistics."""
    # Create a test run
    test_run_response = await client.post("/api/v1/test-runs", json=test_run_data)
    test_run_id = test_run_response.json()["id"]

    # Create multiple request logs with varying response times
    for i in range(10):
        await client.post("/api/v1/requests", json={
            **request_log_data,
            "test_run_id": test_run_id,
            "response_time": 100 + (i * 10),
            "success": i % 2 == 0  # Half successful, half failed
        })

    # Get statistics
    response = await client.get(f"/api/v1/requests/stats/{test_run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total_requests"] == 10
    assert data["failure_count"] == 5
    assert data["failure_rate"] == 50.0
    assert data["avg_response_time"] > 0
    assert data["min_response_time"] > 0
    assert data["max_response_time"] > 0

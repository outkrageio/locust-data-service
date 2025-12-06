"""Pytest configuration and fixtures."""
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.base import Base
from app.api.dependencies import get_db


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with dependency override."""

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def test_run_data():
    """Sample test run data."""
    return {
        "project": "test-project",
        "test_name": "load-test-1",
        "user_count": 100,
        "spawn_rate": 10.0,
        "host": "https://example.com",
        "test_metadata": {"environment": "staging", "version": "1.0.0"},
    }


@pytest.fixture
def request_log_data():
    """Sample request log data."""
    return {
        "request_type": "GET",
        "name": "/api/users",
        "url": "https://example.com/api/users",
        "response_time": 125.5,
        "response_length": 2048,
        "success": True,
        "exception": None,
        "user_id": "user-1",
        "context": {"custom_field": "value"},
    }


@pytest.fixture
def failure_data():
    """Sample failure data."""
    return {
        "request_type": "POST",
        "name": "/api/orders",
        "error_message": "ConnectionError: Connection refused",
        "occurrences": 5,
    }


@pytest.fixture
def stats_snapshot_data():
    """Sample stats snapshot data."""
    return {
        "total_requests": 1000,
        "failure_count": 50,
        "failure_rate": 5.0,
        "avg_response_time": 150.0,
        "median_response_time": 120.0,
        "min_response_time": 50.0,
        "max_response_time": 500.0,
        "percentile_95": 300.0,
        "percentile_99": 450.0,
        "requests_per_second": 50.0,
        "current_user_count": 100,
    }

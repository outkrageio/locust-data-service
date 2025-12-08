"""Seed test data for E2E testing"""

import asyncio
import os
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Failure, RequestLog, StatsSnapshot, TestLog, TestRun


async def seed_test_data():
    """Seed the database with test data for E2E tests"""
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/locust_data")

    # Convert to async URL
    async_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(async_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Create test runs
        base_time = datetime.utcnow()

        # Test Run 1: Completed
        test_run_1 = TestRun(
            id=uuid4(),
            project="E2E Test Project",
            test_name="Load Test 1",
            start_time=base_time - timedelta(hours=2),
            end_time=base_time - timedelta(hours=1),
            user_count=100,
            spawn_rate=10,
            host="https://api.example.com",
            status="completed",
            test_metadata={"environment": "staging"},
        )
        session.add(test_run_1)

        # Test Run 2: Running
        test_run_2 = TestRun(
            id=uuid4(),
            project="E2E Test Project",
            test_name="Load Test 2",
            start_time=base_time - timedelta(minutes=30),
            end_time=None,
            user_count=50,
            spawn_rate=5,
            host="https://api.example.com",
            status="running",
            test_metadata={"environment": "production"},
        )
        session.add(test_run_2)

        # Test Run 3: Failed
        test_run_3 = TestRun(
            id=uuid4(),
            project="Another Project",
            test_name="Stress Test",
            start_time=base_time - timedelta(days=1),
            end_time=base_time - timedelta(days=1) + timedelta(hours=1),
            user_count=200,
            spawn_rate=20,
            host="https://api.test.com",
            status="failed",
            test_metadata={"environment": "staging"},
        )
        session.add(test_run_3)

        await session.flush()

        # Add stats for test run 1
        for i in range(5):
            stats = StatsSnapshot(
                id=uuid4(),
                test_run_id=test_run_1.id,
                timestamp=test_run_1.start_time + timedelta(minutes=i * 10),
                total_requests=1000 * (i + 1),
                failure_count=10 * (i + 1),
                failure_rate=0.01,
                avg_response_time=150.5 + i * 10,
                median_response_time=140.0,
                min_response_time=50.0,
                max_response_time=500.0,
                percentile_95=200.0 + i * 5,
                percentile_99=300.0 + i * 10,
                requests_per_second=100.0 + i * 5,
                current_user_count=20 * (i + 1),
            )
            session.add(stats)

        # Add request logs
        for i in range(10):
            request = RequestLog(
                id=uuid4(),
                test_run_id=test_run_1.id,
                request_type="GET",
                name="/api/users",
                url="https://api.example.com/api/users",
                response_time=100.0 + i * 10,
                response_length=1024 * (i + 1),
                success=i < 8,  # 2 failures
                exception="Connection timeout" if i >= 8 else None,
                start_time=test_run_1.start_time + timedelta(seconds=i * 30),
                user_id=f"user_{i}",
                context={"endpoint": "users"},
            )
            session.add(request)

        # Add failures
        failure = Failure(
            id=uuid4(),
            test_run_id=test_run_1.id,
            request_type="GET",
            name="/api/users",
            error_message="Connection timeout after 30s",
            occurrences=2,
            first_occurrence=test_run_1.start_time + timedelta(minutes=5),
            last_occurrence=test_run_1.start_time + timedelta(minutes=15),
        )
        session.add(failure)

        # Add test logs
        log_levels = ["INFO", "WARNING", "ERROR"]
        for i, level in enumerate(log_levels):
            log = TestLog(
                id=uuid4(),
                test_run_id=test_run_1.id,
                timestamp=test_run_1.start_time + timedelta(minutes=i * 5),
                level=level,
                logger="locust.runner",
                message=f"Test {level.lower()} message {i + 1}",
                exception="Test exception details" if level == "ERROR" else None,
            )
            session.add(log)

        await session.commit()

    await engine.dispose()

    print("✅ Test data seeded successfully!")
    print("   - Created 3 test runs")
    print("   - Created 5 stats snapshots for test run 1")
    print("   - Created 10 request logs")
    print("   - Created 1 failure")
    print("   - Created 3 test logs")


if __name__ == "__main__":
    asyncio.run(seed_test_data())

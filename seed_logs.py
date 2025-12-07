"""Seed script to populate test_logs with sample data."""

import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.test_log import TestLog
from app.models.test_run import TestRun


async def seed_logs():
    """Seed the database with sample logs."""
    async with AsyncSessionLocal() as session:
        # Get all test runs
        result = await session.execute(select(TestRun))
        test_runs = result.scalars().all()

        if not test_runs:
            print("No test runs found. Please run a test or seed test runs first.")
            return

        print(f"Found {len(test_runs)} test run(s)")

        logs_to_create = []

        for test_run in test_runs:
            print(f"Creating logs for test run: {test_run.id} ({test_run.test_name})")

            # Calculate log timestamps based on test run start time
            start_time = test_run.start_time
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time.replace("Z", "+00:00"))

            # Make sure start_time is timezone-aware
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=UTC)

            # Sample logs with different levels
            sample_logs = [
                {
                    "timestamp": start_time + timedelta(seconds=1),
                    "level": "INFO",
                    "logger": "locust.main",
                    "message": f"Starting Locust test: {test_run.test_name}",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=5),
                    "level": "INFO",
                    "logger": "locust.runners",
                    "message": f"Ramping to {test_run.user_count} users at a rate of {test_run.spawn_rate} per second",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=10),
                    "level": "DEBUG",
                    "logger": "locust.stats",
                    "message": "Current RPS: 45.3, Response time (median): 234ms",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=15),
                    "level": "WARNING",
                    "logger": "locust.runners",
                    "message": "Response time exceeded threshold: 1250ms > 1000ms",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=20),
                    "level": "INFO",
                    "logger": "locust.runners",
                    "message": f"All {test_run.user_count} users spawned successfully",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=30),
                    "level": "ERROR",
                    "logger": "locust.user",
                    "message": "Request to /api/users/123 failed with status 500",
                    "exception": 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.11/site-packages/locust/user/task.py", line 368, in run\n    self.execute_task(task, *args, **kwargs)\n  File "/usr/local/lib/python3.11/site-packages/locust/user/task.py", line 341, in execute_task\n    task(self, *args, **kwargs)\n  File "./locustfile.py", line 45, in get_user\n    response.raise_for_status()\n  File "/usr/local/lib/python3.11/site-packages/requests/models.py", line 1021, in raise_for_status\n    raise HTTPError(http_error_msg, response=self)\nrequests.exceptions.HTTPError: 500 Server Error: Internal Server Error for url: http://example.com/api/users/123',
                },
                {
                    "timestamp": start_time + timedelta(seconds=45),
                    "level": "WARNING",
                    "logger": "locust.stats",
                    "message": "Failure rate increased to 2.3% (threshold: 1%)",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=60),
                    "level": "ERROR",
                    "logger": "locust.user",
                    "message": "Connection timeout while accessing /api/products",
                    "exception": 'Traceback (most recent call last):\n  File "/usr/local/lib/python3.11/site-packages/urllib3/connectionpool.py", line 467, in _make_request\n    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)\n  File "/usr/local/lib/python3.11/site-packages/urllib3/connectionpool.py", line 358, in _raise_timeout\n    raise ReadTimeoutError(\nurllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host=\'example.com\', port=80): Read timed out. (read timeout=30)',
                },
                {
                    "timestamp": start_time + timedelta(seconds=75),
                    "level": "INFO",
                    "logger": "locust.stats",
                    "message": "Test statistics - Total requests: 5234, Failures: 45, Avg response time: 342ms",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=90),
                    "level": "DEBUG",
                    "logger": "locust.runners",
                    "message": "Current user distribution: 60% browsing, 25% purchasing, 15% searching",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=100),
                    "level": "WARNING",
                    "logger": "locust.user",
                    "message": "Retry attempt 2/3 for failed request to /api/checkout",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=110),
                    "level": "ERROR",
                    "logger": "locust.user",
                    "message": "Authentication failed for user session",
                    "exception": 'Traceback (most recent call last):\n  File "./locustfile.py", line 78, in login\n    if response.status_code == 401:\n  File "/usr/local/lib/python3.11/site-packages/locust/clients.py", line 89, in __getattr__\n    raise AuthenticationError(\'Authentication required\')\nlocust.exception.AuthenticationError: Authentication required - session token expired',
                },
                {
                    "timestamp": start_time + timedelta(seconds=125),
                    "level": "INFO",
                    "logger": "locust.runners",
                    "message": "Load test reaching steady state, maintaining current user count",
                    "exception": None,
                },
                {
                    "timestamp": start_time + timedelta(seconds=140),
                    "level": "DEBUG",
                    "logger": "locust.stats",
                    "message": "Performance metrics stable: P95=450ms, P99=890ms",
                    "exception": None,
                },
            ]

            for log_data in sample_logs:
                log = TestLog(
                    id=uuid4(),
                    test_run_id=test_run.id,
                    timestamp=log_data["timestamp"],
                    level=log_data["level"],
                    logger=log_data["logger"],
                    message=log_data["message"],
                    exception=log_data["exception"],
                )
                logs_to_create.append(log)

        # Bulk insert all logs
        session.add_all(logs_to_create)
        await session.commit()

        print(f"\n✅ Successfully created {len(logs_to_create)} sample logs!")
        print(f"   - {sum(1 for log in logs_to_create if log.level == 'ERROR')} ERROR logs")
        print(f"   - {sum(1 for log in logs_to_create if log.level == 'WARNING')} WARNING logs")
        print(f"   - {sum(1 for log in logs_to_create if log.level == 'INFO')} INFO logs")
        print(f"   - {sum(1 for log in logs_to_create if log.level == 'DEBUG')} DEBUG logs")


if __name__ == "__main__":
    asyncio.run(seed_logs())

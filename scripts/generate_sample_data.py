"""
Generate comprehensive sample test data for the Locust Data Service.
This script creates diverse test runs with associated stats, requests, and failures.
"""

import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4

import httpx

API_URL = "http://localhost:8500/api/v1"

# Configuration for diverse test data
PROJECTS = [
    "E-Commerce Platform",
    "Mobile API",
    "Payment Gateway",
    "Analytics Service",
    "Content Delivery",
]

TEST_TEMPLATES = [
    {"name": "Homepage Load Test", "endpoints": ["/", "/home", "/index"], "methods": ["GET"]},
    {"name": "API Stress Test", "endpoints": ["/api/v1/data", "/api/v1/users"], "methods": ["GET", "POST"]},
    {"name": "Login Flow Test", "endpoints": ["/auth/login", "/auth/verify"], "methods": ["POST"]},
    {
        "name": "Checkout Performance",
        "endpoints": ["/cart", "/checkout", "/payment"],
        "methods": ["GET", "POST", "PUT"],
    },
    {"name": "Search Functionality", "endpoints": ["/search", "/autocomplete"], "methods": ["GET"]},
    {"name": "Product Catalog", "endpoints": ["/products", "/categories"], "methods": ["GET"]},
    {"name": "User Profile CRUD", "endpoints": ["/users", "/profile"], "methods": ["GET", "POST", "PUT", "DELETE"]},
    {"name": "File Upload Test", "endpoints": ["/upload", "/media"], "methods": ["POST", "PUT"]},
    {"name": "Notification Service", "endpoints": ["/notifications", "/webhooks"], "methods": ["POST"]},
    {"name": "Admin Dashboard", "endpoints": ["/admin", "/analytics"], "methods": ["GET"]},
]

HOSTS = [
    "https://example.com",
    "https://api.example.com",
    "https://mobile-api.example.com",
    "https://checkout.example.com",
    "https://cdn.example.com",
    "https://staging.example.com",
    "https://prod.example.com",
]

ENVIRONMENTS = ["production", "staging", "development", "qa", "performance"]
VERSIONS = ["1.0.0", "1.1.0", "1.2.3", "2.0.0-beta", "2.1.5", "3.0.0"]

ERROR_MESSAGES = [
    "Connection timeout after 30s",
    "500 Internal Server Error",
    "503 Service Unavailable",
    "404 Not Found",
    "Connection refused",
    "SSL handshake failed",
    "Database connection pool exhausted",
    "Rate limit exceeded (429)",
    "502 Bad Gateway",
    "Gateway timeout (504)",
    "Invalid JSON response",
    "Memory allocation failed",
    "Disk quota exceeded",
    "Authentication token expired",
]


async def create_test_run(
    client: httpx.AsyncClient,
    project: str,
    test_name: str,
    status: str,
    hours_ago: float,
    duration_minutes: int,
    user_count: int,
    spawn_rate: float,
    host: str,
    environment: str,
    version: str,
) -> str:
    """Create a test run and return its ID."""
    start_time = datetime.utcnow() - timedelta(hours=hours_ago)

    if status == "completed":
        end_time = start_time + timedelta(minutes=duration_minutes)
    elif status == "failed":
        # Failed tests end partway through
        end_time = start_time + timedelta(minutes=duration_minutes // 2)
    else:
        end_time = None

    data = {
        "project": project,
        "test_name": test_name,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat() if end_time else None,
        "user_count": user_count,
        "spawn_rate": spawn_rate,
        "host": host,
        "status": status,
        "test_metadata": {
            "environment": environment,
            "version": version,
            "region": random.choice(["us-east-1", "us-west-2", "eu-central-1"]),
            "test_type": random.choice(["load", "stress", "spike", "endurance"]),
            "tags": random.sample(["smoke", "regression", "performance", "critical"], k=2),
        },
    }

    response = await client.post(f"{API_URL}/test-runs", json=data)
    response.raise_for_status()
    test_run = response.json()
    print(f"✓ Created test run: {test_name} ({status}) - {user_count} users - ID: {test_run['id']}")
    return test_run["id"]


async def create_stats_snapshots(
    client: httpx.AsyncClient,
    test_run_id: str,
    num_snapshots: int,
    duration_minutes: int,
    failure_profile: str,
):
    """Create stats snapshots for a test run with different failure profiles."""
    start_time = datetime.utcnow() - timedelta(minutes=duration_minutes)

    # Define failure profiles
    if failure_profile == "low":
        base_failure_rate = 0.01
    elif failure_profile == "medium":
        base_failure_rate = 0.05
    elif failure_profile == "high":
        base_failure_rate = 0.15
    elif failure_profile == "spike":
        base_failure_rate = 0.02
    else:
        base_failure_rate = 0.03

    for i in range(num_snapshots):
        timestamp = start_time + timedelta(seconds=i * 10)
        progress = i / num_snapshots

        # Spike profile has sudden failure increase mid-test
        if failure_profile == "spike" and 0.4 < progress < 0.6:
            failure_rate_multiplier = 10
        else:
            failure_rate_multiplier = 1

        # Simulate realistic metrics that change over time
        total_requests = int(100 + (progress * random.randint(5000, 20000)))
        failure_count = int(total_requests * base_failure_rate * failure_rate_multiplier)
        failure_rate = (failure_count / total_requests * 100) if total_requests > 0 else 0

        # Response times vary by load
        load_factor = 1 + (progress * 0.5)  # Response times increase as load increases
        avg_response = random.uniform(50, 200) * load_factor

        data = {
            "test_run_id": test_run_id,
            "timestamp": timestamp.isoformat(),
            "total_requests": total_requests,
            "failure_count": failure_count,
            "failure_rate": failure_rate,
            "avg_response_time": avg_response,
            "median_response_time": avg_response * 0.8,
            "min_response_time": random.uniform(10, 50),
            "max_response_time": avg_response * random.uniform(5, 15),
            "percentile_95": avg_response * random.uniform(2, 4),
            "percentile_99": avg_response * random.uniform(4, 8),
            "requests_per_second": random.uniform(50, 1000) * (1 + progress),
            "current_user_count": int(50 + (progress * random.randint(100, 1000))),
        }

        await client.post(f"{API_URL}/stats", json=data)

    print(f"  ✓ Created {num_snapshots} stats snapshots ({failure_profile} failure profile)")


async def create_request_logs(
    client: httpx.AsyncClient,
    test_run_id: str,
    num_requests: int,
    duration_minutes: int,
    endpoints: list,
    methods: list,
    success_rate: float,
):
    """Create request logs for a test run."""
    start_time = datetime.utcnow() - timedelta(minutes=duration_minutes)
    requests_batch = []

    for i in range(num_requests):
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        success = random.random() < success_rate

        # Response times are faster for successful requests
        if success:
            response_time = random.uniform(10, 500)
        else:
            response_time = random.uniform(1000, 30000)

        request_data = {
            "test_run_id": test_run_id,
            "request_type": method,
            "name": endpoint,
            "url": f"https://example.com{endpoint}",
            "response_time": response_time,
            "response_length": random.randint(100, 50000) if success else random.randint(0, 500),
            "success": success,
            "exception": None if success else random.choice(ERROR_MESSAGES),
            "start_time": (start_time + timedelta(seconds=i * (duration_minutes * 60 / num_requests))).isoformat(),
            "user_id": f"user_{random.randint(1, 500)}",
            "context": {
                "iteration": i,
                "worker_id": f"worker_{random.randint(1, 10)}",
                "session_id": str(uuid4()),
            },
        }
        requests_batch.append(request_data)

        # Send in batches of 100
        if len(requests_batch) >= 100:
            await client.post(f"{API_URL}/requests/batch", json={"requests": requests_batch})
            requests_batch = []

    # Send remaining requests
    if requests_batch:
        await client.post(f"{API_URL}/requests/batch", json={"requests": requests_batch})

    print(f"  ✓ Created {num_requests} request logs ({success_rate*100:.0f}% success rate)")


async def create_failures(
    client: httpx.AsyncClient,
    test_run_id: str,
    num_failures: int,
    duration_minutes: int,
    endpoints: list,
    methods: list,
):
    """Create failure records for a test run."""
    start_time = datetime.utcnow() - timedelta(minutes=duration_minutes)

    for _ in range(num_failures):
        # Some failures occur many times, others are rare
        occurrences = random.choice(
            [
                random.randint(1, 5),  # Rare
                random.randint(5, 20),  # Uncommon
                random.randint(20, 100),  # Common
                random.randint(100, 500),  # Very common
            ]
        )

        data = {
            "test_run_id": test_run_id,
            "request_type": random.choice(methods),
            "name": random.choice(endpoints),
            "error_message": random.choice(ERROR_MESSAGES),
            "occurrences": occurrences,
            "first_occurrence": start_time.isoformat(),
            "last_occurrence": (start_time + timedelta(minutes=random.randint(0, duration_minutes))).isoformat(),
        }

        await client.post(f"{API_URL}/failures", json=data)

    print(f"  ✓ Created {num_failures} failure records")


async def generate_test_run(client: httpx.AsyncClient, config: dict):
    """Generate a single test run with all associated data."""
    test_template = random.choice(TEST_TEMPLATES)

    test_id = await create_test_run(
        client,
        project=config["project"],
        test_name=config.get("test_name", test_template["name"]),
        status=config["status"],
        hours_ago=config["hours_ago"],
        duration_minutes=config["duration_minutes"],
        user_count=config["user_count"],
        spawn_rate=config["spawn_rate"],
        host=config.get("host", random.choice(HOSTS)),
        environment=config.get("environment", random.choice(ENVIRONMENTS)),
        version=config.get("version", random.choice(VERSIONS)),
    )

    endpoints = config.get("endpoints", test_template["endpoints"])
    methods = config.get("methods", test_template["methods"])

    # Create stats snapshots
    await create_stats_snapshots(
        client,
        test_id,
        config["num_snapshots"],
        config["duration_minutes"],
        config.get("failure_profile", "low"),
    )

    # Create request logs
    await create_request_logs(
        client,
        test_id,
        config["num_requests"],
        config["duration_minutes"],
        endpoints,
        methods,
        config.get("success_rate", 0.95),
    )

    # Create failures (skip for highly successful tests)
    if config.get("num_failures", 0) > 0:
        await create_failures(
            client,
            test_id,
            config["num_failures"],
            config["duration_minutes"],
            endpoints,
            methods,
        )


async def main():
    """Generate comprehensive sample data."""
    print("🚀 Generating comprehensive sample data for Locust Data Service...")
    print(f"API URL: {API_URL}\n")

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Generate 30 diverse test runs
        test_configs = [
            # Recent successful tests
            {
                "project": "E-Commerce Platform",
                "test_name": "Homepage Load Test",
                "status": "completed",
                "hours_ago": 2,
                "duration_minutes": 15,
                "user_count": 500,
                "spawn_rate": 10.0,
                "num_snapshots": 90,
                "num_requests": 1000,
                "num_failures": 3,
                "failure_profile": "low",
                "success_rate": 0.98,
            },
            {
                "project": "E-Commerce Platform",
                "test_name": "API Stress Test",
                "status": "running",
                "hours_ago": 0.5,
                "duration_minutes": 30,
                "user_count": 1000,
                "spawn_rate": 20.0,
                "num_snapshots": 60,
                "num_requests": 500,
                "num_failures": 0,
                "failure_profile": "low",
                "success_rate": 0.99,
            },
            {
                "project": "Mobile API",
                "test_name": "Login Endpoint Test",
                "status": "completed",
                "hours_ago": 24,
                "duration_minutes": 30,
                "user_count": 200,
                "spawn_rate": 5.0,
                "num_snapshots": 180,
                "num_requests": 1500,
                "num_failures": 12,
                "failure_profile": "medium",
                "success_rate": 0.92,
            },
            {
                "project": "Payment Gateway",
                "test_name": "Transaction Processing",
                "status": "completed",
                "hours_ago": 12,
                "duration_minutes": 45,
                "user_count": 750,
                "spawn_rate": 15.0,
                "num_snapshots": 270,
                "num_requests": 2000,
                "num_failures": 8,
                "failure_profile": "low",
                "success_rate": 0.96,
            },
            # Tests from yesterday
            {
                "project": "E-Commerce Platform",
                "test_name": "Checkout Flow Test",
                "status": "completed",
                "hours_ago": 36,
                "duration_minutes": 20,
                "user_count": 300,
                "spawn_rate": 15.0,
                "num_snapshots": 120,
                "num_requests": 1200,
                "num_failures": 5,
                "failure_profile": "low",
                "success_rate": 0.97,
            },
            {
                "project": "Analytics Service",
                "test_name": "Data Ingestion Test",
                "status": "completed",
                "hours_ago": 40,
                "duration_minutes": 60,
                "user_count": 100,
                "spawn_rate": 2.0,
                "num_snapshots": 360,
                "num_requests": 3000,
                "num_failures": 20,
                "failure_profile": "medium",
                "success_rate": 0.90,
            },
            # Failed tests
            {
                "project": "Mobile API",
                "test_name": "Search Performance Test",
                "status": "failed",
                "hours_ago": 48,
                "duration_minutes": 10,
                "user_count": 100,
                "spawn_rate": 10.0,
                "num_snapshots": 30,
                "num_requests": 200,
                "num_failures": 25,
                "failure_profile": "high",
                "success_rate": 0.70,
            },
            {
                "project": "Content Delivery",
                "test_name": "CDN Edge Performance",
                "status": "failed",
                "hours_ago": 72,
                "duration_minutes": 8,
                "user_count": 2000,
                "spawn_rate": 50.0,
                "num_snapshots": 24,
                "num_requests": 300,
                "num_failures": 40,
                "failure_profile": "spike",
                "success_rate": 0.65,
            },
            # High load tests
            {
                "project": "E-Commerce Platform",
                "test_name": "Black Friday Simulation",
                "status": "completed",
                "hours_ago": 96,
                "duration_minutes": 120,
                "user_count": 5000,
                "spawn_rate": 50.0,
                "num_snapshots": 720,
                "num_requests": 5000,
                "num_failures": 15,
                "failure_profile": "low",
                "success_rate": 0.95,
            },
            {
                "project": "Payment Gateway",
                "test_name": "Peak Load Test",
                "status": "completed",
                "hours_ago": 120,
                "duration_minutes": 90,
                "user_count": 3000,
                "spawn_rate": 30.0,
                "num_snapshots": 540,
                "num_requests": 4000,
                "num_failures": 25,
                "failure_profile": "medium",
                "success_rate": 0.91,
            },
            # Edge cases - very short tests
            {
                "project": "Mobile API",
                "test_name": "Quick Smoke Test",
                "status": "completed",
                "hours_ago": 6,
                "duration_minutes": 2,
                "user_count": 10,
                "spawn_rate": 1.0,
                "num_snapshots": 12,
                "num_requests": 50,
                "num_failures": 0,
                "failure_profile": "low",
                "success_rate": 1.0,
            },
            {
                "project": "Analytics Service",
                "test_name": "Sanity Check",
                "status": "completed",
                "hours_ago": 8,
                "duration_minutes": 1,
                "user_count": 5,
                "spawn_rate": 0.5,
                "num_snapshots": 6,
                "num_requests": 20,
                "num_failures": 0,
                "failure_profile": "low",
                "success_rate": 1.0,
            },
            # Edge cases - very long tests
            {
                "project": "Content Delivery",
                "test_name": "Endurance Test 24h",
                "status": "completed",
                "hours_ago": 200,
                "duration_minutes": 1440,
                "user_count": 500,
                "spawn_rate": 5.0,
                "num_snapshots": 720,  # One snapshot every 2 minutes
                "num_requests": 8000,
                "num_failures": 50,
                "failure_profile": "low",
                "success_rate": 0.94,
            },
            # Medium user counts
            {
                "project": "E-Commerce Platform",
                "test_name": "Product Catalog Browse",
                "status": "completed",
                "hours_ago": 18,
                "duration_minutes": 25,
                "user_count": 400,
                "spawn_rate": 8.0,
                "num_snapshots": 150,
                "num_requests": 1800,
                "num_failures": 7,
                "failure_profile": "low",
                "success_rate": 0.96,
            },
            {
                "project": "Payment Gateway",
                "test_name": "Refund Processing",
                "status": "completed",
                "hours_ago": 30,
                "duration_minutes": 35,
                "user_count": 150,
                "spawn_rate": 3.0,
                "num_snapshots": 210,
                "num_requests": 900,
                "num_failures": 4,
                "failure_profile": "low",
                "success_rate": 0.98,
            },
            # Low user counts
            {
                "project": "Analytics Service",
                "test_name": "Report Generation",
                "status": "completed",
                "hours_ago": 15,
                "duration_minutes": 40,
                "user_count": 50,
                "spawn_rate": 1.0,
                "num_snapshots": 240,
                "num_requests": 600,
                "num_failures": 3,
                "failure_profile": "low",
                "success_rate": 0.99,
            },
            {
                "project": "Mobile API",
                "test_name": "Push Notification Service",
                "status": "completed",
                "hours_ago": 20,
                "duration_minutes": 15,
                "user_count": 80,
                "spawn_rate": 2.0,
                "num_snapshots": 90,
                "num_requests": 400,
                "num_failures": 2,
                "failure_profile": "low",
                "success_rate": 0.99,
            },
            # Various spawn rates
            {
                "project": "Content Delivery",
                "test_name": "Gradual Ramp Up",
                "status": "completed",
                "hours_ago": 50,
                "duration_minutes": 30,
                "user_count": 1000,
                "spawn_rate": 2.0,
                "num_snapshots": 180,
                "num_requests": 2500,
                "num_failures": 10,
                "failure_profile": "low",
                "success_rate": 0.96,
            },
            {
                "project": "E-Commerce Platform",
                "test_name": "Rapid Spike Test",
                "status": "completed",
                "hours_ago": 60,
                "duration_minutes": 10,
                "user_count": 2000,
                "spawn_rate": 100.0,
                "num_snapshots": 60,
                "num_requests": 1000,
                "num_failures": 30,
                "failure_profile": "spike",
                "success_rate": 0.85,
            },
            # Different environments and versions
            {
                "project": "Payment Gateway",
                "test_name": "QA Environment Test",
                "status": "completed",
                "hours_ago": 4,
                "duration_minutes": 20,
                "user_count": 200,
                "spawn_rate": 5.0,
                "environment": "qa",
                "version": "2.1.5",
                "num_snapshots": 120,
                "num_requests": 800,
                "num_failures": 15,
                "failure_profile": "medium",
                "success_rate": 0.88,
            },
            {
                "project": "Analytics Service",
                "test_name": "Staging Performance",
                "status": "completed",
                "hours_ago": 10,
                "duration_minutes": 25,
                "user_count": 300,
                "spawn_rate": 10.0,
                "environment": "staging",
                "version": "2.0.0-beta",
                "num_snapshots": 150,
                "num_requests": 1000,
                "num_failures": 8,
                "failure_profile": "low",
                "success_rate": 0.95,
            },
            {
                "project": "Mobile API",
                "test_name": "Production Validation",
                "status": "completed",
                "hours_ago": 3,
                "duration_minutes": 15,
                "user_count": 500,
                "spawn_rate": 15.0,
                "environment": "production",
                "version": "3.0.0",
                "num_snapshots": 90,
                "num_requests": 1500,
                "num_failures": 2,
                "failure_profile": "low",
                "success_rate": 0.99,
            },
            # More variety in projects
            {
                "project": "Content Delivery",
                "test_name": "Video Streaming Test",
                "status": "completed",
                "hours_ago": 28,
                "duration_minutes": 45,
                "user_count": 800,
                "spawn_rate": 12.0,
                "num_snapshots": 270,
                "num_requests": 2200,
                "num_failures": 12,
                "failure_profile": "low",
                "success_rate": 0.94,
            },
            {
                "project": "Content Delivery",
                "test_name": "Image Optimization",
                "status": "completed",
                "hours_ago": 55,
                "duration_minutes": 30,
                "user_count": 600,
                "spawn_rate": 10.0,
                "num_snapshots": 180,
                "num_requests": 1800,
                "num_failures": 5,
                "failure_profile": "low",
                "success_rate": 0.97,
            },
            {
                "project": "E-Commerce Platform",
                "test_name": "Cart Abandonment Flow",
                "status": "completed",
                "hours_ago": 45,
                "duration_minutes": 20,
                "user_count": 250,
                "spawn_rate": 7.0,
                "num_snapshots": 120,
                "num_requests": 900,
                "num_failures": 4,
                "failure_profile": "low",
                "success_rate": 0.98,
            },
            # More running tests
            {
                "project": "Payment Gateway",
                "test_name": "Live Transaction Monitor",
                "status": "running",
                "hours_ago": 1,
                "duration_minutes": 60,
                "user_count": 400,
                "spawn_rate": 8.0,
                "num_snapshots": 120,
                "num_requests": 800,
                "num_failures": 0,
                "failure_profile": "low",
                "success_rate": 0.97,
            },
            {
                "project": "Analytics Service",
                "test_name": "Real-time Analytics",
                "status": "running",
                "hours_ago": 0.25,
                "duration_minutes": 15,
                "user_count": 150,
                "spawn_rate": 5.0,
                "num_snapshots": 30,
                "num_requests": 200,
                "num_failures": 0,
                "failure_profile": "low",
                "success_rate": 0.99,
            },
            # Additional failed tests
            {
                "project": "E-Commerce Platform",
                "test_name": "Database Overload",
                "status": "failed",
                "hours_ago": 80,
                "duration_minutes": 15,
                "user_count": 1500,
                "spawn_rate": 40.0,
                "num_snapshots": 45,
                "num_requests": 400,
                "num_failures": 35,
                "failure_profile": "high",
                "success_rate": 0.60,
            },
            {
                "project": "Content Delivery",
                "test_name": "Cache Miss Scenario",
                "status": "failed",
                "hours_ago": 100,
                "duration_minutes": 12,
                "user_count": 800,
                "spawn_rate": 25.0,
                "num_snapshots": 36,
                "num_requests": 300,
                "num_failures": 28,
                "failure_profile": "high",
                "success_rate": 0.72,
            },
            # Week-old tests
            {
                "project": "Mobile API",
                "test_name": "Weekly Regression",
                "status": "completed",
                "hours_ago": 168,
                "duration_minutes": 50,
                "user_count": 600,
                "spawn_rate": 12.0,
                "num_snapshots": 300,
                "num_requests": 2500,
                "num_failures": 10,
                "failure_profile": "low",
                "success_rate": 0.96,
            },
        ]

        print(f"Generating {len(test_configs)} test runs with comprehensive data...\n")

        for i, config in enumerate(test_configs, 1):
            print(f"[{i}/{len(test_configs)}]")
            await generate_test_run(client, config)
            print()

    print("✅ Comprehensive sample data generation complete!")
    print("\n📊 Summary:")
    print(f"   - {len(test_configs)} test runs created")
    print(f"   - Multiple projects: {', '.join(PROJECTS)}")
    print("   - Various statuses: completed, running, failed")
    print("   - User counts: 5 - 5,000")
    print("   - Durations: 1 min - 24 hours")
    print(f"   - Environments: {', '.join(ENVIRONMENTS)}")
    print("\nView the dashboard at: http://localhost:3002/test-runs")


if __name__ == "__main__":
    asyncio.run(main())

# Locust Data Service

A FastAPI service for storing and analyzing historical Locust load test data. This service provides a REST API for collecting test run metrics, request logs, failures, and performance statistics, with support for multiple database backends (PostgreSQL and Snowflake).

## Features

- **REST API** for storing and retrieving Locust test data
- **Multiple Database Support**: Easy switching between PostgreSQL and Snowflake
- **Comprehensive Data Collection**:
  - Test run metadata (project, test name, user count, custom tags)
  - Individual request logs with response times and success/failure status
  - Failure tracking and aggregation
  - Performance statistics snapshots
- **Batch Operations**: Optimized endpoints for high-throughput data ingestion
- **Query & Filter**: Flexible endpoints for filtering by project, test name, date range, and status
- **Docker Support**: Ready-to-use Docker Compose setup
- **Locust Plugin**: Automatic data collection from your Locust tests
- **Comprehensive Tests**: Full pytest test suite for all API endpoints

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Docker and Docker Compose (for containerized deployment)

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd locust-data-service
```

2. **Install dependencies with uv**:
```bash
uv sync
```

3. **Copy environment configuration**:
```bash
cp .env.example .env
```

Edit `.env` to configure your database settings.

### Running with Docker Compose

The easiest way to get started is with Docker Compose:

```bash
# Start the service with PostgreSQL
docker-compose -f docker/docker-compose.yml up

# The API will be available at http://localhost:8000
# PostgreSQL will be on port 5432
# PgAdmin (optional) will be on port 5050
```

To include PgAdmin for database management:

```bash
docker-compose -f docker/docker-compose.yml --profile tools up
```

### Running Locally (Development)

1. **Start a PostgreSQL database** (or use the Docker Compose database):
```bash
# Using Docker for just the database
docker run -d \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=locust_data \
  -p 5432:5432 \
  postgres:16-alpine
```

2. **Run database migrations**:
```bash
uv run alembic upgrade head
```

3. **Start the API server**:
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/api/v1/health

## Configuration

### Environment Variables

Configure the service via `.env` file or environment variables:

```bash
# Database Selection
DATABASE_TYPE=postgres  # Options: postgres, snowflake

# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=locust_data

# Snowflake Configuration (when DATABASE_TYPE=snowflake)
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=public
SNOWFLAKE_WAREHOUSE=your_warehouse

# Application Configuration
APP_NAME=Locust Data Service
DEBUG=false
LOG_LEVEL=INFO
API_V1_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000"]
```

### Switching Database Types

To switch from PostgreSQL to Snowflake:

1. Update `.env`:
```bash
DATABASE_TYPE=snowflake
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
# ... other Snowflake settings
```

2. Restart the service - the database adapter will automatically switch.

## Using the Locust Plugin

### Installation

Install the plugin along with Locust:

```bash
uv pip install -e ".[locust]"
```

### Example Locustfile

Create a `locustfile.py`:

```python
from locust import HttpUser, task, between
from locust_plugin.data_collector import LocustDataCollector

# Initialize the data collector
collector = LocustDataCollector(
    service_url="http://localhost:8000",
    project="my-ecommerce-app",
    test_name="checkout-load-test",
    metadata={
        "environment": "staging",
        "version": "2.1.0",
        "team": "backend"
    }
)

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def view_products(self):
        self.client.get("/api/products")

    @task(2)
    def view_product_detail(self):
        self.client.get("/api/products/123")

    @task(1)
    def checkout(self):
        self.client.post("/api/checkout", json={
            "product_id": "123",
            "quantity": 1
        })
```

### Run Your Test

```bash
locust -f locustfile.py --host=https://your-api.com --users 100 --spawn-rate 10
```

All test data will automatically be sent to the Locust Data Service!

## API Documentation

### Test Runs

**Create a test run**:
```bash
curl -X POST http://localhost:8000/api/v1/test-runs \
  -H "Content-Type: application/json" \
  -d '{
    "project": "my-project",
    "test_name": "load-test-1",
    "user_count": 100,
    "spawn_rate": 10.0,
    "host": "https://example.com",
    "test_metadata": {"environment": "production"}
  }'
```

**List test runs**:
```bash
# All test runs
curl http://localhost:8000/api/v1/test-runs

# Filter by project
curl http://localhost:8000/api/v1/test-runs?project=my-project

# Filter by project and test name
curl http://localhost:8000/api/v1/test-runs?project=my-project&test_name=load-test-1

# Filter by status
curl http://localhost:8000/api/v1/test-runs?status=completed

# Filter by date range
curl "http://localhost:8000/api/v1/test-runs?start_date=2025-01-01T00:00:00&end_date=2025-12-31T23:59:59"
```

**Update test run status**:
```bash
curl -X PATCH http://localhost:8000/api/v1/test-runs/{test_run_id} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "end_time": "2025-12-06T10:00:00"
  }'
```

### Request Logs

**Log a single request**:
```bash
curl -X POST http://localhost:8000/api/v1/requests \
  -H "Content-Type: application/json" \
  -d '{
    "test_run_id": "test-run-uuid",
    "request_type": "GET",
    "name": "/api/users",
    "url": "https://example.com/api/users",
    "response_time": 125.5,
    "response_length": 2048,
    "success": true
  }'
```

**Batch create requests** (optimized for high throughput):
```bash
curl -X POST http://localhost:8000/api/v1/requests/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {
        "test_run_id": "test-run-uuid",
        "request_type": "GET",
        "name": "/api/endpoint1",
        "url": "https://example.com/api/endpoint1",
        "response_time": 120.0,
        "response_length": 1024,
        "success": true
      },
      ...
    ]
  }'
```

**Get aggregated statistics**:
```bash
curl http://localhost:8000/api/v1/requests/stats/{test_run_id}
```

### Failures

**List failures for a test run**:
```bash
curl http://localhost:8000/api/v1/failures?test_run_id={test_run_id}
```

### Stats Snapshots

**Create a stats snapshot**:
```bash
curl -X POST http://localhost:8000/api/v1/stats \
  -H "Content-Type: application/json" \
  -d '{
    "test_run_id": "test-run-uuid",
    "total_requests": 10000,
    "failure_count": 50,
    "failure_rate": 0.5,
    "avg_response_time": 150.0,
    "requests_per_second": 100.0,
    "current_user_count": 500
  }'
```

**List stats snapshots** (time-series data):
```bash
curl http://localhost:8000/api/v1/stats?test_run_id={test_run_id}
```

For complete API documentation, visit http://localhost:8000/docs (Swagger UI) or http://localhost:8000/redoc (ReDoc).

## Development

### Running Tests

Run the full test suite:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=app --cov-report=html
```

View coverage report:

```bash
open htmlcov/index.html
```

### Database Migrations

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Rollback migration:

```bash
uv run alembic downgrade -1
```

## Project Structure

```
locust-data-service/
├── app/
│   ├── api/v1/endpoints/    # API endpoint implementations
│   ├── core/                # Configuration and settings
│   ├── db/                  # Database session and adapters
│   ├── models/              # SQLAlchemy models
│   ├── repositories/        # Data access layer
│   ├── schemas/             # Pydantic schemas
│   └── main.py             # FastAPI application
├── locust_plugin/          # Locust integration plugin
├── tests/                  # Pytest test suite
├── alembic/               # Database migrations
├── docker/                # Docker configuration
├── pyproject.toml         # Project dependencies (uv)
└── README.md
```

## Architecture

The service follows clean architecture principles:

- **API Layer** (`app/api`): FastAPI endpoints for HTTP requests
- **Schema Layer** (`app/schemas`): Pydantic models for request/response validation
- **Service Layer** (optional, `app/services`): Business logic
- **Repository Layer** (`app/repositories`): Data access abstraction
- **Model Layer** (`app/models`): SQLAlchemy ORM models
- **Database Adapter** (`app/db/adapters`): Database-specific optimizations

This architecture allows for:
- Easy testing with dependency injection
- Database-agnostic code (easily switch between PostgreSQL and Snowflake)
- Clear separation of concerns
- Maintainable and scalable codebase

## License

[Your License Here]

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For issues, questions, or feature requests, please open an issue on GitHub

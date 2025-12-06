## Locust Plugin - Quick Start Guide

This plugin automatically sends your Locust test data to the Data Service for storage and analysis.

### Prerequisites

1. **Start the Data Service:**
   ```bash
   # From the project root directory
   uvicorn app.main:app --reload
   ```
   The service will be available at `http://localhost:8000`

2. **Install Locust:**
   ```bash
   pip install locust
   ```

### Basic Usage

Create a `locustfile.py` with the plugin:

```python
from locust import HttpUser, task, between
from locust_plugin.data_collector import LocustDataCollector

# Initialize the collector - this automatically captures all test data
collector = LocustDataCollector(
    service_url="http://localhost:8000",
    project="my-project",
    test_name="api-load-test",
)

class MyUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def my_task(self):
        self.client.get("/api/endpoint")
```

**Run your test:**
```bash
locust -f locustfile.py --host=https://your-api.com
```

That's it! Your test data is now being collected automatically.

### Configuration Options

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `service_url` | Yes | - | URL of the Data Service (e.g., `http://localhost:8000`) |
| `project` | Yes | - | Project name for organizing tests |
| `test_name` | Yes | - | Name of this specific test |
| `metadata` | No | `{}` | Custom metadata (environment, version, etc.) |
| `batch_size` | No | `50` | Send after collecting this many requests |
| `batch_interval` | No | `5.0` | Or send after this many seconds |

**Example with all options:**
```python
collector = LocustDataCollector(
    service_url="http://localhost:8000",
    project="ecommerce",
    test_name="checkout-flow",
    metadata={"environment": "staging", "version": "2.1.0"},
    batch_size=100,
    batch_interval=10.0,
)
```

### What Gets Collected

The plugin automatically captures:

✅ **Test Run Details** - Project, test name, start/end times, user count, spawn rate
✅ **Every Request** - Method, endpoint, response time, size, success/failure
✅ **Errors** - Exception details for failed requests
✅ **Performance Stats** - Calculated from request logs in the API

### View Your Test Data

**API Documentation (Interactive):**
```bash
open http://localhost:8000/docs
```

**Example API Queries:**
```bash
# List all test runs for a project
curl "http://localhost:8000/api/v1/test-runs?project=my-project"

# Get specific test run
curl "http://localhost:8000/api/v1/test-runs/{test_run_id}"

# Get aggregated stats
curl "http://localhost:8000/api/v1/requests/stats/{test_run_id}"

# List all requests (with pagination)
curl "http://localhost:8000/api/v1/requests?test_run_id={test_run_id}&limit=100"
```

---

## Advanced Usage

### Adding Custom Metadata to Requests

Add custom context data to individual requests:

```python
@task
def premium_user_flow(self):
    with self.client.get(
        "/api/checkout",
        context={"user_tier": "premium", "ab_test": "variant_b"}
    ) as response:
        if response.status_code == 200:
            response.success()
```

### Organizing Multiple Test Scenarios

Use different test names and metadata to organize scenarios:

```python
# Baseline test
baseline = LocustDataCollector(
    service_url="http://localhost:8000",
    project="ecommerce",
    test_name="baseline-load",
    metadata={"scenario": "normal", "max_users": 1000}
)

# Stress test
stress = LocustDataCollector(
    service_url="http://localhost:8000",
    project="ecommerce",
    test_name="black-friday-stress",
    metadata={"scenario": "peak", "max_users": 50000}
)
```

### Troubleshooting

**Plugin not collecting data?**
- Verify the Data Service is running: `curl http://localhost:8000/api/v1/health`
- Check Locust logs for error messages
- Ensure `service_url` doesn't have a trailing slash

**Requests not showing up?**
- Data is sent in batches (default: every 50 requests or 5 seconds)
- Check the `/api/v1/requests/batch` endpoint is accessible
- Look for "Failed to send request batch" errors in Locust output

**Need help?**
- View API docs: `http://localhost:8000/docs`
- Check test run was created: `GET /api/v1/test-runs`

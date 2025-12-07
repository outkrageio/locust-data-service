import asyncio
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx
from locust import events
from locust.env import Environment

logger = logging.getLogger(__name__)


class LogCaptureHandler(logging.Handler):
    """Custom logging handler that captures log records for sending to the service."""

    def __init__(self, collector: "LocustDataCollector"):
        super().__init__()
        self.collector = collector

    def emit(self, record: logging.LogRecord):
        if not self.collector.test_run_id:
            return

        try:
            log_data = {
                "test_run_id": str(self.collector.test_run_id),
                "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "exception": self.format_exception(record) if record.exc_info else None,
            }

            self.collector.log_batch.append(log_data)

            now = datetime.utcnow()
            should_send = (
                len(self.collector.log_batch) >= self.collector.batch_size
                or (now - self.collector.last_log_batch_send).total_seconds() >= self.collector.batch_interval
            )

            if should_send:
                asyncio.run(self.collector._send_log_batch())
                self.collector.last_log_batch_send = now

        except Exception:
            pass

    def format_exception(self, record: logging.LogRecord) -> str | None:
        if record.exc_info:
            import traceback

            return "".join(traceback.format_exception(*record.exc_info))
        return None


class LocustDataCollector:
    """Collects Locust test data and sends it to the Data Service."""

    def __init__(
        self,
        service_url: str,
        project: str,
        test_name: str,
        metadata: dict[str, Any] | None = None,
        batch_size: int = 50,
        batch_interval: float = 5.0,
        capture_logs: bool = True,
        log_level: int = logging.INFO,
    ):
        self.service_url = service_url.rstrip("/")
        self.project = project
        self.test_name = test_name
        self.metadata = metadata or {}
        self.batch_size = batch_size
        self.batch_interval = batch_interval
        self.capture_logs = capture_logs

        self.test_run_id: UUID | None = None
        self.client = httpx.AsyncClient(timeout=10.0)
        self.request_batch: list[dict[str, Any]] = []
        self.log_batch: list[dict[str, Any]] = []
        self.last_batch_send = datetime.utcnow()
        self.last_log_batch_send = datetime.utcnow()

        if self.capture_logs:
            self.log_handler = LogCaptureHandler(self)
            self.log_handler.setLevel(log_level)
            logging.getLogger().addHandler(self.log_handler)

        events.test_start.add_listener(self.on_test_start)
        events.test_stop.add_listener(self.on_test_stop)
        events.request.add_listener(self.on_request)

    def on_test_start(self, environment: Environment, **kwargs):
        try:
            logger.info(f"Starting test run: {self.project}/{self.test_name}")

            test_run_data = {
                "project": self.project,
                "test_name": self.test_name,
                "user_count": environment.parsed_options.num_users or 0,
                "spawn_rate": environment.parsed_options.spawn_rate or 0,
                "host": environment.host or "unknown",
                "test_metadata": self.metadata,
                "start_time": datetime.utcnow().isoformat(),
                "status": "running",
            }

            response = httpx.post(
                f"{self.service_url}/api/v1/test-runs",
                json=test_run_data,
                timeout=10.0,
            )
            response.raise_for_status()

            result = response.json()
            self.test_run_id = result["id"]
            logger.info(f"Test run created with ID: {self.test_run_id}")

        except Exception as e:
            logger.error(f"Failed to create test run: {e}")
            self.test_run_id = None

    def on_test_stop(self, environment: Environment, **kwargs):
        if not self.test_run_id:
            return

        try:
            if self.request_batch:
                asyncio.run(self._send_request_batch())

            if self.log_batch:
                asyncio.run(self._send_log_batch())

            update_data = {
                "status": "completed",
                "end_time": datetime.utcnow().isoformat(),
            }

            response = httpx.patch(
                f"{self.service_url}/api/v1/test-runs/{self.test_run_id}",
                json=update_data,
                timeout=10.0,
            )
            response.raise_for_status()

            logger.info(f"Test run {self.test_run_id} marked as completed")

        except Exception as e:
            logger.error(f"Failed to finalize test run: {e}")

        finally:
            if self.capture_logs and hasattr(self, "log_handler"):
                logging.getLogger().removeHandler(self.log_handler)
            asyncio.run(self.client.aclose())

    def on_request(
        self,
        request_type: str,
        name: str,
        response_time: float,
        response_length: int,
        exception: Exception | None,
        context: dict[str, Any],
        **kwargs,
    ):
        if not self.test_run_id:
            return

        try:
            request_data = {
                "test_run_id": str(self.test_run_id),
                "request_type": request_type,
                "name": name,
                "url": context.get("url", ""),
                "response_time": response_time,
                "response_length": response_length,
                "success": exception is None,
                "exception": str(exception) if exception else None,
                "start_time": kwargs.get("start_time", datetime.utcnow()).isoformat()
                if isinstance(kwargs.get("start_time"), datetime)
                else datetime.utcnow().isoformat(),
                "user_id": None,
                "context": context if context else None,
            }

            self.request_batch.append(request_data)

            now = datetime.utcnow()
            should_send = (
                len(self.request_batch) >= self.batch_size
                or (now - self.last_batch_send).total_seconds() >= self.batch_interval
            )

            if should_send:
                asyncio.run(self._send_request_batch())
                self.last_batch_send = now

        except Exception as e:
            logger.error(f"Failed to collect request data: {e}")

    async def _send_request_batch(self):
        if not self.request_batch:
            return

        try:
            batch_data = {"requests": self.request_batch.copy()}

            response = await self.client.post(
                f"{self.service_url}/api/v1/requests/batch",
                json=batch_data,
            )
            response.raise_for_status()

            logger.debug(f"Sent batch of {len(self.request_batch)} requests")
            self.request_batch.clear()

        except Exception as e:
            logger.error(f"Failed to send request batch: {e}")

    async def _send_log_batch(self):
        if not self.log_batch:
            return

        try:
            batch_data = {"logs": self.log_batch.copy()}

            response = await self.client.post(
                f"{self.service_url}/api/v1/logs/batch",
                json=batch_data,
            )
            response.raise_for_status()

            logger.debug(f"Sent batch of {len(self.log_batch)} logs")
            self.log_batch.clear()

        except Exception as e:
            logger.error(f"Failed to send log batch: {e}")

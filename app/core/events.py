"""Application lifecycle events."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Handle application startup and shutdown events."""
    logger.info("Starting up Locust Data Service...")
    logger.info("Application startup complete")

    yield

    logger.info("Shutting down Locust Data Service...")
    await engine.dispose()
    logger.info("Application shutdown complete")

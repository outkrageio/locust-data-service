from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "0.1.0"
    }


@router.get("/health/db")
async def database_health_check(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        return {
            "status": "healthy",
            "database": settings.database_type,
            "connected": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": settings.database_type,
            "connected": False,
            "error": str(e)
        }

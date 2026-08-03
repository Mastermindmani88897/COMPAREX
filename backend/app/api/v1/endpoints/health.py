"""
COMPAREX Backend – Health Check Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import redis_client
from app.db.session import get_db
from app.schemas.common import SuccessResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    summary="Application & Infrastructure Health Check",
    description="Verify backend API, Neon PostgreSQL database, and Upstash Redis connectivity.",
)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check verifying database and Redis connections."""
    db_healthy = False
    try:
        res = await db.execute(text("SELECT 1"))
        db_healthy = res.scalar() == 1
    except Exception:
        db_healthy = False

    redis_healthy = False
    try:
        redis_healthy = await redis_client.ping()
    except Exception:
        redis_healthy = False

    return SuccessResponse(
        message="Service health check completed",
        data={
            "status": "ok" if (db_healthy and redis_healthy) else "degraded",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "database": "connected" if db_healthy else "disconnected",
            "redis": "connected" if redis_healthy else "disconnected",
        },
    )

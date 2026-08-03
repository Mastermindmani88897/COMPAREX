"""
COMPAREX Backend – Health Check Endpoint
"""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.common import HealthResponse, SuccessResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=SuccessResponse[HealthResponse],
    summary="Health Check",
    description="Verify the API is running and return version information.",
)
async def health_check() -> SuccessResponse[HealthResponse]:
    """
    Health check endpoint.

    Returns:
        200 OK with status, version, and environment information.
    """
    return SuccessResponse(
        message="Service is healthy",
        data=HealthResponse(
            status="ok",
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
        ),
    )

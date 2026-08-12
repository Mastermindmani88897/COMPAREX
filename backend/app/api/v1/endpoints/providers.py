"""
COMPAREX Backend - Marketplace API Provider Status Endpoints
"""

from fastapi import APIRouter
from app.adapters.provider_status import ProviderHealthTracker
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get(
    "/status",
    summary="Get Marketplace Provider Status Map",
    description=(
        "Retrieve operational status (AVAILABLE, CONFIGURATION_ERROR, QUOTA_EXHAUSTED, "
        "NOT_CONFIGURED) for all marketplace providers. Secrets are never exposed."
    ),
)
async def get_providers_status():
    """Retrieve provider status map."""
    status_map = ProviderHealthTracker.get_provider_status_map()
    return SuccessResponse(
        message="Marketplace provider status map retrieved successfully",
        data=status_map,
    )


@router.get(
    "",
    summary="Get Detailed Provider Health & Diagnostics",
    description="Retrieve diagnostic health overview array for all marketplace API providers.",
)
async def get_providers_health():
    """Retrieve diagnostic provider health list."""
    health_data = ProviderHealthTracker.get_health_status()
    return SuccessResponse(
        message="Marketplace provider health overview retrieved successfully",
        data=health_data,
    )

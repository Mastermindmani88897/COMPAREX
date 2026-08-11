"""
COMPAREX Backend – Marketplace Management & Connector Endpoints
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.registry import CategoryCapabilityRegistry, ConnectorRegistry
from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.marketplace import MarketplaceCreate, MarketplacePublic, MarketplaceUpdate
from app.services.marketplace_service import MarketplaceService

from app.adapters.provider_status import ProviderHealthTracker

router = APIRouter(prefix="/marketplaces", tags=["Marketplaces"])


@router.get(
    "/health",
    summary="Get Marketplace Provider Health & Quotas",
    description=(
        "Retrieve diagnostic health status, HTTP status codes, and quota states "
        "for all external marketplace API providers. Secrets and API keys are never exposed."
    ),
)
async def get_provider_health():
    """Retrieve diagnostic provider health overview."""
    health_data = ProviderHealthTracker.get_health_status()
    return SuccessResponse(
        message="Marketplace provider health retrieved successfully",
        data=health_data,
    )


@router.get(
    "/connectors",
    summary="List Registered Connectors",
    description="Retrieve registered marketplace connectors, status, priority, and capabilities.",
)
async def list_registered_connectors(
    category: Optional[str] = Query(None, description="Filter by category capability"),
    enabled_only: bool = Query(True, description="Filter only active enabled connectors"),
):
    """List marketplace connectors endpoint."""
    connectors = ConnectorRegistry.list_connectors(category=category, enabled_only=enabled_only)
    data = [c.to_dict() for c in connectors]
    return SuccessResponse(
        message="Marketplace connectors retrieved successfully",
        data=data,
    )


@router.get(
    "/capabilities",
    summary="List Category Capability Registry",
    description="Retrieve category-to-marketplace capability mappings.",
)
async def list_category_capabilities():
    """List category capabilities mapping endpoint."""
    capabilities = CategoryCapabilityRegistry.get_all_capabilities()
    return SuccessResponse(
        message="Category capability mapping retrieved",
        data=capabilities,
    )


@router.get(
    "",
    response_model=SuccessResponse[list[MarketplacePublic]],
    summary="List Marketplaces",
    description="Retrieve all supported marketplaces.",
)
async def list_marketplaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List marketplaces endpoint."""
    service = MarketplaceService(db)
    marketplaces = await service.list_marketplaces(skip=skip, limit=limit)
    return SuccessResponse(
        message="Marketplaces retrieved successfully",
        data=marketplaces,
    )


@router.post(
    "",
    response_model=SuccessResponse[MarketplacePublic],
    status_code=status.HTTP_201_CREATED,
    summary="Create Marketplace",
    description="Create a new marketplace entry.",
)
async def create_marketplace(
    req: MarketplaceCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create marketplace endpoint."""
    service = MarketplaceService(db)
    marketplace = await service.create_marketplace(req)
    return SuccessResponse(
        message="Marketplace created successfully",
        data=marketplace,
    )


@router.get(
    "/{marketplace_id}",
    response_model=SuccessResponse[MarketplacePublic],
    summary="Get Marketplace Details",
    description="Retrieve details of a single marketplace by UUID.",
)
async def get_marketplace(
    marketplace_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get marketplace by ID endpoint."""
    service = MarketplaceService(db)
    marketplace = await service.get_marketplace_by_id(marketplace_id)
    return SuccessResponse(
        message="Marketplace details retrieved",
        data=marketplace,
    )


@router.put(
    "/{marketplace_id}",
    response_model=SuccessResponse[MarketplacePublic],
    summary="Update Marketplace",
    description="Update an existing marketplace entry.",
)
async def update_marketplace(
    marketplace_id: UUID,
    req: MarketplaceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update marketplace endpoint."""
    service = MarketplaceService(db)
    updated = await service.update_marketplace(marketplace_id, req)
    return SuccessResponse(
        message="Marketplace updated successfully",
        data=updated,
    )


@router.delete(
    "/{marketplace_id}",
    response_model=SuccessResponse[None],
    summary="Delete Marketplace",
    description="Delete a marketplace entry.",
)
async def delete_marketplace(
    marketplace_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete marketplace endpoint."""
    service = MarketplaceService(db)
    await service.delete_marketplace(marketplace_id)
    return SuccessResponse(
        message="Marketplace deleted successfully",
        data=None,
    )

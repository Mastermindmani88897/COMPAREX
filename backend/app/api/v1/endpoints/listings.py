"""
COMPAREX Backend – Product Listings API Endpoints

Manages price listings of products across different marketplaces.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.product_listing import (
    ProductListingCreate,
    ProductListingPublic,
    ProductListingUpdate,
)
from app.services.product_listing_service import ProductListingService

router = APIRouter(prefix="/listings", tags=["Price Listings"])


@router.post(
    "",
    response_model=SuccessResponse[ProductListingPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Create/Update Price Listing",
    description=(
        "Create a new product price listing on a marketplace. "
        "If a listing already exists for product+marketplace, "
        "it will be updated (upsert)."
    ),
)
async def create_listing(
    req: ProductListingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create or upsert listing endpoint."""
    service = ProductListingService(db)
    listing = await service.create_listing(req)
    return SuccessResponse(
        message="Listing created/updated successfully",
        data=listing,
    )


@router.patch(
    "/{listing_id}",
    response_model=SuccessResponse[ProductListingPublic],
    summary="Update Listing",
    description="Update price, availability, or fields of a listing.",
)
async def update_listing(
    listing_id: UUID,
    req: ProductListingUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update listing endpoint."""
    service = ProductListingService(db)
    listing = await service.update_listing(listing_id, req)
    return SuccessResponse(
        message="Listing updated successfully",
        data=listing,
    )


@router.delete(
    "/{listing_id}",
    response_model=SuccessResponse[None],
    summary="Delete Listing",
    description="Delete a price listing by its UUID.",
)
async def delete_listing(
    listing_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete listing endpoint."""
    service = ProductListingService(db)
    await service.delete_listing(listing_id)
    return SuccessResponse(
        message="Listing deleted successfully",
        data=None,
    )

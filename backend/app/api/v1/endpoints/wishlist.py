"""
COMPAREX Backend - Wishlist & Favorites API Endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.wishlist import (
    WishlistItemCreate,
    WishlistItemPublic,
    WishlistItemUpdate,
    WishlistResponse,
)
from app.services.wishlist_service import WishlistService

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get(
    "",
    response_model=SuccessResponse[WishlistResponse],
    summary="Get User Wishlist",
    description=(
        "Retrieve all wishlist items for logged in user enriched with live prices, target alerts, "
        "and AI recommendations."
    ),
)
async def get_user_wishlist(
    search: Optional[str] = Query(None, description="Search term filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    sort_by: str = Query(
        "date_added", description="Sort by: date_added, price_low, price_high, price_drop"
    ),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user wishlist endpoint."""
    service = WishlistService(db)
    res = await service.get_user_wishlist(
        current_user=current_user, search=search, category=category, sort_by=sort_by
    )
    return SuccessResponse(message="Wishlist retrieved successfully", data=res)


@router.post(
    "",
    response_model=SuccessResponse[WishlistItemPublic],
    status_code=status.HTTP_201_CREATED,
    summary="Add Product to Wishlist",
    description=(
        "Add a product to user wishlist with optional target price and preferred marketplace."
    ),
)
async def add_to_wishlist(
    req: WishlistItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add to wishlist endpoint."""
    service = WishlistService(db)
    item = await service.add_to_wishlist(current_user=current_user, req=req)
    return SuccessResponse(message="Product added to wishlist", data=item)


@router.patch(
    "/{id}",
    response_model=SuccessResponse[WishlistItemPublic],
    summary="Update Wishlist Item",
    description="Update target price, preferred marketplace, or notes for a wishlist item.",
)
async def update_wishlist_item(
    id: str,
    req: WishlistItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update wishlist item endpoint."""
    service = WishlistService(db)
    updated = await service.update_wishlist_item(current_user=current_user, item_id=id, req=req)
    return SuccessResponse(message="Wishlist item updated", data=updated)


@router.delete(
    "/{id}",
    response_model=SuccessResponse[None],
    summary="Remove from Wishlist",
    description="Remove a product from wishlist by Wishlist Item ID or Product ID.",
)
async def remove_from_wishlist(
    id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove from wishlist endpoint."""
    service = WishlistService(db)
    await service.remove_from_wishlist(current_user=current_user, id_or_product_id=id)
    return SuccessResponse(message="Wishlist item removed", data=None)

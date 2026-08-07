"""
COMPAREX Backend – Price Alert & Watchlist API Endpoints

Manages target price alerts, marketplace preferences, status toggles, and product watchlist.
"""

from typing import Any, Dict, List
import uuid

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.price_alert import (
    PriceAlertCreate,
    WatchlistCreate,
    WatchlistResponse,
)
from app.services.price_alert_service import PriceAlertService

router = APIRouter(tags=["Price Drop Alerts & Watchlist"])


@router.post(
    "/alerts",
    response_model=SuccessResponse[Dict[str, Any]],
    status_code=status.HTTP_201_CREATED,
    summary="Create Price Drop Alert",
    description=(
        "Set target price threshold, marketplace preference, and notification method for a product."
    ),
)
async def create_price_alert(
    payload: PriceAlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set new price drop target alert."""
    res = await PriceAlertService.create_alert(db, current_user.id, payload)
    return SuccessResponse(message="Price alert configured successfully", data=res)


@router.get(
    "/alerts",
    response_model=SuccessResponse[List[Dict[str, Any]]],
    summary="List Active User Price Alerts",
    description="Retrieve all configured price alerts for authenticated user.",
)
async def list_price_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List active user price alerts."""
    res = await PriceAlertService.list_user_alerts(db, current_user.id)
    return SuccessResponse(message="Price alerts retrieved successfully", data=res)


@router.patch(
    "/alerts/{id}",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Update Price Alert",
    description="Update target price, marketplace, notification method, or status toggle.",
)
async def update_price_alert(
    id: str,
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update price alert endpoint."""
    try:
        aid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    res = await PriceAlertService.update_alert(db, current_user.id, aid, payload)
    return SuccessResponse(message="Price alert updated successfully", data=res)


@router.delete(
    "/alerts/{id}",
    response_model=SuccessResponse[Dict[str, Any]],
    summary="Delete Price Alert",
    description="Remove a configured price alert.",
)
async def delete_price_alert(
    id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete price alert endpoint."""
    try:
        aid = uuid.UUID(id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    success = await PriceAlertService.delete_alert(db, current_user.id, aid)
    return SuccessResponse(message="Price alert deleted successfully", data={"success": success})


@router.post(
    "/watchlist",
    response_model=SuccessResponse[WatchlistResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Product to Watchlist",
    description="Bookmark product for price monitoring in watchlist.",
)
async def add_to_watchlist(
    payload: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add product to user watchlist."""
    res = await PriceAlertService.add_to_watchlist(db, current_user.id, payload)
    return SuccessResponse(message="Product added to watchlist", data=res)


@router.get(
    "/watchlist",
    response_model=SuccessResponse[List[WatchlistResponse]],
    summary="List User Watchlist Items",
    description="Retrieve bookmarked watchlist products for current user.",
)
async def list_watchlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve user watchlist."""
    res = await PriceAlertService.list_watchlist(db, current_user.id)
    return SuccessResponse(message="Watchlist retrieved successfully", data=res)

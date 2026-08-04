"""
COMPAREX Backend – Price Alert & Watchlist API Endpoints

Manages target price alerts and product watchlist bookmarks.
"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import SuccessResponse
from app.schemas.price_alert import (
    PriceAlertCreate,
    PriceAlertResponse,
    WatchlistCreate,
    WatchlistResponse,
)
from app.services.price_alert_service import PriceAlertService

router = APIRouter(tags=["Price Drop Alerts & Watchlist"])


@router.post(
    "/alerts",
    response_model=SuccessResponse[PriceAlertResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Price Drop Alert",
    description="Set target price threshold alert for a product.",
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
    response_model=SuccessResponse[List[PriceAlertResponse]],
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

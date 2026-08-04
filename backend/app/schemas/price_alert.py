"""
COMPAREX Backend – PriceAlert & Watchlist Schemas

Pydantic models for watchlist management and price drop alert configurations.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PriceAlertCreate(BaseModel):
    """Payload to set a new price drop alert."""

    product_id: UUID
    target_price: float = Field(gt=0, description="Target threshold price for alert")
    notification_channel: str = Field(default="email", description="email, push, or sms")


class PriceAlertResponse(BaseModel):
    """Response model for price alert entry."""

    id: UUID
    user_id: UUID
    product_id: UUID
    target_price: float
    initial_price: float
    notification_channel: str
    is_active: bool
    triggered: bool
    product_name: Optional[str] = None
    current_price: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class WatchlistCreate(BaseModel):
    """Payload to add product to watchlist."""

    product_id: UUID


class WatchlistResponse(BaseModel):
    """Response model for watchlist entry."""

    id: UUID
    user_id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    current_lowest_price: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

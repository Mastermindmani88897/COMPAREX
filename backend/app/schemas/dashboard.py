"""
COMPAREX Backend – Dashboard Summary Schemas

Pydantic models for user shopping dashboard metrics and activity stats.
"""

from typing import List

from pydantic import BaseModel, Field

from app.schemas.price_alert import PriceAlertResponse, WatchlistResponse


class ShoppingStats(BaseModel):
    """Aggregated shopping statistics."""

    total_money_saved: float = 0.0
    monthly_savings: float = 0.0
    active_alerts_count: int = 0
    watchlist_count: int = 0
    recent_searches_count: int = 0
    favorite_marketplaces: List[str] = Field(default_factory=list)


class DashboardSummaryResponse(BaseModel):
    """Complete user dashboard overview response model."""

    user_name: str
    stats: ShoppingStats
    recent_watchlist: List[WatchlistResponse] = Field(default_factory=list)
    active_alerts: List[PriceAlertResponse] = Field(default_factory=list)
    recent_searches: List[str] = Field(default_factory=list)
    deal_history_highlights: List[str] = Field(default_factory=list)

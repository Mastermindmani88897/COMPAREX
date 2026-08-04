"""
COMPAREX Backend – PriceHistory Schemas

Pydantic models for price history analytics, trends, and price predictions.
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class PricePoint(BaseModel):
    """Single historical price point data item."""

    date: str
    price: float
    marketplace_slug: str = "amazon"
    model_config = ConfigDict(from_attributes=True)


class PriceHistoryAnalyticsResponse(BaseModel):
    """Complete price history analytics summary response."""

    product_id: str
    product_name: str
    currency: str = "INR"
    today_price: float
    lowest_price: float
    highest_price: float
    average_price: float
    price_trend: str = Field(description="RISING, FALLING, or STABLE")
    weekly_trend_pct: float = Field(description="Percentage price change over 7 days")
    monthly_trend_pct: float = Field(description="Percentage price change over 30 days")
    best_purchase_period: str = Field(description="Recommended buying window")
    price_volatility_index: float = Field(description="0.0 (stable) to 1.0 (volatile)")
    predicted_target_price: float = Field(description="Projected future price")
    price_points: List[PricePoint] = Field(default_factory=list)

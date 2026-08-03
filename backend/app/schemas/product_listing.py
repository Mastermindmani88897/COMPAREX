"""
COMPAREX Backend – ProductListing Pydantic Schemas
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class MarketplaceSummary(BaseModel):
    """Minimal marketplace info embedded in listing responses."""

    id: uuid.UUID
    name: str
    slug: str
    logo_url: Optional[str] = None
    base_url: str

    model_config = {"from_attributes": True}


class ProductListingBase(BaseModel):
    price: Decimal = Field(gt=0, description="Current listing price")
    original_price: Optional[Decimal] = Field(
        None, ge=0, description="Original/MRP price before discount"
    )
    discount_percent: Optional[Decimal] = Field(
        None, ge=0, le=100, description="Calculated discount percentage"
    )
    currency: str = Field(default="INR", max_length=10)
    listing_url: str = Field(
        description="Direct URL to the product listing on marketplace"
    )
    marketplace_product_id: Optional[str] = Field(
        None, max_length=255, description="Marketplace internal item ID"
    )
    seller_name: Optional[str] = Field(None, max_length=255)
    is_available: bool = True
    is_prime: bool = False
    stock_status: str = Field(default="IN_STOCK", description="Stock availability badge string")
    delivery_estimate: Optional[str] = Field(None, description="Delivery timeframe estimate")
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)


class ProductListingCreate(ProductListingBase):
    product_id: uuid.UUID
    marketplace_id: uuid.UUID


class ProductListingUpdate(BaseModel):
    price: Optional[Decimal] = Field(None, gt=0)
    original_price: Optional[Decimal] = Field(None, ge=0)
    discount_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    listing_url: Optional[str] = None
    seller_name: Optional[str] = None
    is_available: Optional[bool] = None
    is_prime: Optional[bool] = None
    stock_status: Optional[str] = None
    delivery_estimate: Optional[str] = None
    rating: Optional[Decimal] = Field(None, ge=0, le=5)
    review_count: Optional[int] = Field(None, ge=0)


class ProductListingPublic(ProductListingBase):
    id: uuid.UUID
    product_id: uuid.UUID
    marketplace_id: uuid.UUID
    marketplace: Optional[MarketplaceSummary] = None
    badges: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PriceCompareResult(BaseModel):
    """Price comparison result for a single product across all marketplaces."""

    product_id: uuid.UUID
    product_name: str
    listings: list[ProductListingPublic]
    total_listings: int = 0
    lowest_price: Optional[Decimal] = None
    highest_price: Optional[Decimal] = None
    average_price: Optional[Decimal] = None
    price_spread: Optional[Decimal] = None
    max_savings: Optional[Decimal] = None
    best_listing_id: Optional[uuid.UUID] = None

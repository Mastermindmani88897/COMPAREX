"""
COMPAREX Backend – Shopping Profile Pydantic Schemas

User opt-in consent profile, budget preferences, and sensitivity settings.
"""

from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ShoppingProfileCreate(BaseModel):
    """Payload to configure or update shopping profile."""

    consent_opt_in: bool = Field(default=True, description="Explicit user consent for learning")
    preferred_brands: List[str] = Field(default_factory=list)
    preferred_marketplaces: List[str] = Field(default_factory=list)
    preferred_categories: List[str] = Field(default_factory=list)
    min_budget: float = Field(default=0.0, ge=0)
    max_budget: float = Field(default=500000.0, ge=0)
    delivery_speed: str = Field(default="EXPRESS")
    seller_preference: str = Field(default="VERIFIED_ONLY")
    discount_sensitivity: str = Field(default="HIGH")


class ShoppingProfileResponse(BaseModel):
    """Shopping profile response schema."""

    id: UUID
    user_id: UUID
    consent_opt_in: bool
    preferred_brands: List[str] = Field(default_factory=list)
    preferred_marketplaces: List[str] = Field(default_factory=list)
    preferred_categories: List[str] = Field(default_factory=list)
    min_budget: float
    max_budget: float
    delivery_speed: str
    seller_preference: str
    discount_sensitivity: str
    model_config = ConfigDict(from_attributes=True)

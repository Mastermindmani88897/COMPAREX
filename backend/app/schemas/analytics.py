"""
COMPAREX Backend – Shopping Analytics Schemas

Monthly/yearly savings stats, favorite category insights, and recommendation accuracy.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ShoppingAnalyticsResponse(BaseModel):
    """User shopping analytics overview response model."""

    id: Optional[UUID] = None
    user_id: UUID
    month_year: str
    total_saved: float
    avg_discount: float
    top_brand: Optional[str] = None
    top_category: Optional[str] = None
    recommendation_accuracy: float = 0.92
    insights: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

"""
COMPAREX Backend – AI Advisor Schemas

Pydantic models for AI buying advice, market risk analysis, and alternative options.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class AIAlternativeProduct(BaseModel):
    """Recommended alternative product item."""

    product_name: str
    price: float
    marketplace_name: str
    tier: str = Field(description="BUDGET or PREMIUM")
    reasoning: str


class AIAdvisorRequest(BaseModel):
    """Payload to query AI Shopping Advisor."""

    product_name: str
    current_price: float = Field(gt=0)
    category: Optional[str] = None
    marketplace_slug: Optional[str] = "amazon"


class AIAdvisorResponse(BaseModel):
    """Comprehensive AI buying advice response schema."""

    product_name: str
    current_price: float
    verdict: str = Field(description="BUY_NOW or WAIT_FOR_SALE")
    verdict_reasoning: str
    expected_future_price: float
    value_for_money_score: float = Field(description="0.0 to 10.0 rating")
    risk_analysis: List[str] = Field(default_factory=list)
    budget_alternatives: List[AIAlternativeProduct] = Field(default_factory=list)
    premium_alternatives: List[AIAlternativeProduct] = Field(default_factory=list)
    similar_products: List[str] = Field(default_factory=list)

"""
COMPAREX Backend – Explainable AI & CompareX Explain Schemas

Provides transparent AI reasoning breakdowns and "Why not Product B?" comparisons.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CompareExplainRequest(BaseModel):
    """Payload to request 'Why Product A over Product B?' explanation."""

    product_a_name: str
    product_b_name: str
    product_a_price: float
    product_b_price: float
    category: Optional[str] = None


class CompareExplainResponse(BaseModel):
    """Structured 'Why Product A was ranked higher than Product B' response."""

    product_a_name: str
    product_b_name: str
    winner_name: str
    explanation: str
    key_advantages_a: List[str] = Field(default_factory=list)
    key_disadvantages_b: List[str] = Field(default_factory=list)
    confidence_score: float = 0.95

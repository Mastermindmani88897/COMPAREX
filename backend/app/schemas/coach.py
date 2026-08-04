"""
COMPAREX Backend – AI Shopping Coach Schemas

Conversational coach advisory questions and structured response schemas.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class AICoachRequest(BaseModel):
    """Query payload for AI Shopping Coach."""

    question: str = Field(description="User shopping question, e.g., 'Should I buy now?'")
    product_name: Optional[str] = None
    current_price: Optional[float] = None
    category: Optional[str] = None


class AICoachResponse(BaseModel):
    """AI Shopping Coach answer response model."""

    question: str
    advice: str
    verdict: str = Field(description="BUY, WAIT, ALTERNATIVE, CAUTION")
    confidence_score: float = Field(ge=0.0, le=1.0)
    key_factors: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)

"""
COMPAREX Backend – AI Feedback Schemas

User helpful/not helpful recommendation rating feedback schemas.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AIFeedbackCreate(BaseModel):
    """Payload to rate an AI recommendation."""

    recommendation_id: Optional[UUID] = None
    is_helpful: bool = Field(description="True if helpful, False if not helpful")
    feedback_text: Optional[str] = None


class AIFeedbackResponse(BaseModel):
    """AI feedback response schema."""

    id: UUID
    user_id: UUID
    recommendation_id: Optional[UUID] = None
    is_helpful: bool
    feedback_text: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

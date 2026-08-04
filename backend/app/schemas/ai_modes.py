"""
COMPAREX Backend – Advanced AI Modes Schemas

9 specialized AI modes: Budget, Performance, Premium, Gaming, Eco, Fast, Gift.
"""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class AIModeDefinition(BaseModel):
    """Definition model for an AI mode profile."""

    mode_id: str
    mode_name: str
    description: str
    weights: Dict[str, float] = Field(default_factory=dict)


class AIModeSelectRequest(BaseModel):
    """Payload to select or switch active AI mode."""

    mode_id: str = Field(description="BUDGET, PERFORMANCE, PREMIUM, STUDENT, GAMING, ECO, etc.")
    prompt: Optional[str] = None


class AIModeSelectResponse(BaseModel):
    """Active AI mode configuration response."""

    active_mode: str
    mode_definition: AIModeDefinition
    message: str

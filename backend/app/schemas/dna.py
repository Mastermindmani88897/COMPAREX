"""
COMPAREX Backend – Shopping DNA & Persona Schemas

User shopping persona (Budget Shopper, Deal Hunter, Tech Enthusiast, etc.) schemas.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ShoppingDNAResponse(BaseModel):
    """Shopping DNA persona schema."""

    id: UUID
    user_id: UUID
    persona_name: str
    traits: List[str] = Field(default_factory=list)
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)


class ShoppingDNAUpdate(BaseModel):
    """Payload to update or customize Shopping DNA persona."""

    persona_name: Optional[str] = None
    traits: Optional[List[str]] = None
    is_active: Optional[bool] = None

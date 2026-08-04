"""
COMPAREX Backend – Shopping Memory Schemas

Interaction history events and context timeline schemas.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ShoppingMemoryCreate(BaseModel):
    """Payload to log shopping interaction memory."""

    memory_type: str = Field(description="SEARCH, VIEW, COMPARE, WISHLIST, ALERT")
    query: Optional[str] = None
    product_id: Optional[UUID] = None
    details: Optional[str] = None


class ShoppingMemoryResponse(BaseModel):
    """Shopping memory item response schema."""

    id: UUID
    user_id: UUID
    memory_type: str
    query: Optional[str] = None
    product_id: Optional[UUID] = None
    details: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

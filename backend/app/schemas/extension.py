"""
COMPAREX Backend - Extension Pydantic Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExtensionProductPayload(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    price: float = Field(ge=0)
    currency: str = Field(default="INR")
    url: str = Field(min_length=1)
    image_url: Optional[str] = None
    seller_name: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    marketplace_slug: str = Field(min_length=1)
    extension_version: str = Field(default="1.0.0")


class ExtensionCompareRequest(BaseModel):
    product_title: str = Field(min_length=1, max_length=500)
    category: Optional[str] = None
    current_price: Optional[float] = Field(None, ge=0)
    marketplace_slug: Optional[str] = None


class ExtensionStatusResponse(BaseModel):
    status: str = "online"
    environment: str
    api_version: str
    min_supported_extension_version: str = "1.0.0"
    active_connectors_count: int
    supported_marketplaces: List[str]


class ExtensionVersionCheck(BaseModel):
    client_version: str
    latest_version: str = "1.0.0"
    is_compatible: bool = True
    update_required: bool = False
    download_url: Optional[str] = None

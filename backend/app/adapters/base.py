"""
COMPAREX Backend - Marketplace Adapter & Connector Interface

Defines the contract that all marketplace connectors/adapters must implement
for search, details, pricing, availability, and delivery estimation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseMarketplaceAdapter(ABC):
    """Abstract Base Class for Marketplace Adapters and Connectors."""

    def __init__(self, marketplace_slug: str, base_url: str = "") -> None:
        self.marketplace_slug = marketplace_slug
        self.base_url = base_url

    @abstractmethod
    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for products on the target marketplace."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_product_details(self, listing_url: str) -> Dict[str, Any]:
        """Fetch full details and current pricing for a product listing URL."""
        raise NotImplementedError

    @abstractmethod
    async def fetch_latest_price(self, listing_url: str) -> Dict[str, Any]:
        """Fetch only the latest price and availability status for a listing URL."""
        raise NotImplementedError

    @abstractmethod
    def normalize_listing(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw payload into standardized COMPAREX format."""
        raise NotImplementedError

    # ── Standardized Connector Interface Methods (Phase 4 Specification) ────

    async def get_product_details(self, listing_id_or_url: str) -> Dict[str, Any]:
        """Alias / helper for fetch_product_details."""
        return await self.fetch_product_details(listing_id_or_url)

    async def get_product_price(self, listing_id_or_url: str) -> Dict[str, Any]:
        """Alias / helper for fetch_latest_price."""
        return await self.fetch_latest_price(listing_id_or_url)

    async def get_availability(self, listing_id_or_url: str) -> Dict[str, Any]:
        """Retrieve availability status for a listing."""
        details = await self.fetch_latest_price(listing_id_or_url)
        return {
            "is_available": details.get("is_available", True),
            "stock_status": details.get("stock_status", "IN_STOCK"),
        }

    async def get_delivery_estimate(self, listing_id_or_url: str) -> Dict[str, Any]:
        """Retrieve delivery estimate timeframe for a listing."""
        details = await self.fetch_product_details(listing_id_or_url)
        return {
            "delivery_estimate": details.get("delivery_estimate", "Standard Delivery 2-3 Days"),
            "is_prime": details.get("is_prime", False),
        }

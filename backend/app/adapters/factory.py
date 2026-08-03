"""
COMPAREX Backend – Marketplace Factory Pattern

Factory for registering and instantiating marketplace adapters dynamically.
"""

from typing import Any, Type

from app.adapters.base import BaseMarketplaceAdapter


class SampleMockAdapter(BaseMarketplaceAdapter):
    """Sample mock adapter implementation for core testing without external network requests."""

    async def search_products(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        return [
            {
                "title": f"{query} - Mock Item",
                "price": 29990.0,
                "original_price": 34990.0,
                "discount_percent": 14.29,
                "currency": "INR",
                "seller_name": "Official Retailer",
                "listing_url": f"{self.base_url}/item/mock-123",
                "marketplace_product_id": "MOCK-123",
                "is_available": True,
                "stock_status": "IN_STOCK",
                "delivery_estimate": "Express Delivery Tomorrow",
                "rating": 4.5,
                "review_count": 120,
            }
        ]

    async def fetch_product_details(self, listing_url: str) -> dict[str, Any]:
        return {
            "title": "Mock Product Details",
            "price": 29990.0,
            "original_price": 34990.0,
            "discount_percent": 14.29,
            "currency": "INR",
            "listing_url": listing_url,
            "marketplace_product_id": "MOCK-123",
            "seller_name": "Official Retailer",
            "is_available": True,
            "stock_status": "IN_STOCK",
            "delivery_estimate": "Delivery in 2 days",
            "rating": 4.6,
            "review_count": 145,
        }

    async def fetch_latest_price(self, listing_url: str) -> dict[str, Any]:
        return {
            "price": 29990.0,
            "original_price": 34990.0,
            "currency": "INR",
            "is_available": True,
            "stock_status": "IN_STOCK",
        }

    def normalize_listing(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "price": float(raw_data.get("price", 0.0)),
            "original_price": (
                float(raw_data["original_price"]) if raw_data.get("original_price") else None
            ),
            "currency": raw_data.get("currency", "INR"),
            "listing_url": raw_data.get("listing_url", ""),
            "seller_name": raw_data.get("seller_name", "Unknown Seller"),
            "is_available": bool(raw_data.get("is_available", True)),
            "stock_status": raw_data.get("stock_status", "IN_STOCK"),
            "rating": float(raw_data["rating"]) if raw_data.get("rating") else None,
            "review_count": raw_data.get("review_count"),
        }


class MarketplaceFactory:
    """Factory registry for instantiating Marketplace Adapters."""

    _registry: dict[str, Type[BaseMarketplaceAdapter]] = {}

    @classmethod
    def register(cls, slug: str, adapter_cls: Type[BaseMarketplaceAdapter]) -> None:
        """Register a new marketplace adapter class."""
        cls._registry[slug.lower()] = adapter_cls

    @classmethod
    def get_adapter(cls, slug: str, base_url: str = "") -> BaseMarketplaceAdapter:
        """Instantiate an adapter instance for a registered marketplace slug."""
        adapter_cls = cls._registry.get(slug.lower(), SampleMockAdapter)
        return adapter_cls(marketplace_slug=slug, base_url=base_url)

    @classmethod
    def list_registered_slugs(cls) -> list[str]:
        """Return list of all registered adapter marketplace slugs."""
        return list(cls._registry.keys())


# Register default sample mock adapter
MarketplaceFactory.register("mock", SampleMockAdapter)

"""
COMPAREX Backend - Phase 4 Mock Connectors

Realistic mock connector implementations for Indian retail marketplaces:
Amazon, Flipkart, Croma, Reliance Digital, Vijay Sales, Myntra, Ajio, Meesho, Nykaa.
"""

from typing import Any, Dict, List

from app.adapters.base import BaseMarketplaceAdapter
from app.adapters.registry import ConnectorMetadata, ConnectorRegistry


class BaseMockMarketplaceConnector(BaseMarketplaceAdapter):
    """Base class for generating category-aware realistic mock marketplace listings."""

    multiplier: float = 1.0
    discount_rate: float = 0.12
    seller_default: str = "Authorized Seller"
    express_delivery: bool = False
    badge_label: str = "Verified"
    default_rating: float = 4.3

    def _generate_price(self, query: str) -> float:
        q = query.lower()
        if "iphone" in q or "macbook" in q or "laptop" in q:
            base = 64990.0
        elif "watch" in q or "headphone" in q or "earbuds" in q:
            base = 12990.0
        elif "shirt" in q or "jeans" in q or "dress" in q:
            base = 1990.0
        elif "lipstick" in q or "cream" in q or "serum" in q or "perfume" in q:
            base = 990.0
        elif "tv" in q or "refrigerator" in q:
            base = 34990.0
        else:
            base = 4990.0
        calculated = round(base * self.multiplier / 10.0) * 10.0
        return max(199.0, calculated)

    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        price = self._generate_price(query)
        orig_price = round(price / (1.0 - self.discount_rate) / 50.0) * 50.0
        discount = round(((orig_price - price) / orig_price) * 100.0, 1)
        slug_url = query.lower().replace(" ", "-")
        title_str = query.title() + " (" + self.badge_label + " Edition)"
        url_str = self.base_url + "/product/" + slug_url + "-01"
        prod_id = self.marketplace_slug.upper() + "-PROD-01"
        eta_str = (
            "Express Delivery Tomorrow"
            if self.express_delivery
            else "Standard Delivery in 2-3 Days"
        )

        items: List[Dict[str, Any]] = [
            {
                "title": title_str,
                "price": price,
                "original_price": orig_price,
                "discount_percent": discount,
                "currency": "INR",
                "seller_name": self.seller_default,
                "listing_url": url_str,
                "marketplace_product_id": prod_id,
                "is_available": True,
                "is_prime": self.express_delivery,
                "stock_status": "IN_STOCK",
                "delivery_estimate": eta_str,
                "rating": self.default_rating,
                "review_count": 840,
                "badges": [self.badge_label],
            }
        ]
        return items[:limit]

    async def fetch_product_details(self, listing_url: str) -> Dict[str, Any]:
        price = 29990.0 * self.multiplier
        orig_price = price * 1.15
        det_title = "Marketplace Item - " + self.marketplace_slug.title()
        det_id = self.marketplace_slug.upper() + "-DET-99"
        return {
            "title": det_title,
            "price": round(price, 2),
            "original_price": round(orig_price, 2),
            "discount_percent": 13.0,
            "currency": "INR",
            "listing_url": listing_url,
            "marketplace_product_id": det_id,
            "seller_name": self.seller_default,
            "is_available": True,
            "is_prime": self.express_delivery,
            "stock_status": "IN_STOCK",
            "delivery_estimate": "Delivery within 2 days",
            "rating": self.default_rating,
            "review_count": 1250,
        }

    async def fetch_latest_price(self, listing_url: str) -> Dict[str, Any]:
        price = 29990.0 * self.multiplier
        return {
            "price": round(price, 2),
            "original_price": round(price * 1.15, 2),
            "currency": "INR",
            "is_available": True,
            "stock_status": "IN_STOCK",
        }

    def normalize_listing(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "price": float(raw_data.get("price", 0.0)),
            "original_price": (
                float(raw_data["original_price"]) if raw_data.get("original_price") else None
            ),
            "discount_percent": (
                float(raw_data["discount_percent"]) if raw_data.get("discount_percent") else None
            ),
            "currency": raw_data.get("currency", "INR"),
            "listing_url": raw_data.get("listing_url", ""),
            "seller_name": raw_data.get("seller_name", self.seller_default),
            "is_available": bool(raw_data.get("is_available", True)),
            "is_prime": bool(raw_data.get("is_prime", False)),
            "stock_status": raw_data.get("stock_status", "IN_STOCK"),
            "delivery_estimate": raw_data.get("delivery_estimate", "Standard Delivery"),
            "rating": float(raw_data["rating"]) if raw_data.get("rating") else None,
            "review_count": raw_data.get("review_count"),
        }


# ── Specific Connector Implementations ───────────────────────────────────────


class AmazonMockConnector(BaseMockMarketplaceConnector):
    multiplier = 0.96
    discount_rate = 0.15
    seller_default = "Appario Retail Private Ltd"
    express_delivery = True
    badge_label = "Amazon Prime"
    default_rating = 4.7


class FlipkartMockConnector(BaseMockMarketplaceConnector):
    multiplier = 0.97
    discount_rate = 0.14
    seller_default = "OmniTech Retail"
    express_delivery = True
    badge_label = "Flipkart Assured"
    default_rating = 4.6


class CromaMockConnector(BaseMockMarketplaceConnector):
    multiplier = 0.99
    discount_rate = 0.10
    seller_default = "Croma Digital Store"
    express_delivery = False
    badge_label = "Tata Croma Direct"
    default_rating = 4.4


class RelianceDigitalMockConnector(BaseMockMarketplaceConnector):
    multiplier = 0.985
    discount_rate = 0.11
    seller_default = "Reliance Retail Official"
    express_delivery = True
    badge_label = "Reliance Express"
    default_rating = 4.5


class VijaySalesMockConnector(BaseMockMarketplaceConnector):
    multiplier = 0.995
    discount_rate = 0.08
    seller_default = "Vijay Sales Retail"
    express_delivery = False
    badge_label = "Vijay Guarantee"
    default_rating = 4.3


class MyntraMockConnector(BaseMockMarketplaceConnector):
    multiplier = 0.92
    discount_rate = 0.25
    seller_default = "Myntra Fashion Brand Hub"
    express_delivery = True
    badge_label = "Myntra Insider"
    default_rating = 4.5


class AjioMockConnector(BaseMockMarketplaceConnector):
    multiplier = 0.91
    discount_rate = 0.28
    seller_default = "AJIO Trends Store"
    express_delivery = False
    badge_label = "AJIO Luxe/Trends"
    default_rating = 4.4


class MeeshoMockConnector(BaseMockMarketplaceConnector):
    multiplier = 0.85
    discount_rate = 0.35
    seller_default = "Direct Manufacturer Outlet"
    express_delivery = False
    badge_label = "Meesho Trusted Seller"
    default_rating = 4.1


class NykaaMockConnector(BaseMockMarketplaceConnector):
    multiplier = 0.98
    discount_rate = 0.12
    seller_default = "Nykaa E-Retail Pvt Ltd"
    express_delivery = True
    badge_label = "100% Authentic Beauty"
    default_rating = 4.8


# ── Auto-Registration ─────────────────────────────────────────────────────────

CONNECTORS_TO_REGISTER = [
    (
        ConnectorMetadata(
            name="Amazon India",
            slug="amazon",
            base_url="https://www.amazon.in",
            supported_categories=["electronics", "fashion", "beauty"],
            is_enabled=True,
            priority=1,
            supports_search=True,
            supports_details=True,
            supports_price_lookup=True,
            logo_url="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        ),
        AmazonMockConnector,
    ),
    (
        ConnectorMetadata(
            name="Flipkart",
            slug="flipkart",
            base_url="https://www.flipkart.com",
            supported_categories=["electronics", "fashion", "beauty"],
            is_enabled=True,
            priority=1,
            supports_search=True,
            supports_details=True,
            supports_price_lookup=True,
            logo_url="https://upload.wikimedia.org/wikipedia/commons/7/7a/Flipkart_logo.svg",
        ),
        FlipkartMockConnector,
    ),
    (
        ConnectorMetadata(
            name="Croma",
            slug="croma",
            base_url="https://www.croma.com",
            supported_categories=["electronics"],
            is_enabled=True,
            priority=2,
            supports_search=True,
            supports_details=True,
            supports_price_lookup=True,
            logo_url="https://upload.wikimedia.org/wikipedia/commons/5/53/Croma_Logo.svg",
        ),
        CromaMockConnector,
    ),
    (
        ConnectorMetadata(
            name="Reliance Digital",
            slug="reliance_digital",
            base_url="https://www.reliancedigital.in",
            supported_categories=["electronics"],
            is_enabled=True,
            priority=2,
            supports_search=True,
            supports_details=True,
            supports_price_lookup=True,
        ),
        RelianceDigitalMockConnector,
    ),
    (
        ConnectorMetadata(
            name="Vijay Sales",
            slug="vijay_sales",
            base_url="https://www.vijaysales.com",
            supported_categories=["electronics"],
            is_enabled=True,
            priority=3,
            supports_search=True,
            supports_details=True,
            supports_price_lookup=True,
        ),
        VijaySalesMockConnector,
    ),
    (
        ConnectorMetadata(
            name="Myntra",
            slug="myntra",
            base_url="https://www.myntra.com",
            supported_categories=["fashion"],
            is_enabled=True,
            priority=1,
            supports_search=True,
            supports_details=True,
            supports_price_lookup=True,
        ),
        MyntraMockConnector,
    ),
    (
        ConnectorMetadata(
            name="Ajio",
            slug="ajio",
            base_url="https://www.ajio.com",
            supported_categories=["fashion"],
            is_enabled=True,
            priority=2,
            supports_search=True,
            supports_details=True,
            supports_price_lookup=True,
        ),
        AjioMockConnector,
    ),
    (
        ConnectorMetadata(
            name="Meesho",
            slug="meesho",
            base_url="https://www.meesho.com",
            supported_categories=["fashion"],
            is_enabled=True,
            priority=3,
            supports_search=True,
            supports_details=True,
            supports_price_lookup=True,
        ),
        MeeshoMockConnector,
    ),
    (
        ConnectorMetadata(
            name="Nykaa",
            slug="nykaa",
            base_url="https://www.nykaa.com",
            supported_categories=["beauty"],
            is_enabled=True,
            priority=1,
            supports_search=True,
            supports_details=True,
            supports_price_lookup=True,
        ),
        NykaaMockConnector,
    ),
]


def register_all_mock_connectors() -> None:
    """Register all mock connectors with both ConnectorRegistry and MarketplaceFactory."""
    from app.adapters.factory import MarketplaceFactory
    for meta, connector_cls in CONNECTORS_TO_REGISTER:
        ConnectorRegistry.register(meta, connector_cls)
        MarketplaceFactory.register(meta.slug, connector_cls)


# Execute registration upon module load
register_all_mock_connectors()

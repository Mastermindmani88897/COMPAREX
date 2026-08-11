"""
COMPAREX Backend - SerpAPI Adapter (Google Shopping Specialist)

Connects to SerpAPI (https://serpapi.com/search.json?engine=google_shopping) to fetch
real-time price comparisons across multi-merchant Google Shopping aggregations.
Includes diagnostic provider status classification and health tracking.
"""

import re
import time
from typing import Any, Dict, List
import httpx

from app.adapters.base import BaseMarketplaceAdapter
from app.adapters.provider_status import ProviderHealthTracker, ProviderResponse, ProviderStatus
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

STORE_LOGOS = {
    "amazon": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
    "flipkart": "https://pngimg.com/uploads/flipkart/flipkart_PNG1.png",
    "croma": "https://www.croma.com/assets/images/croma_logo.png",
    "reliance": "https://www.reliancedigital.in/build/client/images/rd_logo.svg",
    "reliance digital": "https://www.reliancedigital.in/build/client/images/rd_logo.svg",
    "tata cliq": "https://www.tatacliq.com/favicon.ico",
    "meesho": "https://images.meesho.com/images/pow/meeshoLogo.png",
    "myntra": (
        "https://a57.foxnews.com/static.foxnews.com/foxnews.com/content/uploads/"
        "2021/02/1200/675/Myntra-logo.jpg"
    ),
    "vijay sales": "https://www.vijaysales.com/images/vijaysales-logo.png",
}


def _parse_price(val: Any) -> float:
    """Robust price parsing handling INR format, strings with commas, and floats."""
    if isinstance(val, (int, float)):
        return float(val)
    if not val or not isinstance(val, str):
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", val.replace(",", ""))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


class SerpApiAdapter(BaseMarketplaceAdapter):
    """Adapter for SerpAPI Google Shopping search results."""

    def __init__(
        self,
        marketplace_slug: str = "google_shopping",
        base_url: str = "https://shopping.google.com",
    ) -> None:
        super().__init__(marketplace_slug=marketplace_slug, base_url=base_url)
        self.api_key = settings.SERPAPI_API_KEY or ""
        self.api_url = "https://serpapi.com/search.json"

    async def search_products_detailed(self, query: str, limit: int = 10) -> ProviderResponse:
        """Detailed query returning structured ProviderResponse."""
        start_t = time.time()
        is_cfg = bool(self.api_key)

        if not is_cfg:
            logger.warning("SerpAPI key not configured.")
            ProviderHealthTracker.record_call(
                provider="SerpAPI",
                configured=False,
                status=ProviderStatus.NOT_CONFIGURED,
                error_message="SerpAPI Key not configured",
            )
            return ProviderResponse(
                provider_name="SerpAPI",
                status=ProviderStatus.NOT_CONFIGURED,
                error_message="API Key not configured",
            )

        params = {
            "engine": "google_shopping",
            "q": query,
            "api_key": self.api_key,
            "gl": "in",
            "hl": "en",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url, params=params)
                elapsed_ms = (time.time() - start_t) * 1000.0

                if response.status_code == 200:
                    data = response.json()

                    # Check for SerpAPI error payload inside HTTP 200 response
                    if "error" in data:
                        err_msg = str(data.get("error", ""))
                        err_lower = err_msg.lower()
                        is_quota = "out of searches" in err_lower or "credit" in err_lower
                        status = (
                            ProviderStatus.QUOTA_EXHAUSTED
                            if is_quota
                            else ProviderStatus.CONFIGURATION_ERROR
                        )
                        logger.warning(
                            "SERPAPI: HTTP 200 status=%s error='%s'", status.value, err_msg
                        )
                        ProviderHealthTracker.record_call(
                            provider="SerpAPI",
                            configured=True,
                            status=status,
                            http_status=200,
                            error_message=err_msg,
                            response_time_ms=elapsed_ms,
                        )
                        return ProviderResponse(
                            provider_name="SerpAPI",
                            status=status,
                            http_status=200,
                            error_message=err_msg,
                            response_time_ms=elapsed_ms,
                        )

                    # Extract items across supported SerpAPI keys
                    raw_items = (
                        data.get("shopping_results")
                        or data.get("inline_shopping_results")
                        or data.get("organic_results")
                        or []
                    )

                    raw_count = len(raw_items)
                    listings: List[Dict[str, Any]] = []

                    for item in raw_items[:limit]:
                        extracted_price = _parse_price(item.get("extracted_price"))
                        if extracted_price == 0.0:
                            extracted_price = _parse_price(item.get("price"))

                        if extracted_price == 0.0:
                            continue

                        merchant = item.get("source", "Google Merchant")
                        merchant_slug = merchant.lower().replace(" ", "_")
                        logo = STORE_LOGOS.get(merchant.lower(), "")
                        delivery = item.get("delivery") or "Standard Delivery"
                        rating = float(item["rating"]) if item.get("rating") else None
                        reviews = int(item["reviews"]) if item.get("reviews") else None

                        item_url = (
                            item.get("link")
                            or item.get("product_link")
                            or f"https://www.google.com/search?q={query}"
                        )

                        listings.append(
                            {
                                "title": item.get("title", f"{query} on {merchant}"),
                                "price": float(extracted_price),
                                "original_price": None,
                                "discount_percent": None,
                                "currency": "INR",
                                "seller_name": merchant,
                                "listing_url": item_url,
                                "marketplace_product_id": item.get(
                                    "product_id", f"SERP-{abs(hash(merchant)) % 1000}"
                                ),
                                "is_available": True,
                                "stock_status": "IN_STOCK",
                                "delivery_estimate": delivery,
                                "rating": rating,
                                "review_count": reviews,
                                "image_url": item.get("thumbnail") or item.get("image") or "",
                                "marketplace_slug": merchant_slug,
                                "marketplace_name": merchant,
                                "marketplace_logo": logo,
                            }
                        )

                    parsed_count = len(listings)
                    status = (
                        ProviderStatus.SUCCESS_WITH_RESULTS
                        if parsed_count > 0
                        else ProviderStatus.SUCCESS_NO_RESULTS
                    )

                    logger.info(
                        "SERPAPI: HTTP 200 status=%s raw_results=%d parsed_results=%d query='%s'",
                        status.value,
                        raw_count,
                        parsed_count,
                        query,
                    )

                    ProviderHealthTracker.record_call(
                        provider="SerpAPI",
                        configured=True,
                        status=status,
                        http_status=200,
                        result_count=parsed_count,
                        response_time_ms=elapsed_ms,
                    )

                    return ProviderResponse(
                        provider_name="SerpAPI",
                        status=status,
                        http_status=200,
                        results=listings,
                        raw_result_count=raw_count,
                        parsed_result_count=parsed_count,
                        response_time_ms=elapsed_ms,
                    )
                else:
                    err_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    if response.status_code == 429:
                        status = ProviderStatus.RATE_LIMITED
                    elif response.status_code in (401, 403):
                        status = ProviderStatus.AUTHENTICATION_ERROR
                    else:
                        status = ProviderStatus.UNKNOWN_ERROR

                    logger.warning(
                        "SERPAPI: HTTP %d status=%s", response.status_code, status.value
                    )
                    ProviderHealthTracker.record_call(
                        provider="SerpAPI",
                        configured=True,
                        status=status,
                        http_status=response.status_code,
                        error_message=err_msg,
                        response_time_ms=elapsed_ms,
                    )
                    return ProviderResponse(
                        provider_name="SerpAPI",
                        status=status,
                        http_status=response.status_code,
                        error_message=err_msg,
                        response_time_ms=elapsed_ms,
                    )

        except httpx.TimeoutException:
            elapsed_ms = (time.time() - start_t) * 1000.0
            logger.error("SERPAPI: TIMEOUT query='%s'", query)
            ProviderHealthTracker.record_call(
                provider="SerpAPI",
                configured=True,
                status=ProviderStatus.TIMEOUT,
                error_message="Request timeout",
                response_time_ms=elapsed_ms,
            )
            return ProviderResponse(
                provider_name="SerpAPI",
                status=ProviderStatus.TIMEOUT,
                error_message="Request timeout",
                response_time_ms=elapsed_ms,
            )
        except Exception as exc:
            elapsed_ms = (time.time() - start_t) * 1000.0
            logger.error("SERPAPI: NETWORK_ERROR error='%s'", exc)
            ProviderHealthTracker.record_call(
                provider="SerpAPI",
                configured=True,
                status=ProviderStatus.NETWORK_ERROR,
                error_message=str(exc),
                response_time_ms=elapsed_ms,
            )
            return ProviderResponse(
                provider_name="SerpAPI",
                status=ProviderStatus.NETWORK_ERROR,
                error_message=str(exc),
                response_time_ms=elapsed_ms,
            )

    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Backwards compatible list return."""
        resp = await self.search_products_detailed(query=query, limit=limit)
        return resp.results

    async def fetch_product_details(self, listing_url: str) -> Dict[str, Any]:
        return {
            "title": "Google Shopping Details",
            "price": 0.0,
            "listing_url": listing_url,
        }

    async def fetch_latest_price(self, listing_url: str) -> Dict[str, Any]:
        return {"price": 0.0, "currency": "INR", "is_available": True}

    def normalize_listing(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        merchant = raw_data.get("seller_name", "Google Merchant")
        slug = raw_data.get("marketplace_slug") or merchant.lower().replace(" ", "_")
        logo = raw_data.get("marketplace_logo") or STORE_LOGOS.get(merchant.lower(), "")
        orig = float(raw_data["original_price"]) if raw_data.get("original_price") else None
        disc = float(raw_data["discount_percent"]) if raw_data.get("discount_percent") else None
        return {
            "title": raw_data.get("title", f"Listing on {merchant}"),
            "price": float(raw_data.get("price", 0.0)),
            "original_price": orig,
            "discount_percent": disc,
            "currency": raw_data.get("currency", "INR"),
            "listing_url": raw_data.get("listing_url", "https://www.google.com"),
            "marketplace_product_id": raw_data.get("marketplace_product_id", "SERP-01"),
            "seller_name": merchant,
            "is_available": bool(raw_data.get("is_available", True)),
            "is_prime": False,
            "stock_status": raw_data.get("stock_status", "IN_STOCK"),
            "delivery_estimate": raw_data.get("delivery_estimate", "Standard Delivery"),
            "rating": float(raw_data["rating"]) if raw_data.get("rating") else None,
            "review_count": int(raw_data["review_count"]) if raw_data.get("review_count") else None,
            "image_url": raw_data.get("image_url", ""),
            "marketplace_slug": slug,
            "marketplace_name": merchant,
            "marketplace_logo": logo,
            "data_priority": 2,
            "marketplace_source": "SerpAPI",
        }

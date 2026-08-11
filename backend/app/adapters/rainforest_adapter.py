"""
COMPAREX Backend - Rainforest API Adapter (Amazon Specialist)

Connects to Rainforest API (https://api.rainforestapi.com/request) for live Amazon product data.
Includes diagnostic provider status classification and health tracking.
"""

import time
from typing import Any, Dict, List
import httpx

from app.adapters.base import BaseMarketplaceAdapter
from app.adapters.provider_status import ProviderHealthTracker, ProviderResponse, ProviderStatus
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RainforestAdapter(BaseMarketplaceAdapter):
    """Adapter for Rainforest API providing Amazon India marketplace listings."""

    def __init__(
        self, marketplace_slug: str = "amazon", base_url: str = "https://www.amazon.in"
    ) -> None:
        super().__init__(marketplace_slug=marketplace_slug, base_url=base_url)
        self.api_key = settings.RAINFOREST_API_KEY or ""
        self.api_url = "https://api.rainforestapi.com/request"

    async def search_products_detailed(self, query: str, limit: int = 10) -> ProviderResponse:
        """Detailed query returning structured ProviderResponse."""
        start_t = time.time()
        is_cfg = bool(self.api_key)

        if not is_cfg:
            logger.warning("Rainforest API key not configured.")
            ProviderHealthTracker.record_call(
                provider="Rainforest",
                configured=False,
                status=ProviderStatus.NOT_CONFIGURED,
                error_message="Rainforest Key not configured",
            )
            return ProviderResponse(
                provider_name="Rainforest",
                status=ProviderStatus.NOT_CONFIGURED,
                error_message="API Key not configured",
            )

        params = {
            "api_key": self.api_key,
            "type": "search",
            "amazon_domain": "amazon.in",
            "search_term": query,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url, params=params)
                elapsed_ms = (time.time() - start_t) * 1000.0

                if response.status_code == 200:
                    data = response.json()
                    search_results = data.get("search_results", [])
                    raw_count = len(search_results)
                    listings = []

                    for item in search_results[:limit]:
                        price_obj = item.get("price", {})
                        raw_price = price_obj.get("value") if isinstance(price_obj, dict) else None
                        if not raw_price:
                            continue

                        asin = item.get("asin", "")
                        listing_url = item.get("link") or f"https://www.amazon.in/dp/{asin}"
                        image_url = item.get("image") or ""
                        title = item.get("title", f"{query} on Amazon")
                        rating = float(item.get("rating", 4.5)) if item.get("rating") else 4.5
                        reviews = (
                            int(item.get("ratings_total", 120))
                            if item.get("ratings_total")
                            else 120
                        )
                        delivery_info = item.get("delivery", {})
                        is_prime = (
                            bool(delivery_info.get("is_prime", True))
                            if isinstance(delivery_info, dict)
                            else True
                        )
                        deliv_str = (
                            "Express Delivery Tomorrow" if is_prime else "Delivery in 2-3 Days"
                        )

                        listings.append(
                            {
                                "title": title,
                                "price": float(raw_price),
                                "original_price": None,
                                "discount_percent": None,
                                "currency": "INR",
                                "seller_name": "Amazon Merchant",
                                "listing_url": listing_url,
                                "marketplace_product_id": asin,
                                "is_available": True,
                                "stock_status": "IN_STOCK",
                                "delivery_estimate": deliv_str,
                                "rating": rating,
                                "review_count": reviews,
                                "image_url": image_url,
                                "is_prime": is_prime,
                                "marketplace_slug": "amazon",
                                "marketplace_name": "Amazon",
                                "marketplace_logo": (
                                    "https://upload.wikimedia.org/wikipedia/commons/a/a9/"
                                    "Amazon_logo.svg"
                                ),
                            }
                        )

                    parsed_count = len(listings)
                    status = (
                        ProviderStatus.SUCCESS_WITH_RESULTS
                        if parsed_count > 0
                        else ProviderStatus.SUCCESS_NO_RESULTS
                    )

                    logger.info(
                        "RAINFOREST: HTTP 200 status=%s raw=%d parsed=%d query='%s'",
                        status.value,
                        raw_count,
                        parsed_count,
                        query,
                    )
                    ProviderHealthTracker.record_call(
                        provider="Rainforest",
                        configured=True,
                        status=status,
                        http_status=200,
                        result_count=parsed_count,
                        response_time_ms=elapsed_ms,
                    )
                    return ProviderResponse(
                        provider_name="Rainforest",
                        status=status,
                        http_status=200,
                        results=listings,
                        raw_result_count=raw_count,
                        parsed_result_count=parsed_count,
                        response_time_ms=elapsed_ms,
                    )
                elif response.status_code in (402, 429):
                    if response.status_code == 402:
                        status = ProviderStatus.PAYMENT_REQUIRED
                        err_msg = "HTTP 402 Payment Required - Rainforest API credits exhausted"
                    else:
                        status = ProviderStatus.RATE_LIMITED
                        err_msg = "HTTP 429 Rate Limit"

                    logger.warning(
                        "RAINFOREST: HTTP %d status=%s error='%s'",
                        response.status_code,
                        status.value,
                        err_msg,
                    )
                    ProviderHealthTracker.record_call(
                        provider="Rainforest",
                        configured=True,
                        status=status,
                        http_status=response.status_code,
                        error_message=err_msg,
                        response_time_ms=elapsed_ms,
                    )
                    return ProviderResponse(
                        provider_name="Rainforest",
                        status=status,
                        http_status=response.status_code,
                        error_message=err_msg,
                        response_time_ms=elapsed_ms,
                    )
                else:
                    err_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    if response.status_code in (401, 403):
                        status = ProviderStatus.AUTHENTICATION_ERROR
                    else:
                        status = ProviderStatus.UNKNOWN_ERROR

                    logger.warning(
                        "RAINFOREST: HTTP %d status=%s", response.status_code, status.value
                    )
                    ProviderHealthTracker.record_call(
                        provider="Rainforest",
                        configured=True,
                        status=status,
                        http_status=response.status_code,
                        error_message=err_msg,
                        response_time_ms=elapsed_ms,
                    )
                    return ProviderResponse(
                        provider_name="Rainforest",
                        status=status,
                        http_status=response.status_code,
                        error_message=err_msg,
                        response_time_ms=elapsed_ms,
                    )

        except httpx.TimeoutException:
            elapsed_ms = (time.time() - start_t) * 1000.0
            logger.error("RAINFOREST: TIMEOUT query='%s'", query)
            ProviderHealthTracker.record_call(
                provider="Rainforest",
                configured=True,
                status=ProviderStatus.TIMEOUT,
                error_message="Request timeout",
                response_time_ms=elapsed_ms,
            )
            return ProviderResponse(
                provider_name="Rainforest",
                status=ProviderStatus.TIMEOUT,
                error_message="Request timeout",
                response_time_ms=elapsed_ms,
            )
        except Exception as exc:
            elapsed_ms = (time.time() - start_t) * 1000.0
            logger.error("RAINFOREST: NETWORK_ERROR error='%s'", exc)
            ProviderHealthTracker.record_call(
                provider="Rainforest",
                configured=True,
                status=ProviderStatus.NETWORK_ERROR,
                error_message=str(exc),
                response_time_ms=elapsed_ms,
            )
            return ProviderResponse(
                provider_name="Rainforest",
                status=ProviderStatus.NETWORK_ERROR,
                error_message=str(exc),
                response_time_ms=elapsed_ms,
            )

    async def search_products(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Backwards compatible search."""
        resp = await self.search_products_detailed(query=query, limit=limit)
        return resp.results

    async def fetch_product_details(self, listing_url: str) -> Dict[str, Any]:
        return {"title": "Amazon Product Details", "price": 0.0, "listing_url": listing_url}

    async def fetch_latest_price(self, listing_url: str) -> Dict[str, Any]:
        return {"price": 0.0, "currency": "INR", "is_available": True}

    def normalize_listing(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        orig = float(raw_data["original_price"]) if raw_data.get("original_price") else None
        disc = float(raw_data["discount_percent"]) if raw_data.get("discount_percent") else None
        logo = "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg"
        return {
            "title": raw_data.get("title", "Amazon Product"),
            "price": float(raw_data.get("price", 0.0)),
            "original_price": orig,
            "discount_percent": disc,
            "currency": raw_data.get("currency", "INR"),
            "listing_url": raw_data.get("listing_url", "https://www.amazon.in"),
            "marketplace_product_id": raw_data.get("marketplace_product_id", "AMZN-01"),
            "seller_name": raw_data.get("seller_name", "Amazon Merchant"),
            "is_available": bool(raw_data.get("is_available", True)),
            "is_prime": bool(raw_data.get("is_prime", True)),
            "stock_status": raw_data.get("stock_status", "IN_STOCK"),
            "delivery_estimate": raw_data.get("delivery_estimate", "Express Delivery Tomorrow"),
            "rating": float(raw_data.get("rating", 4.5)),
            "review_count": int(raw_data.get("review_count", 120)),
            "image_url": raw_data.get("image_url", ""),
            "marketplace_slug": "amazon",
            "marketplace_name": "Amazon",
            "marketplace_logo": logo,
            "data_priority": 2,
            "marketplace_source": "Rainforest API",
        }

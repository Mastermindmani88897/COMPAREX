"""
COMPAREX Backend - SerpAPI Adapter (Google Shopping Specialist)

Connects to SerpAPI (https://serpapi.com/search.json?engine=google_shopping) to fetch
real-time price comparisons across multi-merchant Google Shopping aggregations.
Includes diagnostic provider status classification and health tracking.

Root-Cause Fix (2026-08-18):
    Bug: parsed_results=0 when raw_results=17.
    Cause: Parser skipped items where extracted_price==0 BEFORE trying the `price`
           string field. Google Shopping results from SerpAPI often omit extracted_price
           and use a localized price string like "₹1,29,990" in the `price` field.
    Fix:  Try extracted_price first, then parse the `price` string with INR-aware
          regex. Only skip the item if neither yields a valid price.
"""

import re
import time
from typing import Any, Dict, List, Optional
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

# INR price patterns — handles ₹1,29,990 / Rs. 1,29,990 / 129990 / 1,29,990
_INR_PATTERN = re.compile(
    r"(?:₹|Rs\.?\s*|INR\s*)([0-9][0-9,]*(?:\.\d{1,2})?)|^([0-9][0-9,]*(?:\.\d{1,2})?)$",
    re.IGNORECASE,
)


def _parse_price(val: Any) -> Optional[float]:
    """
    Robust price parser.

    Returns float > 0 on success, None when no price can be extracted.
    Never returns 0.0 — caller should treat None as "no price".

    Handles:
      - float / int already
      - "₹1,29,990"  "Rs. 1,29,990"  "INR 129990"
      - plain numeric strings "129990" / "1,29,990"
      - SerpAPI extracted_price field (usually a clean float)
    """
    if isinstance(val, (int, float)):
        v = float(val)
        return v if v > 0 else None

    if not val or not isinstance(val, str):
        return None

    val_stripped = val.strip()

    # Try INR-prefixed pattern first
    m = _INR_PATTERN.search(val_stripped)
    if m:
        num_str = (m.group(1) or m.group(2) or "").replace(",", "")
        try:
            v = float(num_str)
            return v if v > 0 else None
        except ValueError:
            pass

    # Fallback: strip all non-numeric except decimal point
    cleaned = re.sub(r"[^\d.]", "", val_stripped.replace(",", ""))
    try:
        v = float(cleaned)
        return v if v > 0 else None
    except ValueError:
        return None


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
        api_key = self.api_key or settings.SERPAPI_API_KEY or ""
        is_cfg = bool(api_key)

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

        # Use google_shopping engine — purpose-built for product/price extraction
        params = {
            "engine": "google_shopping",
            "q": query,
            "api_key": api_key,
            "gl": "in",
            "hl": "en",
            "num": min(limit * 3, 40),  # request more to compensate for filtering
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.api_url, params=params)
                elapsed_ms = (time.time() - start_t) * 1000.0

                if response.status_code == 200:
                    data = response.json()

                    # Check for SerpAPI error payload inside HTTP 200 response
                    if "error" in data:
                        err_msg = str(data.get("error", ""))
                        err_lower = err_msg.lower()
                        is_quota = "out of searches" in err_lower or "credit" in err_lower
                        st = (
                            ProviderStatus.QUOTA_EXHAUSTED
                            if is_quota
                            else ProviderStatus.CONFIGURATION_ERROR
                        )
                        logger.warning(
                            "SERPAPI: HTTP 200 status=%s error='%s'", st.value, err_msg
                        )
                        ProviderHealthTracker.record_call(
                            provider="SerpAPI",
                            configured=True,
                            status=st,
                            http_status=200,
                            error_message=err_msg,
                            response_time_ms=elapsed_ms,
                        )
                        return ProviderResponse(
                            provider_name="SerpAPI",
                            status=st,
                            http_status=200,
                            error_message=err_msg,
                            response_time_ms=elapsed_ms,
                        )

                    # ── Diagnostic: log top-level response keys (never log values) ──
                    top_keys = list(data.keys()) if isinstance(data, dict) else []
                    shopping_count = len(data.get("shopping_results") or [])
                    inline_count = len(data.get("inline_shopping_results") or [])
                    organic_count = len(data.get("organic_results") or [])
                    logger.info(
                        "SERPAPI_RESPONSE_KEYS: keys=%s shopping=%d inline=%d organic=%d",
                        top_keys,
                        shopping_count,
                        inline_count,
                        organic_count,
                    )

                    # ── Select the best result set ────────────────────────────────
                    # Priority: shopping_results > inline_shopping_results
                    # Do NOT use organic_results for price extraction — they are
                    # editorial/blog pages, not structured product listings.
                    raw_items: List[Dict[str, Any]] = (
                        data.get("shopping_results")
                        or data.get("inline_shopping_results")
                        or []
                    )

                    raw_count = len(raw_items)
                    listings: List[Dict[str, Any]] = []
                    skipped_no_price = 0

                    for item in raw_items[:limit * 3]:
                        # ── Price extraction: multi-field fallback ────────────────
                        # SerpAPI may provide:
                        #   extracted_price: 129990.0   (clean float, preferred)
                        #   price: "₹1,29,990"          (INR string, common fallback)
                        #   old_price / original_price: original/MRP
                        extracted_price = _parse_price(item.get("extracted_price"))
                        if extracted_price is None:
                            extracted_price = _parse_price(item.get("price"))

                        if extracted_price is None:
                            skipped_no_price += 1
                            # Log item keys for diagnostics (never the values)
                            logger.debug(
                                "SERPAPI_ITEM_NO_PRICE: keys=%s title='%s'",
                                list(item.keys()),
                                str(item.get("title", ""))[:60],
                            )
                            continue

                        # ── Original/MRP price ────────────────────────────────────
                        original_price = (
                            _parse_price(item.get("original_price"))
                            or _parse_price(item.get("old_price"))
                        )

                        merchant = item.get("source") or item.get("seller") or "Google Merchant"
                        merchant_slug = merchant.lower().replace(" ", "_")
                        logo = STORE_LOGOS.get(merchant.lower(), "")
                        delivery = item.get("delivery") or None
                        rating = float(item["rating"]) if item.get("rating") else None
                        reviews = int(item["reviews"]) if item.get("reviews") else None

                        item_url = (
                            item.get("link")
                            or item.get("product_link")
                            or f"https://www.google.com/search?q={query}"
                        )

                        image = item.get("thumbnail") or item.get("image") or None

                        # Compute discount if we have both prices
                        discount_pct = None
                        if original_price and extracted_price and original_price > extracted_price:
                            discount_pct = round(
                                ((original_price - extracted_price) / original_price) * 100, 1
                            )

                        listings.append(
                            {
                                "title": item.get("title", f"{query} on {merchant}"),
                                "price": extracted_price,
                                "original_price": original_price,
                                "discount_percent": discount_pct,
                                "currency": "INR",
                                "seller_name": merchant,
                                "listing_url": item_url,
                                "marketplace_product_id": item.get(
                                    "product_id",
                                    f"SERP-{abs(hash(merchant + str(extracted_price))) % 100000}",
                                ),
                                "is_available": True,
                                "stock_status": "IN_STOCK",
                                "delivery_estimate": delivery,
                                "rating": rating,
                                "review_count": reviews,
                                "image_url": image,
                                "marketplace_slug": merchant_slug,
                                "marketplace_name": merchant,
                                "marketplace_logo": logo,
                            }
                        )

                        if len(listings) >= limit:
                            break

                    parsed_count = len(listings)
                    st = (
                        ProviderStatus.SUCCESS_WITH_RESULTS
                        if parsed_count > 0
                        else ProviderStatus.SUCCESS_NO_RESULTS
                    )

                    logger.info(
                        "SERPAPI: HTTP 200 status=%s raw_results=%d parsed_results=%d "
                        "skipped_no_price=%d query='%s'",
                        st.value,
                        raw_count,
                        parsed_count,
                        skipped_no_price,
                        query,
                    )

                    ProviderHealthTracker.record_call(
                        provider="SerpAPI",
                        configured=True,
                        status=st,
                        http_status=200,
                        result_count=parsed_count,
                        response_time_ms=elapsed_ms,
                    )

                    return ProviderResponse(
                        provider_name="SerpAPI",
                        status=st,
                        http_status=200,
                        results=listings,
                        raw_result_count=raw_count,
                        parsed_result_count=parsed_count,
                        response_time_ms=elapsed_ms,
                    )
                else:
                    err_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    if response.status_code == 429:
                        st = ProviderStatus.RATE_LIMITED
                    elif response.status_code in (401, 403):
                        st = ProviderStatus.AUTHENTICATION_ERROR
                    elif response.status_code == 402:
                        st = ProviderStatus.QUOTA_EXHAUSTED
                    else:
                        st = ProviderStatus.UNKNOWN_ERROR

                    logger.warning(
                        "SERPAPI: HTTP %d status=%s", response.status_code, st.value
                    )
                    ProviderHealthTracker.record_call(
                        provider="SerpAPI",
                        configured=True,
                        status=st,
                        http_status=response.status_code,
                        error_message=err_msg,
                        response_time_ms=elapsed_ms,
                    )
                    return ProviderResponse(
                        provider_name="SerpAPI",
                        status=st,
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
        orig = _parse_price(raw_data.get("original_price"))
        disc = float(raw_data["discount_percent"]) if raw_data.get("discount_percent") else None
        price = _parse_price(raw_data.get("price")) or 0.0
        return {
            "title": raw_data.get("title", f"Listing on {merchant}"),
            "price": price,
            "original_price": orig,
            "discount_percent": disc,
            "currency": raw_data.get("currency", "INR"),
            "listing_url": raw_data.get("listing_url", "https://www.google.com"),
            "marketplace_product_id": raw_data.get(
                "marketplace_product_id",
                f"SERP-{abs(hash(merchant)) % 100000}",
            ),
            "seller_name": merchant,
            "is_available": bool(raw_data.get("is_available", True)),
            "is_prime": False,
            "stock_status": raw_data.get("stock_status", "IN_STOCK"),
            "delivery_estimate": raw_data.get("delivery_estimate"),
            "rating": float(raw_data["rating"]) if raw_data.get("rating") else None,
            "review_count": int(raw_data["review_count"]) if raw_data.get("review_count") else None,
            "image_url": raw_data.get("image_url"),
            "marketplace_slug": slug,
            "marketplace_name": merchant,
            "marketplace_logo": logo,
            "data_priority": 2,
            "marketplace_source": "SerpAPI",
        }

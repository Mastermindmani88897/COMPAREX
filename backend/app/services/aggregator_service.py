"""
COMPAREX Backend - Marketplace Aggregator & Intelligent Matching Service

Queries Rainforest API, Bright Data, SerpAPI, and ZenRows simultaneously using clean product terms,
filters out model mismatches and accessories using ExactProductMatchEngine, and collects HD gallery.
NO FABRICATED SYNTHETIC MARKETPLACE PRICES OR GENERATED FALLBACK LISTINGS.

Provider failures are isolated — one provider failing does not block the rest.
All 7 major Indian marketplaces are always represented in the status layer,
even when providers cannot retrieve verified prices for them.
"""

import asyncio
import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.adapters.brightdata_adapter import BrightDataAdapter
from app.adapters.rainforest_adapter import RainforestAdapter
from app.adapters.serpapi_adapter import SerpApiAdapter
from app.adapters.zenrows_adapter import ZenRowsAdapter
from app.core.logging import get_logger
from app.core.redis import redis_client
from app.services.matching_engine import ExactProductMatchEngine, SearchQueryGenerator

logger = get_logger(__name__)

CACHE_TTL_SECONDS = 300  # 5 minutes TTL

# Major Indian marketplaces — always shown in UI with status, even if provider has no data.
MAJOR_MARKETPLACES = [
    {
        "slug": "amazon",
        "name": "Amazon",
        "search_url_template": "https://www.amazon.in/s?k={query}",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "priority": 1,
    },
    {
        "slug": "flipkart",
        "name": "Flipkart",
        "search_url_template": "https://www.flipkart.com/search?q={query}",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/7/7a/Flipkart_logo.svg",
        "priority": 1,
    },
    {
        "slug": "croma",
        "name": "Croma",
        "search_url_template": "https://www.croma.com/searchB?q={query}",
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/5/53/Croma_Logo.svg",
        "priority": 2,
    },
    {
        "slug": "reliance_digital",
        "name": "Reliance Digital",
        "search_url_template": "https://www.reliancedigital.in/search?q={query}",
        "logo_url": "https://www.reliancedigital.in/build/client/images/rd_logo.svg",
        "priority": 2,
    },
    {
        "slug": "tata_cliq",
        "name": "Tata CLiQ",
        "search_url_template": "https://www.tatacliq.com/search/?searchCategory=all&text={query}",
        "logo_url": "https://www.tatacliq.com/favicon.ico",
        "priority": 3,
    },
    {
        "slug": "myntra",
        "name": "Myntra",
        "search_url_template": "https://www.myntra.com/{query}",
        "logo_url": "https://constant.myntassets.com/web/assets/img/800x500_2019-05-01-17-53-43_b6a039ede6cbb28eddca38bde021e0c3.jpg",
        "priority": 3,
    },
    {
        "slug": "meesho",
        "name": "Meesho",
        "search_url_template": "https://www.meesho.com/search?q={query}",
        "logo_url": "https://images.meesho.com/images/pow/meeshoLogo.png",
        "priority": 3,
    },
]

# Store logo registry
STORE_LOGOS: Dict[str, str] = {m["slug"]: m["logo_url"] for m in MAJOR_MARKETPLACES}
STORE_LOGOS.update(
    {
        "amazon": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "flipkart": "https://pngimg.com/uploads/flipkart/flipkart_PNG1.png",
        "vijay_sales": "https://www.vijaysales.com/images/vijaysales-logo.png",
    }
)

# Price outlier detection: a listing is suspicious if its price deviates by this factor
# from the median of other verified offers.
OUTLIER_FACTOR_HIGH = 10.0  # 10× median — likely a wrong currency, bundle, or parse error
OUTLIER_FACTOR_LOW = 0.1   # 1/10th median — likely accessory, wrong variant, or currency error


class MarketplaceAggregatorService:
    """Service handling multi-marketplace provider query execution and zero-synthetic reporting."""

    @classmethod
    def is_uuid(cls, val: str) -> bool:
        """Check if a string is a valid UUID format."""
        try:
            uuid.UUID(val)
            return True
        except (ValueError, TypeError):
            return False

    @classmethod
    def normalize_query(cls, raw_query: str) -> str:
        """Clean and normalize product search query."""
        clean = raw_query.replace("-", " ").strip()
        clean = re.sub(r"\s+", " ", clean)
        return clean

    @classmethod
    def classify_url_exactness(cls, url: str) -> bool:
        """Return True if direct product URL, False if generic search URL."""
        if not url:
            return False
        u = url.lower()
        if "/s?k=" in u or "/search" in u or "?q=" in u or "/s/" in u:
            return False
        return True

    @classmethod
    def _build_major_marketplace_status(
        cls,
        verified_listings: List[Dict[str, Any]],
        provider_statuses: Dict[str, str],
        query: str,
        last_checked: str,
    ) -> List[Dict[str, Any]]:
        """
        Build always-visible status for every major marketplace.

        Each entry shows whether a verified price was found,
        what the price is (or why it's unavailable), and a search URL fallback.

        This list is ALWAYS returned regardless of provider failures —
        the UI must NEVER hide major marketplaces because of provider issues.
        """
        # Build lookup: marketplace_slug → best verified listing
        verified_by_slug: Dict[str, Dict[str, Any]] = {}
        for lst in verified_listings:
            slug = (lst.get("marketplace_slug") or "").lower()
            if slug and slug not in verified_by_slug:
                verified_by_slug[slug] = lst
            # Also handle compound slugs (e.g. "reliance_digital" from "reliance")
            if slug == "reliance" and "reliance_digital" not in verified_by_slug:
                verified_by_slug["reliance_digital"] = lst

        status_list = []
        for mp in MAJOR_MARKETPLACES:
            slug = mp["slug"]
            search_url = mp["search_url_template"].format(
                query=query.replace(" ", "+")
            )

            if slug in verified_by_slug:
                lst = verified_by_slug[slug]
                entry = {
                    "slug": slug,
                    "name": mp["name"],
                    "logo_url": mp.get("logo_url", ""),
                    "priority": mp["priority"],
                    "status": "verified",
                    "title": lst.get("title"),
                    "price": float(lst.get("price", 0)),
                    "original_price": float(lst["original_price"]) if lst.get("original_price") else None,
                    "discount_percent": float(lst["discount_percent"]) if lst.get("discount_percent") else None,
                    "currency": lst.get("currency", "INR"),
                    "listing_url": lst.get("listing_url", search_url),
                    "image_url": lst.get("image_url") or mp.get("logo_url", ""),
                    "is_exact_url": lst.get("is_exact_url", False),
                    "seller_name": lst.get("seller_name"),
                    "delivery_estimate": lst.get("delivery_estimate"),
                    "rating": float(lst["rating"]) if lst.get("rating") else None,
                    "review_count": int(lst["review_count"]) if lst.get("review_count") else None,
                    "is_available": lst.get("is_available", True),
                    "match_score": float(lst.get("match_score", 1.0)),
                    "last_checked": last_checked,
                    "search_url": search_url,
                    "has_verified_price": True,
                }
            else:
                # Determine reason
                reason = "No verified listing found"
                for prov_key, prov_status in provider_statuses.items():
                    if "401" in prov_status or "authentication" in prov_status.lower():
                        reason = "Provider authentication error"
                        break
                    elif "402" in prov_status or "credit" in prov_status.lower():
                        reason = "Provider credits exhausted"
                        break
                    elif "provider_failure" in prov_status:
                        reason = "Provider temporarily unavailable"
                        break

                entry = {
                    "slug": slug,
                    "name": mp["name"],
                    "logo_url": mp.get("logo_url", ""),
                    "priority": mp["priority"],
                    "status": "unavailable",
                    "title": None,
                    "price": None,
                    "original_price": None,
                    "discount_percent": None,
                    "currency": "INR",
                    "listing_url": search_url,
                    "image_url": mp.get("logo_url", ""),
                    "is_exact_url": False,
                    "seller_name": None,
                    "delivery_estimate": None,
                    "rating": None,
                    "review_count": None,
                    "is_available": None,
                    "match_score": None,
                    "last_checked": last_checked,
                    "search_url": search_url,
                    "has_verified_price": False,
                    "unavailable_reason": reason,
                }

            status_list.append(entry)

        return status_list

    @classmethod
    def _detect_price_outliers(
        cls,
        listings: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Flag price outliers using a median-based approach.

        A listing price is flagged as suspicious if it is more than OUTLIER_FACTOR_HIGH times
        the median or less than OUTLIER_FACTOR_LOW times the median.

        Flagged listings are NOT removed — they are marked with is_outlier=True
        so the frontend can decide how to display them.
        """
        if len(listings) < 2:
            for lst in listings:
                lst["is_outlier"] = False
                lst["outlier_reason"] = None
            return listings

        prices = [float(lst["price"]) for lst in listings if lst.get("price") and float(lst["price"]) > 0]
        if not prices:
            return listings

        sorted_prices = sorted(prices)
        mid = len(sorted_prices) // 2
        if len(sorted_prices) % 2 == 0:
            median = (sorted_prices[mid - 1] + sorted_prices[mid]) / 2
        else:
            median = sorted_prices[mid]

        if median <= 0:
            for lst in listings:
                lst["is_outlier"] = False
                lst["outlier_reason"] = None
            return listings

        for lst in listings:
            p = float(lst.get("price") or 0)
            if p <= 0:
                lst["is_outlier"] = False
                lst["outlier_reason"] = None
                continue

            if p > median * OUTLIER_FACTOR_HIGH:
                lst["is_outlier"] = True
                lst["outlier_reason"] = (
                    f"Price ₹{p:,.0f} is suspiciously high (>{OUTLIER_FACTOR_HIGH}× "
                    f"median ₹{median:,.0f}). May be wrong variant, bundle, or currency."
                )
                logger.warning(
                    "OUTLIER_PRICE_HIGH: price=%.2f median=%.2f marketplace=%s title=%s",
                    p,
                    median,
                    lst.get("marketplace_slug"),
                    lst.get("title", "")[:60],
                )
            elif p < median * OUTLIER_FACTOR_LOW:
                lst["is_outlier"] = True
                lst["outlier_reason"] = (
                    f"Price ₹{p:,.0f} is suspiciously low (<{OUTLIER_FACTOR_LOW}× "
                    f"median ₹{median:,.0f}). May be accessory, wrong variant, or currency issue."
                )
                logger.warning(
                    "OUTLIER_PRICE_LOW: price=%.2f median=%.2f marketplace=%s title=%s",
                    p,
                    median,
                    lst.get("marketplace_slug"),
                    lst.get("title", "")[:60],
                )
            else:
                lst["is_outlier"] = False
                lst["outlier_reason"] = None

        return listings

    @classmethod
    async def aggregate_search(
        cls,
        query: str,
        product_id: Optional[str] = None,
        category: Optional[str] = None,
        limit_per_connector: int = 10,
        sort_by: str = "price",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = False,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Execute multi-provider search with exact matching and zero synthetic fallbacks."""
        raw_query = query.strip()
        target_search_term = raw_query

        # If query is a UUID: do NOT hardcode a product name.
        # The caller should pass the real product name. Log and use the UUID as-is
        # which will return empty results rather than fabricate data for the wrong product.
        if cls.is_uuid(raw_query):
            logger.warning(
                "UUID '%s' passed as search query to aggregate_search. "
                "The caller should pass the product name, not the product ID. "
                "Returning empty result to avoid fabricating wrong product data.",
                raw_query,
            )
            # Return a structured empty response rather than searching with a UUID
            last_checked = datetime.now(timezone.utc).isoformat()
            empty_status = cls._build_major_marketplace_status([], {}, "", last_checked)
            return {
                "query": raw_query,
                "product_id": product_id,
                "total_listings": 0,
                "marketplaces_queried": [],
                "provider_statuses": {},
                "major_marketplace_status": empty_status,
                "verified_marketplace_count": 0,
                "total_major_marketplaces": len(MAJOR_MARKETPLACES),
                "lowest_price": None,
                "highest_price": None,
                "average_price": None,
                "verification_status": "unavailable",
                "verification_message": (
                    "Product name must be provided instead of product ID for marketplace search."
                ),
                "listings": [],
                "from_cache": False,
                "last_updated_time": last_checked,
                "data_quality": "unavailable",
                "verified_offer_count": 0,
            }

        clean_search_term = SearchQueryGenerator.generate_clean_query(target_search_term)
        cache_key = f"comparex:aggregator:v6:{clean_search_term.lower()}:{sort_by}"

        if use_cache:
            try:
                cached_bytes = await redis_client.get(cache_key)
                if cached_bytes:
                    logger.info("Cache HIT for query='%s'", clean_search_term)
                    data = json.loads(cached_bytes)
                    data["from_cache"] = True
                    return data
            except Exception as exc:
                logger.warning("Redis cache error: %s", exc)

        # ── 1. Execute Adapters in parallel ─────────────────────────────────────
        rainforest = RainforestAdapter()
        brightdata = BrightDataAdapter()
        serpapi = SerpApiAdapter()
        zenrows = ZenRowsAdapter()

        rf_task = rainforest.search_products(clean_search_term, limit=limit_per_connector)
        bd_task = brightdata.search_products(clean_search_term, limit=limit_per_connector)
        sa_task = serpapi.search_products(clean_search_term, limit=limit_per_connector)
        zr_task = zenrows.search_products(clean_search_term, limit=limit_per_connector)

        rf_res, bd_res, sa_res, zr_res = await asyncio.gather(
            rf_task, bd_task, sa_task, zr_task, return_exceptions=True
        )

        raw_candidates: List[Dict[str, Any]] = []
        provider_statuses: Dict[str, str] = {}

        for provider_name, result, adapter in [
            ("rainforest", rf_res, rainforest),
            ("brightdata", bd_res, brightdata),
            ("serpapi", sa_res, serpapi),
            ("zenrows", zr_res, zenrows),
        ]:
            if isinstance(result, Exception):
                err_str = str(result)
                # Classify error type for observability
                if "401" in err_str or "Unauthorized" in err_str or "authentication" in err_str.lower():
                    status_str = "authentication_error (401)"
                elif "402" in err_str or "Payment" in err_str or "credit" in err_str.lower():
                    status_str = "credits_exhausted (402)"
                elif "400" in err_str:
                    status_str = "bad_request (400)"
                elif "timeout" in err_str.lower() or "TimeoutException" in err_str:
                    status_str = "timeout"
                else:
                    status_str = f"provider_failure ({type(result).__name__})"
                logger.error(
                    "PROVIDER_FAILURE | provider=%s | query='%s' | status=%s | error=%s",
                    provider_name,
                    clean_search_term,
                    status_str,
                    err_str[:200],
                )
                provider_statuses[provider_name] = status_str
            elif isinstance(result, list):
                count = len(result)
                provider_statuses[provider_name] = (
                    f"provider_success ({count} results)" if count else "provider_no_match"
                )
                logger.info(
                    "PROVIDER_SUCCESS | provider=%s | query='%s' | results=%d",
                    provider_name,
                    clean_search_term,
                    count,
                )
                for item in result:
                    raw_candidates.append(adapter.normalize_listing(item))
            else:
                provider_statuses[provider_name] = "provider_unknown_response"

        # ── 2. Exact Attribute Matching ──────────────────────────────────────────
        verified_listings: List[Dict[str, Any]] = []
        rejected_count = 0

        for candidate in raw_candidates:
            title = candidate.get("title", "")
            is_match, score, reason = ExactProductMatchEngine.evaluate_marketplace_match(
                clean_search_term, title
            )

            if is_match and score >= 0.85:
                url = candidate.get("listing_url", "")
                is_exact_url = cls.classify_url_exactness(url)

                candidate["match_score"] = float(score)
                candidate["is_exact_url"] = is_exact_url
                candidate["verification_status"] = "verified"
                candidate["retrieved_at"] = datetime.now(timezone.utc).isoformat()
                verified_listings.append(candidate)
            else:
                rejected_count += 1
                logger.info(
                    "REJECTED_LISTING | title='%s' | reason='%s'", title[:80], reason
                )

        # ── 3. Price outlier detection ───────────────────────────────────────────
        if verified_listings:
            verified_listings = cls._detect_price_outliers(verified_listings)

        # ── 4. Sort verified listings by price ──────────────────────────────────
        if sort_by in ("price", "lowest_price"):
            verified_listings.sort(key=lambda x: float(x.get("price", 0)))

        # Only use non-outlier, available listings for price stats
        stat_listings = [
            x for x in verified_listings
            if x.get("is_available", True) and x.get("price") and not x.get("is_outlier", False)
        ]
        avail_prices = [float(x["price"]) for x in stat_listings]

        lowest = min(avail_prices) if avail_prices else None
        highest = max(avail_prices) if avail_prices else None
        avg = round(sum(avail_prices) / len(avail_prices), 2) if avail_prices else None

        last_checked = datetime.now(timezone.utc).isoformat()

        # ── 5. Major Marketplace Status Layer ────────────────────────────────────
        major_status = cls._build_major_marketplace_status(
            verified_listings, provider_statuses, clean_search_term, last_checked
        )
        verified_major_count = sum(1 for m in major_status if m["has_verified_price"])

        # Price data quality classification
        if verified_major_count >= 4:
            data_quality = "high"
            quality_message = f"High confidence — {verified_major_count} major marketplaces verified"
        elif verified_major_count >= 2:
            data_quality = "medium"
            quality_message = f"Medium confidence — {verified_major_count} major marketplaces verified"
        elif verified_major_count == 1:
            data_quality = "low"
            quality_message = "Low confidence — only 1 major marketplace verified"
        else:
            data_quality = "unavailable"
            quality_message = "0 major marketplaces verified — providers returned no results"

        logger.info(
            "MARKETPLACE_SUMMARY | query='%s' | raw=%d | verified=%d | rejected=%d | "
            "major_verified=%d/%d | lowest=%s | quality=%s",
            clean_search_term,
            len(raw_candidates),
            len(verified_listings),
            rejected_count,
            verified_major_count,
            len(MAJOR_MARKETPLACES),
            f"₹{lowest:,.2f}" if lowest else "UNAVAILABLE",
            data_quality,
        )

        response_payload = {
            "query": clean_search_term,
            "product_id": product_id,
            "total_listings": len(verified_listings),
            "marketplaces_queried": [m["slug"] for m in MAJOR_MARKETPLACES],
            "provider_statuses": provider_statuses,
            # Always-visible major marketplace status (never hidden on failure)
            "major_marketplace_status": major_status,
            "verified_marketplace_count": verified_major_count,
            "total_major_marketplaces": len(MAJOR_MARKETPLACES),
            # Price statistics — ONLY from non-outlier verified prices
            "lowest_price": lowest,
            "highest_price": highest,
            "average_price": avg,
            "verified_offer_count": len(stat_listings),
            # Verification
            "verification_status": "verified" if verified_listings else "unavailable",
            "verification_message": (
                f"Verified {len(verified_listings)} listing(s) from live providers."
                if verified_listings
                else (
                    "Live marketplace prices are temporarily unavailable. "
                    "Providers could not verify current listings. "
                    "Major marketplace search links are provided below."
                )
            ),
            # Listings (for backward compat)
            "listings": verified_listings,
            # Data quality
            "data_quality": data_quality,
            "data_quality_message": quality_message,
            "marketplace_coverage": f"{verified_major_count}/{len(MAJOR_MARKETPLACES)} major marketplaces verified",
            # Timestamps
            "from_cache": False,
            "last_updated_time": last_checked,
            "last_checked": last_checked,
        }

        try:
            await redis_client.set(
                cache_key, json.dumps(response_payload), expire_seconds=CACHE_TTL_SECONDS
            )
        except Exception as exc:
            logger.warning("Redis cache write error: %s", exc)

        return response_payload

    @classmethod
    def _build_multi_image_gallery(cls, query: str, listings: List[Dict[str, Any]]) -> List[str]:
        """Collect image URLs from real verified listings only."""
        images: List[str] = []
        for item in listings:
            img = item.get("image_url")
            if img and img.startswith("http") and img not in images:
                images.append(img)
        return images[:10]

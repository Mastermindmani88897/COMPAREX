"""
COMPAREX Backend - Phase 4 Marketplace Aggregator Service

Queries multiple connectors concurrently, merges, normalizes, deduplicates,
sorts results, and caches aggregated responses in Redis.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from app.adapters.registry import ConnectorRegistry
from app.core.logging import get_logger
from app.core.redis import redis_client

logger = get_logger(__name__)

CACHE_TTL_SECONDS = 300  # 5 minutes default TTL


class MarketplaceAggregatorService:
    """Service handling multi-marketplace data aggregation, deduplication, and caching."""

    @classmethod
    async def aggregate_search(
        cls,
        query: str,
        category: Optional[str] = None,
        limit_per_connector: int = 5,
        sort_by: str = "price",
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = False,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Concurrently query connectors, aggregate, deduplicate, and return structured comparison data."""
        cache_key = (
            "comparex:aggregator:search:"
            + query.lower().strip()
            + ":"
            + (category or "all")
            + ":"
            + str(sort_by)
            + ":"
            + str(min_price)
            + ":"
            + str(max_price)
            + ":"
            + str(in_stock_only)
        )

        if use_cache:
            try:
                cached_bytes = await redis_client.get(cache_key)
                if cached_bytes:
                    logger.info("Cache HIT for aggregator search query=%s", query)
                    data = json.loads(cached_bytes)
                    data["from_cache"] = True
                    return data
            except Exception as exc:
                logger.warning("Redis cache read error: %s", exc)

        active_connectors = ConnectorRegistry.get_active_connectors_for_category(category)
        if not active_connectors:
            active_connectors = ConnectorRegistry.get_active_connectors_for_category(None)

        logger.info(
            "Aggregating search for query=%s across %d connectors (category=%s)",
            query,
            len(active_connectors),
            category or "all",
        )

        tasks = [
            connector.search_products(query=query, limit=limit_per_connector)
            for _, connector in active_connectors
        ]

        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        all_listings: List[Dict[str, Any]] = []
        queried_slugs: List[str] = []

        for idx, (meta, connector) in enumerate(active_connectors):
            queried_slugs.append(meta.slug)
            result = raw_results[idx]

            if isinstance(result, Exception):
                logger.error("Connector %s search failed: %s", meta.slug, result)
                continue

            if isinstance(result, list):
                for item in result:
                    norm = connector.normalize_listing(item)
                    norm["marketplace_slug"] = meta.slug
                    norm["marketplace_name"] = meta.name
                    norm["marketplace_logo"] = meta.logo_url
                    norm["marketplace_base_url"] = meta.base_url
                    norm["title"] = item.get("title", query.title() + " on " + meta.name)
                    norm["badges"] = item.get("badges", [meta.name])
                    all_listings.append(norm)

        filtered_listings: List[Dict[str, Any]] = []
        for lst in all_listings:
            p = float(lst["price"])
            if min_price is not None and p < min_price:
                continue
            if max_price is not None and p > max_price:
                continue
            if in_stock_only and not lst.get("is_available", True):
                continue
            filtered_listings.append(lst)

        deduped = cls._deduplicate_listings(filtered_listings)
        enriched_listings = cls._enrich_and_score_listings(deduped)

        if sort_by == "price":
            enriched_listings.sort(key=lambda x: float(x["price"]))
        elif sort_by == "price_desc":
            enriched_listings.sort(key=lambda x: float(x["price"]), reverse=True)
        elif sort_by == "rating":
            enriched_listings.sort(key=lambda x: float(x.get("rating") or 0.0), reverse=True)
        elif sort_by == "discount":
            enriched_listings.sort(key=lambda x: float(x.get("discount_percent") or 0.0), reverse=True)
        elif sort_by == "deal_score":
            enriched_listings.sort(key=lambda x: float(x.get("deal_score") or 0.0), reverse=True)

        prices = [float(x["price"]) for x in enriched_listings if x.get("is_available", True)]
        lowest = min(prices) if prices else None
        highest = max(prices) if prices else None
        avg = round(sum(prices) / len(prices), 2) if prices else None
        spread = round(highest - lowest, 2) if (highest and lowest) else 0.0

        max_savings = None
        for lst in enriched_listings:
            orig = lst.get("original_price")
            curr = float(lst["price"])
            if orig and float(orig) > curr:
                diff = float(orig) - curr
                if max_savings is None or diff > max_savings:
                    max_savings = round(diff, 2)

        best_deal_id = enriched_listings[0]["id"] if enriched_listings else None

        response_payload = {
            "query": query,
            "category": category,
            "total_listings": len(enriched_listings),
            "marketplaces_queried": queried_slugs,
            "lowest_price": lowest,
            "highest_price": highest,
            "average_price": avg,
            "price_spread": spread,
            "max_savings": max_savings,
            "best_deal_listing_id": best_deal_id,
            "listings": enriched_listings,
            "from_cache": False,
        }

        try:
            await redis_client.set(
                cache_key, json.dumps(response_payload), expire_seconds=CACHE_TTL_SECONDS
            )
            logger.info("Saved aggregator search query=%s to cache (TTL=%ds)", query, CACHE_TTL_SECONDS)
        except Exception as exc:
            logger.warning("Redis cache write error: %s", exc)

        return response_payload

    @classmethod
    def _deduplicate_listings(cls, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen: Dict[str, Dict[str, Any]] = {}
        unique_list: List[Dict[str, Any]] = []

        for lst in listings:
            key = str(lst["marketplace_slug"]) + ":" + str(lst["title"]).lower() + ":" + str(lst["price"])
            if key not in seen:
                seen[key] = lst
                unique_list.append(lst)

        return unique_list

    @classmethod
    def _enrich_and_score_listings(cls, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not listings:
            return []

        prices = [float(item["price"]) for item in listings if item.get("is_available", True)]
        min_p = min(prices) if prices else 1.0
        max_p = max(prices) if prices else min_p

        enriched: List[Dict[str, Any]] = []
        for idx, lst in enumerate(listings):
            lst_copy = dict(lst)
            if "id" not in lst_copy:
                lst_copy["id"] = "lst-" + str(lst_copy["marketplace_slug"]) + "-" + str(idx + 1)

            price = float(lst_copy["price"])

            if max_p > min_p:
                price_score = (max_p - price) / (max_p - min_p)
            else:
                price_score = 1.0

            rating = float(lst_copy.get("rating") or 4.0)
            rating_score = rating / 5.0

            discount = float(lst_copy.get("discount_percent") or 0.0)
            discount_score = min(discount / 50.0, 1.0)

            prime_score = 1.0 if lst_copy.get("is_prime") else 0.0

            deal_score = round(
                (price_score * 0.70)
                + (rating_score * 0.14)
                + (discount_score * 0.08)
                + (prime_score * 0.08),
                2,
            )
            lst_copy["deal_score"] = deal_score

            badges: List[str] = list(lst_copy.get("badges", []))
            if price == min_p and lst_copy.get("is_available", True):
                if "Lowest Price" not in badges:
                    badges.insert(0, "Lowest Price")
            if rating >= 4.7 and "Top Rated" not in badges:
                badges.append("Top Rated")
            if lst_copy.get("is_prime") and "Express Delivery" not in badges:
                badges.append("Express Delivery")
            if not lst_copy.get("is_available", True) and "Out of Stock" not in badges:
                badges.append("Out of Stock")

            lst_copy["badges"] = badges
            enriched.append(lst_copy)

        return enriched

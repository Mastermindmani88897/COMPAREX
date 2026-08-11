"""
COMPAREX Backend - Single Source of Truth Marketplace Normalizer & Offer Dataset

Normalizes marketplace keys, handles backend deduplication, and provides the single
canonical verified marketplace-offer dataset for:
1. Major Marketplace Coverage
2. Marketplace Price Comparison Matrix
3. Current Best Price & Stats
4. Price History
5. Market Trend
6. Price Drop Alerts
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

CANONICAL_MARKETPLACES: Dict[str, Dict[str, Any]] = {
    "amazon": {
        "slug": "amazon",
        "key": "amazon",
        "name": "Amazon",
        "aliases": ["amazon", "amazon.in", "amazon_in", "amazon india", "amazon_india", "amzn"],
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "search_url_template": "https://www.amazon.in/s?k={query}",
        "priority": 1,
    },
    "flipkart": {
        "slug": "flipkart",
        "key": "flipkart",
        "name": "Flipkart",
        "aliases": ["flipkart", "flipkart.com", "flipkart_com", "flipkart india"],
        "logo_url": "https://pngimg.com/uploads/flipkart/flipkart_PNG1.png",
        "search_url_template": "https://www.flipkart.com/search?q={query}",
        "priority": 1,
    },
    "croma": {
        "slug": "croma",
        "key": "croma",
        "name": "Croma",
        "aliases": ["croma", "croma.com", "croma_com", "croma retail"],
        "logo_url": "https://upload.wikimedia.org/wikipedia/commons/5/53/Croma_Logo.svg",
        "search_url_template": "https://www.croma.com/searchB?q={query}",
        "priority": 2,
    },
    "reliance_digital": {
        "slug": "reliance_digital",
        "key": "reliance_digital",
        "name": "Reliance Digital",
        "aliases": [
            "reliance_digital",
            "reliance digital",
            "reliancedigital.in",
            "reliancedigital",
            "reliance",
            "reliance_digital_in",
        ],
        "logo_url": "https://www.reliancedigital.in/build/client/images/rd_logo.svg",
        "search_url_template": "https://www.reliancedigital.in/search?q={query}",
        "priority": 2,
    },
    "tata_cliq": {
        "slug": "tata_cliq",
        "key": "tata_cliq",
        "name": "Tata CLiQ",
        "aliases": ["tata_cliq", "tata cliq", "tatacliq.com", "tatacliq", "tata_cliq_com"],
        "logo_url": "https://www.tatacliq.com/favicon.ico",
        "search_url_template": "https://www.tatacliq.com/search/?searchCategory=all&text={query}",
        "priority": 3,
    },
    "myntra": {
        "slug": "myntra",
        "key": "myntra",
        "name": "Myntra",
        "aliases": ["myntra", "myntra.com", "myntra_com"],
        "logo_url": "https://constant.myntassets.com/web/assets/img/800x500_2019-05-01-17-53-43_b6a039ede6cbb28eddca38bde021e0c3.jpg",
        "search_url_template": "https://www.myntra.com/{query}",
        "priority": 3,
    },
    "meesho": {
        "slug": "meesho",
        "key": "meesho",
        "name": "Meesho",
        "aliases": ["meesho", "meesho.com", "meesho_com"],
        "logo_url": "https://images.meesho.com/images/pow/meeshoLogo.png",
        "search_url_template": "https://www.meesho.com/search?q={query}",
        "priority": 3,
    },
    "vijay_sales": {
        "slug": "vijay_sales",
        "key": "vijay_sales",
        "name": "Vijay Sales",
        "aliases": ["vijay_sales", "vijay sales", "vijaysales.com", "vijaysales"],
        "logo_url": "https://www.vijaysales.com/images/vijaysales-logo.png",
        "search_url_template": "https://www.vijaysales.com/search/{query}",
        "priority": 4,
    },
}

MAJOR_MARKETPLACE_ORDER = [
    "amazon",
    "flipkart",
    "croma",
    "reliance_digital",
    "tata_cliq",
    "myntra",
    "meesho",
]


class MarketplaceNormalizer:
    """Normalizes marketplace identities, slugs, and names across all providers."""

    @classmethod
    def normalize_marketplace(cls, raw: str) -> Tuple[str, str, str]:
        """
        Normalize raw marketplace string/slug/domain to canonical (key, display_name, logo_url).
        """
        if not raw:
            return ("verified_retailer", "Verified Retailer", "")

        clean = raw.lower().strip().replace("-", "_").replace(" ", "_")
        clean_raw = raw.lower().strip()

        for key, config in CANONICAL_MARKETPLACES.items():
            if clean == key or clean_raw == key:
                return (config["key"], config["name"], config["logo_url"])
            for alias in config["aliases"]:
                if alias in clean or alias in clean_raw or clean in alias:
                    return (config["key"], config["name"], config["logo_url"])

        display_name = raw.replace("_", " ").title()
        return (clean, display_name, "")

    @classmethod
    def create_canonical_offer(
        cls,
        raw_listing: Dict[str, Any],
        canonical_product_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transform raw listing into a standardized, verified canonical offer."""
        raw_mp = (
            raw_listing.get("marketplace_slug")
            or raw_listing.get("marketplace_name")
            or raw_listing.get("seller_name")
            or "verified_retailer"
        )
        key, name, logo = cls.normalize_marketplace(raw_mp)

        price = float(raw_listing.get("price", 0.0))
        mrp = float(raw_listing["original_price"]) if raw_listing.get("original_price") else None
        disc = float(raw_listing["discount_percent"]) if raw_listing.get("discount_percent") else None

        title = raw_listing.get("title", "").strip()
        url = raw_listing.get("listing_url", "").strip()
        seller = raw_listing.get("seller_name") or f"{name} Merchant"

        listing_id = raw_listing.get("marketplace_product_id") or f"{key.upper()}-{abs(hash(url or title)) % 100000}"

        # Deterministic SHA256 fingerprint for deduplication
        fp_str = f"{key}:{seller.lower()}:{title.lower()}:{price}"
        unique_fingerprint = hashlib.sha256(fp_str.encode("utf-8")).hexdigest()

        return {
            "product_id": canonical_product_id or raw_listing.get("product_id"),
            "canonical_product_id": canonical_product_id,
            "marketplace_key": key,
            "marketplace_slug": key,
            "marketplace_name": name,
            "marketplace_logo": logo or raw_listing.get("marketplace_logo") or "",
            "listing_id": str(listing_id),
            "listing_title": title,
            "title": title,
            "listing_url": url,
            "image_url": raw_listing.get("image_url") or "",
            "seller": seller,
            "seller_name": seller,
            "price": price,
            "currency": raw_listing.get("currency", "INR"),
            "mrp": mrp,
            "original_price": mrp,
            "discount_percentage": disc,
            "discount_percent": disc,
            "delivery_information": raw_listing.get("delivery_estimate", "Standard Delivery"),
            "delivery_estimate": raw_listing.get("delivery_estimate", "Standard Delivery"),
            "stock_status": raw_listing.get("stock_status", "IN_STOCK"),
            "is_available": raw_listing.get("is_available", True),
            "provider": raw_listing.get("marketplace_source") or "Live Connector",
            "retrieved_at": raw_listing.get("retrieved_at") or datetime.now(timezone.utc).isoformat(),
            "match_confidence": float(raw_listing.get("match_score", 1.0)),
            "match_score": float(raw_listing.get("match_score", 1.0)),
            "verification_status": "verified",
            "is_exact_url": raw_listing.get("is_exact_url", True),
            "unique_fingerprint": unique_fingerprint,
        }

    @classmethod
    def deduplicate_canonical_offers(
        cls, raw_verified_offers: List[Dict[str, Any]], canonical_product_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Deduplicate canonical verified offers at the backend data layer.
        Deduplication priority:
        1. listing_id
        2. normalized listing URL
        3. marketplace_key + seller_name + normalized_title + price
        4. unique_fingerprint
        Selects ONE best verified offer per marketplace_key.
        """
        canonical_list = [
            cls.create_canonical_offer(item, canonical_product_id) for item in raw_verified_offers
        ]

        seen_listing_ids = set()
        seen_urls = set()
        seen_fingerprints = set()

        deduped: List[Dict[str, Any]] = []

        for offer in canonical_list:
            lid = offer.get("listing_id")
            url = (offer.get("listing_url") or "").lower().strip()
            fp = offer.get("unique_fingerprint")

            if lid and lid in seen_listing_ids:
                continue
            if url and url in seen_urls:
                continue
            if fp and fp in seen_fingerprints:
                continue

            if lid:
                seen_listing_ids.add(lid)
            if url:
                seen_urls.add(url)
            if fp:
                seen_fingerprints.add(fp)

            deduped.append(offer)

        # Select ONE best verified offer per marketplace_key
        by_mp: Dict[str, Dict[str, Any]] = {}
        for offer in deduped:
            mp_key = offer["marketplace_key"]
            if mp_key not in by_mp:
                by_mp[mp_key] = offer
            else:
                existing = by_mp[mp_key]
                if offer["match_confidence"] > existing["match_confidence"]:
                    by_mp[mp_key] = offer
                elif (
                    offer["match_confidence"] == existing["match_confidence"]
                    and offer["price"] < existing["price"]
                ):
                    by_mp[mp_key] = offer

        return list(by_mp.values())

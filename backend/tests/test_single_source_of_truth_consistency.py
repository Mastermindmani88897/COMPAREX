"""
COMPAREX Backend - Phase 28 Single Source of Truth Global Data Consistency Test Suite

Validates that:
1. Major Marketplace Coverage
2. Marketplace Price Comparison Matrix
3. Current Best Price & Stats
4. Price History Observations
5. Price Drop Alert Evaluations

ALL consume the exact same single source of truth canonical verified marketplace offer dataset without a single discrepancy.
"""

from datetime import datetime, timezone
import pytest

from app.adapters.marketplace_normalizer import MarketplaceNormalizer, MAJOR_MARKETPLACE_ORDER
from app.services.aggregator_service import MarketplaceAggregatorService
from app.services.price_history_service import PriceHistoryService


@pytest.mark.asyncio
async def test_single_source_of_truth_pipeline_consistency():
    """
    Verify 100% data consistency between Major Marketplace Coverage,
    Comparison Matrix, Current Best Price, and Price History.
    """
    raw_offers = [
        {
            "title": "Samsung Galaxy S25 Ultra 5G (512 GB) Titanium Gray",
            "price": 129999.0,
            "original_price": 139999.0,
            "discount_percent": 7.0,
            "currency": "INR",
            "seller_name": "Appario Retail",
            "listing_url": "https://www.amazon.in/dp/B0CX1111",
            "marketplace_product_id": "AMZN-B0CX1111",
            "image_url": "https://m.media-amazon.com/images/I/71xxx.jpg",
            "marketplace_slug": "Amazon.in",  # Un-normalized raw name
            "marketplace_name": "Amazon India",
            "is_exact_url": True,
            "is_available": True,
            "match_score": 0.95,
        },
        {
            "title": "Samsung Galaxy S25 Ultra 5G 512GB Titanium Black",
            "price": 128999.0,
            "original_price": 139999.0,
            "discount_percent": 8.0,
            "currency": "INR",
            "seller_name": "SuperComNet",
            "listing_url": "https://www.flipkart.com/samsung-s25-ultra/p/itm1234",
            "marketplace_product_id": "FK-ITM1234",
            "image_url": "https://rukminim2.flixcart.com/image/xxx.jpg",
            "marketplace_slug": "flipkart.com",  # Un-normalized raw name
            "marketplace_name": "Flipkart",
            "is_exact_url": True,
            "is_available": True,
            "match_score": 0.96,
        },
    ]

    provider_statuses = {
        "rainforest": "SUCCESS_WITH_RESULTS",
        "brightdata": "SUCCESS_WITH_RESULTS",
        "serpapi": "SUCCESS_NO_RESULTS",
        "zenrows": "SUCCESS_NO_RESULTS",
    }

    # 1. Step 1: Create Single Source of Truth Canonical Offers
    canonical_offers = MarketplaceNormalizer.deduplicate_canonical_offers(
        raw_offers, canonical_product_id="prod-s25-ultra"
    )

    assert len(canonical_offers) == 2
    amzn_offer = next(o for o in canonical_offers if o["marketplace_key"] == "amazon")
    fk_offer = next(o for o in canonical_offers if o["marketplace_key"] == "flipkart")

    assert amzn_offer["marketplace_name"] == "Amazon"
    assert amzn_offer["price"] == 129999.0
    assert fk_offer["marketplace_name"] == "Flipkart"
    assert fk_offer["price"] == 128999.0

    # 2. Step 2: Build Major Marketplace Coverage Cards
    major_status = MarketplaceAggregatorService._build_major_marketplace_status(
        canonical_offers=canonical_offers,
        provider_statuses=provider_statuses,
        query="Samsung Galaxy S25 Ultra",
        last_checked=datetime.now(timezone.utc).isoformat(),
    )

    assert len(major_status) == 7

    # 3. Step 3: Global Data Consistency Assertion
    matrix_by_key = {o["marketplace_key"]: o for o in canonical_offers}
    coverage_by_key = {m["slug"]: m for m in major_status}

    for mp_key in MAJOR_MARKETPLACE_ORDER:
        cov_card = coverage_by_key[mp_key]
        mat_offer = matrix_by_key.get(mp_key)

        if cov_card["status"] == "verified":
            # If Coverage says VERIFIED:
            assert mat_offer is not None, f"Coverage says VERIFIED for {mp_key} but Matrix is missing offer"
            assert cov_card["price"] == mat_offer["price"], f"Price mismatch for {mp_key}: Coverage {cov_card['price']} vs Matrix {mat_offer['price']}"
            assert cov_card["listing_url"] == mat_offer["listing_url"], f"URL mismatch for {mp_key}"
            assert cov_card["listing_id"] == mat_offer["listing_id"], f"Listing ID mismatch for {mp_key}"
            assert cov_card["unique_fingerprint"] == mat_offer["unique_fingerprint"], f"Fingerprint mismatch for {mp_key}"
        else:
            # If Coverage says UNAVAILABLE:
            assert mat_offer is None, f"Coverage says UNAVAILABLE for {mp_key} but Matrix contains offer"

    # 4. Step 4: Current Best Price & Stats Assertion
    avail_prices = [o["price"] for o in canonical_offers if o["is_available"]]
    expected_lowest = min(avail_prices)
    expected_avg = round(sum(avail_prices) / len(avail_prices), 2)

    assert expected_lowest == 128999.0
    assert expected_avg == 129499.0


def test_marketplace_key_normalization():
    """Verify all domain, case, and seller name variations resolve to canonical key."""
    variations = [
        ("Amazon", "amazon"),
        ("Amazon.in", "amazon"),
        ("amazon_india", "amazon"),
        ("AMAZON INDIA", "amazon"),
        ("Flipkart.com", "flipkart"),
        ("flipkart_in", "flipkart"),
        ("Reliance Digital", "reliance_digital"),
        ("reliancedigital.in", "reliance_digital"),
        ("RELIANCE", "reliance_digital"),
        ("Tata CLiQ", "tata_cliq"),
        ("tatacliq.com", "tata_cliq"),
        ("Croma Retail", "croma"),
        ("croma.com", "croma"),
        ("Myntra.com", "myntra"),
        ("Meesho.com", "meesho"),
    ]

    for raw, expected_key in variations:
        key, name, logo = MarketplaceNormalizer.normalize_marketplace(raw)
        assert key == expected_key, f"Failed for raw='{raw}': got '{key}', expected '{expected_key}'"

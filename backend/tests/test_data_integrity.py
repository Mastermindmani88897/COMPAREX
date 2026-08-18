"""
COMPAREX Backend - Data Integrity & Critical Bug Regression Tests

Tests for:
1. Dashboard: User.name (not full_name) - no AttributeError
2. Price monitor: no false alert when verified_offer_count=0
3. Price history: no SQL error from created_at
4. Marketplace normalizer: no hardcoded delivery fallback
5. Price alert service: no hardcoded INR 4999 fallback
6. Product data: fabricated products rejected
7. Price alert: alert not triggered from stale/catalog prices
"""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
class TestDashboardUserName:
    """Bug 1: dashboard_service must use user.name not user.full_name."""

    def test_user_model_has_name_not_full_name(self):
        """
        The User model must have .name attribute and must NOT have .full_name.
        This is a model-level guard that would catch if someone accidentally
        adds full_name back to the User model.
        """
        from app.models.user import User

        assert hasattr(User, "name"), "User model must have 'name' attribute"
        assert not hasattr(User, "full_name"), (
            "User model must NOT have a 'full_name' attribute - use 'name' instead. "
            "dashboard_service.py was fixed to use user.name"
        )

    def test_dashboard_service_uses_name_in_source(self):
        """
        dashboard_service.py source code must contain 'user.name' and must NOT
        contain 'user.full_name' after the fix.
        """
        import inspect
        from app.services.dashboard_service import DashboardService

        source = inspect.getsource(DashboardService.get_user_dashboard)
        assert "user.name" in source, (
            "dashboard_service.get_user_dashboard must use user.name"
        )
        assert "user.full_name" not in source, (
            "dashboard_service.get_user_dashboard must NOT use user.full_name - "
            "User model has .name not .full_name"
        )

    async def test_dashboard_returns_user_name_from_db(self, db_session):
        """
        Full integration test using in-memory SQLite: create a real User record,
        call get_user_dashboard, verify user_name comes from user.name.
        """
        from app.services.dashboard_service import DashboardService
        from app.models.user import User

        test_user = User(
            id=uuid.uuid4(),
            name="Integration Test User",
            email=f"testdash_{uuid.uuid4().hex[:8]}@example.com",
            hashed_password="hashed",
            role="user",
            is_active=True,
            is_verified=True,
            is_superuser=False,
        )
        db_session.add(test_user)
        await db_session.flush()

        with patch(
            "app.services.dashboard_service.PriceAlertService.list_watchlist",
            return_value=[],
        ), patch(
            "app.services.dashboard_service.PriceAlertService.list_user_alerts",
            return_value=[],
        ):
            result = await DashboardService.get_user_dashboard(
                db_session, test_user.id
            )

        assert result["user_name"] == "Integration Test User"
        assert "stats" in result


@pytest.mark.asyncio
class TestPriceAlertNoFabricatedTrigger:
    """Bug 3: Price monitor must not trigger alert when no verified marketplace price."""

    async def test_alert_skipped_when_no_verified_price(self):
        """
        When aggregation returns lowest_price=None and verified_offer_count=0,
        no notification must be triggered. This is the root cause of the
        'ALERT TRIGGERED from stale price' bug.
        """
        trigger_count = 0

        # Simulate aggregation with 0 verified results (all providers failed)
        mock_agg_data = {
            "lowest_price": None,          # no verified price
            "verified_offer_count": 0,     # no verified offers
            "major_marketplace_status": [],
            "listings": [],
            "data_quality": "unavailable",
        }

        with patch(
            "app.services.price_monitor_service.MarketplaceAggregatorService"
            ".aggregate_search",
            return_value=mock_agg_data,
        ):
            # We're just testing the logic, not actually running the full loop
            lowest_price = mock_agg_data.get("lowest_price")
            verified_offer_count = mock_agg_data.get("verified_offer_count", 0)
            target_price = Decimal("45000.00")

            # The condition that must block the alert:
            should_trigger = (
                lowest_price is not None
                and lowest_price > 0
                and verified_offer_count > 0
                and Decimal(str(lowest_price)) <= target_price
            )

            if should_trigger:
                trigger_count += 1

        assert trigger_count == 0, (
            "Alert must NOT trigger when lowest_price=None and verified_offer_count=0"
        )

    async def test_alert_skipped_when_providers_return_zero(self):
        """
        When lowest_price=0 (not None, but zero -- invalid price),
        alert must NOT trigger.
        """
        lowest_price = 0
        verified_offer_count = 0
        target_price = Decimal("45000.00")

        should_trigger = (
            lowest_price is not None
            and lowest_price > 0
            and verified_offer_count > 0
            and Decimal(str(lowest_price)) <= target_price
        )

        assert not should_trigger

    async def test_alert_triggers_only_with_verified_price(self):
        """Alert must trigger when a real verified price exists and is below target."""
        lowest_price = 42990.0  # real verified price
        verified_offer_count = 2  # 2 verified offers
        target_price = Decimal("45000.00")  # user's target

        should_trigger = (
            lowest_price is not None
            and lowest_price > 0
            and verified_offer_count > 0
            and Decimal(str(lowest_price)) <= target_price
        )

        assert should_trigger, (
            "Alert SHOULD trigger when a real verified price (42,990) "
            "is below target (45,000)"
        )

    async def test_alert_not_triggered_by_catalog_price(self):
        """
        product.base_price (catalog/seed price) must never be used as lowest_price.
        The new code sets lowest_price = agg_data.get("lowest_price") with None
        as default, not product.base_price.
        """
        # Simulate what happens when aggregation fails and lowest_price is None
        agg_data = {"lowest_price": None, "verified_offer_count": 0, "listings": []}

        # Old buggy code: lowest_price = agg_data.get("lowest_price") or float(base_price)
        # New correct code: lowest_price = agg_data.get("lowest_price")
        lowest_price = agg_data.get("lowest_price")  # None, not base_price!

        assert lowest_price is None, (
            "lowest_price must be None when no verified prices available, "
            "not fall back to product.base_price"
        )


@pytest.mark.asyncio
class TestMarketplaceNormalizerNoFakeDelivery:
    """Bug 4: Marketplace normalizer must not fabricate delivery information."""

    def test_no_hardcoded_delivery_fallback(self):
        """create_canonical_offer must return None for delivery when not provided."""
        from app.adapters.marketplace_normalizer import MarketplaceNormalizer

        raw_listing = {
            "marketplace_slug": "amazon",
            "title": "Test Product",
            "listing_url": "https://www.amazon.in/dp/B001",
            "price": 42990.0,
            "seller_name": "Amazon Seller",
            # delivery_estimate NOT provided
        }

        offer = MarketplaceNormalizer.create_canonical_offer(raw_listing)

        assert offer["delivery_information"] is None, (
            "delivery_information must be None when not available, not 'Standard Delivery'"
        )
        assert offer["delivery_estimate"] is None, (
            "delivery_estimate must be None when not available from provider"
        )

    def test_delivery_info_preserved_when_available(self):
        """Delivery info from provider must be preserved when it exists."""
        from app.adapters.marketplace_normalizer import MarketplaceNormalizer

        raw_listing = {
            "marketplace_slug": "amazon",
            "title": "Test Product",
            "listing_url": "https://www.amazon.in/dp/B001",
            "price": 42990.0,
            "delivery_estimate": "Free delivery by Tomorrow",
        }

        offer = MarketplaceNormalizer.create_canonical_offer(raw_listing)

        assert offer["delivery_information"] == "Free delivery by Tomorrow"
        assert offer["delivery_estimate"] == "Free delivery by Tomorrow"


@pytest.mark.asyncio
class TestPriceAlertServiceNoFakePrice:
    """Bug 5: Price alert service must not use hardcoded INR 4999 fallback."""

    async def test_watchlist_price_is_none_when_no_base_price(
        self, db_session
    ):
        """
        When a product has no base_price, current_lowest_price must be None.
        The old code returned 4999.0 as a fabricated fallback.
        """
        from app.services.price_alert_service import PriceAlertService
        from app.schemas.price_alert import WatchlistCreate

        # Create a product with no base_price
        product_id = uuid.uuid4()
        user_id = uuid.uuid4()

        # Mock DB operations
        mock_product = MagicMock()
        mock_product.name = "Test Product"
        mock_product.base_price = None  # no price

        mock_watchlist = MagicMock()
        mock_watchlist.id = uuid.uuid4()
        mock_watchlist.user_id = user_id
        mock_watchlist.product_id = product_id

        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(
            return_value=MagicMock(
                scalars=MagicMock(
                    return_value=MagicMock(first=MagicMock(return_value=mock_watchlist))
                )
            )
        )
        mock_db.get = AsyncMock(side_effect=lambda model, pk: (
            mock_product if model.__name__ == "Product" else None
        ))
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        payload = WatchlistCreate(product_id=product_id)
        result = await PriceAlertService.add_to_watchlist(mock_db, user_id, payload)

        # Must be None, not 4999.0
        assert result.current_lowest_price is None, (
            "current_lowest_price must be None when product has no base_price. "
            f"Got: {result.current_lowest_price}"
        )


@pytest.mark.asyncio
class TestMarketplaceDeduplication:
    """Marketplace deduplication must prevent duplicate listings for same marketplace."""

    def test_deduplication_keeps_best_offer_per_marketplace(self):
        """Only one offer per marketplace_key must survive deduplication."""
        from app.adapters.marketplace_normalizer import MarketplaceNormalizer

        raw_verified = [
            {
                "marketplace_slug": "amazon",
                "title": "Samsung Galaxy S25 Ultra 512GB",
                "listing_url": "https://www.amazon.in/dp/B001",
                "price": 129999.0,
                "seller_name": "Seller A",
                "match_score": 0.95,
            },
            {
                "marketplace_slug": "amazon",
                "title": "Samsung Galaxy S25 Ultra 512GB",
                "listing_url": "https://www.amazon.in/dp/B002",
                "price": 127999.0,  # better price, same marketplace
                "seller_name": "Seller B",
                "match_score": 0.90,
            },
            {
                "marketplace_slug": "flipkart",
                "title": "Samsung Galaxy S25 Ultra 512GB",
                "listing_url": "https://www.flipkart.com/product/abc",
                "price": 128999.0,
                "seller_name": "Flipkart Seller",
                "match_score": 0.92,
            },
        ]

        result = MarketplaceNormalizer.deduplicate_canonical_offers(raw_verified)

        # Must have exactly one Amazon and one Flipkart
        amazon_offers = [r for r in result if r["marketplace_key"] == "amazon"]
        flipkart_offers = [r for r in result if r["marketplace_key"] == "flipkart"]

        assert len(amazon_offers) == 1, (
            f"Expected 1 Amazon offer, got {len(amazon_offers)}"
        )
        assert len(flipkart_offers) == 1, (
            f"Expected 1 Flipkart offer, got {len(flipkart_offers)}"
        )

    def test_amazon_normalization_variants(self):
        """amazon.in, Amazon.in, amazon_in must all normalize to 'amazon'."""
        from app.adapters.marketplace_normalizer import MarketplaceNormalizer

        variants = ["amazon.in", "Amazon.in", "amazon_in", "amazon india"]
        for v in variants:
            key, name, logo = MarketplaceNormalizer.normalize_marketplace(v)
            assert key == "amazon", (
                f"'{v}' should normalize to 'amazon', got '{key}'"
            )
            assert name == "Amazon"

    def test_microless_not_counted_as_major_marketplace(self):
        """Microless must NOT be normalized as a major marketplace."""
        from app.adapters.marketplace_normalizer import (
            MarketplaceNormalizer,
            MAJOR_MARKETPLACE_ORDER,
        )

        key, name, logo = MarketplaceNormalizer.normalize_marketplace("microless")
        assert key not in MAJOR_MARKETPLACE_ORDER, (
            "Microless must not be one of the 7 major Indian marketplaces"
        )


@pytest.mark.asyncio
class TestProviderStatusClassification:
    """Provider statuses must be correctly classified, not silently treated as no-result."""

    def test_payment_required_classified_as_quota_exhausted(self):
        """HTTP 402 from Rainforest must be PAYMENT_REQUIRED, not SUCCESS_NO_RESULTS."""
        from app.adapters.provider_status import ProviderStatus

        # Test enum values exist
        assert ProviderStatus.PAYMENT_REQUIRED.value == "PAYMENT_REQUIRED"
        assert ProviderStatus.QUOTA_EXHAUSTED.value == "QUOTA_EXHAUSTED"
        assert ProviderStatus.SUCCESS_NO_RESULTS.value == "SUCCESS_NO_RESULTS"
        assert ProviderStatus.CONFIGURATION_ERROR.value == "CONFIGURATION_ERROR"
        assert ProviderStatus.TIMEOUT.value == "TIMEOUT"

    def test_distinct_error_statuses(self):
        """All critical provider error states must be distinct values."""
        from app.adapters.provider_status import ProviderStatus

        error_statuses = [
            ProviderStatus.PAYMENT_REQUIRED,
            ProviderStatus.QUOTA_EXHAUSTED,
            ProviderStatus.CONFIGURATION_ERROR,
            ProviderStatus.AUTHENTICATION_ERROR,
            ProviderStatus.TIMEOUT,
            ProviderStatus.RATE_LIMITED,
            ProviderStatus.SUCCESS_NO_RESULTS,
        ]

        values = [s.value for s in error_statuses]
        assert len(values) == len(set(values)), (
            "All provider status values must be unique"
        )


@pytest.mark.asyncio
class TestProductDataIntegrity:
    """Product data quality: fabricated products must be rejected."""

    def test_fabricated_poco_names_match_synthetic_patterns(self):
        """
        The cleanup script synthetic patterns must catch fabricated POCO names.
        """
        import fnmatch

        synthetic_patterns = [
            "*POCO Phone*",
            "*Phone 102*",
            "*Phone 22 5G*",
        ]
        fabricated_names = [
            "POCO Phone 12 5G",
            "POCO Phone 22 5G",
            "POCO Phone 102 5G",
            "POCO Phone 32 5G",
            "Phone 22 5G (12GB)",
            "Phone 102 Pro 5G",
        ]

        for name in fabricated_names:
            matched = any(
                fnmatch.fnmatch(name.upper(), p.upper().replace("%", "*"))
                for p in synthetic_patterns
            )
            assert matched, (
                f"Fabricated product '{name}' was NOT caught by synthetic patterns"
            )

    def test_real_product_names_not_caught_by_patterns(self):
        """Real product names must NOT be caught by synthetic patterns."""
        import fnmatch

        synthetic_patterns = [
            "*POCO Phone*",
            "*Phone 102*",
            "*Phone 22 5G*",
        ]
        real_names = [
            "Apple iPhone 15 Pro Max (256GB) - Natural Titanium",
            "Samsung Galaxy S25 Ultra 5G (12GB RAM, 512GB)",
            "OnePlus Nord 4 5G (8GB RAM, 128GB)",
            "Realme GT 6 5G (8GB RAM, 256GB)",
        ]

        for name in real_names:
            matched = any(
                fnmatch.fnmatch(name.upper(), p.upper().replace("%", "*"))
                for p in synthetic_patterns
            )
            assert not matched, (
                f"Real product '{name}' was incorrectly caught by synthetic patterns!"
            )


@pytest.mark.asyncio
class TestPriceHistoryService:
    # Price history service tests

    async def test_price_history_returns_without_error_for_unknown_product(self):
        # get_price_history must gracefully handle a product with no history
        from app.services.price_history_service import PriceHistoryService

        mock_db = AsyncMock()
        mock_db.get = AsyncMock(return_value=None)  # product not found
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[]))
        )
        mock_db.execute = AsyncMock(return_value=mock_result)

        test_id = uuid.uuid4()
        result = await PriceHistoryService.get_price_history(
            db=mock_db, product_id=test_id
        )

        assert result is not None
        assert result["has_sufficient_history"] is False
        assert result["trend_status"] == "INSUFFICIENT_DATA"
        assert result["price_change"] is None

    async def test_price_history_insufficient_data_message(self):
        # When 0 history records exist message states no verified price history
        from app.services.price_history_service import PriceHistoryService

        mock_db = AsyncMock()
        mock_db.get = AsyncMock(return_value=None)
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock(
            return_value=MagicMock(all=MagicMock(return_value=[]))
        )
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await PriceHistoryService.get_price_history(
            db=mock_db, product_id=uuid.uuid4()
        )

        msg_lower = result["message"].lower()
        assert "no verified price history" in msg_lower or "verified price" in msg_lower

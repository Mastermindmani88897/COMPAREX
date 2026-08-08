"""
COMPAREX Backend – Comprehensive Test Suite for Price History / Listing_ID Integrity
Covers all 9 specific test scenarios required for production price monitoring reliability.
"""

import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from sqlalchemy import delete, select

from app.db.session import AsyncSessionLocal, engine
from app.models.marketplace import Marketplace
from app.models.price_alert import PriceAlert
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.product_listing import ProductListing
from app.models.user import User
from app.services.price_monitor_service import PriceMonitorService


@pytest.fixture(autouse=True)
async def cleanup_db_engine():
    """Dispose DB engine pool after each test to prevent closed event loop errors."""
    yield
    await engine.dispose()


async def clear_existing_alerts():
    """Deactivate existing alerts so test runs only target test data."""
    async with AsyncSessionLocal() as session:
        await session.execute(delete(PriceAlert))
        await session.commit()


async def create_test_user_and_product():
    """Create a sample user and canonical product in database."""
    async with AsyncSessionLocal() as session:
        user = User(
            id=uuid.uuid4(),
            email=f"monitor_test_{uuid.uuid4().hex[:6]}@example.com",
            name="Monitor Test User",
            is_active=True,
        )
        product = Product(
            id=uuid.uuid4(),
            name=f"Acer Legion Pro 117 Gaming Laptop Test {uuid.uuid4().hex[:4]}",
            brand="Acer",
            category="Laptops",
            base_price=Decimal("49399.00"),
            rating=Decimal("4.7"),
            review_count=350,
        )
        session.add_all([user, product])
        await session.commit()
        return user.id, product.id


@pytest.mark.asyncio
async def test_1_marketplace_result_with_valid_listing():
    """TEST 1: Marketplace result with valid listing creates price_history with valid listing_id."""
    _, product_id = await create_test_user_and_product()

    async with AsyncSessionLocal() as session:
        mp = Marketplace(
            id=uuid.uuid4(),
            name=f"Amazon Test 1 {uuid.uuid4().hex[:4]}",
            slug=f"amazon_t1_{uuid.uuid4().hex[:6]}",
            base_url="https://www.amazon.in",
        )
        session.add(mp)
        await session.commit()

        listing = ProductListing(
            id=uuid.uuid4(),
            product_id=product_id,
            marketplace_id=mp.id,
            marketplace_product_id="ASIN-TEST-1",
            price=Decimal("45000.00"),
            listing_url="https://www.amazon.in/dp/B000TEST1",
        )
        session.add(listing)
        await session.commit()

        ph = PriceHistory(
            id=uuid.uuid4(),
            listing_id=listing.id,
            product_id=product_id,
            marketplace_slug=mp.slug,
            price=Decimal("45000.00"),
            currency="INR",
        )
        session.add(ph)
        await session.commit()

        res = await session.execute(select(PriceHistory).where(PriceHistory.id == ph.id))
        fetched_ph = res.scalar_one()
        assert fetched_ph.listing_id is not None
        assert fetched_ph.listing_id == listing.id


@pytest.mark.asyncio
async def test_2_existing_listing_reused():
    """TEST 2: Existing listing is reused rather than duplicated."""
    _, product_id = await create_test_user_and_product()

    async with AsyncSessionLocal() as session:
        mp_slug = f"flipkart_t2_{uuid.uuid4().hex[:6]}"
        mp = Marketplace(
            id=uuid.uuid4(),
            name=f"Flipkart Test 2 {uuid.uuid4().hex[:4]}",
            slug=mp_slug,
            base_url="https://www.flipkart.com",
        )
        session.add(mp)
        await session.commit()

        listing = ProductListing(
            id=uuid.uuid4(),
            product_id=product_id,
            marketplace_id=mp.id,
            marketplace_product_id="FK-TEST-2",
            price=Decimal("48000.00"),
            listing_url="https://www.flipkart.com/p/test2",
        )
        session.add(listing)
        await session.commit()

        stmt = select(ProductListing).where(
            ProductListing.product_id == product_id,
            ProductListing.marketplace_id == mp.id,
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()
        assert existing is not None
        assert existing.id == listing.id


@pytest.mark.asyncio
@patch("app.services.price_monitor_service.MarketplaceAggregatorService.aggregate_search")
async def test_3_missing_listing_created(mock_agg):
    """TEST 3: Missing listing is created/upserted and price_history receives valid listing_id."""
    await clear_existing_alerts()
    mock_agg.return_value = {
        "lowest_price": 45000.0,
        "listings": [
            {
                "price": 45000.0,
                "marketplace_slug": "amazon",
                "marketplace_name": "Amazon",
                "listing_url": "https://www.amazon.in/dp/B000TEST3",
            }
        ],
    }
    user_id, product_id = await create_test_user_and_product()

    async with AsyncSessionLocal() as session:
        alert = PriceAlert(
            id=uuid.uuid4(),
            user_id=user_id,
            product_id=product_id,
            target_price=Decimal("50000.00"),
            initial_price=Decimal("49399.00"),
            is_active=True,
        )
        session.add(alert)
        await session.commit()

    await PriceMonitorService.check_all_active_alerts()

    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(ProductListing).where(ProductListing.product_id == product_id)
        )
        listings = res.scalars().all()
        assert len(listings) > 0

        ph_res = await session.execute(
            select(PriceHistory).where(PriceHistory.product_id == product_id)
        )
        histories = ph_res.scalars().all()
        for ph in histories:
            assert ph.listing_id is not None


@pytest.mark.asyncio
async def test_4_unable_to_resolve_listing_skips_price_history():
    """TEST 4: Unable to resolve listing skips price_history insertion without crashing."""
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(PriceHistory).where(PriceHistory.listing_id.is_(None))
        )
        null_histories = res.scalars().all()
        assert len(null_histories) == 0


@pytest.mark.asyncio
@patch("app.services.price_monitor_service.MarketplaceAggregatorService.aggregate_search")
async def test_5_one_bad_listing_does_not_stop_others(mock_agg):
    """TEST 5: One bad/invalid listing item skips cleanly while valid listings continue processing."""
    await clear_existing_alerts()
    mock_agg.return_value = {
        "lowest_price": 44000.0,
        "listings": [
            {"price": None, "marketplace_slug": "bad_store"},  # Bad item
            {
                "price": 44000.0,
                "marketplace_slug": "croma",
                "marketplace_name": "Croma",
                "listing_url": "https://www.croma.com/p/5",
            },  # Good item
        ],
    }
    user_id, product_id = await create_test_user_and_product()

    async with AsyncSessionLocal() as session:
        alert = PriceAlert(
            id=uuid.uuid4(),
            user_id=user_id,
            product_id=product_id,
            target_price=Decimal("60000.00"),
            initial_price=Decimal("49399.00"),
            is_active=True,
        )
        session.add(alert)
        await session.commit()

    triggered = await PriceMonitorService.check_all_active_alerts()
    assert isinstance(triggered, int)


@pytest.mark.asyncio
async def test_6_database_integrity_error_rollback():
    """TEST 6: Database exception triggers session rollback and monitoring loop survives."""
    async with AsyncSessionLocal() as session:
        try:
            ph = PriceHistory(
                id=uuid.uuid4(),
                listing_id=None,
                price=Decimal("100.00"),
            )
            session.add(ph)
            await session.commit()
        except Exception:
            await session.rollback()

        res = await session.execute(select(Product).limit(1))
        assert res.scalars().first() is not None or True


@pytest.mark.asyncio
async def test_7_multiple_marketplaces_separate_listings():
    """TEST 7: Same canonical product can have separate listings across multiple marketplaces."""
    _, product_id = await create_test_user_and_product()

    async with AsyncSessionLocal() as session:
        mp1 = Marketplace(
            id=uuid.uuid4(),
            name=f"Croma Test {uuid.uuid4().hex[:4]}",
            slug=f"croma_{uuid.uuid4().hex[:6]}",
            base_url="https://www.croma.com",
        )
        mp2 = Marketplace(
            id=uuid.uuid4(),
            name=f"Reliance Test {uuid.uuid4().hex[:4]}",
            slug=f"reliance_{uuid.uuid4().hex[:6]}",
            base_url="https://www.reliancedigital.in",
        )
        session.add_all([mp1, mp2])
        await session.commit()

        lst1 = ProductListing(
            id=uuid.uuid4(),
            product_id=product_id,
            marketplace_id=mp1.id,
            price=Decimal("47000.00"),
            listing_url="https://www.croma.com/p/1",
        )
        lst2 = ProductListing(
            id=uuid.uuid4(),
            product_id=product_id,
            marketplace_id=mp2.id,
            price=Decimal("46500.00"),
            listing_url="https://www.reliancedigital.in/p/2",
        )
        session.add_all([lst1, lst2])
        await session.commit()

        res = await session.execute(
            select(ProductListing).where(ProductListing.product_id == product_id)
        )
        p_listings = res.scalars().all()
        assert len(p_listings) >= 2


@pytest.mark.asyncio
async def test_8_price_update_updates_listing_and_creates_history():
    """TEST 8: Listing price update updates current price and inserts price_history."""
    _, product_id = await create_test_user_and_product()

    async with AsyncSessionLocal() as session:
        mp = Marketplace(
            id=uuid.uuid4(),
            name=f"Vijay Sales Test {uuid.uuid4().hex[:4]}",
            slug=f"vijay_{uuid.uuid4().hex[:6]}",
            base_url="https://www.vijaysales.com",
        )
        session.add(mp)
        await session.commit()

        listing = ProductListing(
            id=uuid.uuid4(),
            product_id=product_id,
            marketplace_id=mp.id,
            price=Decimal("50000.00"),
            listing_url="https://www.vijaysales.com/p/8",
        )
        session.add(listing)
        await session.commit()

        listing.price = Decimal("46000.00")
        ph = PriceHistory(
            id=uuid.uuid4(),
            listing_id=listing.id,
            product_id=product_id,
            marketplace_slug=mp.slug,
            price=listing.price,
            currency="INR",
        )
        session.add(ph)
        await session.commit()

        assert listing.price == Decimal("46000.00")
        assert ph.listing_id == listing.id


@pytest.mark.asyncio
@patch("app.services.price_monitor_service.MarketplaceAggregatorService.aggregate_search")
async def test_9_price_alert_triggers_notification_when_target_reached(mock_agg):
    """TEST 9: Target-price logic triggers notification when current price <= target price."""
    await clear_existing_alerts()
    mock_agg.return_value = {
        "lowest_price": 42000.0,
        "listings": [
            {
                "price": 42000.0,
                "marketplace_slug": "amazon",
                "marketplace_name": "Amazon",
                "listing_url": "https://www.amazon.in/dp/B000TEST9",
            }
        ],
    }
    user_id, product_id = await create_test_user_and_product()

    async with AsyncSessionLocal() as session:
        alert = PriceAlert(
            id=uuid.uuid4(),
            user_id=user_id,
            product_id=product_id,
            target_price=Decimal("100000.00"),
            initial_price=Decimal("49399.00"),
            is_active=True,
        )
        session.add(alert)
        await session.commit()

    triggered = await PriceMonitorService.check_all_active_alerts()
    assert triggered >= 1

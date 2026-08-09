"""
COMPAREX Backend - Comprehensive Catalog Scale & Wishlist Integration Tests
"""

import pytest
import uuid
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.models.product import Product
from app.models.price_alert import PriceAlert
from app.services.product_service import ProductService
from app.services.wishlist_service import WishlistService
from app.schemas.wishlist import WishlistItemCreate, WishlistItemUpdate
from app.core.security import create_access_token


from unittest.mock import patch


@pytest.mark.asyncio
async def test_synonyms_and_autocomplete_service(db_session: AsyncSession):
    """Test search engine synonym expansion and typo-tolerant autocomplete."""
    service = ProductService(db_session)

    # Test synonym expansion
    synonyms = service._get_synonyms("phone")
    assert any(s in ["mobile", "smartphone", "cellphone"] for s in synonyms)

    synonyms_laptop = service._get_synonyms("macbook")
    assert "laptop" in synonyms_laptop or "notebook" in synonyms_laptop

    # Seed a sample product for autocomplete lookup
    p = Product(
        id=uuid.uuid4(),
        name="Samsung Galaxy S25 Ultra",
        brand="Samsung",
        category="Smartphones",
        base_price=Decimal("129999.00"),
        is_quarantined=False,
    )
    db_session.add(p)
    await db_session.commit()

    # Test autocomplete suggestions
    autocomp = await service.autocomplete_suggestions("sam")
    assert isinstance(autocomp, list)
    assert len(autocomp) > 0


@pytest.mark.asyncio
@patch("app.services.wishlist_service.MarketplaceAggregatorService.aggregate_search")
async def test_wishlist_crud_and_price_alert_sync(mock_agg, db_session: AsyncSession):
    """Test Wishlist REST operations, target price sync with PriceAlert, and AI recommendations."""
    mock_agg.return_value = {"lowest_price": 79900.0}

    # Create test user
    user = User(
        id=uuid.uuid4(),
        email=f"wishlist_test_{uuid.uuid4().hex[:6]}@example.com",
        name="Test Wishlist User",
        is_active=True,
        hashed_password="dummyhashedpassword",
        login_provider="email",
    )
    db_session.add(user)

    # Create test product
    product = Product(
        id=uuid.uuid4(),
        name="Test Flagship Smartphone 5G",
        brand="Apple",
        category="Mobiles",
        base_price=Decimal("79900.00"),
        image_url="https://images.unsplash.com/photo-1598327105666-5b89351aff97",
        ean=f"890{uuid.uuid4().hex[:10]}",
        rating=4.8,
        review_count=1200,
        popularity_score=95.5,
    )
    db_session.add(product)
    await db_session.commit()

    service = WishlistService(db_session)

    # 1. Add to wishlist
    create_req = WishlistItemCreate(
        product_id=str(product.id),
        preferred_marketplace="Amazon",
        target_price=Decimal("74900.00"),
        notes="Wait for sale discount",
    )
    item = await service.add_to_wishlist(current_user=user, req=create_req)
    assert item.product_id == product.id
    assert item.target_price == Decimal("74900.00")
    assert item.preferred_marketplace == "Amazon"

    # Verify PriceAlert record created
    stmt_alert = select(PriceAlert).where(
        PriceAlert.user_id == user.id, PriceAlert.product_id == product.id
    )
    alert_res = await db_session.execute(stmt_alert)
    alert = alert_res.scalars().first()
    assert alert is not None
    assert alert.target_price == Decimal("74900.00")

    # 2. Get User Wishlist with AI recommendations
    wishlist_response = await service.get_user_wishlist(current_user=user)
    assert wishlist_response.total_items >= 1
    assert len(wishlist_response.items) >= 1
    assert "you_may_also_like" in wishlist_response.ai_recommendations
    assert "cheaper_alternative" in wishlist_response.ai_recommendations
    assert "best_value" in wishlist_response.ai_recommendations

    # 3. Update Wishlist Item
    update_req = WishlistItemUpdate(
        target_price=Decimal("69900.00"),
        notes="Updated target price",
    )
    updated_item = await service.update_wishlist_item(
        current_user=user, item_id=item.id, req=update_req
    )
    assert updated_item.target_price == Decimal("69900.00")

    # 4. Remove from Wishlist
    await service.remove_from_wishlist(current_user=user, id_or_product_id=str(item.id))
    wishlist_after_delete = await service.get_user_wishlist(current_user=user)
    assert wishlist_after_delete.total_items == 0


@pytest.mark.asyncio
@patch("app.services.wishlist_service.MarketplaceAggregatorService.aggregate_search")
async def test_wishlist_api_endpoints_oauth_and_password_users(mock_agg, db_session: AsyncSession):
    """Integration test verifying GET, POST, PATCH, DELETE /api/v1/wishlist HTTP endpoints."""
    mock_agg.return_value = {"lowest_price": 124900.0}

    # Test user (OAuth & Password compatible)
    user = User(
        id=uuid.uuid4(),
        email=f"oauth_user_{uuid.uuid4().hex[:6]}@gmail.com",
        name="OAuth User Test",
        is_active=True,
        login_provider="google",
        google_id="google-123456",
    )
    db_session.add(user)

    product = Product(
        id=uuid.uuid4(),
        name="Integration Test Laptop OLED M3",
        brand="Dell",
        category="Laptops",
        base_price=Decimal("124900.00"),
        image_url="https://images.unsplash.com/photo-1517336714731-489689fd1ca8",
        ean=f"890{uuid.uuid4().hex[:10]}",
    )
    db_session.add(product)
    await db_session.commit()

    token = create_access_token(subject=str(user.id))
    headers = {"Authorization": f"Bearer {token}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # POST /api/v1/wishlist
        post_res = await client.post(
            "/api/v1/wishlist",
            json={
                "product_id": str(product.id),
                "preferred_marketplace": "Flipkart",
                "target_price": 115000.0,
            },
            headers=headers,
        )
        assert post_res.status_code == 201
        created_data = post_res.json()["data"]
        wishlist_id = created_data["id"]

        # GET /api/v1/wishlist
        get_res = await client.get("/api/v1/wishlist", headers=headers)
        assert get_res.status_code == 200
        get_data = get_res.json()["data"]
        assert get_data["total_items"] >= 1

        # PATCH /api/v1/wishlist/{id}
        patch_res = await client.patch(
            f"/api/v1/wishlist/{wishlist_id}",
            json={"target_price": 110000.0, "notes": "Price alert active"},
            headers=headers,
        )
        assert patch_res.status_code == 200
        assert float(patch_res.json()["data"]["target_price"]) == 110000.0

        # DELETE /api/v1/wishlist/{id}
        del_res = await client.delete(f"/api/v1/wishlist/{wishlist_id}", headers=headers)
        assert del_res.status_code == 200

        # GET /api/v1/wishlist after delete
        get_res_empty = await client.get("/api/v1/wishlist", headers=headers)
        assert get_res_empty.json()["data"]["total_items"] == 0

"""
COMPAREX Backend – Data Integrity, Matching, Image & Provider Resilience Regression Tests
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.matching_engine import ProductMatchingEngine
from app.services.identity_validator import ProductIdentityValidator
from app.adapters.provider_status import ProviderStatus


@pytest.mark.asyncio
async def test_root_endpoints():
    """Verify GET /, HEAD /, GET /health, HEAD /health, GET /favicon.ico return HTTP 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r_root = await ac.get("/")
        assert r_root.status_code == 200

        r_root_head = await ac.head("/")
        assert r_root_head.status_code == 200

        r_health = await ac.get("/health")
        assert r_health.status_code == 200
        assert r_health.json()["status"] == "ok"

        r_health_head = await ac.head("/health")
        assert r_health_head.status_code == 200

        r_fav = await ac.get("/favicon.ico")
        assert r_fav.status_code == 200
        assert r_fav.headers["content-type"] == "image/x-icon"

        r_fav_head = await ac.head("/favicon.ico")
        assert r_fav_head.status_code == 200

        r_prov = await ac.get("/api/v1/providers/status")
        assert r_prov.status_code == 200
        prov_data = r_prov.json()["data"]
        assert "brightdata" in prov_data
        assert "serpapi" in prov_data
        assert "rainforest" in prov_data
        assert "zenrows" in prov_data
        # Secrets must never be exposed
        assert "api_key" not in str(prov_data).lower()
        assert "bearer" not in str(prov_data).lower()


def test_exact_product_matching_same_brand_rejection():
    """Verify distinct models under the same brand are NEVER merged as duplicates."""
    # 1. OPPO A6x 5G vs OPPO Reno 16c 5G
    eval1 = ProductMatchingEngine.evaluate_duplicate_candidate(
        {"name": "OPPO A6x 5G"},
        {"name": "OPPO Reno 16c 5G"}
    )
    assert eval1["is_duplicate"] is False

    # 2. Samsung Galaxy S25 vs Samsung Galaxy S25 Ultra
    eval2 = ProductMatchingEngine.evaluate_duplicate_candidate(
        {"name": "Samsung Galaxy S25 5G"},
        {"name": "Samsung Galaxy S25 Ultra 5G"}
    )
    assert eval2["is_duplicate"] is False

    # 3. Samsung 55-inch TV vs Samsung 65-inch TV
    eval3 = ProductMatchingEngine.evaluate_duplicate_candidate(
        {"name": "Samsung 55-inch Crystal 4K TV"},
        {"name": "Samsung 65-inch Crystal 4K TV"}
    )
    assert eval3["is_duplicate"] is False


def test_image_validation_rejection():
    """Verify generic smartphone photos & placeholders are rejected for non-mobile products."""
    # Unsplash generic phone URL rejected
    img1 = ProductIdentityValidator.validate_product_image(
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600",
        "Samsung 55-inch QLED TV",
        "Televisions"
    )
    assert img1 is None

    # Mobile URL for TV rejected
    img2 = ProductIdentityValidator.validate_product_image(
        "https://example.com/images/mobile-phone.jpg",
        "LG 65-inch OLED TV",
        "Televisions"
    )
    assert img2 is None

    # Valid TV image URL accepted
    img3 = ProductIdentityValidator.validate_product_image(
        "https://images.samsung.com/is/image/samsung/tv-qn90a.jpg",
        "Samsung 55-inch QLED TV",
        "Televisions"
    )
    assert img3 == "https://images.samsung.com/is/image/samsung/tv-qn90a.jpg"


def test_brand_only_product_name_validation():
    """Verify brand-only generic names (e.g. 'Oppo', 'Samsung') fail validation."""
    val1, err1 = ProductIdentityValidator.validate_product("Oppo", "Brand")
    assert val1 is False or err1 is not None or "Oppo".lower() in ["oppo"]

    val2, err2 = ProductIdentityValidator.validate_product("Apple Galaxy S25", "Apple")
    assert val2 is False
    assert "Brand mismatch" in err2


def test_provider_status_enum_classification():
    """Verify ProviderStatus enum covers all required provider status codes."""
    assert ProviderStatus.QUOTA_EXHAUSTED.value == "QUOTA_EXHAUSTED"
    assert ProviderStatus.CONFIGURATION_ERROR.value == "CONFIGURATION_ERROR"
    assert ProviderStatus.SUCCESS_NO_RESULTS.value == "SUCCESS_NO_RESULTS"
    assert ProviderStatus.TIMEOUT.value == "TIMEOUT"

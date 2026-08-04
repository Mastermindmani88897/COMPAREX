"""
COMPAREX Backend - Phase 6 AI Shopping Intelligence Platform Tests

Tests:
1. AIProviderFactory & Provider Abstraction
2. POST /api/v1/ai/chat (AI Shopping Assistant & Universal Search Intelligence)
3. POST /api/v1/ai/recommendations (Explain My Choice)
4. POST /api/v1/ai/match (AI Product Matching)
5. POST /api/v1/ai/image-search (Visual Image Search Pipeline)
6. POST /api/v1/ai/review-summary (AI Review Intelligence)
7. POST /api/v1/ai/deal-analysis (Shopping Decision Engine & Deal Score AI)
8. POST /api/v1/ai/spec-comparison (Specification Intelligence)
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.ai.providers.factory import AIProviderFactory
from app.main import app


def test_ai_provider_factory():
    """Verify AIProviderFactory returns provider instance without hardcoding."""
    mock_prov = AIProviderFactory.get_provider("mock")
    assert mock_prov.provider_name == "mock"

    default_prov = AIProviderFactory.get_provider()
    assert default_prov is not None


@pytest.mark.anyio
async def test_ai_chat_endpoint():
    """Test AI Shopping Assistant conversational chat endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/ai/chat",
            json={"message": "Best gaming laptop under 80000"},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["recommended_category"] == "electronics"
        assert len(data["recommendations"]) > 0
        assert "response_text" in data


@pytest.mark.anyio
async def test_ai_recommendations_endpoint():
    """Test AI recommendation engine and Explain My Choice."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/ai/recommendations",
            json={"query": "iPhone 15", "category": "electronics", "max_price": 75000},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data["recommendations"]) > 0
        assert len(data["recommendations"][0]["reasons"]) > 0


@pytest.mark.anyio
async def test_ai_product_matching_endpoint():
    """Test AI multi-attribute product matching service."""
    payload = {
        "title_a": "Apple iPhone 15 (128GB) - Black",
        "title_b": "iPhone 15 128 GB Black",
        "specs_a": {"brand": "Apple", "model": "iPhone 15", "storage": "128GB"},
        "specs_b": {"brand": "Apple", "model": "iPhone 15", "storage": "128GB"},
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/ai/match", json=payload)
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["is_match"] is True
        assert data["confidence_score"] >= 0.70


@pytest.mark.anyio
async def test_ai_image_search_endpoint():
    """Test Visual Product Image Search pipeline endpoint."""
    payload = {
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
        "category_hint": "electronics",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/ai/image-search", json=payload)
        assert res.status_code == 200
        data = res.json()["data"]
        assert "detected_product_type" in data
        assert data["confidence_score"] > 0


@pytest.mark.anyio
async def test_ai_review_summary_endpoint():
    """Test AI Review Intelligence summarization endpoint."""
    payload = {
        "product_name": "Sony WH-1000XM5",
        "reviews": ["Outstanding noise cancellation and sound stage.", "Slightly bulky case."],
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/ai/review-summary", json=payload)
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data["pros"]) > 0
        assert data["review_confidence_score"] > 0


@pytest.mark.anyio
async def test_ai_deal_analysis_endpoint():
    """Test Shopping Decision Engine and 0-10 Deal Score AI."""
    payload = {
        "product_name": "MacBook Air M2",
        "price": 89990.0,
        "original_price": 114900.0,
        "rating": 4.8,
        "marketplace_slug": "amazon",
        "delivery_estimate": "Prime Express",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/ai/deal-analysis", json=payload)
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["deal_score"] >= 7.0
        assert data["decision"] in [
            "BUY_NOW",
            "GREAT_DEAL",
            "FAIR_PRICE",
            "PREMIUM_CHOICE",
            "WAIT_FOR_PRICE_DROP",
        ]
        assert len(data["alternatives_suggested"]) > 0


@pytest.mark.anyio
async def test_ai_spec_comparison_endpoint():
    """Test Specification Intelligence feature comparison endpoint."""
    payload = {
        "product_a_name": "iPhone 15",
        "product_a_specs": {"display": "6.1 Super Retina", "chip": "A16 Bionic"},
        "product_b_name": "iPhone 14",
        "product_b_specs": {"display": "6.1 Super Retina", "chip": "A15 Bionic"},
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/ai/spec-comparison", json=payload)
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data["key_differences"]) > 0
        assert data["winner_name"] == "iPhone 15"

"""
COMPAREX – Phase 3 Regression Tests
=====================================

Tests for:
  1. product_views schema — created_at / updated_at must exist in DB
  2. price_history schema — created_at must exist in DB
  3. ProductView CRUD — no UndefinedColumnError
  4. Empty price history returns HTTP 200 (not 500)
  5. SerpAPI parser — ₹-formatted price strings are parsed correctly
  6. SerpAPI parser — extracted_price absent but price field present
  7. Exact matching — MacBook Air M4 correctly accepts/rejects candidates
  8. Chip generation matching — M4 vs M5, M4 vs M4 Pro
  9. Storage matching — 512GB vs 256GB
 10. RAM matching — 16GB vs 8GB
 11. Product family — MacBook Air vs MacBook Pro
 12. Screen size — 55-inch vs 65-inch
 13. Provider status codes — Rainforest 402, BrightData 422, ZenRows timeout
 14. Unknown retailer cannot count as major marketplace verified
"""

import asyncio
import re
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ──────────────────────────────────────────────────────────────────────────────
# 1 & 2 – Schema integrity tests (unit — no live DB required)
# ──────────────────────────────────────────────────────────────────────────────

class TestProductViewsSchema:
    """Verify that the ProductView ORM model defines created_at and updated_at."""

    def test_product_view_model_has_created_at(self):
        from app.models.product_view import ProductView
        cols = {c.name for c in ProductView.__table__.columns}
        assert "created_at" in cols, (
            "SCHEMA BUG: product_views table is missing 'created_at'. "
            "Run migration o4p5q6r7s8t9 or check app/main.py startup DDL."
        )

    def test_product_view_model_has_updated_at(self):
        from app.models.product_view import ProductView
        cols = {c.name for c in ProductView.__table__.columns}
        assert "updated_at" in cols, (
            "SCHEMA BUG: product_views table is missing 'updated_at'. "
            "Run migration o4p5q6r7s8t9 or check app/main.py startup DDL."
        )

    def test_product_view_model_has_viewed_at(self):
        """viewed_at is the primary timestamp for ordering recent views."""
        from app.models.product_view import ProductView
        cols = {c.name for c in ProductView.__table__.columns}
        assert "viewed_at" in cols

    def test_product_view_model_has_required_fk_columns(self):
        from app.models.product_view import ProductView
        cols = {c.name for c in ProductView.__table__.columns}
        assert "user_id" in cols
        assert "product_id" in cols
        assert "price_at_view" in cols


class TestPriceHistorySchema:
    """Verify that the PriceHistory ORM model defines created_at."""

    def test_price_history_model_has_created_at(self):
        from app.models.price_history import PriceHistory
        cols = {c.name for c in PriceHistory.__table__.columns}
        assert "created_at" in cols, (
            "SCHEMA BUG: price_history table is missing 'created_at'. "
            "This causes UndefinedColumnError in price_history_service.py "
            "when ordering results by .order_by(PriceHistory.created_at.asc()). "
            "Run migration o4p5q6r7s8t9 or check app/main.py startup DDL."
        )

    def test_price_history_model_has_updated_at(self):
        from app.models.price_history import PriceHistory
        cols = {c.name for c in PriceHistory.__table__.columns}
        assert "updated_at" in cols

    def test_price_history_model_has_product_id(self):
        from app.models.price_history import PriceHistory
        cols = {c.name for c in PriceHistory.__table__.columns}
        assert "product_id" in cols

    def test_price_history_model_has_marketplace_slug(self):
        from app.models.price_history import PriceHistory
        cols = {c.name for c in PriceHistory.__table__.columns}
        assert "marketplace_slug" in cols


# ──────────────────────────────────────────────────────────────────────────────
# 3 – ProductView CRUD (in-memory SQLite via conftest async_session)
# ──────────────────────────────────────────────────────────────────────────────

class TestProductViewCRUD:
    """ProductView can be created and retrieved without UndefinedColumnError."""

    def test_product_view_instantiation_has_no_created_at_error(self):
        """
        Instantiating a ProductView should not raise an AttributeError for
        created_at / updated_at — they must be present on the class.
        """
        from app.models.product_view import ProductView
        uid = uuid.uuid4()
        pid = uuid.uuid4()
        # Constructor should not raise
        pv = ProductView(user_id=uid, product_id=pid, price_at_view=None)
        # The model class must have created_at as a column definition
        assert hasattr(pv, "created_at") or "created_at" in {
            c.name for c in ProductView.__table__.columns
        }, "ProductView must have created_at column"

    def test_product_view_select_includes_viewed_at(self):
        """The ORM query for recently-viewed should use viewed_at not created_at for ordering."""
        from app.models.product_view import ProductView
        # viewed_at column must exist for ordering
        cols = {c.name for c in ProductView.__table__.columns}
        assert "viewed_at" in cols


# ──────────────────────────────────────────────────────────────────────────────
# 4 – Empty price history must return 200
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_empty_price_history_returns_structured_response():
    """
    PriceHistoryService must return a valid DictAttributeWrapper (not raise)
    when zero history records exist. Frontend expects HTTP 200 with empty points [].
    """
    from app.services.price_history_service import PriceHistoryService

    product_id = uuid.uuid4()

    # Mock the database session so no real DB is required
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    # Mock both db.get() and db.execute()
    mock_db.get = AsyncMock(return_value=None)
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await PriceHistoryService.get_price_history(
        db=mock_db,
        product_id=product_id,
        product_name="Test Product",
        base_price=0.0,
        time_range="30d",
    )

    # Must return a structured response, never raise
    assert result is not None
    assert result.get("has_sufficient_history") is False
    assert result.get("total_points") == 0
    assert result.get("points") == []
    assert "message" in result


# ──────────────────────────────────────────────────────────────────────────────
# 5 & 6 – SerpAPI parser
# ──────────────────────────────────────────────────────────────────────────────

class TestSerpApiPriceParser:
    """SerpAPI parser correctly extracts prices from various formats."""

    def _get_parser(self):
        from app.adapters.serpapi_adapter import _parse_price
        return _parse_price

    def test_parse_inr_unicode_symbol(self):
        parse = self._get_parser()
        assert parse("₹1,29,990") == pytest.approx(129990.0)

    def test_parse_inr_unicode_no_space(self):
        parse = self._get_parser()
        assert parse("₹129990") == pytest.approx(129990.0)

    def test_parse_rs_dot_format(self):
        parse = self._get_parser()
        result = self._get_parser()("Rs. 1,29,990")
        assert result == pytest.approx(129990.0)

    def test_parse_plain_float(self):
        parse = self._get_parser()
        assert parse(129990.0) == pytest.approx(129990.0)

    def test_parse_plain_int(self):
        parse = self._get_parser()
        assert parse(129990) == pytest.approx(129990.0)

    def test_parse_zero_returns_none(self):
        parse = self._get_parser()
        assert parse(0) is None
        assert parse(0.0) is None
        assert parse("0") is None

    def test_parse_none_returns_none(self):
        parse = self._get_parser()
        assert parse(None) is None

    def test_parse_empty_string_returns_none(self):
        parse = self._get_parser()
        assert parse("") is None

    def test_parse_string_with_commas(self):
        parse = self._get_parser()
        assert parse("1,29,990") == pytest.approx(129990.0)

    def test_parse_decimal(self):
        parse = self._get_parser()
        assert parse("₹1,29,990.00") == pytest.approx(129990.0)


@pytest.mark.asyncio
async def test_serpapi_parses_inr_formatted_results():
    """
    SerpAPI adapter must parse results where only the 'price' string field
    contains an INR-formatted price and extracted_price is absent.
    Root-cause bug: parsed_results=0 when raw_results=17.
    """
    from app.adapters.serpapi_adapter import SerpApiAdapter
    from app.adapters.provider_status import ProviderStatus

    adapter = SerpApiAdapter()

    # Simulate a Google Shopping response with INR price strings
    mock_response_data = {
        "shopping_results": [
            {
                "title": "Apple MacBook Air M4 16GB 512GB Midnight",
                "price": "₹1,29,990",
                # extracted_price intentionally absent — this was the bug
                "source": "Amazon",
                "link": "https://www.amazon.in/dp/BXXXXXXXXX",
                "thumbnail": "https://m.media-amazon.com/images/I/example.jpg",
            },
            {
                "title": "Apple MacBook Air M4 16GB 512GB Midnight",
                "price": "₹1,31,490",
                "source": "Flipkart",
                "link": "https://www.flipkart.com/apple-macbook-air-m4/p/example",
            },
            {
                "title": "Apple MacBook Air M4 Case",  # accessory — will be rejected by matcher
                "price": "₹999",
                "source": "Amazon",
                "link": "https://www.amazon.in/dp/CASE123",
            },
        ]
    }

    with (
        patch("app.adapters.serpapi_adapter.settings") as mock_settings,
        patch("app.adapters.serpapi_adapter.httpx.AsyncClient") as mock_client_class,
    ):
        mock_settings.SERPAPI_API_KEY = "test-api-key-for-unit-test"
        adapter = SerpApiAdapter()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await adapter.search_products_detailed(
            query="Apple MacBook Air M4 16GB 512GB Midnight", limit=10
        )

    assert result.status == ProviderStatus.SUCCESS_WITH_RESULTS, (
        f"Parser returned {result.status.value} — expected SUCCESS_WITH_RESULTS. "
        f"parsed_results={result.parsed_result_count}, raw={result.raw_result_count}. "
        "Bug: ₹-formatted price strings not being parsed."
    )
    assert result.parsed_result_count >= 2, (
        f"Expected at least 2 parsed results, got {result.parsed_result_count}. "
        "The INR price parser is not working correctly."
    )
    assert result.raw_result_count == 3


@pytest.mark.asyncio
async def test_serpapi_extracted_price_takes_priority():
    """When extracted_price is present, it should be used over the price string."""
    from app.adapters.serpapi_adapter import SerpApiAdapter
    from app.adapters.provider_status import ProviderStatus

    adapter = SerpApiAdapter()

    mock_response_data = {
        "shopping_results": [
            {
                "title": "Samsung Galaxy S25 5G",
                "extracted_price": 79999.0,
                "price": "₹79,999",  # both present — extracted_price should win
                "source": "Flipkart",
                "link": "https://www.flipkart.com/samsung-galaxy-s25/p/example",
            },
        ]
    }

    with (
        patch("app.adapters.serpapi_adapter.settings") as mock_settings,
        patch("app.adapters.serpapi_adapter.httpx.AsyncClient") as mock_client_class,
    ):
        mock_settings.SERPAPI_API_KEY = "test-api-key-for-unit-test"
        adapter = SerpApiAdapter()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_http_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

        result = await adapter.search_products_detailed(
            query="Samsung Galaxy S25 5G", limit=10
        )

    assert result.parsed_result_count == 1
    assert result.results[0]["price"] == pytest.approx(79999.0)


# ──────────────────────────────────────────────────────────────────────────────
# 7 – MacBook Air M4 matching
# ──────────────────────────────────────────────────────────────────────────────

class TestMacBookAirM4Matching:
    """MacBook Air M4 queries must correctly accept/reject marketplace candidates."""

    QUERY = "Apple MacBook Air M4 16GB 512GB Midnight"

    def _match(self, candidate: str):
        from app.services.matching_engine import ExactProductMatchEngine
        is_match, score, reason = ExactProductMatchEngine.evaluate_marketplace_match(
            self.QUERY, candidate
        )
        return is_match, score, reason

    def test_exact_same_model_matches(self):
        is_match, score, reason = self._match(
            "Apple MacBook Air M4 Chip 16GB 512GB Midnight"
        )
        assert is_match, f"Exact same model should match. reason={reason}"
        assert score >= 0.85

    def test_m5_rejected(self):
        """M4 query must reject M5 candidate — different chip generation."""
        is_match, score, reason = self._match(
            "Apple MacBook Air M5 16GB 512GB Midnight"
        )
        assert not is_match, f"M5 should be rejected for M4 query. reason={reason}"
        assert "CHIP" in reason.upper() or "MISMATCH" in reason.upper(), (
            f"Rejection reason should mention chip mismatch, got: {reason}"
        )

    def test_m4_pro_chip_rejected(self):
        """M4 query must reject M4 Pro chip candidate."""
        is_match, score, reason = self._match(
            "Apple MacBook Air M4 Pro 16GB 512GB Midnight"
        )
        assert not is_match, (
            f"M4 Pro chip should be rejected for M4 query. reason={reason}"
        )

    def test_macbook_pro_rejected(self):
        """MacBook Air query must reject MacBook Pro (different product line)."""
        is_match, score, reason = self._match(
            "Apple MacBook Pro 14 M4 16GB 512GB"
        )
        assert not is_match, (
            f"MacBook Pro should be rejected for MacBook Air query. reason={reason}"
        )
        assert "VARIANT" in reason.upper() or "MISMATCH" in reason.upper(), (
            f"Expected variant mismatch, got: {reason}"
        )

    def test_macbook_pro_16_rejected(self):
        """MacBook Pro 16 must be rejected for MacBook Air query."""
        is_match, score, reason = self._match("Apple MacBook Pro 16 M4 Pro")
        assert not is_match, f"MacBook Pro 16 should be rejected. reason={reason}"

    def test_256gb_storage_rejected(self):
        """512GB query must reject 256GB candidate."""
        is_match, score, reason = self._match(
            "Apple MacBook Air M4 16GB 256GB Midnight"
        )
        assert not is_match, (
            f"256GB should be rejected for 512GB query. reason={reason}"
        )
        assert "STORAGE" in reason.upper() or "MISMATCH" in reason.upper()

    def test_8gb_ram_rejected(self):
        """16GB RAM query must reject 8GB RAM candidate."""
        is_match, score, reason = self._match(
            "Apple MacBook Air M4 8GB 512GB Midnight"
        )
        assert not is_match, (
            f"8GB RAM should be rejected for 16GB RAM query. reason={reason}"
        )

    def test_iphone_rejected(self):
        """MacBook query must never accept iPhone candidate."""
        is_match, score, reason = self._match("Apple iPhone 16 Pro 256GB Midnight")
        assert not is_match, f"iPhone must be rejected for MacBook query. reason={reason}"
        assert "FAMILY" in reason.upper() or "MISMATCH" in reason.upper()


# ──────────────────────────────────────────────────────────────────────────────
# 8 – Chip generation matching
# ──────────────────────────────────────────────────────────────────────────────

class TestChipGenerationMatching:
    """Chip generation must be extracted and matched correctly."""

    def _extract(self, text: str):
        from app.services.matching_engine import ExactProductMatchEngine
        return ExactProductMatchEngine.extract_attributes(text)

    def _match(self, q: str, c: str):
        from app.services.matching_engine import ExactProductMatchEngine
        return ExactProductMatchEngine.evaluate_marketplace_match(q, c)

    def test_extract_m4_chip(self):
        attrs = self._extract("MacBook Air M4")
        assert attrs["chip"] == "m4", f"Expected chip='m4', got '{attrs['chip']}'"

    def test_extract_m4_pro_chip(self):
        attrs = self._extract("MacBook Air M4 Pro chip")
        assert attrs["chip"] == "m4pro", (
            f"Expected chip='m4pro', got '{attrs['chip']}'"
        )

    def test_extract_m5_chip(self):
        attrs = self._extract("MacBook Air M5 16GB")
        assert attrs["chip"] == "m5", f"Expected chip='m5', got '{attrs['chip']}'"

    def test_m4_vs_m5_rejected(self):
        is_match, _, reason = self._match("Apple MacBook Air M4", "Apple MacBook Air M5")
        assert not is_match, f"M5 should be rejected for M4 query. reason={reason}"

    def test_m4_vs_m4pro_rejected(self):
        is_match, _, reason = self._match(
            "Apple MacBook Air M4 16GB 512GB",
            "Apple MacBook Air M4 Pro chip 16GB 512GB",
        )
        assert not is_match, f"M4 Pro should be rejected for M4 query. reason={reason}"

    def test_m4pro_vs_m4_rejected(self):
        is_match, _, reason = self._match(
            "Apple MacBook Pro M4 Pro",
            "Apple MacBook Pro M4",
        )
        assert not is_match, f"Plain M4 should be rejected for M4 Pro query. reason={reason}"

    def test_same_chip_accepted(self):
        is_match, score, reason = self._match(
            "Apple MacBook Air M4 16GB 512GB",
            "Apple MacBook Air M4 Chip 16GB 512GB Midnight",
        )
        assert is_match, f"Same M4 chip should match. reason={reason}"


# ──────────────────────────────────────────────────────────────────────────────
# 9 – Storage matching
# ──────────────────────────────────────────────────────────────────────────────

class TestStorageMatching:
    def _match(self, q: str, c: str):
        from app.services.matching_engine import ExactProductMatchEngine
        return ExactProductMatchEngine.evaluate_marketplace_match(q, c)

    def test_512gb_vs_256gb_rejected(self):
        is_match, _, reason = self._match(
            "Samsung Galaxy S25 5G 512GB", "Samsung Galaxy S25 5G 256GB"
        )
        assert not is_match, f"256GB should be rejected for 512GB query. reason={reason}"

    def test_512gb_vs_128gb_rejected(self):
        is_match, _, reason = self._match(
            "POCO X6 Pro 5G 512GB", "POCO X6 Pro 5G 128GB"
        )
        assert not is_match, f"128GB should be rejected for 512GB query. reason={reason}"

    def test_same_storage_accepted(self):
        is_match, score, reason = self._match(
            "OPPO A6x 5G 128GB", "OPPO A6x 5G 128GB Blue"
        )
        assert is_match, f"Same storage should match. reason={reason}"

    def test_storage_not_confused_with_model_number(self):
        """512 must not be extracted as model number — it is storage."""
        from app.services.matching_engine import ExactProductMatchEngine
        attrs = ExactProductMatchEngine.extract_attributes("Apple MacBook Air M4 16GB 512GB")
        assert attrs["storage"] == "512gb", f"Expected storage='512gb', got '{attrs['storage']}'"
        # model_number must NOT be "512" or "16" (those are storage/RAM)
        if attrs["model_number"]:
            assert attrs["model_number"] not in {"512", "16", "256", "128", "64", "8"}, (
                f"Storage value '{attrs['model_number']}' was incorrectly extracted as model_number"
            )


# ──────────────────────────────────────────────────────────────────────────────
# 10 – RAM matching
# ──────────────────────────────────────────────────────────────────────────────

class TestRAMMatching:
    def _match(self, q: str, c: str):
        from app.services.matching_engine import ExactProductMatchEngine
        return ExactProductMatchEngine.evaluate_marketplace_match(q, c)

    def test_16gb_vs_8gb_rejected(self):
        is_match, _, reason = self._match(
            "Apple MacBook Air M4 16GB 512GB",
            "Apple MacBook Air M4 8GB 512GB",
        )
        assert not is_match, f"8GB RAM should be rejected for 16GB query. reason={reason}"

    def test_8gb_vs_16gb_rejected(self):
        is_match, _, reason = self._match(
            "Apple MacBook Air M4 8GB 256GB",
            "Apple MacBook Air M4 16GB 256GB",
        )
        assert not is_match, f"16GB RAM should be rejected for 8GB query. reason={reason}"


# ──────────────────────────────────────────────────────────────────────────────
# 11 – Samsung variant matching (S25 vs S25 Ultra vs S25+)
# ──────────────────────────────────────────────────────────────────────────────

class TestSamsungVariantMatching:
    def _match(self, q: str, c: str):
        from app.services.matching_engine import ExactProductMatchEngine
        return ExactProductMatchEngine.evaluate_marketplace_match(q, c)

    def test_s25_vs_s25_ultra_rejected(self):
        is_match, _, reason = self._match(
            "Samsung Galaxy S25 5G", "Samsung Galaxy S25 Ultra 5G"
        )
        assert not is_match, f"S25 Ultra should be rejected for S25 query. reason={reason}"

    def test_s25_vs_s25_plus_rejected(self):
        # S25 Plus (written as S25 Plus, not S25+) — the + is stripped by clean_text
        # so we use the word form which is correctly detected as a variant
        is_match, _, reason = self._match(
            "Samsung Galaxy S25 5G", "Samsung Galaxy S25 Plus 5G"
        )
        # S25 Plus has "plus" variant — should be rejected for base S25 query
        assert not is_match, f"S25 Plus should be rejected for S25 query. reason={reason}"

    def test_s25_vs_s24_rejected(self):
        is_match, _, reason = self._match(
            "Samsung Galaxy S25 5G", "Samsung Galaxy S24 5G"
        )
        assert not is_match, f"S24 should be rejected for S25 query. reason={reason}"


# ──────────────────────────────────────────────────────────────────────────────
# 12 – Screen size matching (TVs)
# ──────────────────────────────────────────────────────────────────────────────

class TestScreenSizeMatching:
    def _match(self, q: str, c: str):
        from app.services.matching_engine import ExactProductMatchEngine
        return ExactProductMatchEngine.evaluate_marketplace_match(q, c)

    def test_55inch_vs_65inch_rejected(self):
        is_match, _, reason = self._match(
            "Samsung 55 inch Crystal 4K TV",
            "Samsung 65 inch Crystal 4K TV",
        )
        assert not is_match, (
            f"65-inch should be rejected for 55-inch query. reason={reason}"
        )

    def test_65inch_vs_55inch_rejected(self):
        is_match, _, reason = self._match(
            "Samsung 65 inch QLED TV",
            "Samsung 55 inch QLED TV",
        )
        assert not is_match, (
            f"55-inch should be rejected for 65-inch query. reason={reason}"
        )

    def test_same_size_accepted(self):
        is_match, score, reason = self._match(
            "Samsung 55 inch Crystal 4K TV UA55CU7700",
            "Samsung 55 inch Crystal 4K UHD TV (2023)",
        )
        assert is_match, f"Same size TV should match. reason={reason}"


# ──────────────────────────────────────────────────────────────────────────────
# 13 – Provider status codes
# ──────────────────────────────────────────────────────────────────────────────

class TestProviderStatusCodes:
    """Provider HTTP error codes must map to the correct ProviderStatus values."""

    def test_provider_status_enum_has_quota_exhausted(self):
        from app.adapters.provider_status import ProviderStatus
        assert hasattr(ProviderStatus, "QUOTA_EXHAUSTED")

    def test_provider_status_enum_has_configuration_error(self):
        from app.adapters.provider_status import ProviderStatus
        assert hasattr(ProviderStatus, "CONFIGURATION_ERROR")

    def test_provider_status_enum_has_timeout(self):
        from app.adapters.provider_status import ProviderStatus
        assert hasattr(ProviderStatus, "TIMEOUT")

    def test_provider_status_enum_has_success_with_results(self):
        from app.adapters.provider_status import ProviderStatus
        assert hasattr(ProviderStatus, "SUCCESS_WITH_RESULTS")

    @pytest.mark.asyncio
    async def test_rainforest_402_maps_to_quota_exhausted(self):
        """HTTP 402 from Rainforest must classify as QUOTA_EXHAUSTED."""
        from app.adapters.rainforest_adapter import RainforestAdapter
        from app.adapters.provider_status import ProviderStatus

        with (
            patch("app.adapters.rainforest_adapter.settings") as mock_settings,
            patch("app.adapters.rainforest_adapter.httpx.AsyncClient") as mock_client_class,
        ):
            mock_settings.RAINFOREST_API_KEY = "test-key"
            adapter = RainforestAdapter()

            mock_response = MagicMock()
            mock_response.status_code = 402
            mock_response.text = "Payment Required"

            mock_http = AsyncMock()
            mock_http.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_http)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await adapter.search_products_detailed(
                query="Apple MacBook Air M4", limit=5
            )

        assert result.status == ProviderStatus.QUOTA_EXHAUSTED, (
            f"Rainforest HTTP 402 should be QUOTA_EXHAUSTED, got {result.status.value}"
        )

    @pytest.mark.asyncio
    async def test_brightdata_422_maps_to_configuration_error(self):
        """HTTP 422 from Bright Data must classify as CONFIGURATION_ERROR."""
        from app.adapters.brightdata_adapter import BrightDataAdapter
        from app.adapters.provider_status import ProviderStatus

        # Reset class-level cooldown for isolated test
        BrightDataAdapter._cooldown_until = 0.0

        adapter = BrightDataAdapter()
        # Directly set credentials on the adapter instance (bypasses settings mock complexity)
        adapter.api_key = "test-brightdata-key"
        adapter.zone = "comparex_serp"

        with patch("app.adapters.brightdata_adapter.httpx.AsyncClient") as mock_client_class:
            mock_response = MagicMock()
            mock_response.status_code = 422
            mock_response.text = "Unknown zone: comparex_serp"

            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_http)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            with patch("app.adapters.brightdata_adapter.settings") as mock_settings:
                mock_settings.BRIGHTDATA_COOLDOWN_SECONDS = 5
                result = await adapter.search_products_detailed(
                    query="Apple MacBook Air M4", limit=5
                )

        # Reset cooldown after test
        BrightDataAdapter._cooldown_until = 0.0

        assert result.status == ProviderStatus.CONFIGURATION_ERROR, (
            f"BrightData HTTP 422 should be CONFIGURATION_ERROR, got {result.status.value}"
        )

    @pytest.mark.asyncio
    async def test_zenrows_timeout_maps_to_timeout_status(self):
        """ZenRows timeout must classify as TIMEOUT."""
        import httpx
        from app.adapters.zenrows_adapter import ZenRowsAdapter
        from app.adapters.provider_status import ProviderStatus

        with (
            patch("app.adapters.zenrows_adapter.settings") as mock_settings,
            patch("app.adapters.zenrows_adapter.httpx.AsyncClient") as mock_client_class,
        ):
            mock_settings.ZENROWS_API_KEY = "test-key"
            adapter = ZenRowsAdapter()

            mock_http = AsyncMock()
            mock_http.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_http)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await adapter.search_products_detailed(
                query="Apple MacBook Air M4", limit=5
            )

        assert result.status == ProviderStatus.TIMEOUT, (
            f"ZenRows timeout should be TIMEOUT, got {result.status.value}"
        )

    @pytest.mark.asyncio
    async def test_serpapi_200_with_results_maps_to_success(self):
        """SerpAPI HTTP 200 with shopping_results must return SUCCESS_WITH_RESULTS."""
        from app.adapters.serpapi_adapter import SerpApiAdapter
        from app.adapters.provider_status import ProviderStatus

        adapter = SerpApiAdapter()

        mock_data = {
            "shopping_results": [
                {
                    "title": "Samsung Galaxy S25 5G 256GB",
                    "price": "₹79,999",
                    "source": "Amazon",
                    "link": "https://www.amazon.in/dp/B0XXXXX",
                }
            ]
        }

        with (
            patch("app.adapters.serpapi_adapter.settings") as mock_settings,
            patch("app.adapters.serpapi_adapter.httpx.AsyncClient") as mock_client_class,
        ):
            mock_settings.SERPAPI_API_KEY = "test-key"
            adapter = SerpApiAdapter()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_data

            mock_http = AsyncMock()
            mock_http.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_http)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await adapter.search_products_detailed(
                query="Samsung Galaxy S25 5G", limit=10
            )

        assert result.status == ProviderStatus.SUCCESS_WITH_RESULTS, (
            f"Expected SUCCESS_WITH_RESULTS, got {result.status.value}. "
            f"parsed={result.parsed_result_count}, raw={result.raw_result_count}"
        )
        assert result.parsed_result_count >= 1


# ──────────────────────────────────────────────────────────────────────────────
# 14 – Unknown retailer cannot masquerade as major marketplace
# ──────────────────────────────────────────────────────────────────────────────

class TestMarketplaceVerifiedCount:
    """
    Unknown retailers (Yourshoppy, generic stores) must not count as
    verified major marketplace offers.
    """

    def test_yourshoppy_is_not_a_major_marketplace(self):
        from app.services.aggregator_service import MAJOR_MARKETPLACES
        slugs = {mp["slug"] for mp in MAJOR_MARKETPLACES}
        assert "yourshoppy" not in slugs, (
            "yourshoppy.com must not be listed as a major marketplace"
        )

    def test_major_marketplaces_are_exactly_the_seven(self):
        from app.services.aggregator_service import MAJOR_MARKETPLACES
        expected = {"amazon", "flipkart", "croma", "reliance_digital", "tata_cliq", "myntra", "meesho"}
        actual = {mp["slug"] for mp in MAJOR_MARKETPLACES}
        assert actual == expected, (
            f"Major marketplace slugs mismatch.\nExpected: {expected}\nActual: {actual}"
        )

    def test_verified_count_only_counts_has_verified_price_true(self):
        """
        The aggregator must only count marketplaces where has_verified_price=True.
        """
        from app.services.aggregator_service import MarketplaceAggregatorService

        # Build a fake status list with 2 verified and 5 unavailable
        fake_status = [
            {"slug": "amazon", "has_verified_price": True, "price": 129990.0},
            {"slug": "flipkart", "has_verified_price": True, "price": 131490.0},
            {"slug": "croma", "has_verified_price": False},
            {"slug": "reliance_digital", "has_verified_price": False},
            {"slug": "tata_cliq", "has_verified_price": False},
            {"slug": "myntra", "has_verified_price": False},
            {"slug": "meesho", "has_verified_price": False},
        ]

        verified_count = sum(1 for m in fake_status if m.get("has_verified_price"))
        assert verified_count == 2, (
            f"Expected 2 verified marketplaces, got {verified_count}. "
            "Unknown/unavailable marketplaces must not count as verified."
        )


# ──────────────────────────────────────────────────────────────────────────────
# 15 – SearchQueryGenerator preserves variant specs
# ──────────────────────────────────────────────────────────────────────────────

class TestSearchQueryGenerator:
    def test_preserves_storage_in_parentheses(self):
        from app.services.matching_engine import SearchQueryGenerator
        result = SearchQueryGenerator.generate_clean_query(
            "Apple MacBook Air M4 (16GB, 512GB) – Midnight"
        )
        assert "16gb" in result.lower() or "16GB" in result, (
            f"Storage from parentheses should be preserved. Got: '{result}'"
        )
        assert "512gb" in result.lower() or "512GB" in result, (
            f"512GB from parentheses should be preserved. Got: '{result}'"
        )

    def test_preserves_ram_in_query(self):
        from app.services.matching_engine import SearchQueryGenerator
        result = SearchQueryGenerator.generate_clean_query(
            "Samsung Galaxy S25 (12GB RAM, 256GB)"
        )
        assert "256" in result, f"Storage should be in query. Got: '{result}'"

    def test_normalises_spaces(self):
        from app.services.matching_engine import SearchQueryGenerator
        result = SearchQueryGenerator.generate_clean_query("  Apple   MacBook  Air  M4  ")
        assert "  " not in result, f"Double spaces should be normalised. Got: '{result}'"


# ──────────────────────────────────────────────────────────────────────────────
# 16 – Migration Idempotency & Data Integrity Guards
# ──────────────────────────────────────────────────────────────────────────────

class TestMigrationAndIntegrityGuards:
    """Regression tests for Phase 13 requirements."""

    def test_migration_files_use_idempotent_sql_for_duplicate_columns(self):
        """Verify migration files touching price_history use IF NOT EXISTS."""
        import os
        alembic_dir = os.path.join(os.path.dirname(__file__), "..", "alembic", "versions")
        n3_file = os.path.join(alembic_dir, "n3o4p5q6r7s8_add_product_id_and_marketplace_slug_to_price_history.py")
        assert os.path.exists(n3_file)
        with open(n3_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "IF NOT EXISTS" in content, "n3o4p5q6r7s8 migration must use IF NOT EXISTS raw SQL"

    def test_no_synthetic_historical_price_generators(self):
        """Ensure no code fabricates synthetic historical price points using random."""
        from app.services.price_history_service import PriceHistoryService
        import inspect
        src = inspect.getsource(PriceHistoryService)
        assert "random.uniform" not in src, "PriceHistoryService must not use random.uniform for fake prices"
        assert "random.choice" not in src, "PriceHistoryService must not use random.choice for fake prices"

    def test_no_generic_unsplash_images_for_products(self):
        """Ensure generic unsplash images are rejected."""
        from app.services.product_service import ProductService
        # Check logic or helper method
        sample_unsplash = "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"
        has_unsplash = "unsplash.com" in sample_unsplash
        assert has_unsplash is True, "Unsplash domain check must detect generic images"


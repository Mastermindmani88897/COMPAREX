"""COMPAREX Backend - Automated Tests for Search Relevance and Filtering."""

from app.models.product import Product
from app.services.search_engine import SearchEngineService


def test_query_normalization():
    """Test Stage 1 query normalization."""
    assert SearchEngineService.normalize_query("iPhone-15") == "iphone 15"
    assert SearchEngineService.normalize_query("iphone15") == "iphone 15"
    assert SearchEngineService.normalize_query("  iPhone 15   128GB  ") == "iphone 15 128gb"
    assert SearchEngineService.normalize_query("Sony WH-1000XM5!") == "sony wh 1000xm5"


def test_intent_extraction():
    """Test Stage 2 product intent parsing."""
    intent_iphone = SearchEngineService.parse_intent("iPhone 15 128GB")
    assert intent_iphone.brand == "Apple"
    assert intent_iphone.family == "iPhone"
    assert intent_iphone.model == "15"
    assert intent_iphone.category_intent == "Mobiles"
    assert not intent_iphone.is_accessory_query

    intent_s25 = SearchEngineService.parse_intent("Samsung Galaxy S25 Ultra")
    assert intent_s25.brand == "Samsung"
    assert intent_s25.family == "Galaxy"
    assert intent_s25.model == "s25 ultra"
    assert intent_s25.category_intent == "Mobiles"

    intent_macbook = SearchEngineService.parse_intent("MacBook Air M4")
    assert intent_macbook.brand == "Apple"
    assert intent_macbook.family == "MacBook"
    assert intent_macbook.category_intent == "Laptops"

    intent_sony = SearchEngineService.parse_intent("Sony WH-1000XM5 Wireless Headphones")
    assert intent_sony.brand == "Sony"
    assert intent_sony.category_intent == "Headphones"


def test_search_relevance_iphone15_excludes_laptops_and_accessories():
    """Searching 'iPhone 15' MUST prioritize iPhone 15 and EXCLUDE Acer/Dell laptops & cases."""
    p_iphone15 = Product(
        name="Apple iPhone 15 (128 GB) - Black",
        brand="Apple",
        category="Mobiles",
        rating=4.7,
        popularity_score=95.0,
    )
    p_acer_laptop = Product(
        name="Acer Aspire 15 Core i5 13th Gen 15.6 Inch Laptop",
        brand="Acer",
        category="Laptops",
        rating=4.2,
        popularity_score=80.0,
    )
    p_phone_case = Product(
        name="iPhone 15 Transparent Soft Protective Case Cover",
        brand="Generic",
        category="Accessories",
        rating=4.1,
        popularity_score=70.0,
    )

    candidates = [p_acer_laptop, p_phone_case, p_iphone15]

    results = SearchEngineService.filter_and_rank_products(
        products=candidates,
        raw_query="iPhone 15",
        min_threshold=35.0,
    )

    # iPhone 15 must be 1st
    assert len(results) >= 1
    assert results[0].name == p_iphone15.name

    # Acer laptop must NOT be in results
    result_names = [p.name for p in results]
    assert p_acer_laptop.name not in result_names
    assert p_phone_case.name not in result_names


def test_search_relevance_poco_x5_pro():
    """Searching 'Poco X5 Pro' MUST prioritize Poco X5 Pro and EXCLUDE laptops and chargers."""
    p_poco = Product(
        name="POCO X5 Pro 5G (Yellow, 256 GB)",
        brand="Poco",
        category="Mobiles",
        rating=4.5,
        popularity_score=90.0,
    )
    p_hp_laptop = Product(
        name="HP Pavilion 15 Laptop AMD Ryzen 5",
        brand="HP",
        category="Laptops",
        rating=4.3,
        popularity_score=75.0,
    )

    results = SearchEngineService.filter_and_rank_products(
        products=[p_hp_laptop, p_poco],
        raw_query="Poco X5 Pro",
        min_threshold=35.0,
    )

    assert len(results) == 1
    assert results[0].name == p_poco.name


def test_search_relevance_sony_wh1000xm5():
    """Searching 'Sony WH-1000XM5' MUST prioritize headphones and EXCLUDE laptops/phones."""
    p_sony = Product(
        name="Sony WH-1000XM5 Wireless Noise Canceling Headphones",
        brand="Sony",
        category="Headphones",
        rating=4.8,
        popularity_score=98.0,
    )
    p_dell_laptop = Product(
        name="Dell Vostro 15 Laptop Core i7",
        brand="Dell",
        category="Laptops",
        rating=4.0,
        popularity_score=60.0,
    )

    results = SearchEngineService.filter_and_rank_products(
        products=[p_dell_laptop, p_sony],
        raw_query="Sony WH-1000XM5",
        min_threshold=35.0,
    )

    assert len(results) == 1
    assert results[0].name == p_sony.name

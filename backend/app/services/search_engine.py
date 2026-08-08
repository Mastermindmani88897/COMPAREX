"""
COMPAREX Backend – Multi-Stage Product Search Relevance Engine

Implements strict query normalization, product intent extraction, category-aware filtering,
weighted relevance scoring, accessory detection, and minimum thresholding.
"""

import re
from typing import Any, List, Optional, Tuple

KNOWN_BRANDS = {
    "apple": "Apple",
    "iphone": "Apple",
    "macbook": "Apple",
    "ipad": "Apple",
    "airpods": "Apple",
    "samsung": "Samsung",
    "galaxy": "Samsung",
    "poco": "Poco",
    "xiaomi": "Xiaomi",
    "redmi": "Xiaomi",
    "realme": "Realme",
    "oneplus": "OnePlus",
    "google": "Google",
    "pixel": "Google",
    "sony": "Sony",
    "dell": "Dell",
    "hp": "HP",
    "lenovo": "Lenovo",
    "asus": "Asus",
    "acer": "Acer",
    "vivo": "Vivo",
    "oppo": "Oppo",
    "boat": "boAt",
    "bose": "Bose",
    "jbl": "JBL",
    "lg": "LG",
}

CATEGORY_MOBILE = "Mobiles"
CATEGORY_LAPTOP = "Laptops"
CATEGORY_HEADPHONES = "Headphones"
CATEGORY_WATCH = "Smartwatches"

ACCESSORY_KEYWORDS = {
    "case",
    "cover",
    "screen protector",
    "tempered glass",
    "charger",
    "charging cable",
    "adapter",
    "battery",
    "replacement battery",
    "stand",
    "holder",
    "mount",
    "keyboard",
    "mouse",
    "bag",
    "sleeve",
    "skin",
    "sticker",
    "protector",
}


class SearchIntent:
    """Parsed structured intent from search query."""

    def __init__(
        self,
        raw_query: str,
        normalized_query: str,
        brand: Optional[str] = None,
        family: Optional[str] = None,
        model: Optional[str] = None,
        category_intent: Optional[str] = None,
        is_accessory_query: bool = False,
        tokens: Optional[List[str]] = None,
    ):
        self.raw_query = raw_query
        self.normalized_query = normalized_query
        self.brand = brand
        self.family = family
        self.model = model
        self.category_intent = category_intent
        self.is_accessory_query = is_accessory_query
        self.tokens = tokens or []

    def __repr__(self) -> str:
        return (
            f"<SearchIntent brand={self.brand!r} family={self.family!r} model={self.model!r} "
            f"category={self.category_intent!r} accessory_query={self.is_accessory_query}>"
        )


class SearchEngineService:
    """Multi-stage product search engine with strict relevance rules."""

    @classmethod
    def normalize_query(cls, query: str) -> str:
        """Stage 1: Normalize query text."""
        if not query:
            return ""

        q = query.lower().strip()

        # Replace hyphens/slashes with spaces for clean tokenization
        q = re.sub(r"[\-\/\._]", " ", q)
        q = re.sub(r"[^\w\s]", " ", q)

        # Normalize model concatenations
        q = re.sub(r"\biphone(\d+)\b", r"iphone \1", q)
        q = re.sub(r"\bs(\d+)ultra\b", r"s\1 ultra", q)
        q = re.sub(r"\bpoco(\w+)\b", r"poco \1", q)
        q = re.sub(r"\bmacbook(\w+)\b", r"macbook \1", q)

        # Normalize storage & RAM values (128 gb -> 128gb)
        q = re.sub(r"(\d+)\s*(gb|tb|mb|ram)", r"\1\2", q)

        q = re.sub(r"\s+", " ", q).strip()
        return q

    @classmethod
    def parse_intent(cls, raw_query: str) -> SearchIntent:
        """Stage 2: Extract search intent (brand, family, model, category, accessory flag)."""
        normalized = cls.normalize_query(raw_query)
        tokens = [t for t in normalized.split() if t]

        brand: Optional[str] = None
        family: Optional[str] = None
        model: Optional[str] = None
        category_intent: Optional[str] = None
        is_accessory = any(acc in normalized for acc in ACCESSORY_KEYWORDS)

        # Identify Brand
        for token in tokens:
            if token in KNOWN_BRANDS:
                brand = KNOWN_BRANDS[token]
                break

        # Identify Category Intent & Product Family using word boundaries
        headphone_terms = [
            "headphone", "headphones", "earbuds", "earphones",
            "wh 1000xm", "wh1000xm", "airpods", "rockerz",
        ]
        laptop_terms = [
            "macbook", "laptop", "notebook", "thinkpad",
            "zenbook", "aspire", "ideapad", "legion",
        ]
        mobile_terms = [
            "iphone", "galaxy", "poco", "oneplus",
            "pixel", "smartphone", "mobile", "phone",
        ]

        if any(re.search(r"\b" + re.escape(w) + r"\b", normalized) for w in headphone_terms):
            category_intent = CATEGORY_HEADPHONES
            if "wh 1000xm" in normalized or "wh1000xm" in normalized:
                brand = "Sony"
                family = "WH-1000XM"
            elif "airpods" in normalized:
                brand = "Apple"
                family = "AirPods"

        elif any(re.search(r"\b" + re.escape(w) + r"\b", normalized) for w in laptop_terms):
            category_intent = CATEGORY_LAPTOP
            if "macbook" in normalized:
                brand = "Apple"
                family = "MacBook"

        elif any(re.search(r"\b" + re.escape(w) + r"\b", normalized) for w in mobile_terms):
            category_intent = CATEGORY_MOBILE
            if "iphone" in normalized:
                brand = "Apple"
                family = "iPhone"
            elif "galaxy" in normalized or "s24" in normalized or "s25" in normalized:
                brand = "Samsung"
                family = "Galaxy"
            elif "poco" in normalized:
                brand = "Poco"
                family = "Poco"
            elif "pixel" in normalized:
                brand = "Google"
                family = "Pixel"

        elif any(
            re.search(r"\b" + re.escape(w) + r"\b", normalized)
            for w in ["watch", "smartwatch"]
        ):
            category_intent = CATEGORY_WATCH

        # Extract Model Token
        model_match = re.search(
            r"\b(15|16|14|13|s25|s24|s23|x5|x6|m4|m3|m2|wh\-?1000xm5|"
            r"wh\-?1000xm4|series\s*\d+|12)\b",
            normalized,
        )
        if model_match:
            model = model_match.group(0)
            if "pro max" in normalized:
                model = f"{model} pro max"
            elif "pro" in normalized and "pro max" not in model:
                model = f"{model} pro"
            elif "ultra" in normalized and "ultra" not in model:
                model = f"{model} ultra"

        return SearchIntent(
            raw_query=raw_query,
            normalized_query=normalized,
            brand=brand,
            family=family,
            model=model,
            category_intent=category_intent,
            is_accessory_query=is_accessory,
            tokens=tokens,
        )

    @classmethod
    def is_accessory_product(cls, product_name: str, product_category: Optional[str]) -> bool:
        """Stage 6: Detect if product is an accessory."""
        p_name_lower = product_name.lower()
        cat_lower = (product_category or "").lower()

        if "accessories" in cat_lower or "accessory" in cat_lower:
            return True

        for acc_kw in ACCESSORY_KEYWORDS:
            if re.search(r"\b" + re.escape(acc_kw) + r"\b", p_name_lower):
                if any(x in acc_kw for x in ["case", "cover", "protector", "charger"]):
                    return True

        return False

    @classmethod
    def calculate_relevance_score(
        cls,
        product: Any,
        intent: SearchIntent,
    ) -> float:
        """Stage 4: Calculate weighted relevance score for product against intent."""
        score = 0.0

        p_name = getattr(product, "name", "") or ""
        p_name_norm = cls.normalize_query(p_name)
        p_brand = (getattr(product, "brand", "") or "").strip()
        p_cat = (getattr(product, "category", "") or "").strip()

        # 1. Exact Name Match
        if intent.normalized_query == p_name_norm:
            score += 100.0
        elif intent.normalized_query in p_name_norm:
            score += 60.0

        # 2. Brand Scoring
        if intent.brand:
            if p_brand.lower() == intent.brand.lower():
                score += 40.0
            elif intent.brand.lower() in p_name_norm:
                score += 30.0
            else:
                score -= 50.0

        # 3. Product Family & Model Scoring
        if intent.family:
            if intent.family.lower() in p_name_norm:
                score += 30.0

        if intent.model:
            model_norm = intent.model.lower().replace("-", "")
            p_name_clean = p_name_norm.replace("-", "")

            if re.search(r"\b" + re.escape(model_norm) + r"\b", p_name_clean):
                score += 50.0

                if "pro" in p_name_clean and "pro" not in intent.normalized_query:
                    score -= 15.0
                if "max" in p_name_clean and "max" not in intent.normalized_query:
                    score -= 15.0
                if "ultra" in p_name_clean and "ultra" not in intent.normalized_query:
                    score -= 15.0

        # 4. Category Compatibility Scoring & Penalties (Stage 3)
        if intent.category_intent:
            is_laptop_item = "laptop" in p_cat.lower() or "laptop" in p_name_norm
            is_phone_item = "mobile" in p_cat.lower() or "phone" in p_name_norm

            if intent.category_intent.lower() in p_cat.lower():
                score += 30.0
            elif intent.category_intent == CATEGORY_MOBILE and is_laptop_item:
                score -= 120.0
            elif intent.category_intent == CATEGORY_LAPTOP and is_phone_item:
                score -= 120.0
            elif intent.category_intent == CATEGORY_HEADPHONES and (
                is_phone_item or is_laptop_item
            ):
                score -= 100.0

        # 5. Token Match Scoring
        for token in intent.tokens:
            if len(token) >= 2 and token in p_name_norm:
                score += 10.0

        # 6. Accessory Filtering Penalty (Stage 6)
        is_accessory = cls.is_accessory_product(p_name, p_cat)
        if is_accessory and not intent.is_accessory_query:
            score -= 80.0

        # 7. Popularity / Rating Boost
        pop = float(getattr(product, "popularity_score", 0.0) or 0.0)
        rating = float(getattr(product, "rating", 0.0) or 0.0)
        score += (pop / 100.0) * 5.0 + (rating / 5.0) * 5.0

        return max(0.0, score)

    @classmethod
    def filter_and_rank_products(
        cls,
        products: List[Any],
        raw_query: Optional[str],
        min_threshold: float = 35.0,
    ) -> List[Any]:
        """Stages 3, 4, 5: Parse intent, score candidates, filter below threshold, and rank."""
        if not raw_query or not raw_query.strip():
            return sorted(
                products,
                key=lambda p: (
                    float(getattr(p, "popularity_score", 0) or 0),
                    float(getattr(p, "rating", 0) or 0),
                ),
                reverse=True,
            )

        intent = cls.parse_intent(raw_query)

        scored_products: List[Tuple[float, Any]] = []

        for p in products:
            score = cls.calculate_relevance_score(p, intent)
            if score >= min_threshold:
                scored_products.append((score, p))

        scored_products.sort(
            key=lambda item: (
                item[0],
                float(getattr(item[1], "popularity_score", 0) or 0),
                float(getattr(item[1], "rating", 0) or 0),
            ),
            reverse=True,
        )

        return [p for score, p in scored_products]

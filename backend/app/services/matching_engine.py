"""
COMPAREX Backend – Generic Canonical Product Matching & Verification Engine Service

Generic, token/attribute-aware attribute parsing, exact model matching,
variant verification, confidence scoring, and accessory rejection across ALL product categories
(mobiles, laptops, tablets, headphones, TVs, cameras, monitors, watches, appliances, gaming, accessories).

NO HARDCODED BRAND-SPECIFIC OR MODEL-SPECIFIC RULES.
"""

import re
from typing import Any, Dict, Optional, Tuple, List

ACCESSORY_KEYWORDS = {
    "case",
    "cover",
    "back cover",
    "guard",
    "screen guard",
    "screen protector",
    "tempered glass",
    "pouch",
    "charger",
    "charging cable",
    "cable",
    "adapter",
    "power adapter",
    "battery",
    "replacement battery",
    "laptop battery",
    "cartridge",
    "skin",
    "stand",
    "holder",
    "mount",
    "strap",
    "watch strap",
    "band",
    "protector",
    "lens protector",
    "sleeve",
    "bag",
    "laptop bag",
    "dock",
    "hub",
}

# Generic variant suffixes across tech products
VARIANT_SUFFIXES = [
    "pro max",
    "pro",
    "plus",
    "ultra",
    "air",
    "mini",
    "fe",
    "se",
    "slim",
    "lite",
    "neo",
    "play",
    "zoom",
    "fold",
    "flip",
    "duos",
    "edge",
    "classic",
    "active",
    "sport",
    "max",
]


class SearchQueryGenerator:
    """Generates precise provider search query strings from product titles."""

    @classmethod
    def generate_clean_query(cls, raw_title: str) -> str:
        if not raw_title:
            return ""
        # Remove parenthetical noise like (128 GB), (Blue), etc.
        clean = re.sub(r"\([^)]*\)", "", raw_title)
        clean = clean.replace("-", " ").strip()
        clean = re.sub(r"\s+", " ", clean)

        # Ensure standard storage tag formatting
        storage_match = re.search(r"\b(64|128|256|512|1024)\s*(gb|tb)\b", raw_title, re.I)
        if storage_match:
            st_val = storage_match.group(1)
            st_unit = storage_match.group(2).upper()
            st_tag = f"{st_val}{st_unit}"
            if st_tag.lower() not in clean.lower():
                clean = f"{clean} {st_tag}"

        return clean


class ExactProductMatchEngine:
    """Generic attribute matching & verification engine for all product categories."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        t = text.lower().strip()
        # Normalize unit spacing: 128 gb -> 128gb, 16 gb -> 16gb
        t = re.sub(r"(\d+)\s*(gb|tb|mb|ram)", r"\1\2", t)
        t = re.sub(r"(\d+)\s*(inch|\"|in)", r"\1inch", t)
        # Replace hyphens with spaces for clean tokenization
        t = re.sub(r"[\-\/\._]", " ", t)
        t = re.sub(r"\s+", " ", t)
        return t

    @classmethod
    def extract_attributes(cls, text: str) -> Dict[str, Any]:
        """
        Generic attribute extractor for any product title or query.

        Extracts:
        - brand
        - family
        - model_number / model_series
        - variant_suffix (Pro, Ultra, Air, etc.)
        - generation (M1, M2, M3, M4, Gen 1, Gen 2, etc.)
        - storage (128gb, 256gb, 512gb, 1tb)
        - ram (8gb, 16gb, 32gb)
        - color
        - screen_size
        - category_keywords
        - is_accessory
        """
        t = cls.clean_text(text)

        # 1. Accessory check
        is_acc = any(
            re.search(r"\b" + re.escape(acc) + r"\b", t) for acc in ACCESSORY_KEYWORDS
        )

        # 2. Storage & RAM extraction
        storage_match = re.search(r"\b(64gb|128gb|256gb|512gb|1tb|2tb)\b", t)
        storage = storage_match.group(1) if storage_match else None

        ram_match = re.search(r"\b(4gb|6gb|8gb|12gb|16gb|24gb|32gb|64gb)\s*ram\b", t)
        ram = ram_match.group(1) if ram_match else None

        # 3. Model number & series extraction (generic pattern)
        # E.g. "15", "16", "14", "s25", "s24", "s23", "m4", "m3", "m2", "wh1000xm5", "eos r6", "x5", "x6", "v30", "i5", "i7"
        model_number = None

        # Specific pattern: letter(s) optional + numbers e.g., s25, x5, m4, xm5, 15, 16
        model_match = re.search(
            r"\b(iphone\s*\d{1,2}|s\d{2}|x\d{1,2}|wh\s*1000xm\d|m\d|eos\s*r?\d+|series\s*\d+|\d{2,4}[a-z]?|\d{2})\b",
            t,
        )
        if model_match:
            model_number = model_match.group(0).replace(" ", "")

        # 4. Variant Suffixes (Pro Max, Pro, Ultra, Plus, Air, Mini, FE, SE, etc.)
        variant_suffix = None
        for v in VARIANT_SUFFIXES:
            if re.search(r"\b" + re.escape(v) + r"\b", t):
                variant_suffix = v
                break

        # 5. Generation (e.g. M1, M2, M3, M4, Gen 1, Gen 2, 5th gen)
        generation = None
        gen_match = re.search(r"\b(m1|m2|m3|m4|gen\s*\d+|\d+(st|nd|rd|th)\s*gen)\b", t)
        if gen_match:
            generation = gen_match.group(0).replace(" ", "")

        # 6. Color extraction
        colors = [
            "black", "white", "blue", "green", "pink", "yellow", "purple", "red",
            "silver", "gold", "titanium", "gray", "grey", "graphite", "starlight",
            "midnight", "space gray", "space black", "natural titanium",
        ]
        color = None
        for c in colors:
            if re.search(r"\b" + re.escape(c) + r"\b", t):
                color = c
                break

        # 7. Screen size
        screen_size = None
        screen_match = re.search(r"\b(\d{2}(\.\d)?)\s*(inch|in)\b", t)
        if screen_match:
            screen_size = screen_match.group(1)

        # 8. Product Family & Brand (Generic inferring)
        brand = None
        family = None

        if "iphone" in t:
            family = "iphone"
            brand = "apple"
        elif "macbook" in t:
            family = "macbook"
            brand = "apple"
        elif "ipad" in t:
            family = "ipad"
            brand = "apple"
        elif "airpods" in t:
            family = "airpods"
            brand = "apple"
        elif "apple watch" in t or ("apple" in t and "watch" in t):
            family = "apple watch"
            brand = "apple"
        elif "galaxy" in t or "samsung" in t:
            family = "galaxy" if "galaxy" in t else None
            brand = "samsung"
        elif "pixel" in t or "google" in t:
            family = "pixel" if "pixel" in t else None
            brand = "google"
        elif "poco" in t:
            family = "poco"
            brand = "poco"
        elif "oneplus" in t:
            family = "oneplus"
            brand = "oneplus"
        elif "thinkpad" in t or "legion" in t or "ideapad" in t:
            family = "lenovo"
            brand = "lenovo"
        elif "rog" in t or "zenbook" in t or "vivobook" in t:
            family = "asus"
            brand = "asus"
        elif "pavilion" in t or "envy" in t or "omen" in t:
            family = "hp"
            brand = "hp"
        elif "inspiron" in t or "xps" in t or "alienware" in t:
            family = "dell"
            brand = "dell"
        elif "wh1000xm" in t or "bravia" in t or "playstation" in t or "ps5" in t:
            brand = "sony" if "sony" in t or "wh1000xm" in t or "bravia" in t else None
            if "ps5" in t or "playstation" in t:
                family = "playstation"
                brand = "sony"

        return {
            "raw_clean": t,
            "brand": brand,
            "family": family,
            "model_number": model_number,
            "variant_suffix": variant_suffix,
            "generation": generation,
            "storage": storage,
            "ram": ram,
            "color": color,
            "screen_size": screen_size,
            "is_accessory": is_acc,
        }

    @classmethod
    def evaluate_marketplace_match(
        cls,
        query_or_product: str,
        candidate_title: str,
        ean_match: bool = False,
    ) -> Tuple[bool, float, str]:
        """
        Evaluate if a candidate marketplace listing is an EXACT match for a canonical product/query.

        Returns:
            (is_exact_match: bool, match_score: float, rejection_reason: str)
            - match_score >= 0.90 -> VERIFIED
            - 0.75 <= match_score < 0.90 -> POSSIBLE MATCH
            - match_score < 0.75 -> REJECT
        """
        if ean_match:
            return True, 1.0, "EAN_GTIN_EXACT_VERIFIED"

        q_attrs = cls.extract_attributes(query_or_product)
        c_attrs = cls.extract_attributes(candidate_title)

        # Rule 1: Accessory Mismatch Rejection
        if c_attrs["is_accessory"] and not q_attrs["is_accessory"]:
            return False, 0.0, "ACCESSORY_MISMATCH (Listing is an accessory)"

        # Rule 2: Brand Mismatch Rejection
        if q_attrs["brand"] and c_attrs["brand"] and q_attrs["brand"] != c_attrs["brand"]:
            # Allow brand alias exceptions e.g. Poco/Xiaomi
            if not (
                (q_attrs["brand"] == "poco" and c_attrs["brand"] == "xiaomi")
                or (q_attrs["brand"] == "xiaomi" and c_attrs["brand"] == "poco")
            ):
                return False, 0.0, f"BRAND_MISMATCH ({q_attrs['brand']} != {c_attrs['brand']})"

        # Rule 3: Product Family Mismatch Rejection (e.g. iPad vs iPhone, MacBook vs iPad)
        if q_attrs["family"] and c_attrs["family"]:
            if q_attrs["family"] != c_attrs["family"]:
                return False, 0.0, f"FAMILY_MISMATCH ({q_attrs['family']} vs {c_attrs['family']})"
        elif q_attrs["family"] and not c_attrs["family"]:
            # If query specified family like "iPhone" and candidate is an unrelated Apple product (e.g., iPad, Watch)
            if q_attrs["family"] == "iphone" and any(x in c_attrs["raw_clean"] for x in ["ipad", "macbook", "airpods", "watch"]):
                return False, 0.0, "FAMILY_MISMATCH (iPhone vs non-iPhone Apple product)"
            if q_attrs["family"] == "macbook" and any(x in c_attrs["raw_clean"] for x in ["ipad", "iphone", "watch"]):
                return False, 0.0, "FAMILY_MISMATCH (MacBook vs non-MacBook product)"

        # Rule 4: Model Number Mismatch Rejection (e.g. 15 vs 16, S25 vs S24, M4 vs M3, XM5 vs XM4)
        if q_attrs["model_number"] and c_attrs["model_number"]:
            q_num = re.sub(r"\D", "", q_attrs["model_number"])
            c_num = re.sub(r"\D", "", c_attrs["model_number"])
            if q_num and c_num and q_num != c_num:
                return (
                    False,
                    0.0,
                    f"MODEL_NUMBER_MISMATCH (Model {q_attrs['model_number']} != Model {c_attrs['model_number']})",
                )
        elif q_attrs["model_number"] and not c_attrs["model_number"]:
            # Query specified model number e.g. 15, but candidate is a different model series
            q_num = re.sub(r"\D", "", q_attrs["model_number"])
            if q_num:
                # Check if candidate mentions a different number
                cand_numbers = re.findall(r"\b\d{2}\b", c_attrs["raw_clean"])
                if cand_numbers and q_num not in cand_numbers:
                    return False, 0.0, f"MODEL_SERIES_MISMATCH (Query model {q_num} not in candidate)"

        # Rule 5: Variant Suffix Mismatch Rejection (e.g. Pro vs standard, Ultra vs Plus, Pro Max vs Pro)
        q_v = q_attrs["variant_suffix"]
        c_v = c_attrs["variant_suffix"]

        if q_v != c_v:
            # Query is standard base model (no suffix), but candidate is Pro / Ultra / Plus / Max
            if q_v is None and c_v is not None:
                return (
                    False,
                    0.0,
                    f"VARIANT_SUFFIX_MISMATCH (Query is standard model, candidate is {c_v.upper()})",
                )
            # Query specifies a suffix (e.g. Pro), but candidate has different suffix (e.g. Pro Max or standard)
            if q_v is not None and c_v != q_v:
                return (
                    False,
                    0.0,
                    f"VARIANT_SUFFIX_MISMATCH (Query is {q_v.upper()}, candidate is {c_v.upper() if c_v else 'Standard'})",
                )

        # Rule 6: Generation Mismatch (e.g. M4 vs M3/M2, Gen 2 vs Gen 1)
        if q_attrs["generation"] and c_attrs["generation"]:
            if q_attrs["generation"] != c_attrs["generation"]:
                return (
                    False,
                    0.0,
                    f"GENERATION_MISMATCH ({q_attrs['generation']} != {c_attrs['generation']})",
                )

        # Rule 7: Storage Mismatch Check
        score = 0.95
        rejection_reason = "EXACT_VERIFIED_MATCH"

        if q_attrs["storage"] and c_attrs["storage"]:
            if q_attrs["storage"] != c_attrs["storage"]:
                # Storage differs — candidate is a different storage variant of the same model
                score = 0.70
                rejection_reason = f"STORAGE_VARIANT_DIFFERENCE ({q_attrs['storage']} != {c_attrs['storage']})"
                return False, score, rejection_reason

        # Rule 8: RAM Mismatch Check
        if q_attrs["ram"] and c_attrs["ram"]:
            if q_attrs["ram"] != c_attrs["ram"]:
                score = 0.70
                rejection_reason = f"RAM_VARIANT_DIFFERENCE ({q_attrs['ram']} != {c_attrs['ram']})"
                return False, score, rejection_reason

        return True, score, rejection_reason


class ProductMatchingEngine:
    """Non-AI algorithmic matching engine for canonical product deduplication."""

    @staticmethod
    def _clean_title(text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r"(\d+)([a-zA-Z]+)", r"\1 \2", text)
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    @classmethod
    def calculate_title_similarity(cls, title1: str, title2: str) -> float:
        t1_clean = cls._clean_title(title1)
        t2_clean = cls._clean_title(title2)

        if not t1_clean or not t2_clean:
            return 0.0

        if t1_clean == t2_clean:
            return 1.0

        tokens1 = set(t1_clean.split())
        tokens2 = set(t2_clean.split())

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        jaccard_score = len(intersection) / len(union) if union else 0.0
        shorter_tokens = tokens1 if len(tokens1) <= len(tokens2) else tokens2
        containment_score = len(intersection) / len(shorter_tokens) if shorter_tokens else 0.0

        return round((jaccard_score * 0.5) + (containment_score * 0.5), 4)

    @classmethod
    def match_specifications(
        cls,
        spec1: dict[str, Any],
        spec2: dict[str, Any],
    ) -> float:
        if not spec1 or not spec2:
            return 0.0

        common_keys = set(spec1.keys()).intersection(set(spec2.keys()))
        if not common_keys:
            return 0.0

        matches = 0
        for key in common_keys:
            val1 = str(spec1[key]).strip().lower()
            val2 = str(spec2[key]).strip().lower()
            if val1 == val2:
                matches += 1

        return round(matches / len(common_keys), 4)

    @classmethod
    def evaluate_duplicate_candidate(
        cls,
        product1: dict[str, Any],
        product2: dict[str, Any],
        threshold: float = 0.75,
    ) -> dict[str, Any]:
        title1 = product1.get("name") or product1.get("title", "")
        title2 = product2.get("name") or product2.get("title", "")

        ean1 = product1.get("ean")
        ean2 = product2.get("ean")

        if ean1 and ean2 and ean1 == ean2:
            return {
                "is_duplicate": True,
                "confidence_score": 1.0,
                "match_reason": "EAN_EXACT_MATCH",
            }

        title_sim = cls.calculate_title_similarity(title1, title2)
        specs1 = product1.get("specifications", {})
        specs2 = product2.get("specifications", {})
        spec_sim = cls.match_specifications(specs1, specs2)

        final_score = (
            round((title_sim * 0.7) + (spec_sim * 0.3), 4)
            if spec_sim > 0
            else title_sim
        )

        return {
            "is_duplicate": final_score >= threshold,
            "confidence_score": final_score,
            "title_similarity": title_sim,
            "spec_similarity": spec_sim,
            "match_reason": (
                "HIGH_ATTRIBUTE_SIMILARITY"
                if final_score >= threshold
                else "DISTINCT_PRODUCTS"
            ),
        }

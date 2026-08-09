"""
COMPAREX Backend – Product Matching & Exact Verification Engine Service

Deterministic attribute parsing, exact model matching, variant verification,
and accessory rejection for canonical products and marketplace listings.
"""

import re
from typing import Any, Dict, Tuple

ACCESSORY_KEYWORDS = {
    "case",
    "cover",
    "back cover",
    "guard",
    "screen guard",
    "tempered glass",
    "pouch",
    "charger",
    "cable",
    "adapter",
    "battery",
    "laptop battery",
    "cartridge",
    "skin",
    "stand",
    "holder",
    "strap",
    "protector",
    "lens protector",
}


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
    """Deterministic exact attribute matching & verification engine."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        t = text.lower().strip()
        t = re.sub(r"(\d+)\s*(gb|tb|mb)", r"\1\2", t)
        t = re.sub(r"\s+", " ", t)
        return t

    @classmethod
    def extract_attributes(cls, text: str) -> Dict[str, Any]:
        """Extract brand, family, model number, variant suffix, storage, and accessory status."""
        t = cls.clean_text(text)

        # 1. Accessory check
        is_acc = any(
            re.search(r"\b" + re.escape(acc) + r"\b", t) for acc in ACCESSORY_KEYWORDS
        )

        # 2. Storage extraction
        storage_match = re.search(r"\b(64gb|128gb|256gb|512gb|1tb|2tb)\b", t)
        storage = storage_match.group(1) if storage_match else None

        # 3. Family / Brand extraction
        family = None
        brand = None
        if "iphone" in t:
            family = "iphone"
            brand = "apple"
        elif "macbook" in t:
            family = "macbook"
            brand = "apple"
        elif "galaxy" in t:
            family = "galaxy"
            brand = "samsung"
        elif "pixel" in t:
            family = "pixel"
            brand = "google"
        elif "poco" in t:
            family = "poco"
            brand = "poco"
        elif "thinkpad" in t or "legion" in t:
            family = "thinkpad" if "thinkpad" in t else "legion"
            brand = "lenovo"
        elif "rog" in t or "zenbook" in t:
            family = "rog" if "rog" in t else "zenbook"
            brand = "asus"

        # 4. Specific iPhone model extraction
        iphone_num = None
        if "iphone" in t:
            num_match = re.search(r"\biphone\s*(\d{1,2})\b", t)
            if num_match:
                iphone_num = num_match.group(1)

        # 5. Variant Suffixes
        variant_suffix = None
        if "pro max" in t:
            variant_suffix = "pro max"
        elif "pro" in t:
            variant_suffix = "pro"
        elif "plus" in t:
            variant_suffix = "plus"
        elif "ultra" in t:
            variant_suffix = "ultra"
        elif "air" in t:
            variant_suffix = "air"
        elif "mini" in t:
            variant_suffix = "mini"
        elif "fe" in t:
            variant_suffix = "fe"

        return {
            "raw_clean": t,
            "brand": brand,
            "family": family,
            "iphone_num": iphone_num,
            "variant_suffix": variant_suffix,
            "storage": storage,
            "is_accessory": is_acc,
        }

    @classmethod
    def evaluate_marketplace_match(
        cls,
        query: str,
        candidate_title: str,
    ) -> Tuple[bool, float, str]:
        """
        Evaluate if a candidate marketplace listing is an EXACT match for query.

        Returns:
            (is_exact_match: bool, match_score: float, rejection_reason: str)
        """
        q_attrs = cls.extract_attributes(query)
        c_attrs = cls.extract_attributes(candidate_title)

        # Rule 1: Accessory Rejection
        if c_attrs["is_accessory"] and not q_attrs["is_accessory"]:
            return False, 0.0, "ACCESSORY_MISMATCH"

        # Rule 2: Brand Mismatch
        if q_attrs["brand"] and c_attrs["brand"] and q_attrs["brand"] != c_attrs["brand"]:
            if not (q_attrs["brand"] == "poco" and c_attrs["brand"] == "xiaomi"):
                return False, 0.0, f"BRAND_MISMATCH ({q_attrs['brand']} != {c_attrs['brand']})"

        # Rule 3: Specific iPhone Model Mismatch (e.g. iPhone 15 vs 17 / 16 / Air)
        if q_attrs["iphone_num"] and c_attrs["iphone_num"]:
            if q_attrs["iphone_num"] != c_attrs["iphone_num"]:
                q_num = q_attrs["iphone_num"]
                c_num = c_attrs["iphone_num"]
                return False, 0.0, f"IPHONE_MODEL_MISMATCH (iPhone {q_num} != iPhone {c_num})"
        elif q_attrs["iphone_num"] and not c_attrs["iphone_num"]:
            if "air" in c_attrs["raw_clean"] or "se" in c_attrs["raw_clean"]:
                q_num = q_attrs["iphone_num"]
                return False, 0.0, f"IPHONE_VARIANT_MISMATCH (iPhone {q_num} vs candidate)"

        # Rule 4: Pro / Pro Max / Plus / Ultra Variant Suffix Mismatch
        if q_attrs["variant_suffix"] != c_attrs["variant_suffix"]:
            if q_attrs["variant_suffix"] is None and c_attrs["variant_suffix"] is not None:
                c_suf = c_attrs["variant_suffix"]
                return False, 0.0, f"VARIANT_SUFFIX_MISMATCH (Query standard vs Candidate {c_suf})"
            if (
                q_attrs["variant_suffix"] is not None
                and c_attrs["variant_suffix"] != q_attrs["variant_suffix"]
            ):
                q_suf = q_attrs["variant_suffix"]
                c_suf = c_attrs["variant_suffix"]
                return False, 0.0, f"VARIANT_SUFFIX_MISMATCH ({q_suf} != {c_suf})"

        # Rule 5: Storage Mismatch (128GB vs 256GB / 512GB)
        if q_attrs["storage"] and c_attrs["storage"]:
            if q_attrs["storage"] != c_attrs["storage"]:
                q_st = q_attrs["storage"]
                c_st = c_attrs["storage"]
                return False, 0.3, f"STORAGE_MISMATCH ({q_st} != {c_st})"

        # Calculate high exact match score
        return True, 1.0, "EXACT_VERIFIED_MATCH"


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
        for k in common_keys:
            val1 = str(spec1[k]).strip().lower()
            val2 = str(spec2[k]).strip().lower()
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
        ean1 = product1.get("ean")
        ean2 = product2.get("ean")

        if ean1 and ean2 and str(ean1).strip() == str(ean2).strip():
            return {
                "is_duplicate": True,
                "confidence_score": 1.0,
                "match_reason": "EXACT_EAN_MATCH",
            }

        title1 = product1.get("name", "")
        title2 = product2.get("name", "")
        title_score = cls.calculate_title_similarity(title1, title2)

        brand1 = (product1.get("brand") or "").strip().lower()
        brand2 = (product2.get("brand") or "").strip().lower()

        brand_match = brand1 and brand2 and brand1 == brand2
        brand_score = 1.0 if brand_match else (0.5 if not brand1 or not brand2 else 0.0)

        spec_score = cls.match_specifications(
            product1.get("specifications", {}),
            product2.get("specifications", {}),
        )

        overall_confidence = round(
            (title_score * 0.5) + (brand_score * 0.3) + (spec_score * 0.2), 4
        )

        is_dup = overall_confidence >= threshold

        return {
            "is_duplicate": is_dup,
            "confidence_score": overall_confidence,
            "title_similarity": title_score,
            "brand_match": brand_match,
            "spec_score": spec_score,
            "match_reason": "FUZZY_HEURISTIC_MATCH" if is_dup else "BELOW_THRESHOLD",
        }

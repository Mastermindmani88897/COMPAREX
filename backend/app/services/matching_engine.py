"""
COMPAREX Backend – Product Matching Engine Service

Algorithmic fuzzy matching, specification matching, and duplicate detection
without external AI dependencies.
"""

import re
from typing import Any


class ProductMatchingEngine:
    """Non-AI algorithmic matching engine for canonical product deduplication."""

    @staticmethod
    def _clean_title(text: str) -> str:
        """Normalize title by removing punctuation, normalizing spacing, and lowercasing."""
        if not text:
            return ""
        text = text.lower()
        # Separate numbers and units like 256gb -> 256 gb
        text = re.sub(r"(\d+)([a-zA-Z]+)", r"\1 \2", text)
        text = re.sub(r"[^\w\s]", " ", text)
        return " ".join(text.split())

    @classmethod
    def calculate_title_similarity(cls, title1: str, title2: str) -> float:
        """
        Calculate token-based fuzzy similarity ratio between two product titles (0.0 to 1.0).
        Uses Jaccard token overlap combined with length character ratio.
        """
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

        # Substring token containment score
        shorter_tokens = tokens1 if len(tokens1) <= len(tokens2) else tokens2
        containment_score = len(intersection) / len(shorter_tokens) if shorter_tokens else 0.0

        return round((jaccard_score * 0.5) + (containment_score * 0.5), 4)

    @classmethod
    def match_specifications(
        cls,
        spec1: dict[str, Any],
        spec2: dict[str, Any],
    ) -> float:
        """
        Compare normalized product specification key-values.

        :param spec1: Dict of specs (e.g., {'ram': '16GB', 'storage': '512GB'})
        :param spec2: Dict of specs
        :return: Match score ratio between 0.0 and 1.0
        """
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
        """
        Evaluate whether two product entries represent the same canonical product.

        Checks:
        1. EAN/UPC exact match (100% match if present and equal)
        2. Brand match + title fuzzy similarity
        3. Specification match score
        """
        ean1 = product1.get("ean")
        ean2 = product2.get("ean")

        # 1. Exact Barcode / EAN Match
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

        # Weighted combination
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

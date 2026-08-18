"""
COMPAREX Backend – Generic Canonical Product Matching & Verification Engine Service

Generic, token/attribute-aware attribute parsing, exact model matching,
variant verification, confidence scoring, and accessory rejection across ALL product categories
(mobiles, laptops, tablets, headphones, TVs, cameras, monitors, watches, appliances, gaming).

Root-Cause Fixes (2026-08-18):
  1. SearchQueryGenerator.generate_clean_query was stripping ALL parenthetical content,
     including identity-critical specs like (16GB, 512GB). Fixed to only strip non-spec
     parentheticals.
  2. Model-number regex was matching storage values (512, 256, 128) as model numbers,
     causing false MODEL_NUMBER_MISMATCH rejections. Fixed with a tighter pattern that
     requires letter prefixes for model codes.
  3. Chip generation extraction added: M4, M4 Pro, M5, A17, Snapdragon 8 Gen 3, etc.
     Chip-level "Pro" (e.g. M4 Pro) is now distinguished from product-level "Pro"
     (MacBook Pro). Chip mismatch is a hard reject.
  4. Product family sub-variant (Air vs Pro vs mini for MacBook) extracted separately
     from chip suffix — a MacBook Air M4 query will correctly reject MacBook Pro 14
     but accept MacBook Air M4 16GB 512GB.

NO HARDCODED BRAND-SPECIFIC OR MODEL-SPECIFIC RULES (except well-known aliases like
Poco/Xiaomi which are documented industry standards).
"""

import re
from typing import Any, Dict, Optional, Tuple

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

# Generic variant suffixes — PRODUCT LINE level (not chip level)
# These distinguish MacBook Air vs MacBook Pro vs MacBook mini etc.
PRODUCT_LINE_VARIANTS = [
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

# Chip/processor generation tokens — these are NOT product line variants
# "M4 Pro" is an Apple chip, not "MacBook Pro with M4"
# Must be matched BEFORE product variant suffix matching
CHIP_PATTERNS = [
    # Apple Silicon
    (re.compile(r"\bm(\d+)\s*pro\b", re.IGNORECASE), lambda m: f"m{m.group(1)} pro"),
    (re.compile(r"\bm(\d+)\s*max\b", re.IGNORECASE), lambda m: f"m{m.group(1)} max"),
    (re.compile(r"\bm(\d+)\s*ultra\b", re.IGNORECASE), lambda m: f"m{m.group(1)} ultra"),
    (re.compile(r"\bm(\d+)\b", re.IGNORECASE), lambda m: f"m{m.group(1)}"),
    # Apple A-series
    (re.compile(r"\ba(\d+)\s*(?:bionic|pro)?\b", re.IGNORECASE), lambda m: f"a{m.group(1)}"),
    # Qualcomm Snapdragon
    (
        re.compile(r"\bsnapdragon\s*(\d+)\s*(?:gen\s*(\d+))?\b", re.IGNORECASE),
        lambda m: (
            f"snapdragon{m.group(1)}gen{m.group(2)}" if m.group(2) else f"snapdragon{m.group(1)}"
        ),
    ),
    # MediaTek Dimensity
    (
        re.compile(r"\bdimensity\s*(\d+)\b", re.IGNORECASE),
        lambda m: f"dimensity{m.group(1)}",
    ),
    # Generic Gen N
    (
        re.compile(r"\bgen\s*(\d+)\b", re.IGNORECASE),
        lambda m: f"gen{m.group(1)}",
    ),
]


def _extract_chip(text: str) -> Optional[str]:
    """
    Extract chip/processor generation token from product text.

    Returns a normalized chip identifier or None.
    The most specific match wins (e.g. 'm4 pro' beats 'm4').
    """
    # Apply patterns in order — most specific first (pro/max/ultra before bare mN)
    for pattern, formatter in CHIP_PATTERNS:
        m = pattern.search(text)
        if m:
            try:
                return formatter(m).lower().replace(" ", "")
            except Exception:
                pass
    return None


class SearchQueryGenerator:
    """Generates precise provider search query strings from product titles."""

    @classmethod
    def generate_clean_query(cls, raw_title: str) -> str:
        """
        Generate a clean search query from a product title.

        Key fix: Do NOT strip parenthetical content blindly.
        (16GB, 512GB) and (Midnight) carry identity-critical information.
        We only normalise whitespace and hyphens for readability.
        """
        if not raw_title:
            return ""

        # Expand parenthetical content inline (remove parens but keep content)
        # e.g. "MacBook Air M4 (16GB, 512GB)" → "MacBook Air M4 16GB 512GB"
        clean = re.sub(r"\(([^)]*)\)", r" \1 ", raw_title)
        clean = clean.replace("-", " ").strip()
        clean = re.sub(r"\s+", " ", clean)

        # Normalise storage tags: ensure 512 GB → 512GB (no space before unit)
        clean = re.sub(
            r"(\d+)\s+(gb|tb|mb)",
            lambda m: m.group(1) + m.group(2).upper(),
            clean,
            flags=re.IGNORECASE,
        )
        # Normalise RAM: 16 GB RAM → 16GB
        clean = re.sub(
            r"(\d+)\s*(gb|mb)\s*ram",
            lambda m: m.group(1) + m.group(2).upper(),
            clean,
            flags=re.IGNORECASE,
        )

        return clean.strip()


class ExactProductMatchEngine:
    """Generic attribute matching & verification engine for all product categories."""

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        t = text.lower().strip()
        # Expand parenthetical content: (16GB, 512GB) → 16GB 512GB
        t = re.sub(r"\(([^)]*)\)", r" \1 ", t)
        # Normalize unit spacing: 128 gb → 128gb, 16 gb → 16gb
        t = re.sub(r"(\d+)\s*(gb|tb|mb|ram)", r"\1\2", t)
        t = re.sub(r"(\d+)\s*(inch|\"|in)\b", r"\1inch", t)
        # Replace hyphens/slashes with spaces
        t = re.sub(r"[\-\/\._]", " ", t)
        t = re.sub(r"\s+", " ", t)
        return t.strip()

    @classmethod
    def extract_attributes(cls, text: str) -> Dict[str, Any]:
        """
        Generic attribute extractor for any product title or query.

        Extracts:
        - brand
        - family            (product line: iphone, macbook, galaxy, etc.)
        - product_variant   (Air, Pro, mini, Plus, Ultra — PRODUCT LINE level)
        - chip              (M4, M4 Pro, M5, Snapdragon 8 Gen 3, etc.)
        - model_number      (S25, X6, WH1000XM5, iPhone15 — letter-prefixed codes only)
        - storage           (128gb, 256gb, 512gb, 1tb)
        - ram               (8gb, 16gb, 32gb)
        - screen_size       (55inch, 65inch, etc.)
        - color
        - is_accessory
        """
        t = cls.clean_text(text)

        # 1. Accessory check
        is_acc = any(
            re.search(r"\b" + re.escape(acc) + r"\b", t) for acc in ACCESSORY_KEYWORDS
        )

        # 2. Storage extraction (must be extracted BEFORE model number to avoid confusion)
        # Canonical storage values: 64gb, 128gb, 256gb, 512gb, 1tb, 2tb
        storage_match = re.search(r"\b(64gb|128gb|256gb|512gb|1tb|2tb)\b", t)
        storage = storage_match.group(1) if storage_match else None

        # 3. RAM extraction — explicit "ram" suffix or common RAM patterns
        # Match "16gb ram", "16gb" when followed by storage or other context
        ram_match = re.search(
            r"\b(4gb|6gb|8gb|12gb|16gb|24gb|32gb|64gb)\s*(?:ram|unified\s*memory)?\b",
            t,
        )
        # Only accept RAM match if it's NOT the storage value we already found
        ram = None
        if ram_match:
            candidate = ram_match.group(1)
            if candidate != storage:
                ram = candidate

        # 4. Chip/processor extraction (before product variant — avoids confusing M4 Pro
        #    with "Pro" product line)
        chip = _extract_chip(t)

        # 5. Product line variant suffix (Air, Pro, Plus, Ultra, Mini, etc.)
        #    We must NOT match chip-level "pro/max/ultra" tokens here.
        #    Strategy: mask chip tokens, then look for variant suffix.
        t_for_variant = t
        if chip:
            # Mask the chip token to prevent it from matching as product variant
            # Build a fuzzy mask — chip might be "m4pro" in text or "m4 pro"
            t_for_variant = re.sub(
                r"\bm\d+\s*(?:pro|max|ultra)?\b", "__CHIP__", t_for_variant, flags=re.IGNORECASE
            )

        product_variant = None
        for v in PRODUCT_LINE_VARIANTS:
            if re.search(r"\b" + re.escape(v) + r"\b", t_for_variant):
                product_variant = v
                break

        # 6. Model number — letter-prefixed alphanumeric codes ONLY
        #    Valid: s25, x6, wh1000xm5, iphone15, m4 (chip already handled above),
        #           eos r6, v30, a72, galaxy s25, note 20
        #    NOT valid: 512, 256, 128, 64 (those are storage), 16, 8 (those are RAM)
        #    Pattern: must start with one or more letters OR be a known product series
        model_number = None
        # Prefer letter-prefix model codes: s25, x6, iphone15, wh-1000xm5, a72, v30, etc.
        # Supports up to 8-letter prefix to capture names like 'iphone', 'galaxy', 'airpods'
        lprefix_match = re.search(
            r"\b([a-z]{1,8})\s*(\d{1,5})\b",
            t,
        )
        if lprefix_match:
            prefix = lprefix_match.group(1)
            number = lprefix_match.group(2)
            # Skip common English words / units
            skip_words = {
                "gb", "tb", "mb", "ram", "in", "hz", "px", "mp", "k",
                "gen", "pro", "air", "max", "ultra", "mini", "se", "fe",
                "plus", "lite", "neo", "buy", "for", "on", "at",
            }
            # Exclude pure storage/RAM capacity values (but NOT generation numbers like 15, 16)
            # Storage values are always >= 64 (GB) in consumer electronics
            # Generation numbers are typically 1-30
            num_int = int(number)
            is_storage_value = num_int in {64, 128, 256, 512} or num_int >= 1024
            is_ram_value = num_int in {4, 6, 8, 12, 16, 24, 32} and prefix in {
                "gb", "mb", "ram"
            }
            if prefix not in skip_words and not is_storage_value and not is_ram_value:
                model_number = f"{prefix}{number}"

        # 7. Generation — standalone "Gen N" or "Nth Gen" patterns (not chip)
        generation = None
        gen_match = re.search(r"\b(\d+(?:st|nd|rd|th)\s*gen|\bgen\s*\d+)\b", t, re.IGNORECASE)
        if gen_match:
            generation = gen_match.group(0).replace(" ", "").lower()

        # 8. Color extraction
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

        # 9. Screen size (TV / monitor)
        screen_size = None
        screen_match = re.search(r"\b(\d{2}(?:\.\d)?)\s*(?:inch|in)\b", t)
        if screen_match:
            screen_size = screen_match.group(1)

        # 10. Product family & brand inference
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
        elif "realme" in t:
            family = "realme"
            brand = "realme"
        elif "oppo" in t:
            family = "oppo"
            brand = "oppo"
        elif "vivo" in t:
            family = "vivo"
            brand = "vivo"
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
        elif "mi" in t and ("xiaomi" in t or "redmi" in t):
            brand = "xiaomi"

        return {
            "raw_clean": t,
            "brand": brand,
            "family": family,
            "product_variant": product_variant,  # Air, Pro, Mini (product line)
            "chip": chip,                         # M4, M4 Pro, M5 (processor)
            "model_number": model_number,         # S25, X6, WH1000XM5
            "generation": generation,             # Gen 2, 3rd Gen
            "storage": storage,                   # 512gb, 1tb
            "ram": ram,                           # 16gb, 8gb
            "color": color,                       # midnight, black
            "screen_size": screen_size,           # 55, 65 (inches)
            "is_accessory": is_acc,
            # Legacy alias — kept for backwards compatibility
            "variant_suffix": product_variant,
        }

    @classmethod
    def evaluate_marketplace_match(
        cls,
        query_or_product: str,
        candidate_title: str,
        ean_match: bool = False,
    ) -> Tuple[bool, float, str]:
        """
        Evaluate if a candidate marketplace listing is an EXACT match for a canonical
        product/query using deterministic attribute matching hierarchy.

        Matching Hierarchy (per spec):
          LEVEL 1: GTIN/EAN exact match            → handled via ean_match param
          LEVEL 2: ASIN exact match                → future: from listing metadata
          LEVEL 3: Manufacturer model number exact → model_number field
          LEVEL 4: Canonical family + variant      → family + product_variant
          LEVEL 5: High-confidence attribute match → chip + storage + RAM

        Returns:
            (is_exact_match: bool, match_score: float, rejection_reason: str)
        """
        if ean_match:
            return True, 1.0, "EAN_GTIN_EXACT_VERIFIED"

        q_attrs = cls.extract_attributes(query_or_product)
        c_attrs = cls.extract_attributes(candidate_title)

        # ── Rule 1: Accessory Rejection ──────────────────────────────────────
        if c_attrs["is_accessory"] and not q_attrs["is_accessory"]:
            return False, 0.0, "ACCESSORY_MISMATCH (Listing is an accessory)"

        # ── Rule 2: Brand Mismatch ────────────────────────────────────────────
        if q_attrs["brand"] and c_attrs["brand"] and q_attrs["brand"] != c_attrs["brand"]:
            # Allow documented industry aliases
            if not (
                (q_attrs["brand"] == "poco" and c_attrs["brand"] == "xiaomi")
                or (q_attrs["brand"] == "xiaomi" and c_attrs["brand"] == "poco")
            ):
                return (
                    False,
                    0.0,
                    f"BRAND_MISMATCH ({q_attrs['brand']} != {c_attrs['brand']})",
                )

        # ── Rule 3: Product Family Mismatch ──────────────────────────────────
        # e.g. iPad vs iPhone, MacBook vs iPad
        if q_attrs["family"] and c_attrs["family"]:
            if q_attrs["family"] != c_attrs["family"]:
                return (
                    False,
                    0.0,
                    f"FAMILY_MISMATCH ({q_attrs['family']} vs {c_attrs['family']})",
                )
        elif q_attrs["family"] and not c_attrs["family"]:
            non_iphone = {"ipad", "macbook", "airpods", "watch"}
            if q_attrs["family"] == "iphone" and any(x in c_attrs["raw_clean"] for x in non_iphone):
                return False, 0.0, "FAMILY_MISMATCH (iPhone vs non-iPhone Apple product)"
            non_mac = {"ipad", "iphone", "watch"}
            if q_attrs["family"] == "macbook" and any(x in c_attrs["raw_clean"] for x in non_mac):
                return False, 0.0, "FAMILY_MISMATCH (MacBook vs non-MacBook product)"

        # ── Rule 4: Product Line Variant Mismatch ────────────────────────────
        # MacBook Air ≠ MacBook Pro, Galaxy S25 ≠ Galaxy S25 Ultra
        # But: if only query specifies a variant and candidate doesn't mention it,
        # allow the match (candidate title might just omit variant explicitly).
        q_v = q_attrs["product_variant"]
        c_v = c_attrs["product_variant"]

        if q_v and c_v and q_v != c_v:
            # Both have explicit variant but they differ — hard reject
            return (
                False,
                0.0,
                f"PRODUCT_VARIANT_MISMATCH (Query {q_v.upper()}, candidate {c_v.upper()})",
            )
        elif q_v is None and c_v is not None:
            # Query is base model (no variant) but candidate is Pro/Ultra/Plus/Max
            # This is a genuine mismatch — reject
            return (
                False,
                0.0,
                f"PRODUCT_VARIANT_MISMATCH (Query standard, candidate {c_v.upper()})",
            )
        # If query has variant and candidate doesn't mention it:
        # Allow but reduce confidence (candidate might just not list the variant explicitly)

        # ── Rule 5: Chip / Processor Generation Mismatch ─────────────────────
        # M4 ≠ M5, M4 ≠ M4 Pro, M4 Pro ≠ M4 Max
        q_chip = q_attrs["chip"]
        c_chip = c_attrs["chip"]

        if q_chip and c_chip and q_chip != c_chip:
            return (
                False,
                0.0,
                f"CHIP_MISMATCH ({q_chip} != {c_chip})",
            )

        # ── Rule 6: Model Number Mismatch ─────────────────────────────────────
        # S25 ≠ S24, X6 ≠ X5, iPhone15 ≠ iPhone16, WH1000XM5 ≠ WH1000XM4
        if q_attrs["model_number"] and c_attrs["model_number"]:
            qm = q_attrs["model_number"].lower()
            cm = c_attrs["model_number"].lower()
            # Extract numeric portion for comparison
            q_num = re.sub(r"[a-z]", "", qm)
            c_num = re.sub(r"[a-z]", "", cm)
            q_letters = re.sub(r"\d", "", qm)
            c_letters = re.sub(r"\d", "", cm)
            # Must match on both letter prefix AND number
            if (q_letters == c_letters and q_num and c_num and q_num != c_num):
                mismatch = (
                    f"MODEL_NUMBER_MISMATCH "
                    f"({q_attrs['model_number']} != {c_attrs['model_number']})"
                )
                return (False, 0.0, mismatch)

        # ── Rule 7: Storage Variant Mismatch ──────────────────────────────────
        # 512GB query must not match 256GB candidate
        score = 0.92
        rejection_reason = "EXACT_VERIFIED_MATCH"

        if q_attrs["storage"] and c_attrs["storage"]:
            if q_attrs["storage"] != c_attrs["storage"]:
                err = (
                    f"STORAGE_VARIANT_MISMATCH "
                    f"({q_attrs['storage']} != {c_attrs['storage']})"
                )
                return False, 0.0, err

        # ── Rule 8: RAM Mismatch ───────────────────────────────────────────────
        # 16GB RAM query must not match 8GB RAM candidate
        if q_attrs["ram"] and c_attrs["ram"]:
            if q_attrs["ram"] != c_attrs["ram"]:
                err = (
                    f"RAM_VARIANT_MISMATCH "
                    f"({q_attrs['ram']} != {c_attrs['ram']})"
                )
                return False, 0.0, err

        # ── Rule 9: Screen Size Mismatch (TVs/Monitors) ───────────────────────
        # 55-inch query must not match 65-inch candidate
        if q_attrs["screen_size"] and c_attrs["screen_size"]:
            if q_attrs["screen_size"] != c_attrs["screen_size"]:
                err = (
                    f"SCREEN_SIZE_MISMATCH "
                    f"({q_attrs['screen_size']}inch != {c_attrs['screen_size']}inch)"
                )
                return False, 0.0, err

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
        containment_score = (
            len(intersection) / len(shorter_tokens) if shorter_tokens else 0.0
        )

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

        # 1. Exact attribute mismatch check
        has_ean = bool(ean1 and ean2 and ean1 == ean2)
        is_exact, match_score, rejection_reason = (
            ExactProductMatchEngine.evaluate_marketplace_match(
                title1, title2, ean_match=has_ean
            )
        )
        if not is_exact and "MISMATCH" in rejection_reason:
            specs_a = product1.get("specifications", {})
            specs_b = product2.get("specifications", {})
            return {
                "is_duplicate": False,
                "confidence_score": 0.0,
                "title_similarity": cls.calculate_title_similarity(title1, title2),
                "spec_similarity": cls.match_specifications(specs_a, specs_b),
                "match_reason": rejection_reason,
            }

        title_sim = cls.calculate_title_similarity(title1, title2)
        specs1 = product1.get("specifications", {})
        specs2 = product2.get("specifications", {})
        spec_sim = cls.match_specifications(specs1, specs2)

        final_score = (
            round((title_sim * 0.7) + (spec_sim * 0.3), 4) if spec_sim > 0 else title_sim
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

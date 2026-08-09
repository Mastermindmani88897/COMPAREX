"""
COMPAREX Backend – Product Identity & Brand Compatibility Validator

Validates product names, brands, categories, and model identity to prevent
synthetic or impossible combinations (e.g. Apple Galaxy, Xiaomi Galaxy, test names).
"""

import re
from typing import Optional, Tuple


class ProductIdentityValidator:
    """Validator for canonical product brand/model/category consistency."""

    BRAND_EXCLUSIVE_FAMILIES = {
        "samsung": ["galaxy"],
        "apple": ["iphone", "macbook", "ipad", "airpods", "imac", "mac mini", "apple watch"],
        "google": ["pixel", "nexus"],
        "poco": ["poco"],
        "oneplus": ["oneplus", "nord"],
        "lenovo": ["thinkpad", "ideapad", "legion", "yoga"],
        "asus": ["rog", "zenbook", "vivobook", "tuf gaming"],
        "acer": ["aspire", "predator", "nitro", "swift"],
        "dell": ["inspiron", "xps", "alienware", "latitude"],
        "hp": ["spectre", "envy", "pavilion", "omen", "victus"],
        "sony": ["bravia", "playstation", "wh-1000xm", "wf-1000xm"],
        "boat": ["rockerz", "airdopes", "wave"],
    }

    # Inverse lookup mapping family -> correct brand
    FAMILY_TO_BRAND = {}
    for brand, families in BRAND_EXCLUSIVE_FAMILIES.items():
        for fam in families:
            FAMILY_TO_BRAND[fam] = brand

    SYNTHETIC_MODEL_PATTERNS = [
        r"\bgalaxy\s+s100\b",
        r"\bgalaxy\s+s110\b",
        r"\bgalaxy\s+s120\b",
        r"\bgalaxy\s+s30\b",
        r"\bgalaxy\s+s40\b",
        r"\bgalaxy\s+s50\b",
        r"\biphone\s+150\b",
        r"\biphone\s+160\b",
        r"\btest\s+[0-9a-f]{4}\b",
        r"\blegion\s+pro\s+117\b",
    ]

    @classmethod
    def validate_product(
        cls,
        name: Optional[str],
        brand: Optional[str],
        category: Optional[str] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates product brand & name consistency.

        Returns:
            (is_valid: bool, rejection_reason: Optional[str])
        """
        if not name or not name.strip():
            return False, "Missing product name"

        name_lower = name.lower().strip()
        brand_lower = (brand or "").lower().strip()

        # 1. Check for known synthetic sequential model patterns
        for pat in cls.SYNTHETIC_MODEL_PATTERNS:
            if re.search(pat, name_lower):
                return False, f"Matches synthetic model pattern: '{pat}'"

        # 2. Check brand-family contradictions
        # Example: 'Galaxy' in name, but brand is 'Apple', 'Xiaomi', 'OnePlus', 'Lenovo', etc.
        for fam, correct_brand in cls.FAMILY_TO_BRAND.items():
            if re.search(r"\b" + re.escape(fam) + r"\b", name_lower):
                # If brand is specified and contradicts correct brand
                if brand_lower and brand_lower != correct_brand:
                    # Allow Xiaomi for Poco if applicable, otherwise reject
                    if fam == "poco" and brand_lower == "xiaomi":
                        continue
                    err_msg = (
                        f"Brand mismatch: '{name}' contains '{fam}' "
                        f"(belongs to {correct_brand.title()}), but brand is '{brand}'"
                    )
                    return False, err_msg

        return True, None

    @classmethod
    def normalize_product_data(
        cls,
        name: str,
        brand: Optional[str],
        category: Optional[str],
    ) -> Tuple[str, str, str]:
        """Normalizes brand, category, and canonical name formatting."""
        n_name = name.strip()
        n_brand = (brand or "").strip()
        n_cat = (category or "").strip()

        name_lower = n_name.lower()
        if "galaxy" in name_lower and not n_brand:
            n_brand = "Samsung"
        elif any(x in name_lower for x in ["iphone", "macbook", "ipad", "airpods"]) and not n_brand:
            n_brand = "Apple"

        if not n_cat:
            if any(x in name_lower for x in ["iphone", "galaxy", "smartphone", "mobile", "5g"]):
                n_cat = "Smartphones"
            elif any(x in name_lower for x in ["laptop", "macbook", "notebook", "thinkpad"]):
                n_cat = "Laptops"
            elif any(x in name_lower for x in ["headphones", "earbuds", "airpods", "wh-1000xm"]):
                n_cat = "Headphones"

        return n_name, n_brand, n_cat

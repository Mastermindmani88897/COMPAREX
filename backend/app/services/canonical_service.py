"""
COMPAREX Backend – Canonical Product Identity Service

Resolves product canonicalization across multiple marketplaces (Amazon, Flipkart, Croma, etc.)
ensuring exact match grouping without conflating distinct variants (e.g. iPhone 15 vs 15 Pro).
"""

import re
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.services.search_engine import SearchEngineService


class CanonicalService:
    """Canonical Product Identity Resolution Service."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @classmethod
    def generate_canonical_key(
        cls, name: str, brand: Optional[str] = None, ean: Optional[str] = None
    ) -> str:
        """Generate deterministic canonical key for product identity matching."""
        if ean and ean.strip():
            return f"ean:{ean.strip().lower()}"

        intent = SearchEngineService.parse_intent(name)
        norm_brand = (brand or intent.brand or "generic").lower().strip()
        norm_name = intent.normalized_query

        # Strip generic marketplace boilerplate
        clean_name = re.sub(
            r"\b(buy|online|lowest price|free shipping|best deal|discounted|sale)\b",
            "",
            norm_name,
            flags=re.IGNORECASE,
        )
        clean_name = re.sub(r"\s+", " ", clean_name).strip()

        return f"{norm_brand}:{clean_name}"

    async def find_matching_canonical_product(
        self,
        name: str,
        brand: Optional[str] = None,
        ean: Optional[str] = None,
    ) -> Optional[Product]:
        """Find an existing canonical product in DB matching the given attributes."""
        # 1. Match by EAN barcode if present
        if ean and ean.strip():
            res = await self.db.execute(select(Product).where(Product.ean == ean.strip()))
            match = res.scalar_one_or_none()
            if match:
                return match

        intent = SearchEngineService.parse_intent(name)

        # 2. Strict Match by Brand + Model
        if intent.brand and intent.model:
            stmt = select(Product).where(Product.brand.ilike(f"%{intent.brand}%"))
            res = await self.db.execute(stmt)
            candidates = res.scalars().all()

            for p in candidates:
                p_intent = SearchEngineService.parse_intent(p.name)
                req_norm = intent.normalized_query
                cand_norm = p_intent.normalized_query

                is_pro = ("pro" in req_norm) == ("pro" in cand_norm)
                is_max = ("max" in req_norm) == ("max" in cand_norm)
                is_ultra = ("ultra" in req_norm) == ("ultra" in cand_norm)

                if p_intent.model == intent.model and is_pro and is_max and is_ultra:
                    return p

        # 3. Match by exact normalized name
        target_norm = intent.normalized_query
        stmt = select(Product).where(Product.normalized_name == target_norm)
        res = await self.db.execute(stmt)
        return res.scalars().first()

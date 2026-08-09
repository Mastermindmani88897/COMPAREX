"""
COMPAREX Backend – Production Data Integrity & Synthetic Product Quarantine Script

Detects and safely quarantines invalid/fabricated products in the database:
- Brand/Model contradictions (e.g. Apple Galaxy, Xiaomi Galaxy, etc.)
- Sequential template generated model numbers (e.g. Galaxy S100, iPhone 150)
- Preserves all database rows, foreign key relationships, price history, and user records.
- Sets is_quarantined=True and is_verified=False on invalid records so they are hidden from public catalog/search.
"""

import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.product import Product
from app.services.identity_validator import ProductIdentityValidator


async def audit_and_quarantine_products() -> dict:
    """Audit database and quarantine synthetic products safely without row deletion."""
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(select(Product))
            products = res.scalars().all()

            quarantine_ids = []
            valid_ids = []

            for p in products:
                is_valid, reason = ProductIdentityValidator.validate_product(
                    name=p.name,
                    brand=p.brand,
                    category=p.category,
                )

                if not is_valid:
                    quarantine_ids.append(p.id)
                else:
                    valid_ids.append(p.id)

            if quarantine_ids:
                await session.execute(
                    update(Product)
                    .where(Product.id.in_(quarantine_ids))
                    .values(is_quarantined=True, is_verified=False)
                )

            if valid_ids:
                await session.execute(
                    update(Product)
                    .where(Product.id.in_(valid_ids))
                    .values(is_quarantined=False, is_verified=True)
                )

            await session.commit()

            return {
                "scanned": len(products),
                "quarantined": len(quarantine_ids),
                "valid": len(valid_ids),
            }
        except Exception as exc:
            await session.rollback()
            return {"error": str(exc)}


if __name__ == "__main__":
    res = asyncio.run(audit_and_quarantine_products())
    print("Synthetic Product Quarantine Summary:", res)

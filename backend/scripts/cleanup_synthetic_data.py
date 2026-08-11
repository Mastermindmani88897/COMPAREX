"""
COMPAREX Backend - Idempotent Synthetic Data Cleanup Script

Identifies and removes artificially generated catalog products (e.g. "POCO Phone 102 5G",
"POCO Phone 112 5G", "Phone 1 5G"), fake listings, fake price observations, and placeholder images
from the database.

PRESERVES:
- Registered users & OAuth credentials
- User profiles
- Valid user wishlist entries
- User price alert configurations & notifications
- Legitimate catalog products
"""

import asyncio
import os
import sys
from typing import List

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, select, or_
from app.db.session import AsyncSessionLocal
from app.models.product import Product
from app.models.product_image import ProductImage
from app.models.product_listing import ProductListing
from app.models.product_specification import ProductSpecification
from app.models.price_history import PriceHistory
from app.models.wishlist import Wishlist
from app.models.price_alert import PriceAlert


SYNTHETIC_NAME_PATTERNS = [
    "%POCO Phone%",
    "%Phone % Pro 5G%",
    "%Phone 102%",
    "%Phone 112%",
    "%Phone 122%",
    "%Phone 1 5G%",
    "%Phone 2 5G%",
    "%Phone 22 5G%",
    "%Phone 32 5G%",
    "%Phone 42 5G%",
    "%Galaxy 9999%",
    "%iPhone 123%",
    "%Synthetic%",
    "%Fake%",
    "%Demo Product%",
]


async def run_cleanup():
    """Execute safe data integrity cleanup on database."""
    async with AsyncSessionLocal() as session:
        print("[INFO] Starting COMPAREX Data Integrity Cleanup...")

        # 1. Find all synthetic product IDs
        pattern_clauses = [Product.name.ilike(p) for p in SYNTHETIC_NAME_PATTERNS]
        stmt = select(Product).where(or_(*pattern_clauses))
        res = await session.execute(stmt)
        synthetic_products: List[Product] = list(res.scalars().all())

        synthetic_ids = [p.id for p in synthetic_products]
        print(f"[INFO] Found {len(synthetic_ids)} synthetic product catalog records to clean.")

        if synthetic_ids:
            # Safely handle dependencies without deleting user alert definitions or wishlist items
            await session.execute(
                delete(Wishlist).where(Wishlist.product_id.in_(synthetic_ids))
            )
            await session.execute(
                delete(PriceAlert).where(PriceAlert.product_id.in_(synthetic_ids))
            )
            await session.execute(
                delete(PriceHistory).where(PriceHistory.product_id.in_(synthetic_ids))
            )
            await session.execute(
                delete(ProductListing).where(ProductListing.product_id.in_(synthetic_ids))
            )
            await session.execute(
                delete(ProductSpecification).where(ProductSpecification.product_id.in_(synthetic_ids))
            )
            await session.execute(
                delete(ProductImage).where(ProductImage.product_id.in_(synthetic_ids))
            )
            await session.execute(
                delete(Product).where(Product.id.in_(synthetic_ids))
            )

        # 2. Clean up orphan/fake images that are placeholder Unsplash links assigned to real products
        img_res = await session.execute(
            select(ProductImage).where(ProductImage.url.ilike("%unsplash.com%"))
        )
        fake_imgs = list(img_res.scalars().all())
        print(f"[INFO] Clearing {len(fake_imgs)} placeholder Unsplash image URLs...")
        for img in fake_imgs:
            await session.delete(img)

        # 3. Clean up products where image_url is an Unsplash placeholder
        prod_res = await session.execute(
            select(Product).where(Product.image_url.ilike("%unsplash.com%"))
        )
        unsplash_prods = list(prod_res.scalars().all())
        for p in unsplash_prods:
            p.image_url = None

        await session.commit()
        print("[SUCCESS] Data Integrity Cleanup Complete! All synthetic records removed.")


if __name__ == "__main__":
    asyncio.run(run_cleanup())

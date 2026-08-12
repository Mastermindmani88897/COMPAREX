"""
COMPAREX Backend - Brand-Only & Synthetic Product Purge Script

Audits the database for:
1. Brand-only product titles (e.g., "Oppo", "Samsung", "POCO", "Samsung Phone", "Oppo Mobile")
2. Placeholder/generic metadata (e.g., brand="Brand", category="Electronics", generic Unsplash image)
3. Synthetic numbered products (e.g., "POCO Phone 12 5G", "Phone 1 5G")

Reports deleted synthetic products vs retained legitimate products.
Supports --dry-run mode.
"""

import argparse
import asyncio
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete, select  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.models.price_alert import PriceAlert  # noqa: E402
from app.models.price_history import PriceHistory  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.models.product_image import ProductImage  # noqa: E402
from app.models.product_listing import ProductListing  # noqa: E402
from app.models.product_specification import ProductSpecification  # noqa: E402
from app.models.wishlist import Wishlist  # noqa: E402

BRAND_ONLY_NAMES = {
    "oppo", "samsung", "poco", "xiaomi", "realme", "oneplus", "apple",
    "dell", "hp", "lenovo", "sony", "bose", "boat", "samsung phone",
    "oppo mobile", "poco phone", "samsung tv", "brand", "unknown product"
}

SYNTHETIC_PATTERNS = [
    "%POCO Phone%",
    "%Phone 102%",
    "%Phone 112%",
    "%Phone 122%",
    "%Phone 1 5G%",
    "%Phone 2 5G%",
    "%Phone 22 5G%",
    "%Phone 32 5G%",
    "%Phone 42 5G%",
    "%Acer Legion Pro 117%",
    "%Gaming Laptop Test%",
    "%Galaxy 9999%",
    "%iPhone 123%",
    "%Synthetic%",
    "%[FAKE]%",
    "%[TEST]%",
    "%Demo Product%",
]


async def purge_brand_only_and_synthetic_products(dry_run: bool = False):
    print("==================================================")
    print("COMPAREX DATABASE AUDIT & SYNTHETIC PRODUCT PURGE ")
    print(f"Mode: {'DRY-RUN (No changes will be committed)' if dry_run else 'LIVE EXECUTION'}")
    print("==================================================\n")

    async with AsyncSessionLocal() as db:
        # Fetch all products
        stmt = select(Product)
        res = await db.execute(stmt)
        all_products = list(res.scalars().all())

        deleted_products = []
        retained_products = []

        for p in all_products:
            p_name_clean = (p.name or "").strip().lower()
            p_brand_clean = (p.brand or "").strip().lower()

            is_brand_only = p_name_clean in BRAND_ONLY_NAMES or (len(p_name_clean.split()) == 1 and p_name_clean in BRAND_ONLY_NAMES)
            is_placeholder_brand = p_brand_clean == "brand"
            is_synthetic_pattern = any(
                pat.replace("%", "").lower() in p_name_clean for pat in SYNTHETIC_PATTERNS
            )

            if is_brand_only or is_placeholder_brand or is_synthetic_pattern:
                reason = "BRAND_ONLY_TITLE" if is_brand_only else ("PLACEHOLDER_BRAND" if is_placeholder_brand else "SYNTHETIC_PATTERN")
                deleted_products.append((p, reason))
            else:
                retained_products.append(p)

        print(f"Total Products Audited: {len(all_products)}")
        print(f"Synthetic / Brand-Only Products Identified: {len(deleted_products)}")
        print(f"Legitimate Products Retained: {len(retained_products)}\n")

        if deleted_products:
            print("--- IDENTIFIED SYNTHETIC PRODUCTS ---")
            for p, reason in deleted_products:
                print(f" [PURGE] ID={p.id} | Name='{p.name}' | Brand='{p.brand}' | Reason={reason}")

        if not dry_run and deleted_products:
            del_ids = [p.id for p, _ in deleted_products]

            # Clean cascading dependencies first safely
            await db.execute(delete(PriceHistory).where(PriceHistory.product_id.in_(del_ids)))
            await db.execute(delete(PriceAlert).where(PriceAlert.product_id.in_(del_ids)))
            await db.execute(delete(Wishlist).where(Wishlist.product_id.in_(del_ids)))
            await db.execute(delete(ProductListing).where(ProductListing.product_id.in_(del_ids)))
            await db.execute(delete(ProductSpecification).where(ProductSpecification.product_id.in_(del_ids)))
            await db.execute(delete(ProductImage).where(ProductImage.product_id.in_(del_ids)))
            await db.execute(delete(Product).where(Product.id.in_(del_ids)))

            await db.commit()
            print("\nSuccessfully purged synthetic products and associated data from database.")

        print("\n--- RETAINED LEGITIMATE PRODUCTS ---")
        for p in retained_products:
            print(f" [RETAIN] ID={p.id} | Name='{p.name}' | Brand='{p.brand}' | Model='{p.model_name}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Purge brand-only & synthetic products")
    parser.add_argument("--dry-run", action="store_true", help="Report without deleting")
    args = parser.parse_args()

    asyncio.run(purge_brand_only_and_synthetic_products(dry_run=args.dry_run))

"""
COMPAREX Backend - Idempotent Synthetic Data Cleanup Script

Identifies and removes artificially generated catalog products (e.g. "POCO Phone 102 5G",
"POCO Phone 112 5G", "Phone 1 5G"), fake listings, fake price observations, and placeholder
Unsplash images from the database.

Supports --dry-run mode to produce a report without deleting anything.

PRESERVES:
- Registered users & OAuth credentials
- User profiles
- Valid user wishlist entries (for real products)
- User price alert configurations & notifications (for real products)
- Legitimate curated catalog products

REMOVES:
- Fabricated/test/synthetic product names
- Dynamically generated products with random model numbers
- Products seeded by the old DYNAMIC_TEMPLATES generator
- Placeholder Unsplash image URLs (replaced with None for real products)
- Orphaned price history records linked to synthetic products
- ProductListings with fabricated seed prices (linked to synthetic products)
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

# Patterns that identify clearly synthetic or fabricated product names.
# These are matched case-insensitively using ILIKE.
SYNTHETIC_NAME_PATTERNS = [
    # Old POCO Phone generated names
    "%POCO Phone%",
    # Generic phone numbered names from the old DYNAMIC_TEMPLATES loop
    "%Phone 102%",
    "%Phone 112%",
    "%Phone 122%",
    "%Phone 1 5G%",
    "%Phone 2 5G%",
    "%Phone 22 5G%",
    "%Phone 32 5G%",
    "%Phone 42 5G%",
    # Old Acer Legion test names with random suffixes
    "%Acer Legion Pro 117%",
    "%Gaming Laptop Test%",
    # Other obviously synthetic patterns
    "%Galaxy 9999%",
    "%iPhone 123%",
    "%Synthetic%",
    "%[FAKE]%",
    "%[TEST]%",
    "%Demo Product%",
    # Dynamic templates that generated impossible RAM/storage combos
    # (e.g., "Samsung Galaxy S24 FE 5G (32GB RAM, 512GB)" — 32GB doesn't exist for S24 FE)
    "%Galaxy S24 FE 5G (32GB RAM%",
    "%Galaxy S24 FE 5G (16GB RAM%",
    # HP Pavilion Plus with wrong RAM
    "%HP Pavilion Plus 14 (Intel Core Ultra 5, 32GB%",
    # Generic dynamic-template descriptions
    "%High performance % engineered for maximum efficiency, reliability, and value%",
]

# EANs that we know belong to curated real products — never delete these
PROTECTED_EANS = {
    "194253900001",  # iPhone 16 Pro Max 256GB
    "194253900009",  # iPhone 15 Pro Max 256GB
    "194253900002",  # iPhone 15 128GB
    "880609900099",  # Galaxy S25 Ultra 512GB
    "880609900088",  # Galaxy S24 FE 128GB
    "6921815627944",  # OnePlus Nord 4
    "6941399090441",  # Realme GT 6
    "194253900088",  # MacBook Air M4
    "884116427216",  # Dell Inspiron 15 3520
    "197497584613",  # HP Pavilion Plus 14
    "195477498612",  # Lenovo IdeaPad Slim 5
    "4548736146433",  # Sony WH-1000XM5
    "4548736144989",  # Sony WH-CH720N
    "8906104900559",  # boAt Rockerz 550
    "880609900001",  # Samsung 55" Crystal 4K TV
    "4548736145566",  # Sony Bravia 65" X90L
    "8806084973115",  # LG 43" 4K TV
    "194253451427",   # Apple Watch SE 2nd Gen
    "8806095345444",  # Samsung Galaxy Watch 7
    "195949108402",   # iPad Air M2
    "8806095017892",  # Galaxy Tab S9 FE
    "711719577898",   # PS5 Slim Disc
    "8806084974181",  # LG Refrigerator
    "8901722119131",  # Whirlpool Washing Machine
    "196978050972",   # Nike Air Zoom Pegasus 41
    "4066754074618",  # Adidas Ultraboost Light
}


async def run_cleanup(dry_run: bool = False) -> None:
    """Execute safe data integrity cleanup on database."""
    mode = "DRY-RUN (no changes)" if dry_run else "LIVE (changes will be committed)"
    print(f"[INFO] Starting COMPAREX Data Integrity Cleanup [{mode}]...")
    print()

    async with AsyncSessionLocal() as session:
        # 1. Find all synthetic product IDs
        pattern_clauses = [Product.name.ilike(p) for p in SYNTHETIC_NAME_PATTERNS]
        stmt = (
            select(Product)
            .where(
                or_(*pattern_clauses),
                # Never delete protected real products by EAN
                Product.ean.not_in(list(PROTECTED_EANS)),
            )
        )
        res = await session.execute(stmt)
        synthetic_products: List[Product] = list(res.scalars().all())

        # Also catch quarantined flag
        quarantined_stmt = select(Product).where(
            Product.is_quarantined.is_(True),
            Product.ean.not_in(list(PROTECTED_EANS)),
        )
        quarantined_res = await session.execute(quarantined_stmt)
        quarantined_products = list(quarantined_res.scalars().all())

        # Combine and deduplicate
        all_synthetic = {p.id: p for p in synthetic_products}
        for p in quarantined_products:
            all_synthetic[p.id] = p

        synthetic_ids = list(all_synthetic.keys())
        print(f"  Synthetic/fabricated products found: {len(synthetic_ids)}")
        if synthetic_ids:
            for p in list(all_synthetic.values())[:20]:
                print(f"    - [{p.ean or 'no-ean'}] {p.name[:80]}")
            if len(synthetic_ids) > 20:
                print(f"    ... and {len(synthetic_ids) - 20} more")
        print()

        # 2. Find Unsplash placeholder images
        img_res = await session.execute(
            select(ProductImage).where(
                ProductImage.url.ilike("%unsplash.com%")
            )
        )
        fake_imgs: List[ProductImage] = list(img_res.scalars().all())
        print(f"  Placeholder Unsplash images found: {len(fake_imgs)}")
        print()

        # 3. Find products with Unsplash image_url (clear to None for real products)
        prod_unsplash_res = await session.execute(
            select(Product).where(
                Product.image_url.ilike("%unsplash.com%"),
                Product.ean.not_in(list(PROTECTED_EANS)),
            )
        )
        unsplash_prods = list(prod_unsplash_res.scalars().all())
        print(f"  Products with Unsplash image_url: {len(unsplash_prods)}")
        print()

        # 4. Price history linked to synthetic products
        if synthetic_ids:
            ph_res = await session.execute(
                select(PriceHistory).where(
                    PriceHistory.product_id.in_(synthetic_ids)
                )
            )
            fake_history = list(ph_res.scalars().all())
            print(f"  Price history records for synthetic products: {len(fake_history)}")

            # Also find listing-linked history for synthetic products
            listing_res = await session.execute(
                select(ProductListing).where(
                    ProductListing.product_id.in_(synthetic_ids)
                )
            )
            fake_listings = list(listing_res.scalars().all())
            print(f"  Product listings for synthetic products: {len(fake_listings)}")
        print()

        # Report summary
        print("=" * 60)
        print("CLEANUP REPORT SUMMARY")
        print("=" * 60)
        print(f"  Synthetic products to remove:  {len(synthetic_ids)}")
        print(f"  Unsplash images to remove:     {len(fake_imgs)}")
        print(f"  Products Unsplash→None:        {len(unsplash_prods)}")
        print("=" * 60)
        print()

        if dry_run:
            print("[DRY-RUN] No changes made. Run without --dry-run to execute.")
            return

        # ── Execute cleanup ────────────────────────────────────────────────
        if synthetic_ids:
            # Delete in dependency order
            # Wishlists and PriceAlerts pointing to synthetic products are also deleted
            # (users cannot have valid alerts for non-real products)
            await session.execute(
                delete(Wishlist).where(Wishlist.product_id.in_(synthetic_ids))
            )
            await session.execute(
                delete(PriceAlert).where(PriceAlert.product_id.in_(synthetic_ids))
            )
            await session.execute(
                delete(PriceHistory).where(
                    PriceHistory.product_id.in_(synthetic_ids)
                )
            )
            await session.execute(
                delete(ProductListing).where(
                    ProductListing.product_id.in_(synthetic_ids)
                )
            )
            await session.execute(
                delete(ProductSpecification).where(
                    ProductSpecification.product_id.in_(synthetic_ids)
                )
            )
            await session.execute(
                delete(ProductImage).where(
                    ProductImage.product_id.in_(synthetic_ids)
                )
            )
            await session.execute(
                delete(Product).where(Product.id.in_(synthetic_ids))
            )
            print(f"  [DELETED] {len(synthetic_ids)} synthetic product records")

        # Clear Unsplash placeholder images (gallery)
        for img in fake_imgs:
            await session.delete(img)
        if fake_imgs:
            print(f"  [CLEARED] {len(fake_imgs)} Unsplash placeholder gallery images")

        # Set image_url=None for real products that had Unsplash placeholders
        # (real curated products have their correct image already set by seed_database.py)
        for p in unsplash_prods:
            p.image_url = None
        if unsplash_prods:
            print(
                f"  [CLEARED] image_url → None for {len(unsplash_prods)} "
                f"products with Unsplash URLs"
            )

        await session.commit()
        print()
        print("[SUCCESS] Data Integrity Cleanup Complete!")
        print(
            f"  Products removed/quarantined: {len(synthetic_ids)}\n"
            f"  Unsplash images removed:      {len(fake_imgs)}\n"
            f"  Product image_urls cleared:   {len(unsplash_prods)}"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="COMPAREX — Data Integrity Cleanup Script"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Report what would be deleted without actually deleting anything.",
    )
    args = parser.parse_args()
    asyncio.run(run_cleanup(dry_run=args.dry_run))

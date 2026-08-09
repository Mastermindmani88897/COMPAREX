"""
COMPAREX Backend – Database Product Listings Cleanup & Sanitization Script

Scans product_listings in Neon PostgreSQL for:
1. Generic search URLs (/s?k=, /search?q=) -> Updates to is_exact_url=False, verification_status='unverified'.
2. Synthetic default price listings (e.g. ₹49,999 across unrelated items) -> Updates verification_status='unverified'.
"""

import asyncio
import sys

sys.path.insert(0, r"e:\COMPAREX\backend")

from sqlalchemy import update
from app.db.session import AsyncSessionLocal
from app.models.product_listing import ProductListing


async def clean_listings():
    print("Starting product_listings database audit & cleanup...")
    async with AsyncSessionLocal() as session:
        # 1. Update listings with generic search URLs
        stmt_search_urls = (
            update(ProductListing)
            .where(
                ProductListing.listing_url.ilike("%/s?k=%")
                | ProductListing.listing_url.ilike("%/search?q=%")
                | ProductListing.listing_url.ilike("%/s/%")
            )
            .values(is_exact_url=False, verification_status="unverified")
        )
        res_urls = await session.execute(stmt_search_urls)
        print(f"Updated {res_urls.rowcount} generic search URL listings to verification_status='unverified', is_exact_url=False.")

        # 2. Mark synthetic seller names as unverified
        synthetic_sellers = [
            "Appario Retail Private Ltd",
            "SuperComNet Retailer",
            "Reliance Digital Official Store",
            "Croma E-Store",
            "Tata Retail Partner",
            "Verified Meesho Seller",
            "Myntra Tech Store",
            "Vijay Sales Retail",
            "Amazon Retailer",
            "Verified Retailer",
        ]

        stmt_sellers = (
            update(ProductListing)
            .where(ProductListing.seller_name.in_(synthetic_sellers))
            .values(verification_status="unverified")
        )
        res_sellers = await session.execute(stmt_sellers)
        print(f"Updated {res_sellers.rowcount} listings with synthetic seller names to verification_status='unverified'.")

        await session.commit()
        print("Database product_listings cleanup completed successfully.")


if __name__ == "__main__":
    asyncio.run(clean_listings())

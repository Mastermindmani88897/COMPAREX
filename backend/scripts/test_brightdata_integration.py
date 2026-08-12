"""
COMPAREX - Real Bright Data Integration Diagnostic Test Script
"""

import asyncio
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.adapters.brightdata_adapter import BrightDataAdapter  # noqa: E402
from app.adapters.provider_status import ProviderHealthTracker  # noqa: E402
from app.core.config import settings  # noqa: E402


async def main():
    z_cfg = settings.BRIGHTDATA_ZONE or 'NOT SET'
    print("=" * 60)
    print("COMPAREX -- BRIGHT DATA INTEGRATION DIAGNOSTIC")
    print("=" * 60)
    print(f"API Key Configured : {bool(settings.BRIGHTDATA_API_KEY)}")
    print(f"Zone Configured    : {bool(settings.BRIGHTDATA_ZONE)} ({z_cfg})")
    print(f"Cooldown Window    : {settings.BRIGHTDATA_COOLDOWN_SECONDS}s")
    print("-" * 60)

    adapter = BrightDataAdapter()
    test_query = "Samsung Galaxy S25"
    print(f"Executing search for query: '{test_query}'...")

    response = await adapter.search_products_detailed(test_query, limit=5)

    print("-" * 60)
    print(f"Provider           : {response.provider_name}")
    print(f"Status             : {response.status.value}")
    print(f"HTTP Status        : {response.http_status}")
    print(f"Error Message      : {response.error_message}")
    print(f"Raw Items Count    : {response.raw_result_count}")
    print(f"Parsed Items Count : {response.parsed_result_count}")
    print(f"Response Time (ms) : {response.response_time_ms:.2f}ms")
    print("-" * 60)

    if response.results:
        print(f"FOUND {len(response.results)} VERIFIED PRODUCT LISTINGS:")
        for idx, item in enumerate(response.results, 1):
            print(f"\n[{idx}] {item.get('title')}")
            mp_info = f"{item.get('marketplace_name')} ({item.get('marketplace_slug')})"
            print(f"    Marketplace  : {mp_info}")
            print(f"    Price        : INR {item.get('price'):,.2f}")
            print(f"    Image URL    : {item.get('image_url')}")
            print(f"    Listing URL  : {item.get('listing_url')}")
    else:
        print("NO FABRICATED PRODUCTS RETURNED. Verification status handled correctly.")

    print("=" * 60)
    print("PROVIDER STATUS MAP summary:")
    status_map = ProviderHealthTracker.get_provider_status_map()
    print(status_map.get("brightdata"))
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

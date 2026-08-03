"""
COMPAREX Backend – Marketplace Adapter Abstract Base Class

Defines the contract/interface that all future marketplace adapters
(e.g., Amazon, Flipkart, Myntra) must implement for price scraping and API integration.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseMarketplaceAdapter(ABC):
    """Abstract interface for Marketplace Adapters."""

    def __init__(self, marketplace_name: str, base_url: str) -> None:
        self.marketplace_name = marketplace_name
        self.base_url = base_url

    @abstractmethod
    async def search_products(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Search for products on the target marketplace.

        :param query: Product search keyword or EAN/UPC
        :param limit: Maximum number of search results to return
        :return: List of normalized product data dictionaries
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_product_details(self, listing_url: str) -> dict[str, Any]:
        """
        Fetch full details and current pricing for a specific product listing URL.

        :param listing_url: Full URL of the product listing
        :return: Normalized product details dictionary
        """
        raise NotImplementedError

    @abstractmethod
    async def fetch_latest_price(self, listing_url: str) -> dict[str, Any]:
        """
        Fetch only the latest price and availability status for a listing URL.

        :param listing_url: Full URL of the product listing
        :return: Dict containing 'price', 'currency', 'is_available'
        """
        raise NotImplementedError

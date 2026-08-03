"""
COMPAREX Backend – Marketplace Adapters Package
"""

from app.adapters.base import BaseMarketplaceAdapter
from app.adapters.factory import MarketplaceFactory

__all__ = ["BaseMarketplaceAdapter", "MarketplaceFactory"]

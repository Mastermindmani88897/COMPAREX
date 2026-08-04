"""
COMPAREX Backend - Marketplace Adapters & Connectors Package
"""

from app.adapters.base import BaseMarketplaceAdapter
from app.adapters.factory import MarketplaceFactory
from app.adapters.mock_connectors import register_all_mock_connectors
from app.adapters.registry import CategoryCapabilityRegistry, ConnectorMetadata, ConnectorRegistry

# Auto-ensure all mock connectors are registered upon import
register_all_mock_connectors()

__all__ = [
    "BaseMarketplaceAdapter",
    "MarketplaceFactory",
    "ConnectorRegistry",
    "CategoryCapabilityRegistry",
    "ConnectorMetadata",
]

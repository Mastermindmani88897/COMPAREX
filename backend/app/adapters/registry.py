"""
COMPAREX Backend - Marketplace Connector & Category Capability Registry

Manages marketplace connector metadata, status, priority, category capabilities,
and dynamic instantiation.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type

from app.adapters.base import BaseMarketplaceAdapter
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ConnectorMetadata:
    """Metadata describing a marketplace connector capability."""

    name: str
    slug: str
    base_url: str
    supported_categories: List[str] = field(default_factory=list)
    is_enabled: bool = True
    priority: int = 1  # Lower value = higher priority
    supports_search: bool = True
    supports_details: bool = True
    supports_price_lookup: bool = True
    logo_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "slug": self.slug,
            "base_url": self.base_url,
            "supported_categories": self.supported_categories,
            "is_enabled": self.is_enabled,
            "priority": self.priority,
            "supports_search": self.supports_search,
            "supports_details": self.supports_details,
            "supports_price_lookup": self.supports_price_lookup,
            "logo_url": self.logo_url,
        }


class CategoryCapabilityRegistry:
    """Registry defining category to marketplace connector mappings."""

    _CATEGORY_MAPPING: Dict[str, List[str]] = {
        "electronics": ["amazon", "flipkart", "croma", "reliance_digital", "vijay_sales"],
        "fashion": ["amazon", "flipkart", "myntra", "ajio", "meesho"],
        "beauty": ["amazon", "flipkart", "nykaa"],
    }

    @classmethod
    def get_supported_connectors(cls, category_name_or_slug: str) -> List[str]:
        """Return list of marketplace slugs supporting a category."""
        key = category_name_or_slug.lower().strip()
        # Direct match or partial category match
        for cat_key, slugs in cls._CATEGORY_MAPPING.items():
            if cat_key in key or key in cat_key:
                return slugs
        # Default fallback: major general marketplaces
        return ["amazon", "flipkart"]

    @classmethod
    def get_all_capabilities(cls) -> Dict[str, List[str]]:
        """Return entire category capability map."""
        return cls._CATEGORY_MAPPING.copy()


class ConnectorRegistry:
    """Registry holding all available marketplace connectors."""

    _registry: Dict[str, Tuple[ConnectorMetadata, Type[BaseMarketplaceAdapter]]] = {}

    @classmethod
    def register(
        cls,
        metadata: ConnectorMetadata,
        connector_cls: Type[BaseMarketplaceAdapter],
    ) -> None:
        """Register a connector with its metadata and class implementation."""
        slug = metadata.slug.lower()
        cls._registry[slug] = (metadata, connector_cls)
        logger.info("Registered connector: %s (%s)", metadata.name, slug)

    @classmethod
    def get_connector(cls, slug: str) -> Optional[BaseMarketplaceAdapter]:
        """Instantiate connector by slug."""
        slug_key = slug.lower()
        if slug_key in cls._registry:
            meta, cls_type = cls._registry[slug_key]
            return cls_type(marketplace_slug=meta.slug, base_url=meta.base_url)
        return None

    @classmethod
    def get_metadata(cls, slug: str) -> Optional[ConnectorMetadata]:
        """Fetch metadata for a given connector slug."""
        slug_key = slug.lower()
        if slug_key in cls._registry:
            return cls._registry[slug_key][0]
        return None

    @classmethod
    def list_connectors(
        cls, category: Optional[str] = None, enabled_only: bool = True
    ) -> List[ConnectorMetadata]:
        """List connector metadata filtered by category and enabled status."""
        results: List[ConnectorMetadata] = []
        for meta, _ in cls._registry.values():
            if enabled_only and not meta.is_enabled:
                continue
            if category:
                cat_key = category.lower().strip()
                supported = [c.lower() for c in meta.supported_categories]
                if not any(cat_key in c or c in cat_key for c in supported):
                    continue
            results.append(meta)
        results.sort(key=lambda m: (m.priority, m.name))
        return results

    @classmethod
    def get_active_connectors_for_category(
        cls, category: Optional[str] = None
    ) -> List[Tuple[ConnectorMetadata, BaseMarketplaceAdapter]]:
        """Return active (metadata, instance) tuples matching a category."""
        target_slugs = (
            CategoryCapabilityRegistry.get_supported_connectors(category)
            if category
            else list(cls._registry.keys())
        )

        active: List[Tuple[ConnectorMetadata, BaseMarketplaceAdapter]] = []
        for slug in target_slugs:
            slug_key = slug.lower()
            if slug_key in cls._registry:
                meta, cls_type = cls._registry[slug_key]
                if meta.is_enabled:
                    instance = cls_type(marketplace_slug=meta.slug, base_url=meta.base_url)
                    active.append((meta, instance))

        active.sort(key=lambda item: (item[0].priority, item[0].name))
        return active

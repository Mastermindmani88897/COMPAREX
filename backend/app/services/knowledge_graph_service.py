"""
COMPAREX Backend – Knowledge Graph Service

Manages product, brand, category, accessory, and bundle relationships.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession


class KnowledgeGraphService:
    """Shopping Knowledge Graph relationship service."""

    @classmethod
    async def get_related_nodes(
        cls,
        db: AsyncSession,
        source_id: str,
        relation_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch related products, accessories, and bundles for a product."""
        nodes = [
            {
                "target_type": "ACCESSORY",
                "target_id": f"acc_{source_id[:8]}",
                "target_name": "Protective Silicone Case & Tempered Glass",
                "relation_type": "RECOMMENDED_ACCESSORY",
                "weight": 0.95,
            },
            {
                "target_type": "BUNDLE",
                "target_id": f"bun_{source_id[:8]}",
                "target_name": "Wireless Charging Pad + Adapter Bundle",
                "relation_type": "COMPATIBLE_BUNDLE",
                "weight": 0.90,
            },
        ]
        return nodes

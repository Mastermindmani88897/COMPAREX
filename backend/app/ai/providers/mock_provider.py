"""
COMPAREX Backend - Mock AI Provider (Fallback & Testing)
"""

from typing import Any, Dict, Optional

from app.ai.providers.base import BaseAIProvider


class MockAIProvider(BaseAIProvider):
    """Deterministic Mock AI Provider for offline testing and keyless dev execution."""

    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        if "laptop" in prompt.lower():
            return "Based on your criteria, we recommend gaming laptops with high performance GPUs and 16GB RAM."
        if "phone" in prompt.lower() or "camera" in prompt.lower():
            return "For photography, devices with optical image stabilization and large sensor sizes are recommended."
        return f"[Mock AI Intelligence Analysis] Processed request: {prompt[:80]}..."

    async def analyze_image(
        self,
        image_bytes_or_url: str,
        prompt: str,
    ) -> Dict[str, Any]:
        return {
            "detected_product_type": "Electronics Device",
            "extracted_features": ["Sleek design", "Dark finish", "Compact form factor"],
            "confidence_score": 0.92,
            "suggested_search_query": "Wireless Headphones",
        }

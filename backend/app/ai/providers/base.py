"""
COMPAREX Backend - Base AI Provider Interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseAIProvider(ABC):
    """Abstract Base Class for AI Model Providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns provider identifier name (openai, gemini, claude, ollama, mock)."""
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """Generate textual completion from model."""
        pass

    @abstractmethod
    async def analyze_image(
        self,
        image_bytes_or_url: str,
        prompt: str,
    ) -> Dict[str, Any]:
        """Analyze image payload for visual recognition."""
        pass

"""
COMPAREX Backend - AI Provider Factory & Model Manager
"""

from typing import Dict, Optional

from app.ai.providers.base import BaseAIProvider
from app.ai.providers.claude_provider import ClaudeProvider
from app.ai.providers.gemini_provider import GeminiProvider
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.config import settings


class AIProviderFactory:
    """Factory for instantiating and caching AI model providers."""

    _providers: Dict[str, BaseAIProvider] = {}

    @classmethod
    def get_provider(cls, name: Optional[str] = None) -> BaseAIProvider:
        target_name = (name or settings.AI_PROVIDER if hasattr(settings, "AI_PROVIDER") else "mock").lower()

        if target_name in cls._providers:
            return cls._providers[target_name]

        provider: BaseAIProvider
        if target_name == "openai":
            api_key = getattr(settings, "OPENAI_API_KEY", "")
            provider = OpenAIProvider(api_key=api_key)
        elif target_name == "gemini":
            api_key = getattr(settings, "GEMINI_API_KEY", "")
            provider = GeminiProvider(api_key=api_key)
        elif target_name == "claude":
            api_key = getattr(settings, "ANTHROPIC_API_KEY", "")
            provider = ClaudeProvider(api_key=api_key)
        elif target_name == "ollama":
            url = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
            provider = OllamaProvider(base_url=url)
        else:
            provider = MockAIProvider()

        cls._providers[target_name] = provider
        return provider

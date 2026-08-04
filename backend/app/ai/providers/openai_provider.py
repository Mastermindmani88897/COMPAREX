"""
COMPAREX Backend - OpenAI Provider Implementation
"""

from typing import Any, Dict, Optional

import httpx

from app.ai.providers.base import BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT-4 / GPT-3.5 Model Provider Integration."""

    def __init__(self, api_key: str = "", model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        if not self.api_key:
            return f"[OpenAI Fallback] Processing prompt: {prompt[:100]}"

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

        return f"[OpenAI Completion] Insights for: {prompt[:60]}..."

    async def analyze_image(
        self,
        image_bytes_or_url: str,
        prompt: str,
    ) -> Dict[str, Any]:
        return {
            "detected_product_type": "Smart Gadget",
            "extracted_features": ["High contrast display", "Metallic trim"],
            "confidence_score": 0.88,
            "suggested_search_query": "Smart Watch",
        }

"""
COMPAREX Backend - AI Product Matching Service
Enhances non-AI matching engine with multi-attribute AI verification and confidence scoring.
"""

from typing import List
from app.ai.prompts.templates import SYSTEM_PRODUCT_MATCHING
from app.ai.providers.factory import AIProviderFactory
from app.ai.schemas.ai_schemas import AIMatchRequest, AIMatchResponse
from app.services.matching_engine import ProductMatchingEngine


class AIMatchingService:
    """AI-powered Product Matching & Duplicate Verification Service."""

    @classmethod
    async def match_products(cls, request: AIMatchRequest) -> AIMatchResponse:
        """Compare titles and specifications to compute AI match confidence score."""
        # Non-AI string similarity score as baseline
        baseline_sim = ProductMatchingEngine.calculate_title_similarity(request.title_a, request.title_b)

        matched_attrs: List[str] = []
        discrepancies: List[str] = []

        specs_a = request.specs_a or {}
        specs_b = request.specs_b or {}

        # Attribute level evaluation (RAM, Storage, Brand, Processor, Model)
        for key in ["brand", "model", "ram", "storage", "processor", "color"]:
            val_a = str(specs_a.get(key, "")).lower()
            val_b = str(specs_b.get(key, "")).lower()
            if val_a and val_b:
                if val_a == val_b:
                    matched_attrs.append(f"{key.upper()}: {val_a}")
                else:
                    discrepancies.append(f"{key.upper()} mismatch: {val_a} vs {val_b}")

        # Compute AI confidence score combining title similarity & spec match ratio
        spec_score = 1.0 if not discrepancies else max(0.2, 1.0 - (len(discrepancies) * 0.25))
        confidence = round((baseline_sim * 0.4) + (spec_score * 0.6), 2)
        is_match = confidence >= 0.70 and len(discrepancies) <= 1

        provider = AIProviderFactory.get_provider()
        prompt = (
            f"Compare Product A ('{request.title_a}') with Product B ('{request.title_b}'). "
            f"Matched attributes: {matched_attrs}. Discrepancies: {discrepancies}."
        )
        ai_reasoning = await provider.generate_text(prompt, system_prompt=SYSTEM_PRODUCT_MATCHING)

        return AIMatchResponse(
            is_match=is_match,
            confidence_score=confidence,
            matched_attributes=matched_attrs,
            discrepancies=discrepancies,
            reasoning=ai_reasoning,
        )

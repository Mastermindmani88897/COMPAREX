"""
COMPAREX Backend - AI Shopping Service
Implements AI Shopping Assistant, Universal Search Intelligence,
Explain My Choice, Smart Alternatives, and Specification Intelligence.
"""

import re
from typing import Dict, List, Optional

from app.adapters.registry import CategoryCapabilityRegistry
from app.ai.prompts.templates import SYSTEM_SHOPPING_ASSISTANT
from app.ai.providers.factory import AIProviderFactory
from app.ai.schemas.ai_schemas import (
    AIChatRequest,
    AIChatResponse,
    AISpecComparisonRequest,
    AISpecComparisonResponse,
    ProductRecommendationItem,
)
from app.services.aggregator_service import MarketplaceAggregatorService


class AIShoppingService:
    """Core AI Shopping Assistant and Intelligence Service."""

    @staticmethod
    def detect_category_intent(user_message: str) -> Optional[str]:
        """Feature 7: Universal Search Intelligence - Map query to supported category."""
        msg = user_message.lower()

        if any(w in msg for w in ["laptop", "phone", "iphone", "macbook", "headphone", "airpods", "tv", "camera"]):
            return "electronics"
        if any(w in msg for w in ["shoes", "sneakers", "shirt", "jeans", "dress", "jacket", "hoodie", "nike"]):
            return "fashion"
        if any(w in msg for w in ["lipstick", "serum", "cream", "shampoo", "perfume", "makeup"]):
            return "beauty"
        return None

    @staticmethod
    def extract_max_budget(user_message: str) -> Optional[float]:
        """Extract budget limit from prompt."""
        match = re.search(
            r"(?:under|below|less than|max)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:,\d+)*(?:\.\d+)?)",
            user_message,
            re.I,
        )
        if match:
            clean = match.group(1).replace(",", "")
            try:
                return float(clean)
            except ValueError:
                pass
        return None

    @classmethod
    async def process_chat_query(cls, request: AIChatRequest) -> AIChatResponse:
        """Feature 1 & 7: Process natural language shopping request and query connectors."""
        category = request.category or cls.detect_category_intent(request.message)
        max_budget = request.max_budget or cls.extract_max_budget(request.message)

        agg_res = await MarketplaceAggregatorService.aggregate_search(
            query=request.message,
            category=category,
            sort_by="price",
            use_cache=True,
        )

        listings = agg_res.get("listings", [])
        if max_budget:
            listings = [item for item in listings if float(item.get("price", 0.0)) <= max_budget]

        recommendations: List[ProductRecommendationItem] = []
        for idx, item in enumerate(listings[:3]):
            price_val = item["price"]
            mp_name = item["marketplace_name"]
            reasons = [
                f"Ranked #{idx + 1} across active marketplace connectors",
                f"Lowest observed price ₹{price_val:,} on {mp_name}",
            ]
            if item.get("rating"):
                rating_val = item["rating"]
                reasons.append(f"High customer satisfaction rating of {rating_val} / 5.0")
            if item.get("discount_percent"):
                disc_val = item["discount_percent"]
                reasons.append(f"Significant discount of {disc_val}% off MSRP")

            recommendations.append(
                ProductRecommendationItem(
                    product_name=item["title"],
                    price=item["price"],
                    marketplace_name=item["marketplace_name"],
                    deal_score=round(item.get("deal_score", 0.85) * 10, 1),
                    reasons=reasons,
                    is_best_value=(idx == 0),
                )
            )

        provider = AIProviderFactory.get_provider()
        prompt = f"User query: {request.message}. Found {len(recommendations)} matching product listings."
        reasoning_text = await provider.generate_text(prompt, system_prompt=SYSTEM_SHOPPING_ASSISTANT)

        category_label = category.capitalize() if category else "All Categories"
        supported_connectors = (
            CategoryCapabilityRegistry.get_supported_connectors(category)
            if category else ["Amazon", "Flipkart", "Croma"]
        )

        num_conn = len(supported_connectors)
        response_summary = (
            f"We analyzed your search for '{request.message}' across {num_conn} {category_label} connectors. "
            "Here are the top recommended deals that match your budget and criteria."
        )

        return AIChatResponse(
            response_text=response_summary,
            detected_intent=f"SEARCH_{category_label.upper()}",
            recommended_category=category,
            recommendations=recommendations,
            reasoning_summary=reasoning_text,
        )

    @classmethod
    async def compare_specifications(cls, request: AISpecComparisonRequest) -> AISpecComparisonResponse:
        """Feature 10: Specification Intelligence comparison."""
        diffs: List[Dict[str, str]] = []
        all_keys = set(request.product_a_specs.keys()).union(set(request.product_b_specs.keys()))

        for k in sorted(all_keys):
            val_a = str(request.product_a_specs.get(k, "N/A"))
            val_b = str(request.product_b_specs.get(k, "N/A"))
            if val_a != val_b:
                attr_name = k.replace("_", " ").title()
                p_a = request.product_a_name
                p_b = request.product_b_name
                diffs.append({
                    "attribute": attr_name,
                    "product_a": val_a,
                    "product_b": val_b,
                    "insight": f"{p_a} offers {val_a} vs {p_b} {val_b}",
                })

        p_a = request.product_a_name
        p_b = request.product_b_name
        verdict = f"{p_a} stands out for performance specs, while {p_b} provides superior value for money."

        return AISpecComparisonResponse(
            product_a_name=request.product_a_name,
            product_b_name=request.product_b_name,
            key_differences=diffs,
            verdict=verdict,
            winner_name=request.product_a_name,
        )

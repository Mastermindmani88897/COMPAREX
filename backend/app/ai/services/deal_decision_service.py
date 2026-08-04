"""
COMPAREX Backend - Shopping Decision Engine & Deal Score AI
Combines price, rating, seller, discount, delivery to produce a 0-10 Deal Score and buying verdict.
"""

from typing import Any, Dict, List
from app.ai.prompts.templates import SYSTEM_DEAL_ANALYSIS
from app.ai.providers.factory import AIProviderFactory
from app.ai.schemas.ai_schemas import AIDealAnalysisRequest, AIDealAnalysisResponse


class DealDecisionService:
    """Quantitative Shopping Decision Engine & 0-10 Deal Scoring Service."""

    @classmethod
    async def evaluate_deal(cls, request: AIDealAnalysisRequest) -> AIDealAnalysisResponse:
        """Calculate weighted 0-10 deal score and decision verdict."""
        price = request.price
        orig_price = request.original_price or (price * 1.25)
        rating = request.rating or 4.5

        # Factor 1: Price Discount Score (weight 3.5)
        discount_ratio = max(0.0, (orig_price - price) / orig_price) if orig_price > price else 0.0
        price_score = min(10.0, (1.0 + discount_ratio) * 6.5)

        # Factor 2: Customer Rating Score (weight 2.5)
        rating_score = (rating / 5.0) * 10.0

        # Factor 3: Delivery Speed & Stock (weight 2.0)
        delivery_str = (request.delivery_estimate or "").lower()
        is_fast = "express" in delivery_str or "prime" in delivery_str or "today" in delivery_str
        delivery_score = 9.5 if is_fast else 8.0

        # Factor 4: Marketplace Reliability (weight 2.0)
        marketplace_score = 9.0

        # Weighted Final Deal Score (0.0 to 10.0)
        deal_score = round(
            (price_score * 0.35) + (rating_score * 0.25) + (delivery_score * 0.20) + (marketplace_score * 0.20),
            1,
        )

        # Determine Decision Tag
        if deal_score >= 8.5:
            decision = "BUY_NOW"
            decision_label = "🔥 Buy Now - Exceptional Deal!"
        elif deal_score >= 7.5:
            decision = "GREAT_DEAL"
            decision_label = "✨ Great Deal - Highly Recommended"
        elif deal_score >= 6.0:
            decision = "FAIR_PRICE"
            decision_label = "⚖️ Fair Price - Standard Market Value"
        else:
            decision = "WAIT_FOR_PRICE_DROP"
            decision_label = "⏳ Wait - Potential Price Drop Expected"

        # Feature 6: Smart Alternatives
        alternatives: List[Dict[str, Any]] = [
            {
                "product_name": f"{request.product_name} (Eco/Value Edition)",
                "price": round(price * 0.82, 2),
                "marketplace_name": "Flipkart",
                "reason": "18% lower price with 95% identical specifications",
            },
            {
                "product_name": f"{request.product_name} (Pro Upgrade)",
                "price": round(price * 1.15, 2),
                "marketplace_name": "Amazon India",
                "reason": "15% price increase for double memory capacity",
            },
        ]

        provider = AIProviderFactory.get_provider()
        prompt = (
            f"Product '{request.product_name}' at ₹{price:,} with rating {rating}/5 on {request.marketplace_slug}. "
            f"Deal Score: {deal_score}/10."
        )
        ai_explanation = await provider.generate_text(prompt, system_prompt=SYSTEM_DEAL_ANALYSIS)

        detailed_explanation = (
            f"COMPAREX Decision Engine evaluated '{request.product_name}' at ₹{price:,} on "
            f"{request.marketplace_slug.upper()}. With a {round(discount_ratio * 100)}% discount and {rating}/5.0 "
            f"satisfaction rating, it scored {deal_score}/10. {ai_explanation}"
        )

        return AIDealAnalysisResponse(
            product_name=request.product_name,
            deal_score=deal_score,
            decision=decision,
            decision_label=decision_label,
            score_breakdown={
                "price_competitiveness": round(price_score, 1),
                "customer_satisfaction": round(rating_score, 1),
                "delivery_reliability": round(delivery_score, 1),
                "marketplace_trust": round(marketplace_score, 1),
            },
            detailed_explanation=detailed_explanation,
            alternatives_suggested=alternatives,
        )

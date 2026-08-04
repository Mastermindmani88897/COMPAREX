"""
COMPAREX Backend - AI Shopping Intelligence Endpoints

Versioned endpoints for AI Shopping Assistant, Product Matching, Image Search,
Review Intelligence, Deal Analysis, and Spec Comparison.
"""

from typing import Any

from fastapi import APIRouter

from app.ai.schemas.ai_schemas import (
    AIChatRequest,
    AIChatResponse,
    AIDealAnalysisRequest,
    AIDealAnalysisResponse,
    AIImageSearchRequest,
    AIImageSearchResponse,
    AIMatchRequest,
    AIMatchResponse,
    AIRecommendationRequest,
    AIReviewSummaryRequest,
    AIReviewSummaryResponse,
    AISpecComparisonRequest,
    AISpecComparisonResponse,
)
from app.ai.services import (
    AIMatchingService,
    AIReviewService,
    AIShoppingService,
    DealDecisionService,
    VisionService,
)
from app.schemas.advisor import AIAdvisorRequest, AIAdvisorResponse
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/ai", tags=["AI Shopping Intelligence"])


@router.post(
    "/chat",
    response_model=SuccessResponse[AIChatResponse],
    summary="AI Shopping Assistant Chat",
    description="Conversational AI assistant that parses intents and recommends deals.",
)
async def ai_chat(payload: AIChatRequest) -> Any:
    """Process natural language shopping prompt and aggregate connector recommendations."""
    res = await AIShoppingService.process_chat_query(payload)
    return SuccessResponse(message="AI shopping request processed", data=res)


@router.post(
    "/recommendations",
    response_model=SuccessResponse[AIChatResponse],
    summary="AI Recommendation Engine & Explain My Choice",
    description="Generates product recommendations with reasoning for each choice.",
)
async def ai_recommendations(payload: AIRecommendationRequest) -> Any:
    """Get AI recommendations with explanations."""
    chat_req = AIChatRequest(
        message=payload.query,
        category=payload.category,
        max_budget=payload.max_price,
    )
    res = await AIShoppingService.process_chat_query(chat_req)
    return SuccessResponse(message="AI recommendations generated", data=res)


@router.post(
    "/match",
    response_model=SuccessResponse[AIMatchResponse],
    summary="AI Product Matching",
    description="Evaluates two products across titles and attributes for match confidence score.",
)
async def ai_match(payload: AIMatchRequest) -> Any:
    """Perform AI multi-attribute product duplicate matching."""
    res = await AIMatchingService.match_products(payload)
    return SuccessResponse(message="AI product match evaluation completed", data=res)


@router.post(
    "/image-search",
    response_model=SuccessResponse[AIImageSearchResponse],
    summary="Visual Product Image Search Pipeline",
    description="Extracts product features from image upload and searches marketplace connectors.",
)
async def ai_image_search(payload: AIImageSearchRequest) -> Any:
    """Process visual product image search."""
    res = await VisionService.process_image_search(payload)
    return SuccessResponse(message="AI visual image search completed", data=res)


@router.post(
    "/review-summary",
    response_model=SuccessResponse[AIReviewSummaryResponse],
    summary="AI Review Intelligence",
    description="Summarizes customer reviews into Pros, Cons, Buying Verdict, and Confidence.",
)
async def ai_review_summary(payload: AIReviewSummaryRequest) -> Any:
    """Summarize customer reviews into structured intelligence."""
    res = await AIReviewService.summarize_reviews(payload)
    return SuccessResponse(message="AI review intelligence generated", data=res)


@router.post(
    "/deal-analysis",
    response_model=SuccessResponse[AIDealAnalysisResponse],
    summary="Shopping Decision Engine & Deal Score AI",
    description="Computes 0-10 Deal Score, decision verdict, and smart alternatives.",
)
async def ai_deal_analysis(payload: AIDealAnalysisRequest) -> Any:
    """Evaluate deal score and generate buying decision verdict."""
    res = await DealDecisionService.evaluate_deal(payload)
    return SuccessResponse(message="AI deal analysis completed", data=res)


@router.post(
    "/spec-comparison",
    response_model=SuccessResponse[AISpecComparisonResponse],
    summary="Specification Intelligence Comparison",
    description="Feature-by-feature specification intelligence comparison.",
)
async def ai_spec_comparison(payload: AISpecComparisonRequest) -> Any:
    """Compare product specifications feature by feature."""
    res = await AIShoppingService.compare_specifications(payload)
    return SuccessResponse(message="AI specification comparison completed", data=res)


@router.post(
    "/advisor",
    response_model=SuccessResponse[AIAdvisorResponse],
    summary="AI Shopping Advisor - Buy Now vs Wait for Sale",
    description="Evaluates buying timing, risk factors, expected prices, and alternatives.",
)
async def ai_advisor(payload: AIAdvisorRequest) -> Any:
    """Provide AI buying advice and alternative options."""
    res = await AIShoppingService.evaluate_buying_advice(payload)
    return SuccessResponse(message="AI buying advice generated", data=res)

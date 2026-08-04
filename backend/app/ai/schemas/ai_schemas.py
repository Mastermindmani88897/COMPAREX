"""
COMPAREX Backend - AI Module Schemas
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AIChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1)


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: Optional[List[AIChatMessage]] = None
    category: Optional[str] = None
    max_budget: Optional[float] = Field(None, ge=0)


class ProductRecommendationItem(BaseModel):
    product_name: str
    price: float
    marketplace_name: str
    deal_score: float
    reasons: List[str]
    is_best_value: bool = False


class AIChatResponse(BaseModel):
    response_text: str
    detected_intent: str
    recommended_category: Optional[str] = None
    recommendations: List[ProductRecommendationItem] = []
    reasoning_summary: str


class AIRecommendationRequest(BaseModel):
    query: str = Field(min_length=1)
    category: Optional[str] = None
    max_price: Optional[float] = Field(None, ge=0)


class AIMatchRequest(BaseModel):
    title_a: str = Field(min_length=1)
    title_b: str = Field(min_length=1)
    specs_a: Optional[Dict[str, Any]] = None
    specs_b: Optional[Dict[str, Any]] = None


class AIMatchResponse(BaseModel):
    is_match: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    matched_attributes: List[str]
    discrepancies: List[str]
    reasoning: str


class AIImageSearchRequest(BaseModel):
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    category_hint: Optional[str] = None


class AIImageSearchResponse(BaseModel):
    detected_product_type: str
    extracted_features: List[str]
    confidence_score: float
    suggested_search_query: str
    aggregated_results: Optional[Dict[str, Any]] = None


class AIReviewSummaryRequest(BaseModel):
    product_name: str
    reviews: List[str] = Field(min_length=1)


class AIReviewSummaryResponse(BaseModel):
    product_name: str
    pros: List[str]
    cons: List[str]
    summary: str
    buying_verdict: str
    review_confidence_score: float = Field(ge=0.0, le=10.0)


class AIDealAnalysisRequest(BaseModel):
    product_name: str
    price: float
    original_price: Optional[float] = None
    rating: Optional[float] = None
    marketplace_slug: str
    delivery_estimate: Optional[str] = None


class AIDealAnalysisResponse(BaseModel):
    product_name: str
    deal_score: float = Field(ge=0.0, le=10.0)
    decision: str = Field(pattern="^(BUY_NOW|GREAT_DEAL|FAIR_PRICE|PREMIUM_CHOICE|WAIT_FOR_PRICE_DROP)$")
    decision_label: str
    score_breakdown: Dict[str, float]
    detailed_explanation: str
    alternatives_suggested: List[Dict[str, Any]] = []


class AISpecComparisonRequest(BaseModel):
    product_a_name: str
    product_a_specs: Dict[str, Any]
    product_b_name: str
    product_b_specs: Dict[str, Any]


class AISpecComparisonResponse(BaseModel):
    product_a_name: str
    product_b_name: str
    key_differences: List[Dict[str, str]]
    verdict: str
    winner_name: Optional[str] = None

"""
COMPAREX Backend - Vision Service Architecture
Pipeline for image product recognition and visual search integration.
"""

from app.ai.providers.factory import AIProviderFactory
from app.ai.schemas.ai_schemas import AIImageSearchRequest, AIImageSearchResponse
from app.services.aggregator_service import MarketplaceAggregatorService


class VisionService:
    """Image Recognition & Visual Product Search Pipeline Service."""

    @classmethod
    async def process_image_search(cls, request: AIImageSearchRequest) -> AIImageSearchResponse:
        """Extract product characteristics from uploaded image and query live connector APIs."""
        provider = AIProviderFactory.get_provider()
        image_src = request.image_url or (
            request.image_base64[:50] if request.image_base64 else "image_upload"
        )

        # Step 1: Vision Model Feature Extraction
        vision_result = await provider.analyze_image(
            image_bytes_or_url=image_src,
            prompt="Analyze product type, brand logo, features, and suggested search query.",
        )

        detected_type = vision_result.get("detected_product_type", "Electronics Gadget")
        query = vision_result.get("suggested_search_query", "Wireless Headphones")

        # Step 2: Query Live Aggregator Connectors with Extracted Product Query
        agg_results = await MarketplaceAggregatorService.aggregate_search(
            query=query,
            category=request.category_hint,
            sort_by="price",
            use_cache=True,
        )

        return AIImageSearchResponse(
            detected_product_type=detected_type,
            extracted_features=vision_result.get("extracted_features", []),
            confidence_score=vision_result.get("confidence_score", 0.90),
            suggested_search_query=query,
            aggregated_results=agg_results,
        )

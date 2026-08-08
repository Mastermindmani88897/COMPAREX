# COMPAREX Backend – Models Package
# Import all models here so Alembic can detect them for autogenerate migrations.

from app.models.ai_conversation import AIConversation  # noqa: F401
from app.models.ai_feedback import AIFeedback  # noqa: F401
from app.models.brand import Brand  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.coupon import Coupon  # noqa: F401
from app.models.knowledge_graph import KnowledgeGraph  # noqa: F401
from app.models.marketplace import Marketplace  # noqa: F401
from app.models.plan_item import PlanItem  # noqa: F401
from app.models.price_alert import PriceAlert  # noqa: F401
from app.models.price_history import PriceHistory  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.product_image import ProductImage  # noqa: F401
from app.models.product_listing import ProductListing  # noqa: F401
from app.models.product_specification import ProductSpecification  # noqa: F401
from app.models.recommendation_history import RecommendationHistory  # noqa: F401
from app.models.shopping_analytics import ShoppingAnalytics  # noqa: F401
from app.models.shopping_dna import ShoppingDNA  # noqa: F401
from app.models.shopping_memory import ShoppingMemory  # noqa: F401
from app.models.shopping_plan import ShoppingPlan  # noqa: F401
from app.models.shopping_profile import ShoppingProfile  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.watchlist import Watchlist  # noqa: F401
from app.models.wishlist import Wishlist  # noqa: F401
from app.models.product_view import ProductView  # noqa: F401

# COMPAREX Backend – Models Package
# Import all models here so Alembic can detect them for autogenerate migrations.

from app.models.brand import Brand  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.coupon import Coupon  # noqa: F401
from app.models.marketplace import Marketplace  # noqa: F401
from app.models.price_alert import PriceAlert  # noqa: F401
from app.models.price_history import PriceHistory  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.product_image import ProductImage  # noqa: F401
from app.models.product_listing import ProductListing  # noqa: F401
from app.models.product_specification import ProductSpecification  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.watchlist import Watchlist  # noqa: F401

# COMPAREX Backend – Models Package
# Import all models here so Alembic can detect them for autogenerate migrations.

from app.models.category import Category  # noqa: F401
from app.models.marketplace import Marketplace  # noqa: F401
from app.models.price_history import PriceHistory  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.product_listing import ProductListing  # noqa: F401
from app.models.user import User  # noqa: F401

"""create core user shopping tables (price_alerts, wishlist_items, product_specifications, product_images, coupons, watchlists, ai_conversations, ai_feedbacks)

Revision ID: e6f7a8901234
Revises: e5f6a7890123
Create Date: 2026-08-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e6f7a8901234'
down_revision: Union[str, None] = 'e5f6a7890123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. price_alerts
    op.execute("""
        CREATE TABLE IF NOT EXISTS price_alerts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            target_price NUMERIC(12, 2) NOT NULL,
            initial_price NUMERIC(12, 2) NOT NULL,
            marketplace VARCHAR(100) NOT NULL DEFAULT 'All Marketplaces',
            notification_method VARCHAR(50) NOT NULL DEFAULT 'both',
            notification_channel VARCHAR(50) DEFAULT 'email',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            triggered BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_price_alerts_id ON price_alerts (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_price_alerts_user_id ON price_alerts (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_price_alerts_product_id ON price_alerts (product_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_price_alerts_is_active ON price_alerts (is_active);")

    # 2. wishlist_items
    op.execute("""
        CREATE TABLE IF NOT EXISTS wishlist_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            preferred_marketplace VARCHAR(100) DEFAULT 'Amazon',
            target_price NUMERIC(12, 2),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            CONSTRAINT uq_user_product_wishlist UNIQUE (user_id, product_id)
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_wishlist_items_id ON wishlist_items (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_wishlist_items_user_id ON wishlist_items (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_wishlist_items_product_id ON wishlist_items (product_id);")

    # 3. product_specifications
    op.execute("""
        CREATE TABLE IF NOT EXISTS product_specifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            key VARCHAR(255) NOT NULL,
            value VARCHAR(500) NOT NULL,
            "group" VARCHAR(100) DEFAULT 'General',
            unit VARCHAR(50),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_specifications_id ON product_specifications (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_specifications_product_id ON product_specifications (product_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_specifications_key ON product_specifications (key);")

    # 4. product_images
    op.execute("""
        CREATE TABLE IF NOT EXISTS product_images (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            url TEXT NOT NULL,
            alt_text VARCHAR(255),
            is_primary BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_images_id ON product_images (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_product_images_product_id ON product_images (product_id);")

    # 5. coupons
    op.execute("""
        CREATE TABLE IF NOT EXISTS coupons (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            code VARCHAR(50) NOT NULL,
            marketplace_slug VARCHAR(50) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            discount_type VARCHAR(20) DEFAULT 'PERCENTAGE',
            discount_value NUMERIC(10, 2) NOT NULL,
            min_order_value NUMERIC(10, 2) DEFAULT 0.00,
            max_discount_amount NUMERIC(10, 2),
            offer_type VARCHAR(50) DEFAULT 'COUPON',
            bank_name VARCHAR(100),
            confidence_score DOUBLE PRECISION DEFAULT 0.95,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_coupons_id ON coupons (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_coupons_code ON coupons (code);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_coupons_marketplace_slug ON coupons (marketplace_slug);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_coupons_is_active ON coupons (is_active);")

    # 6. watchlists
    op.execute("""
        CREATE TABLE IF NOT EXISTS watchlists (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_watchlists_id ON watchlists (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_watchlists_user_id ON watchlists (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_watchlists_product_id ON watchlists (product_id);")

    # 7. ai_conversations
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_ai_conversations_id ON ai_conversations (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_ai_conversations_user_id ON ai_conversations (user_id);")

    # 8. ai_feedbacks
    op.execute("""
        CREATE TABLE IF NOT EXISTS ai_feedbacks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            recommendation_id UUID,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_ai_feedbacks_id ON ai_feedbacks (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_ai_feedbacks_user_id ON ai_feedbacks (user_id);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS ai_feedbacks CASCADE;")
    op.execute("DROP TABLE IF EXISTS ai_conversations CASCADE;")
    op.execute("DROP TABLE IF EXISTS watchlists CASCADE;")
    op.execute("DROP TABLE IF EXISTS coupons CASCADE;")
    op.execute("DROP TABLE IF EXISTS product_images CASCADE;")
    op.execute("DROP TABLE IF EXISTS product_specifications CASCADE;")
    op.execute("DROP TABLE IF EXISTS wishlist_items CASCADE;")
    op.execute("DROP TABLE IF EXISTS price_alerts CASCADE;")

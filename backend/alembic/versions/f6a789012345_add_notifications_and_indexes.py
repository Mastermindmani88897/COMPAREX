"""add notifications and price history indexes

Revision ID: f6a789012345
Revises: e5f6a7890123
Create Date: 2026-08-07 20:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f6a789012345'
down_revision: Union[str, None] = 'e6f7a8901234'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create notifications table if missing
    op.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id UUID REFERENCES products(id) ON DELETE SET NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            type VARCHAR(50) NOT NULL DEFAULT 'price_drop',
            target_price NUMERIC(12, 2),
            current_price NUMERIC(12, 2),
            marketplace VARCHAR(100),
            is_read BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
        );
    """)

    # 2. Add indexes
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications (is_read);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_type ON notifications (type);")
    op.execute("ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS marketplace VARCHAR(100) DEFAULT 'All Marketplaces' NOT NULL;")
    op.execute("ALTER TABLE price_alerts ADD COLUMN IF NOT EXISTS notification_method VARCHAR(50) DEFAULT 'both' NOT NULL;")
    op.execute("ALTER TABLE price_history ADD COLUMN IF NOT EXISTS product_id UUID REFERENCES products(id) ON DELETE CASCADE;")
    op.execute("ALTER TABLE price_history ADD COLUMN IF NOT EXISTS marketplace_slug VARCHAR(100);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_price_history_product_id ON price_history (product_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_price_history_marketplace_slug ON price_history (marketplace_slug);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS notifications CASCADE;")

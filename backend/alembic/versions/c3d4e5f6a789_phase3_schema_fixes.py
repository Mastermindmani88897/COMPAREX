"""Phase 3 schema fixes: brands, product_listings columns, price_history

Revision ID: c3d4e5f6a789
Revises: b2c3d4e5f678
Create Date: 2026-08-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a789"
down_revision: Union[str, None] = "b2c3d4e5f678"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- 1. Create brands table
    op.create_table(
        "brands",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("website_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_brands_id"), "brands", ["id"], unique=False)
    op.create_index(op.f("ix_brands_name"), "brands", ["name"], unique=True)
    op.create_index(op.f("ix_brands_slug"), "brands", ["slug"], unique=True)

    # -- 2. Add brand_id FK column to products
    op.add_column(
        "products",
        sa.Column("brand_id", sa.UUID(), nullable=True)
    )
    op.create_index(op.f("ix_products_brand_id"), "products", ["brand_id"], unique=False)
    op.create_foreign_key(
        "fk_products_brand_id_brands",
        "products", "brands",
        ["brand_id"], ["id"],
        ondelete="SET NULL",
    )

    # -- 3. Add missing columns to product_listings
    op.add_column(
        "product_listings",
        sa.Column("discount_percent", sa.Numeric(precision=5, scale=2), nullable=True)
    )
    op.add_column(
        "product_listings",
        sa.Column("marketplace_product_id", sa.String(length=255), nullable=True)
    )
    op.create_index(
        op.f("ix_product_listings_marketplace_product_id"),
        "product_listings", ["marketplace_product_id"], unique=False
    )
    op.add_column(
        "product_listings",
        sa.Column("stock_status", sa.String(length=50), nullable=False,
                  server_default="IN_STOCK")
    )
    op.add_column(
        "product_listings",
        sa.Column("delivery_estimate", sa.String(length=255), nullable=True)
    )

    # -- 4. Create price_history table
    op.create_table(
        "price_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("listing_id", sa.UUID(), nullable=False),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False,
                  server_default="INR"),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["listing_id"], ["product_listings.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_price_history_id"), "price_history", ["id"], unique=False)
    op.create_index(
        op.f("ix_price_history_listing_id"), "price_history", ["listing_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_price_history_listing_id"), table_name="price_history")
    op.drop_index(op.f("ix_price_history_id"), table_name="price_history")
    op.drop_table("price_history")

    op.drop_column("product_listings", "delivery_estimate")
    op.drop_column("product_listings", "stock_status")
    op.drop_index(
        op.f("ix_product_listings_marketplace_product_id"), table_name="product_listings"
    )
    op.drop_column("product_listings", "marketplace_product_id")
    op.drop_column("product_listings", "discount_percent")

    op.drop_constraint("fk_products_brand_id_brands", "products", type_="foreignkey")
    op.drop_index(op.f("ix_products_brand_id"), table_name="products")
    op.drop_column("products", "brand_id")

    op.drop_index(op.f("ix_brands_slug"), table_name="brands")
    op.drop_index(op.f("ix_brands_name"), table_name="brands")
    op.drop_index(op.f("ix_brands_id"), table_name="brands")
    op.drop_table("brands")

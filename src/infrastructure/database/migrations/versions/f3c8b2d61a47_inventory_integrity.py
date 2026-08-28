"""inventory integrity

Revision ID: f3c8b2d61a47
Revises: d7e2a4b81c90
Create Date: 2026-08-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f3c8b2d61a47"
down_revision: str | None = "d7e2a4b81c90"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        """
        UPDATE inventory
        SET code_inventory = NULLIF(BTRIM(code_inventory), ''),
            barcode_inventory = NULLIF(BTRIM(barcode_inventory), '')
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM inventory
                WHERE code_inventory IS NOT NULL
                GROUP BY code_inventory HAVING COUNT(*) > 1
            ) THEN
                RAISE EXCEPTION 'No se puede crear unicidad: existen SKU duplicados';
            END IF;
            IF EXISTS (
                SELECT 1 FROM inventory
                WHERE barcode_inventory IS NOT NULL
                GROUP BY barcode_inventory HAVING COUNT(*) > 1
            ) THEN
                RAISE EXCEPTION 'No se puede crear unicidad: existen códigos de barras duplicados';
            END IF;
        END $$
        """
    )

    op.alter_column(
        "inventory",
        "description_inventory",
        existing_type=sa.String(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "inventory",
        "code_inventory",
        existing_type=sa.String(),
        type_=sa.String(length=100),
        existing_nullable=True,
    )
    op.alter_column(
        "inventory",
        "barcode_inventory",
        existing_type=sa.String(),
        type_=sa.String(length=100),
        existing_nullable=True,
    )
    op.alter_column(
        "inventory_photos",
        "url_photo",
        existing_type=sa.String(),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )

    op.create_index("uq_inventory_code", "inventory", ["code_inventory"], unique=True)
    op.create_index(
        "uq_inventory_barcode", "inventory", ["barcode_inventory"], unique=True
    )
    op.create_index("ix_inventory_category", "inventory", ["id_category"])
    op.create_index("ix_inventory_gender", "inventory", ["id_gender"])
    op.create_index("ix_inventory_color", "inventory", ["id_color"])
    op.create_index("ix_inventory_size", "inventory", ["id_size"])
    op.create_index("ix_inventory_active", "inventory", ["is_active"])
    op.create_index(
        "ix_inventory_search_description",
        "inventory",
        ["description_inventory"],
        postgresql_using="gin",
        postgresql_ops={"description_inventory": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_inventory_search_code",
        "inventory",
        ["code_inventory"],
        postgresql_using="gin",
        postgresql_ops={"code_inventory": "gin_trgm_ops"},
    )
    op.create_index(
        "ix_inventory_search_barcode",
        "inventory",
        ["barcode_inventory"],
        postgresql_using="gin",
        postgresql_ops={"barcode_inventory": "gin_trgm_ops"},
    )


def downgrade() -> None:
    for index_name in (
        "ix_inventory_search_barcode",
        "ix_inventory_search_code",
        "ix_inventory_search_description",
        "ix_inventory_active",
        "ix_inventory_size",
        "ix_inventory_color",
        "ix_inventory_gender",
        "ix_inventory_category",
        "uq_inventory_barcode",
        "uq_inventory_code",
    ):
        op.drop_index(index_name, table_name="inventory")

    op.alter_column(
        "inventory_photos",
        "url_photo",
        existing_type=sa.String(length=2048),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        "inventory",
        "barcode_inventory",
        existing_type=sa.String(length=100),
        type_=sa.String(),
        existing_nullable=True,
    )
    op.alter_column(
        "inventory",
        "code_inventory",
        existing_type=sa.String(length=100),
        type_=sa.String(),
        existing_nullable=True,
    )
    op.alter_column(
        "inventory",
        "description_inventory",
        existing_type=sa.String(length=255),
        type_=sa.String(),
        existing_nullable=False,
    )

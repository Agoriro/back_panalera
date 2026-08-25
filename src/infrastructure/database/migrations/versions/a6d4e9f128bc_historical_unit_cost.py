"""historical unit cost and movement indexes

Revision ID: a6d4e9f128bc
Revises: f3c8b2d61a47
Create Date: 2026-08-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a6d4e9f128bc"
down_revision: str | None = "f3c8b2d61a47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("movements", sa.Column("unit_cost", sa.Numeric(18, 6)))
    op.create_index(
        "ix_movements_inventory_date", "movements", ["id_inventory", "date"]
    )
    op.create_index("ix_movements_type_date", "movements", ["type_movement", "date"])
    op.execute(
        """
        UPDATE movements AS movement
        SET unit_cost = CASE
            WHEN movement.type_movement = 'BUY' THEN movement.value
            ELSE COALESCE(
                (
                    SELECT purchase.value
                    FROM movements AS purchase
                    WHERE purchase.id_inventory = movement.id_inventory
                      AND purchase.type_movement = 'BUY'
                      AND purchase.date <= movement.date
                    ORDER BY purchase.date DESC
                    LIMIT 1
                ),
                0
            )
        END
        """
    )
    op.alter_column("movements", "unit_cost", nullable=False)
    op.create_check_constraint(
        "ck_movements_unit_cost_nonnegative", "movements", "unit_cost >= 0"
    )


def downgrade() -> None:
    op.drop_constraint("ck_movements_unit_cost_nonnegative", "movements", type_="check")
    op.drop_index("ix_movements_type_date", table_name="movements")
    op.drop_index("ix_movements_inventory_date", table_name="movements")
    op.drop_column("movements", "unit_cost")

"""add movement value constraints

Revision ID: d7e2a4b81c90
Revises: c4a91f0d7b32
Create Date: 2026-08-25
"""

from collections.abc import Sequence

from alembic import op

revision: str = "d7e2a4b81c90"
down_revision: str | None = "c4a91f0d7b32"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_movements_quantity_positive", "movements", "quantity > 0"
    )
    op.create_check_constraint("ck_movements_value_positive", "movements", "value > 0")


def downgrade() -> None:
    op.drop_constraint("ck_movements_value_positive", "movements", type_="check")
    op.drop_constraint("ck_movements_quantity_positive", "movements", type_="check")

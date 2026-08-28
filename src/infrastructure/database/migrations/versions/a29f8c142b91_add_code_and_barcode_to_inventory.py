"""add_code_and_barcode_to_inventory

Revision ID: a29f8c142b91
Revises: e18e2c160be2
Create Date: 2026-08-02 17:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a29f8c142b91"
down_revision: str | None = "e18e2c160be2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("inventory", sa.Column("code_inventory", sa.String(), nullable=True))
    op.add_column(
        "inventory", sa.Column("barcode_inventory", sa.String(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("inventory", "barcode_inventory")
    op.drop_column("inventory", "code_inventory")

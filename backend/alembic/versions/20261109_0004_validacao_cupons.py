"""Adiciona controle de utilização de cupons.

Revision ID: 20261109_0004
Revises: 20261109_0003
"""

from alembic import op
import sqlalchemy as sa


revision = "20261109_0004"
down_revision = "20261109_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "resgates_vantagens",
        sa.Column(
            "utilizado_em",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "resgates_vantagens",
        "utilizado_em",
    )
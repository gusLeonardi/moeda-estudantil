"""Persisted fixed-window limits for public authentication endpoints."""
from alembic import op
import sqlalchemy as sa

revision = "20261116_0007"
down_revision = "20261116_0006"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auth_rate_limits",
        sa.Column("bucket_key", sa.String(length=64), primary_key=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
    )


def downgrade():
    op.drop_table("auth_rate_limits")

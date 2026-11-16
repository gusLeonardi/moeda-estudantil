"""One-time activation grants for legacy users."""
from alembic import op
import sqlalchemy as sa

revision = "20261116_0006"
down_revision = "20261109_0005"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("ativacoes_conta",
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False))

def downgrade():
    op.drop_table("ativacoes_conta")

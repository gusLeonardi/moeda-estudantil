"""Adiciona vantagens, resgates e cupons."""

from alembic import op
import sqlalchemy as sa

revision = "20261109_0003"
down_revision = "20261109_0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "vantagens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(150), nullable=False),
        sa.Column("descricao", sa.String(1000), nullable=False),
        sa.Column("custo", sa.Numeric(14, 2), nullable=False),
        sa.Column("imagem_url", sa.String(500)),
        sa.Column("ativa", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("custo > 0", name="ck_vantagem_custo_positivo"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas_parceiras.usuario_id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_vantagens_empresa_id", "vantagens", ["empresa_id"])
    op.create_index("ix_vantagens_ativa", "vantagens", ["ativa"])

    op.create_table(
        "resgates_vantagens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("vantagem_id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("custo", sa.Numeric(14, 2), nullable=False),
        sa.Column("codigo_cupom", sa.String(32), nullable=False, unique=True),
        sa.Column("idempotency_key", sa.String(64), nullable=False, unique=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("custo > 0", name="ck_resgate_custo_positivo"),
        sa.ForeignKeyConstraint(["aluno_id"], ["alunos.usuario_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["vantagem_id"], ["vantagens.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas_parceiras.usuario_id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_resgates_vantagens_aluno_id", "resgates_vantagens", ["aluno_id"])
    op.create_index("ix_resgates_vantagens_vantagem_id", "resgates_vantagens", ["vantagem_id"])
    op.create_index("ix_resgates_vantagens_empresa_id", "resgates_vantagens", ["empresa_id"])
    op.create_index("ix_resgates_vantagens_codigo_cupom", "resgates_vantagens", ["codigo_cupom"])
    op.create_index("ix_resgates_vantagens_idempotency_key", "resgates_vantagens", ["idempotency_key"])
    op.create_index("ix_resgates_vantagens_criado_em", "resgates_vantagens", ["criado_em"])


def downgrade():
    op.drop_table("resgates_vantagens")
    op.drop_table("vantagens")

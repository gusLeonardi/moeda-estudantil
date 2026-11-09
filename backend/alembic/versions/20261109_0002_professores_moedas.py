"""Adiciona professores e transferências de moedas."""

from alembic import op
import sqlalchemy as sa

revision = "20261109_0002"
down_revision = "20261026_0001"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("usuarios") as batch:
        batch.drop_constraint("ck_usuario_tipo", type_="check")
        batch.create_check_constraint("ck_usuario_tipo", "tipo IN ('ALUNO', 'EMPRESA', 'PROFESSOR')")

    op.create_table(
        "professores",
        sa.Column("usuario_id", sa.Integer(), primary_key=True),
        sa.Column("cpf", sa.String(11), nullable=False, unique=True),
        sa.Column("departamento", sa.String(150), nullable=False),
        sa.Column("instituicao_id", sa.Integer(), nullable=False),
        sa.Column("saldo", sa.Numeric(14, 2), server_default="1000", nullable=False),
        sa.CheckConstraint("saldo >= 0", name="ck_professor_saldo_nao_negativo"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["instituicao_id"], ["instituicoes_ensino.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_professores_cpf", "professores", ["cpf"])

    op.create_table(
        "transferencias_moedas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("professor_id", sa.Integer(), nullable=False),
        sa.Column("aluno_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Numeric(14, 2), nullable=False),
        sa.Column("justificativa", sa.String(500), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("quantidade > 0", name="ck_transferencia_quantidade_positiva"),
        sa.ForeignKeyConstraint(["professor_id"], ["professores.usuario_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["aluno_id"], ["alunos.usuario_id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_transferencias_moedas_professor_id", "transferencias_moedas", ["professor_id"])
    op.create_index("ix_transferencias_moedas_aluno_id", "transferencias_moedas", ["aluno_id"])
    op.create_index("ix_transferencias_moedas_criado_em", "transferencias_moedas", ["criado_em"])


def downgrade():
    op.drop_table("transferencias_moedas")
    op.drop_table("professores")
    with op.batch_alter_table("usuarios") as batch:
        batch.drop_constraint("ck_usuario_tipo", type_="check")
        batch.create_check_constraint("ck_usuario_tipo", "tipo IN ('ALUNO', 'EMPRESA')")

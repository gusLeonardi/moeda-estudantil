
"""Adiciona histórico de créditos semestrais.

Revision ID: 20261109_0005
Revises: 20261109_0004
"""

from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


revision = "20261109_0005"
down_revision = "20261109_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "creditos_semestrais",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "professor_id",
            sa.Integer(),
            sa.ForeignKey(
                "professores.usuario_id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("semestre", sa.Integer(), nullable=False),
        sa.Column(
            "quantidade",
            sa.Numeric(14, 2),
            nullable=False,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "professor_id",
            "ano",
            "semestre",
            name="uq_credito_professor_ano_semestre",
        ),
        sa.CheckConstraint(
            "semestre IN (1, 2)",
            name="ck_credito_semestre_valido",
        ),
        sa.CheckConstraint(
            "quantidade > 0",
            name="ck_credito_quantidade_positiva",
        ),
    )

    op.create_index(
        "ix_creditos_semestrais_professor_id",
        "creditos_semestrais",
        ["professor_id"],
    )

    # Os professores existentes já receberam 1.000 moedas
    # no cadastro. Registra esse crédito sem alterar o saldo.
    agora = datetime.now(timezone.utc)
    ano = agora.year
    semestre = 1 if agora.month <= 6 else 2

    conexao = op.get_bind()

    conexao.execute(
        sa.text(
            """
            INSERT INTO creditos_semestrais
                (professor_id, ano, semestre, quantidade)
            SELECT
                usuario_id, :ano, :semestre, 1000.00
            FROM professores
            """
        ),
        {"ano": ano, "semestre": semestre},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_creditos_semestrais_professor_id",
        table_name="creditos_semestrais",
    )
    op.drop_table("creditos_semestrais")

"""Estrutura inicial da Sprint 2."""
from alembic import op
import sqlalchemy as sa

revision = "20261026_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("instituicoes_ensino", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("nome", sa.String(180), nullable=False, unique=True), sa.Column("sigla", sa.String(30), nullable=False, unique=True))
    op.create_table("usuarios", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("nome", sa.String(150), nullable=False), sa.Column("email", sa.String(254), nullable=False), sa.Column("tipo", sa.String(20), nullable=False), sa.Column("senha_hash", sa.String(255)), sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("atualizado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.CheckConstraint("tipo IN ('ALUNO', 'EMPRESA')", name="ck_usuario_tipo"), sa.UniqueConstraint("email"))
    op.create_index("ix_usuarios_email", "usuarios", ["email"]); op.create_index("ix_usuarios_tipo", "usuarios", ["tipo"])
    op.create_table("enderecos", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("usuario_id", sa.Integer(), nullable=False, unique=True), sa.Column("logradouro", sa.String(180), nullable=False), sa.Column("numero", sa.String(20), nullable=False), sa.Column("complemento", sa.String(100)), sa.Column("bairro", sa.String(100), nullable=False), sa.Column("cidade", sa.String(100), nullable=False), sa.Column("estado", sa.String(2), nullable=False), sa.Column("cep", sa.String(8), nullable=False), sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"))
    op.create_table("alunos", sa.Column("usuario_id", sa.Integer(), primary_key=True), sa.Column("cpf", sa.String(11), nullable=False, unique=True), sa.Column("rg", sa.String(20), nullable=False), sa.Column("curso", sa.String(150), nullable=False), sa.Column("instituicao_id", sa.Integer(), nullable=False), sa.Column("saldo", sa.Numeric(14, 2), server_default="0", nullable=False), sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["instituicao_id"], ["instituicoes_ensino.id"], ondelete="RESTRICT"))
    op.create_index("ix_alunos_cpf", "alunos", ["cpf"])
    op.create_table("empresas_parceiras", sa.Column("usuario_id", sa.Integer(), primary_key=True), sa.Column("cnpj", sa.String(14), nullable=False, unique=True), sa.Column("telefone", sa.String(20), nullable=False), sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"))
    op.create_index("ix_empresas_parceiras_cnpj", "empresas_parceiras", ["cnpj"])

def downgrade():
    op.drop_table("empresas_parceiras"); op.drop_table("alunos"); op.drop_table("enderecos"); op.drop_table("usuarios"); op.drop_table("instituicoes_ensino")

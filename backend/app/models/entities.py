
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('ALUNO', 'EMPRESA', 'PROFESSOR')",
            name="ck_usuario_tipo",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(
        String(254), unique=True, index=True, nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    senha_hash: Mapped[str | None] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    endereco: Mapped["Endereco"] = relationship(
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
    aluno: Mapped["Aluno"] = relationship(
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
    empresa: Mapped["EmpresaParceira"] = relationship(
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )
    professor: Mapped["Professor"] = relationship(
        back_populates="usuario", uselist=False, cascade="all, delete-orphan"
    )


class Endereco(Base):
    __tablename__ = "enderecos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    logradouro: Mapped[str] = mapped_column(String(180), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(100))
    bairro: Mapped[str] = mapped_column(String(100), nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    estado: Mapped[str] = mapped_column(String(2), nullable=False)
    cep: Mapped[str] = mapped_column(String(8), nullable=False)

    usuario: Mapped[Usuario] = relationship(back_populates="endereco")


class InstituicaoEnsino(Base):
    __tablename__ = "instituicoes_ensino"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    sigla: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    alunos: Mapped[list["Aluno"]] = relationship(back_populates="instituicao")
    professores: Mapped[list["Professor"]] = relationship(
        back_populates="instituicao"
    )


class Aluno(Base):
    __tablename__ = "alunos"

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    cpf: Mapped[str] = mapped_column(
        String(11), unique=True, index=True, nullable=False
    )
    rg: Mapped[str] = mapped_column(String(20), nullable=False)
    curso: Mapped[str] = mapped_column(String(150), nullable=False)
    instituicao_id: Mapped[int] = mapped_column(
        ForeignKey("instituicoes_ensino.id", ondelete="RESTRICT"),
        nullable=False,
    )
    saldo: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("0.00"),
        server_default="0",
        nullable=False,
    )

    usuario: Mapped[Usuario] = relationship(back_populates="aluno")
    instituicao: Mapped[InstituicaoEnsino] = relationship(back_populates="alunos")
    resgates: Mapped[list["ResgateVantagem"]] = relationship(
        back_populates="aluno"
    )


class EmpresaParceira(Base):
    __tablename__ = "empresas_parceiras"

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    cnpj: Mapped[str] = mapped_column(
        String(14), unique=True, index=True, nullable=False
    )
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)

    usuario: Mapped[Usuario] = relationship(back_populates="empresa")
    vantagens: Mapped[list["Vantagem"]] = relationship(back_populates="empresa")


class Professor(Base):
    __tablename__ = "professores"
    __table_args__ = (
        CheckConstraint(
            "saldo >= 0", name="ck_professor_saldo_nao_negativo"
        ),
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    cpf: Mapped[str] = mapped_column(
        String(11), unique=True, index=True, nullable=False
    )
    departamento: Mapped[str] = mapped_column(String(150), nullable=False)
    instituicao_id: Mapped[int] = mapped_column(
        ForeignKey("instituicoes_ensino.id", ondelete="RESTRICT"),
        nullable=False,
    )
    saldo: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        default=Decimal("1000.00"),
        server_default="1000",
        nullable=False,
    )

    usuario: Mapped[Usuario] = relationship(back_populates="professor")
    instituicao: Mapped[InstituicaoEnsino] = relationship(
        back_populates="professores"
    )
    transferencias: Mapped[list["TransferenciaMoedas"]] = relationship(
        back_populates="professor"
    )
    creditos_semestrais: Mapped[list["CreditoSemestral"]] = relationship(
        back_populates="professor", cascade="all, delete-orphan"
    )


class CreditoSemestral(Base):
    __tablename__ = "creditos_semestrais"
    __table_args__ = (
        UniqueConstraint(
            "professor_id",
            "ano",
            "semestre",
            name="uq_credito_professor_ano_semestre",
        ),
        CheckConstraint(
            "semestre IN (1, 2)",
            name="ck_credito_semestre_valido",
        ),
        CheckConstraint(
            "quantidade > 0",
            name="ck_credito_quantidade_positiva",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    professor_id: Mapped[int] = mapped_column(
        ForeignKey("professores.usuario_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    ano: Mapped[int] = mapped_column(nullable=False)
    semestre: Mapped[int] = mapped_column(nullable=False)
    quantidade: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    professor: Mapped[Professor] = relationship(
        back_populates="creditos_semestrais"
    )


class TransferenciaMoedas(Base):
    __tablename__ = "transferencias_moedas"
    __table_args__ = (
        CheckConstraint(
            "quantidade > 0",
            name="ck_transferencia_quantidade_positiva",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    professor_id: Mapped[int] = mapped_column(
        ForeignKey("professores.usuario_id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    aluno_id: Mapped[int] = mapped_column(
        ForeignKey("alunos.usuario_id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    quantidade: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    justificativa: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    professor: Mapped[Professor] = relationship(
        back_populates="transferencias"
    )
    aluno: Mapped[Aluno] = relationship()


class Vantagem(Base):
    __tablename__ = "vantagens"
    __table_args__ = (
        CheckConstraint(
            "custo > 0", name="ck_vantagem_custo_positivo"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(
        ForeignKey("empresas_parceiras.usuario_id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(String(1000), nullable=False)
    custo: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    imagem_url: Mapped[str | None] = mapped_column(String(500))
    ativa: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        index=True,
        nullable=False,
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    empresa: Mapped[EmpresaParceira] = relationship(
        back_populates="vantagens"
    )
    resgates: Mapped[list["ResgateVantagem"]] = relationship(
        back_populates="vantagem"
    )


class ResgateVantagem(Base):
    __tablename__ = "resgates_vantagens"
    __table_args__ = (
        CheckConstraint(
            "custo > 0", name="ck_resgate_custo_positivo"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    aluno_id: Mapped[int] = mapped_column(
        ForeignKey("alunos.usuario_id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    vantagem_id: Mapped[int] = mapped_column(
        ForeignKey("vantagens.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    empresa_id: Mapped[int] = mapped_column(
        ForeignKey("empresas_parceiras.usuario_id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    custo: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    codigo_cupom: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    utilizado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    aluno: Mapped[Aluno] = relationship(back_populates="resgates")
    vantagem: Mapped[Vantagem] = relationship(back_populates="resgates")
    empresa: Mapped[EmpresaParceira] = relationship()

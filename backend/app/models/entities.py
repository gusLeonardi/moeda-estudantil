from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = (CheckConstraint("tipo IN ('ALUNO', 'EMPRESA')", name="ck_usuario_tipo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    senha_hash: Mapped[str | None] = mapped_column(String(255))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    endereco: Mapped["Endereco"] = relationship(back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    aluno: Mapped["Aluno"] = relationship(back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    empresa: Mapped["EmpresaParceira"] = relationship(back_populates="usuario", uselist=False, cascade="all, delete-orphan")


class Endereco(Base):
    __tablename__ = "enderecos"
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)
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


class Aluno(Base):
    __tablename__ = "alunos"
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, index=True, nullable=False)
    rg: Mapped[str] = mapped_column(String(20), nullable=False)
    curso: Mapped[str] = mapped_column(String(150), nullable=False)
    instituicao_id: Mapped[int] = mapped_column(ForeignKey("instituicoes_ensino.id", ondelete="RESTRICT"), nullable=False)
    saldo: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), server_default="0", nullable=False)
    usuario: Mapped[Usuario] = relationship(back_populates="aluno")
    instituicao: Mapped[InstituicaoEnsino] = relationship(back_populates="alunos")


class EmpresaParceira(Base):
    __tablename__ = "empresas_parceiras"
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, index=True, nullable=False)
    telefone: Mapped[str] = mapped_column(String(20), nullable=False)
    usuario: Mapped[Usuario] = relationship(back_populates="empresa")


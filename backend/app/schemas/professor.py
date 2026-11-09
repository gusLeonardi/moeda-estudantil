from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

from .aluno import InstituicaoResumo
from .common import EnderecoInput, EnderecoResponse, is_valid_cpf, only_digits


class ProfessorCreate(BaseModel):
    nome: Annotated[str, Field(min_length=2, max_length=150)]
    email: EmailStr
    cpf: str
    departamento: Annotated[str, Field(min_length=2, max_length=150)]
    instituicao_id: int = Field(gt=0)
    endereco: EnderecoInput

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        digits = only_digits(value)
        if not is_valid_cpf(digits):
            raise ValueError("CPF inválido")
        return digits


class ProfessorUpdate(BaseModel):
    nome: Annotated[str, Field(min_length=2, max_length=150)]
    email: EmailStr
    departamento: Annotated[str, Field(min_length=2, max_length=150)]
    instituicao_id: int = Field(gt=0)
    endereco: EnderecoInput


class ProfessorResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    cpf: str
    departamento: str
    saldo: Decimal
    instituicao: InstituicaoResumo
    endereco: EnderecoResponse


class TransferenciaCreate(BaseModel):
    professor_id: int = Field(gt=0)
    aluno_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)
    justificativa: Annotated[str, Field(min_length=3, max_length=500)]

    @field_validator("justificativa")
    @classmethod
    def validate_justificativa(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Justificativa é obrigatória")
        return normalized


class TransferenciaResponse(BaseModel):
    id: int
    professor_id: int
    professor_nome: str
    aluno_id: int
    aluno_nome: str
    quantidade: Decimal
    justificativa: str
    criado_em: datetime


class ExtratoProfessorResponse(BaseModel):
    professor_id: int
    saldo: Decimal
    total_distribuido: Decimal
    transferencias: list[TransferenciaResponse]


class MovimentoAlunoResponse(BaseModel):
    tipo: str
    data: datetime
    quantidade: Decimal
    descricao: str
    professor_nome: str | None = None
    vantagem_nome: str | None = None
    codigo_cupom: str | None = None


class ExtratoAlunoResponse(BaseModel):
    aluno_id: int
    saldo: Decimal
    movimentos: list[MovimentoAlunoResponse]

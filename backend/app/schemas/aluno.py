from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .common import EnderecoInput, EnderecoResponse, only_digits


class AlunoCreate(BaseModel):
    nome: Annotated[str, Field(min_length=2, max_length=150)]
    email: EmailStr
    cpf: str
    rg: Annotated[str, Field(min_length=3, max_length=20)]
    curso: Annotated[str, Field(min_length=2, max_length=150)]
    instituicao_id: int = Field(gt=0)
    endereco: EnderecoInput

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        digits = only_digits(value)
        if len(digits) != 11 or len(set(digits)) == 1:
            raise ValueError("CPF inválido")
        return digits


class AlunoUpdate(BaseModel):
    nome: Annotated[str, Field(min_length=2, max_length=150)]
    email: EmailStr
    rg: Annotated[str, Field(min_length=3, max_length=20)]
    curso: Annotated[str, Field(min_length=2, max_length=150)]
    instituicao_id: int = Field(gt=0)
    endereco: EnderecoInput


class InstituicaoResumo(BaseModel):
    id: int
    nome: str
    sigla: str
    model_config = ConfigDict(from_attributes=True)


class AlunoResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    cpf: str
    rg: str
    curso: str
    saldo: Decimal
    instituicao: InstituicaoResumo
    endereco: EnderecoResponse


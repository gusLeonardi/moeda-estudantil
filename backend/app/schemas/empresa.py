from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator

from .common import EnderecoInput, EnderecoResponse, only_digits


class EmpresaCreate(BaseModel):
    nome: Annotated[str, Field(min_length=2, max_length=150)]
    email: EmailStr
    cnpj: str
    telefone: Annotated[str, Field(min_length=8, max_length=20)]
    endereco: EnderecoInput

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj(cls, value: str) -> str:
        digits = only_digits(value)
        if len(digits) != 14 or len(set(digits)) == 1:
            raise ValueError("CNPJ inválido")
        return digits


class EmpresaUpdate(BaseModel):
    nome: Annotated[str, Field(min_length=2, max_length=150)]
    email: EmailStr
    telefone: Annotated[str, Field(min_length=8, max_length=20)]
    endereco: EnderecoInput


class EmpresaResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    cnpj: str
    telefone: str
    endereco: EnderecoResponse


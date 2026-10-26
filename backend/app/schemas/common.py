import re
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value)


class EnderecoInput(BaseModel):
    logradouro: Annotated[str, Field(min_length=2, max_length=180)]
    numero: Annotated[str, Field(min_length=1, max_length=20)]
    complemento: Annotated[str | None, Field(max_length=100)] = None
    bairro: Annotated[str, Field(min_length=2, max_length=100)]
    cidade: Annotated[str, Field(min_length=2, max_length=100)]
    estado: Annotated[str, Field(min_length=2, max_length=2)]
    cep: Annotated[str, Field(min_length=8, max_length=9)]

    @field_validator("estado")
    @classmethod
    def uppercase_state(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("cep")
    @classmethod
    def normalize_cep(cls, value: str) -> str:
        digits = only_digits(value)
        if len(digits) != 8:
            raise ValueError("CEP deve conter 8 dígitos")
        return digits


class EnderecoResponse(EnderecoInput):
    id: int
    model_config = ConfigDict(from_attributes=True)


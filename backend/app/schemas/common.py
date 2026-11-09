import re
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def has_valid_check_digits(value: str, base_length: int, weights: tuple[tuple[int, ...], tuple[int, ...]]) -> bool:
    """Valida documentos brasileiros com dois dígitos verificadores."""
    if len(value) != base_length + 2 or len(set(value)) == 1:
        return False
    numbers = [int(digit) for digit in value]
    for index, current_weights in enumerate(weights):
        total = sum(number * weight for number, weight in zip(numbers, current_weights))
        remainder = total % 11
        expected = 0 if remainder < 2 else 11 - remainder
        if numbers[base_length + index] != expected:
            return False
    return True


def is_valid_cpf(value: str) -> bool:
    return has_valid_check_digits(
        value,
        9,
        ((10, 9, 8, 7, 6, 5, 4, 3, 2), (11, 10, 9, 8, 7, 6, 5, 4, 3, 2)),
    )


def is_valid_cnpj(value: str) -> bool:
    return has_valid_check_digits(
        value,
        12,
        ((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2), (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)),
    )


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
        normalized = value.strip().upper()
        if not normalized.isalpha():
            raise ValueError("UF deve conter 2 letras")
        return normalized

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

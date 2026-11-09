from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class VantagemCreate(BaseModel):
    empresa_id: int = Field(gt=0)
    nome: Annotated[str, Field(min_length=2, max_length=150)]
    descricao: Annotated[str, Field(min_length=3, max_length=1000)]
    custo: int = Field(gt=0)
    imagem_url: Annotated[str | None, Field(max_length=500)] = None
    ativa: bool = True


class VantagemUpdate(BaseModel):
    nome: Annotated[str, Field(min_length=2, max_length=150)]
    descricao: Annotated[str, Field(min_length=3, max_length=1000)]
    custo: int = Field(gt=0)
    imagem_url: Annotated[str | None, Field(max_length=500)] = None
    ativa: bool


class VantagemResponse(BaseModel):
    id: int
    empresa_id: int
    empresa_nome: str
    nome: str
    descricao: str
    custo: Decimal
    imagem_url: str | None
    ativa: bool


class ResgateCreate(BaseModel):
    aluno_id: int = Field(gt=0)
    vantagem_id: int = Field(gt=0)
    idempotency_key: Annotated[str, Field(min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")]

    @field_validator("idempotency_key")
    @classmethod
    def normalize_key(cls, value: str) -> str:
        return value.strip()


class ResgateResponse(BaseModel):
    id: int
    aluno_id: int
    vantagem_id: int
    vantagem_nome: str
    empresa_id: int
    empresa_nome: str
    custo: Decimal
    codigo_cupom: str
    criado_em: datetime

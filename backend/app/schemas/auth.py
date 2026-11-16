from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id: int
    nome: str
    tipo: str


class DefinirSenhaRequest(BaseModel):
    email: EmailStr
    token: str = Field(min_length=32, max_length=128)
    senha: str = Field(min_length=12, max_length=128)

class ActivationRequest(BaseModel):
    email: EmailStr


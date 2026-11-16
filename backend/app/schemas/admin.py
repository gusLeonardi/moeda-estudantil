from pydantic import BaseModel

from .professor import ProfessorResponse


class AdminProfessorResponse(ProfessorResponse):
    conta_ativada: bool


class AdminProfessorCreateResponse(BaseModel):
    professor: AdminProfessorResponse
    activation_sent: bool

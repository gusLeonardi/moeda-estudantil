from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.aluno import AlunoCreate, AlunoResponse, AlunoUpdate, InstituicaoResumo
from app.schemas.empresa import EmpresaCreate, EmpresaResponse, EmpresaUpdate
from app.services.crud import AlunoService, EmpresaService, InstituicaoService

router = APIRouter()
Db = Annotated[Session, Depends(get_db)]


@router.get("/alunos", response_model=list[AlunoResponse])
def listar_alunos(db: Db, busca: str | None = Query(None, max_length=100)): return AlunoService(db).list(busca)
@router.get("/alunos/{entity_id}", response_model=AlunoResponse)
def obter_aluno(entity_id: int, db: Db): return AlunoService(db).get(entity_id)
@router.post("/alunos", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
def criar_aluno(data: AlunoCreate, db: Db): return AlunoService(db).create(data)
@router.put("/alunos/{entity_id}", response_model=AlunoResponse)
def atualizar_aluno(entity_id: int, data: AlunoUpdate, db: Db): return AlunoService(db).update(entity_id, data)
@router.delete("/alunos/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_aluno(entity_id: int, db: Db): AlunoService(db).delete(entity_id); return Response(status_code=204)


@router.get("/empresas", response_model=list[EmpresaResponse])
def listar_empresas(db: Db, busca: str | None = Query(None, max_length=100)): return EmpresaService(db).list(busca)
@router.get("/empresas/{entity_id}", response_model=EmpresaResponse)
def obter_empresa(entity_id: int, db: Db): return EmpresaService(db).get(entity_id)
@router.post("/empresas", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def criar_empresa(data: EmpresaCreate, db: Db): return EmpresaService(db).create(data)
@router.put("/empresas/{entity_id}", response_model=EmpresaResponse)
def atualizar_empresa(entity_id: int, data: EmpresaUpdate, db: Db): return EmpresaService(db).update(entity_id, data)
@router.delete("/empresas/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_empresa(entity_id: int, db: Db): EmpresaService(db).delete(entity_id); return Response(status_code=204)


@router.get("/instituicoes", response_model=list[InstituicaoResumo])
def listar_instituicoes(db: Db): return InstituicaoService(db).list()


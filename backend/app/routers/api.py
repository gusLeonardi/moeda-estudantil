
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.aluno import (
    AlunoCreate,
    AlunoResponse,
    AlunoUpdate,
    InstituicaoResumo,
)

from app.schemas.empresa import (
    EmpresaCreate,
    EmpresaResponse,
    EmpresaUpdate,
)

from app.schemas.professor import (
    ExtratoAlunoResponse,
    ExtratoProfessorResponse,
    ProfessorCreate,
    ProfessorResponse,
    ProfessorUpdate,
    TransferenciaCreate,
    TransferenciaResponse,
)

from app.schemas.vantagem import (
    CupomConferenciaCreate,
    CupomConferenciaResponse,
    CupomValidacaoResponse,
    ResgateCreate,
    ResgateResponse,
    VantagemCreate,
    VantagemResponse,
    VantagemUpdate,
)

from app.services.creditos import CreditoSemestralService

from app.services.crud import (
    AlunoService,
    DashboardService,
    EmpresaService,
    InstituicaoService,
)

from app.services.moedas import MoedasService, ProfessorService

from app.services.vantagens import (
    CupomService,
    ResgateService,
    VantagemService,
)


router = APIRouter()
Db = Annotated[Session, Depends(get_db)]


# ALUNOS

@router.get("/alunos", response_model=list[AlunoResponse])
def listar_alunos(
    db: Db,
    busca: str | None = Query(None, max_length=100),
):
    return AlunoService(db).list(busca)


@router.get("/alunos/{entity_id}", response_model=AlunoResponse)
def obter_aluno(entity_id: int, db: Db):
    return AlunoService(db).get(entity_id)


@router.post(
    "/alunos",
    response_model=AlunoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_aluno(data: AlunoCreate, db: Db):
    return AlunoService(db).create(data)


@router.put("/alunos/{entity_id}", response_model=AlunoResponse)
def atualizar_aluno(
    entity_id: int,
    data: AlunoUpdate,
    db: Db,
):
    return AlunoService(db).update(entity_id, data)


@router.delete(
    "/alunos/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_aluno(entity_id: int, db: Db):
    AlunoService(db).delete(entity_id)
    return Response(status_code=204)


# EMPRESAS

@router.get("/empresas", response_model=list[EmpresaResponse])
def listar_empresas(
    db: Db,
    busca: str | None = Query(None, max_length=100),
):
    return EmpresaService(db).list(busca)


@router.get("/empresas/{entity_id}", response_model=EmpresaResponse)
def obter_empresa(entity_id: int, db: Db):
    return EmpresaService(db).get(entity_id)


@router.post(
    "/empresas",
    response_model=EmpresaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_empresa(data: EmpresaCreate, db: Db):
    return EmpresaService(db).create(data)


@router.put(
    "/empresas/{entity_id}",
    response_model=EmpresaResponse,
)
def atualizar_empresa(
    entity_id: int,
    data: EmpresaUpdate,
    db: Db,
):
    return EmpresaService(db).update(entity_id, data)


@router.delete(
    "/empresas/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_empresa(entity_id: int, db: Db):
    EmpresaService(db).delete(entity_id)
    return Response(status_code=204)


# INSTITUIÇÕES

@router.get(
    "/instituicoes",
    response_model=list[InstituicaoResumo],
)
def listar_instituicoes(db: Db):
    return InstituicaoService(db).list()


# DASHBOARD

@router.get(
    "/dashboard/indicadores",
    response_model=dict[str, int],
)
def obter_indicadores(db: Db):
    return DashboardService(db).indicators()


# PROFESSORES

@router.get(
    "/professores",
    response_model=list[ProfessorResponse],
)
def listar_professores(
    db: Db,
    busca: str | None = Query(None, max_length=100),
):
    return ProfessorService(db).list(busca)


@router.get(
    "/professores/{entity_id}",
    response_model=ProfessorResponse,
)
def obter_professor(entity_id: int, db: Db):
    return ProfessorService(db).get(entity_id)


@router.post(
    "/professores",
    response_model=ProfessorResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_professor(data: ProfessorCreate, db: Db):
    return ProfessorService(db).create(data)


@router.put(
    "/professores/{entity_id}",
    response_model=ProfessorResponse,
)
def atualizar_professor(
    entity_id: int,
    data: ProfessorUpdate,
    db: Db,
):
    return ProfessorService(db).update(entity_id, data)


@router.delete(
    "/professores/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_professor(entity_id: int, db: Db):
    ProfessorService(db).delete(entity_id)
    return Response(status_code=204)


# MOEDAS

@router.post(
    "/moedas/transferencias",
    response_model=TransferenciaResponse,
    status_code=status.HTTP_201_CREATED,
)
def transferir_moedas(
    data: TransferenciaCreate,
    db: Db,
):
    return MoedasService(db).transferir(data)


@router.get(
    "/professores/{professor_id}/extrato",
    response_model=ExtratoProfessorResponse,
)
def extrato_professor(professor_id: int, db: Db):
    return MoedasService(db).extrato_professor(professor_id)


@router.get(
    "/alunos/{aluno_id}/extrato",
    response_model=ExtratoAlunoResponse,
)
def extrato_aluno(aluno_id: int, db: Db):
    return MoedasService(db).extrato_aluno(aluno_id)


# CRÉDITOS SEMESTRAIS

@router.post("/moedas/creditos-semestrais")
def executar_creditos_semestrais(db: Db):
    return CreditoSemestralService(db).executar()


@router.get(
    "/professores/{professor_id}/creditos-semestrais"
)
def historico_creditos_semestrais(
    professor_id: int,
    db: Db,
):
    return CreditoSemestralService(db).historico(
        professor_id
    )


# VANTAGENS

@router.get(
    "/vantagens",
    response_model=list[VantagemResponse],
)
def listar_vantagens(
    db: Db,
    apenas_ativas: bool = Query(False),
    empresa_id: int | None = Query(None, gt=0),
):
    return VantagemService(db).list(
        apenas_ativas,
        empresa_id,
    )


@router.get(
    "/vantagens/{entity_id}",
    response_model=VantagemResponse,
)
def obter_vantagem(entity_id: int, db: Db):
    return VantagemService(db).get(entity_id)


@router.post(
    "/vantagens",
    response_model=VantagemResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_vantagem(data: VantagemCreate, db: Db):
    return VantagemService(db).create(data)


@router.put(
    "/vantagens/{entity_id}",
    response_model=VantagemResponse,
)
def atualizar_vantagem(
    entity_id: int,
    data: VantagemUpdate,
    db: Db,
):
    return VantagemService(db).update(entity_id, data)


@router.post(
    "/vantagens/{entity_id}/desativar",
    response_model=VantagemResponse,
)
def desativar_vantagem(entity_id: int, db: Db):
    return VantagemService(db).desativar(entity_id)


# RESGATES

@router.post(
    "/resgates",
    response_model=ResgateResponse,
    status_code=status.HTTP_201_CREATED,
)
def resgatar_vantagem(data: ResgateCreate, db: Db):
    return ResgateService(db).create(data)


# CONFERÊNCIA DE CUPONS

@router.post(
    "/cupons/consultar",
    response_model=CupomConferenciaResponse,
)
def consultar_cupom(
    data: CupomConferenciaCreate,
    db: Db,
):
    return CupomService(db).consultar(data)


@router.post(
    "/cupons/validar",
    response_model=CupomValidacaoResponse,
)
def validar_cupom(
    data: CupomConferenciaCreate,
    db: Db,
):
    return CupomService(db).validar(data)

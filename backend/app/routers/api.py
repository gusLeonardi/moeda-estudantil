
from typing import Annotated
from ipaddress import ip_address

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status
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
from app.schemas.auth import ActivationRequest, DefinirSenhaRequest, LoginRequest, TokenResponse
from app.services.auth import activate_account, authenticate, current_user, issue_token, request_activation, require_role
from app.services.rate_limit import enforce_auth_limits
from app.core.config import get_settings
from app.models import Usuario


router = APIRouter()
Db = Annotated[Session, Depends(get_db)]

def _request_ip(request: Request) -> str:
    # Render's Cloudflare edge overwrites CF-Connecting-IP; X-Forwarded-For can
    # contain caller-controlled values and is deliberately not trusted here.
    if get_settings().app_env.lower() == "production":
        forwarded = request.headers.get("cf-connecting-ip", "")
        try:
            return str(ip_address(forwarded.strip()))
        except ValueError:
            pass
    return request.client.host if request.client else "unknown"

def _self(actor: Usuario, entity_id: int, role: str) -> None:
    if actor.tipo != role or actor.id != entity_id:
        raise HTTPException(403, "Acesso negado")

@router.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Db, request: Request):
    ip = _request_ip(request)
    enforce_auth_limits(db, "login", [("ip", ip, 20), ("email", str(data.email), 5)], 15 * 60)
    user = authenticate(str(data.email), data.senha, db)
    return TokenResponse(access_token=issue_token(user), id=user.id, nome=user.nome, tipo=user.tipo)

@router.post("/auth/activation/request", status_code=202)
def solicitar_ativacao(data: ActivationRequest, db: Db, request: Request):
    ip = _request_ip(request)
    enforce_auth_limits(db, "activation", [("ip", ip, 10), ("email", str(data.email), 3)], 60 * 60)
    request_activation(str(data.email), db)
    message = "Se a conta estiver elegível, as instruções serão enviadas. Se o e-mail não chegar, entre em contato com a administração."
    return {"detail": message}

@router.post("/auth/activation/complete", status_code=204)
def concluir_ativacao(data: DefinirSenhaRequest, db: Db):
    activate_account(str(data.email), data.token, data.senha, db)
    return Response(status_code=204)


# ALUNOS

@router.get("/alunos", response_model=list[AlunoResponse])
def listar_alunos(
    db: Db,
    actor: Usuario = Depends(require_role("PROFESSOR", "ALUNO")),
    busca: str | None = Query(None, max_length=100),
):
    if actor.tipo == "ALUNO":
        own = AlunoService(db).get(actor.id)
        term = (busca or "").strip().lower()
        searchable = " ".join([own.nome, own.email, own.cpf, own.curso, own.instituicao.nome]).lower()
        digits = "".join(ch for ch in term if ch.isdigit())
        if term and term not in searchable and not (digits and digits in own.cpf): return []
        return [own]
    return AlunoService(db).list(busca)


@router.get("/alunos/{entity_id}", response_model=AlunoResponse)
def obter_aluno(entity_id: int, db: Db, actor: Usuario = Depends(require_role("ALUNO"))):
    _self(actor, entity_id, "ALUNO")
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
    actor: Usuario = Depends(require_role("ALUNO")),
):
    _self(actor, entity_id, "ALUNO")
    return AlunoService(db).update(entity_id, data)


@router.delete(
    "/alunos/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_aluno(entity_id: int, db: Db, actor: Usuario = Depends(require_role("ALUNO"))):
    _self(actor, entity_id, "ALUNO")
    AlunoService(db).delete(entity_id)
    return Response(status_code=204)


# EMPRESAS

@router.get("/empresas", response_model=list[EmpresaResponse])
def listar_empresas(
    db: Db,
    actor: Usuario = Depends(require_role("EMPRESA")),
    busca: str | None = Query(None, max_length=100),
):
    own = EmpresaService(db).get(actor.id)
    term = (busca or "").strip().lower()
    digits = "".join(ch for ch in term if ch.isdigit())
    if term and term not in (own.nome + " " + own.email + " " + own.cnpj).lower() and not (digits and digits in own.cnpj): return []
    return [own]


@router.get("/empresas/{entity_id}", response_model=EmpresaResponse)
def obter_empresa(entity_id: int, db: Db, actor: Usuario = Depends(require_role("EMPRESA"))):
    _self(actor, entity_id, "EMPRESA")
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
    actor: Usuario = Depends(require_role("EMPRESA")),
):
    _self(actor, entity_id, "EMPRESA")
    return EmpresaService(db).update(entity_id, data)


@router.delete(
    "/empresas/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_empresa(entity_id: int, db: Db, actor: Usuario = Depends(require_role("EMPRESA"))):
    _self(actor, entity_id, "EMPRESA")
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
def obter_indicadores(db: Db, actor: Usuario = Depends(require_role("PROFESSOR"))):
    return DashboardService(db).indicators()


# PROFESSORES

@router.get(
    "/professores",
    response_model=list[ProfessorResponse],
)
def listar_professores(
    db: Db,
    actor: Usuario = Depends(require_role("PROFESSOR")),
    busca: str | None = Query(None, max_length=100),
):
    return [ProfessorService(db).get(actor.id)]


@router.get(
    "/professores/{entity_id}",
    response_model=ProfessorResponse,
)
def obter_professor(entity_id: int, db: Db, actor: Usuario = Depends(require_role("PROFESSOR"))):
    _self(actor, entity_id, "PROFESSOR")
    return ProfessorService(db).get(entity_id)


@router.post(
    "/professores",
    response_model=ProfessorResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_professor(data: ProfessorCreate, db: Db, x_admin_token: str | None = Header(None)):
    import hmac
    expected = get_settings().admin_cron_token
    if not expected or not x_admin_token or not hmac.compare_digest(expected, x_admin_token):
        raise HTTPException(404, "Operação indisponível")
    return ProfessorService(db).create(data)


@router.put(
    "/professores/{entity_id}",
    response_model=ProfessorResponse,
)
def atualizar_professor(
    entity_id: int,
    data: ProfessorUpdate,
    db: Db,
    actor: Usuario = Depends(require_role("PROFESSOR")),
):
    _self(actor, entity_id, "PROFESSOR")
    return ProfessorService(db).update(entity_id, data)


@router.delete(
    "/professores/{entity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_professor(entity_id: int, db: Db, actor: Usuario = Depends(require_role("PROFESSOR"))):
    _self(actor, entity_id, "PROFESSOR")
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
    actor: Usuario = Depends(require_role("PROFESSOR")),
):
    data.professor_id = actor.id
    return MoedasService(db).transferir(data)


@router.get(
    "/professores/{professor_id}/extrato",
    response_model=ExtratoProfessorResponse,
)
def extrato_professor(professor_id: int, db: Db, actor: Usuario = Depends(require_role("PROFESSOR"))):
    if actor.id != professor_id: raise HTTPException(403, "Acesso negado")
    return MoedasService(db).extrato_professor(actor.id)


@router.get(
    "/alunos/{aluno_id}/extrato",
    response_model=ExtratoAlunoResponse,
)
def extrato_aluno(aluno_id: int, db: Db, actor: Usuario = Depends(require_role("ALUNO"))):
    if actor.id != aluno_id: raise HTTPException(403, "Acesso negado")
    return MoedasService(db).extrato_aluno(actor.id)


# CRÉDITOS SEMESTRAIS

@router.post("/moedas/creditos-semestrais")
def executar_creditos_semestrais(db: Db, x_admin_token: str | None = Header(None)):
    import hmac
    expected = get_settings().admin_cron_token
    if not expected or not x_admin_token or not hmac.compare_digest(expected, x_admin_token):
        raise HTTPException(404, "Operação indisponível")
    return CreditoSemestralService(db).executar()


@router.get(
    "/professores/{professor_id}/creditos-semestrais"
)
def historico_creditos_semestrais(
    professor_id: int,
    db: Db,
    actor: Usuario = Depends(require_role("PROFESSOR")),
):
    _self(actor, professor_id, "PROFESSOR")
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
    actor: Usuario = Depends(current_user),
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
def obter_vantagem(entity_id: int, db: Db, actor: Usuario = Depends(current_user)):
    return VantagemService(db).get(entity_id)


@router.post(
    "/vantagens",
    response_model=VantagemResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_vantagem(data: VantagemCreate, db: Db, actor: Usuario = Depends(require_role("EMPRESA"))):
    data.empresa_id = actor.id
    return VantagemService(db).create(data)


@router.put(
    "/vantagens/{entity_id}",
    response_model=VantagemResponse,
)
def atualizar_vantagem(
    entity_id: int,
    data: VantagemUpdate,
    db: Db,
    actor: Usuario = Depends(require_role("EMPRESA")),
):
    item = VantagemService(db).get(entity_id)
    if item.empresa_id != actor.id: raise HTTPException(403, "Acesso negado")
    return VantagemService(db).update(entity_id, data)


@router.post(
    "/vantagens/{entity_id}/desativar",
    response_model=VantagemResponse,
)
def desativar_vantagem(entity_id: int, db: Db, actor: Usuario = Depends(require_role("EMPRESA"))):
    item = VantagemService(db).get(entity_id)
    if item.empresa_id != actor.id: raise HTTPException(403, "Acesso negado")
    return VantagemService(db).desativar(entity_id)


# RESGATES

@router.post(
    "/resgates",
    response_model=ResgateResponse,
    status_code=status.HTTP_201_CREATED,
)
def resgatar_vantagem(data: ResgateCreate, db: Db, actor: Usuario = Depends(require_role("ALUNO"))):
    data.aluno_id = actor.id
    return ResgateService(db).create(data)


# CONFERÊNCIA DE CUPONS

@router.post(
    "/cupons/consultar",
    response_model=CupomConferenciaResponse,
)
def consultar_cupom(
    data: CupomConferenciaCreate,
    db: Db,
    actor: Usuario = Depends(require_role("EMPRESA")),
):
    data.empresa_id = actor.id
    return CupomService(db).consultar(data)


@router.post(
    "/cupons/validar",
    response_model=CupomValidacaoResponse,
)
def validar_cupom(
    data: CupomConferenciaCreate,
    db: Db,
    actor: Usuario = Depends(require_role("EMPRESA")),
):
    data.empresa_id = actor.id
    return CupomService(db).validar(data)

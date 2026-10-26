from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Aluno, EmpresaParceira, Endereco, InstituicaoEnsino, Usuario
from app.repositories.usuario import UsuarioRepository
from app.schemas.aluno import AlunoCreate, AlunoResponse, AlunoUpdate
from app.schemas.empresa import EmpresaCreate, EmpresaResponse, EmpresaUpdate
from .errors import ConflictError, NotFoundError


def aluno_response(user: Usuario) -> AlunoResponse:
    return AlunoResponse(id=user.id, nome=user.nome, email=user.email, cpf=user.aluno.cpf, rg=user.aluno.rg, curso=user.aluno.curso, saldo=user.aluno.saldo, instituicao=user.aluno.instituicao, endereco=user.endereco)


def empresa_response(user: Usuario) -> EmpresaResponse:
    return EmpresaResponse(id=user.id, nome=user.nome, email=user.email, cnpj=user.empresa.cnpj, telefone=user.empresa.telefone, endereco=user.endereco)


class AlunoService:
    def __init__(self, db: Session):
        self.db, self.repo = db, UsuarioRepository(db)

    def list(self, busca: str | None = None) -> list[AlunoResponse]:
        return [aluno_response(item) for item in self.repo.list_alunos(busca)]

    def get(self, entity_id: int) -> AlunoResponse:
        user = self.repo.get_aluno(entity_id)
        if not user: raise NotFoundError("Aluno não encontrado")
        return aluno_response(user)

    def create(self, data: AlunoCreate) -> AlunoResponse:
        if not self.repo.instituicao(data.instituicao_id): raise NotFoundError("Instituição de ensino não encontrada")
        if self.repo.email_exists(str(data.email)): raise ConflictError("E-mail já cadastrado")
        if self.db.scalar(select(Aluno.usuario_id).where(Aluno.cpf == data.cpf)): raise ConflictError("CPF já cadastrado")
        user = Usuario(nome=data.nome.strip(), email=str(data.email).lower(), tipo="ALUNO")
        user.endereco = Endereco(**data.endereco.model_dump())
        user.aluno = Aluno(cpf=data.cpf, rg=data.rg.strip(), curso=data.curso.strip(), instituicao_id=data.instituicao_id)
        self.db.add(user)
        self._commit()
        return self.get(user.id)

    def update(self, entity_id: int, data: AlunoUpdate) -> AlunoResponse:
        user = self.repo.get_aluno(entity_id)
        if not user: raise NotFoundError("Aluno não encontrado")
        if not self.repo.instituicao(data.instituicao_id): raise NotFoundError("Instituição de ensino não encontrada")
        if self.repo.email_exists(str(data.email), entity_id): raise ConflictError("E-mail já cadastrado")
        user.nome, user.email = data.nome.strip(), str(data.email).lower()
        user.aluno.rg, user.aluno.curso, user.aluno.instituicao_id = data.rg.strip(), data.curso.strip(), data.instituicao_id
        for key, value in data.endereco.model_dump().items(): setattr(user.endereco, key, value)
        self._commit()
        return self.get(entity_id)

    def delete(self, entity_id: int) -> None:
        user = self.repo.get_aluno(entity_id)
        if not user: raise NotFoundError("Aluno não encontrado")
        self.db.delete(user); self._commit()

    def _commit(self):
        try: self.db.commit()
        except IntegrityError as exc:
            self.db.rollback(); raise ConflictError("Dados já cadastrados") from exc


class EmpresaService:
    def __init__(self, db: Session): self.db, self.repo = db, UsuarioRepository(db)
    def list(self, busca: str | None = None): return [empresa_response(x) for x in self.repo.list_empresas(busca)]
    def get(self, entity_id: int):
        user = self.repo.get_empresa(entity_id)
        if not user: raise NotFoundError("Empresa parceira não encontrada")
        return empresa_response(user)
    def create(self, data: EmpresaCreate):
        if self.repo.email_exists(str(data.email)): raise ConflictError("E-mail já cadastrado")
        if self.db.scalar(select(EmpresaParceira.usuario_id).where(EmpresaParceira.cnpj == data.cnpj)): raise ConflictError("CNPJ já cadastrado")
        user = Usuario(nome=data.nome.strip(), email=str(data.email).lower(), tipo="EMPRESA")
        user.endereco = Endereco(**data.endereco.model_dump())
        user.empresa = EmpresaParceira(cnpj=data.cnpj, telefone=data.telefone.strip())
        self.db.add(user); self._commit(); return self.get(user.id)
    def update(self, entity_id: int, data: EmpresaUpdate):
        user = self.repo.get_empresa(entity_id)
        if not user: raise NotFoundError("Empresa parceira não encontrada")
        if self.repo.email_exists(str(data.email), entity_id): raise ConflictError("E-mail já cadastrado")
        user.nome, user.email, user.empresa.telefone = data.nome.strip(), str(data.email).lower(), data.telefone.strip()
        for key, value in data.endereco.model_dump().items(): setattr(user.endereco, key, value)
        self._commit(); return self.get(entity_id)
    def delete(self, entity_id: int):
        user = self.repo.get_empresa(entity_id)
        if not user: raise NotFoundError("Empresa parceira não encontrada")
        self.db.delete(user); self._commit()
    def _commit(self):
        try: self.db.commit()
        except IntegrityError as exc:
            self.db.rollback(); raise ConflictError("Dados já cadastrados") from exc


class InstituicaoService:
    def __init__(self, db: Session): self.db = db
    def list(self): return list(self.db.scalars(select(InstituicaoEnsino).order_by(InstituicaoEnsino.nome)).all())


from decimal import Decimal
from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Vantagem
from app.repositories.moedas import MoedasRepository
from app.repositories.vantagens import VantagemRepository
from app.schemas.vantagem import ResgateCreate, ResgateResponse, VantagemCreate, VantagemResponse, VantagemUpdate

from .errors import ConflictError, NotFoundError


def vantagem_response(item: Vantagem) -> VantagemResponse:
    return VantagemResponse(
        id=item.id,
        empresa_id=item.empresa_id,
        empresa_nome=item.empresa.usuario.nome,
        nome=item.nome,
        descricao=item.descricao,
        custo=Decimal(item.custo).quantize(Decimal("0.01")),
        imagem_url=item.imagem_url,
        ativa=item.ativa,
    )


def resgate_response(item) -> ResgateResponse:
    return ResgateResponse(
        id=item.id,
        aluno_id=item.aluno_id,
        vantagem_id=item.vantagem_id,
        vantagem_nome=item.vantagem.nome,
        empresa_id=item.empresa_id,
        empresa_nome=item.empresa.usuario.nome,
        custo=Decimal(item.custo).quantize(Decimal("0.01")),
        codigo_cupom=item.codigo_cupom,
        criado_em=item.criado_em,
    )


class VantagemService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = VantagemRepository(db)

    def list(self, apenas_ativas: bool = False, empresa_id: int | None = None) -> list[VantagemResponse]:
        return [vantagem_response(item) for item in self.repo.list(apenas_ativas, empresa_id)]

    def get(self, entity_id: int) -> VantagemResponse:
        item = self.repo.get(entity_id)
        if not item:
            raise NotFoundError("Vantagem não encontrada")
        return vantagem_response(item)

    def create(self, data: VantagemCreate) -> VantagemResponse:
        if not self.repo.empresa_exists(data.empresa_id):
            raise NotFoundError("Empresa parceira não encontrada")
        item = Vantagem(
            empresa_id=data.empresa_id,
            nome=data.nome.strip(),
            descricao=data.descricao.strip(),
            custo=Decimal(data.custo),
            imagem_url=data.imagem_url.strip() if data.imagem_url else None,
            ativa=data.ativa,
        )
        self.repo.add(item)
        self._commit()
        return self.get(item.id)

    def update(self, entity_id: int, data: VantagemUpdate) -> VantagemResponse:
        item = self.repo.get(entity_id)
        if not item:
            raise NotFoundError("Vantagem não encontrada")
        item.nome = data.nome.strip()
        item.descricao = data.descricao.strip()
        item.custo = Decimal(data.custo)
        item.imagem_url = data.imagem_url.strip() if data.imagem_url else None
        item.ativa = data.ativa
        self._commit()
        return self.get(entity_id)

    def desativar(self, entity_id: int) -> VantagemResponse:
        item = self.repo.get(entity_id)
        if not item:
            raise NotFoundError("Vantagem não encontrada")
        item.ativa = False
        self._commit()
        return self.get(entity_id)

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Não foi possível salvar a vantagem") from exc


class ResgateService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = VantagemRepository(db)
        self.moedas = MoedasRepository(db)

    def create(self, data: ResgateCreate) -> ResgateResponse:
        existing = self.repo.resgate_by_key(data.idempotency_key)
        if existing:
            if existing.aluno_id != data.aluno_id or existing.vantagem_id != data.vantagem_id:
                raise ConflictError("Chave de idempotência já utilizada em outro pedido")
            return resgate_response(existing)
        aluno = self.moedas.get_aluno_user(data.aluno_id)
        if not aluno:
            raise NotFoundError("Aluno não encontrado")
        vantagem = self.repo.get(data.vantagem_id)
        if not vantagem:
            raise NotFoundError("Vantagem não encontrada")
        if not vantagem.ativa:
            raise ConflictError("Vantagem inativa")
        codigo = uuid4().hex[:12].upper()
        try:
            item = self.repo.resgatar(data.aluno_id, vantagem, data.idempotency_key, codigo)
            if item is None:
                self.db.rollback()
                raise ConflictError("Saldo insuficiente")
            item_id = item.id
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            existing = self.repo.resgate_by_key(data.idempotency_key)
            if existing:
                if existing.aluno_id != data.aluno_id or existing.vantagem_id != data.vantagem_id:
                    raise ConflictError("Chave de idempotência já utilizada em outro pedido")
                return resgate_response(existing)
            raise ConflictError("Não foi possível concluir o resgate") from exc
        persisted = self.repo.get_resgate(item_id)
        return resgate_response(persisted)

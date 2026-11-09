
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Endereco, Professor, Usuario
from app.repositories.moedas import MoedasRepository
from app.repositories.usuario import UsuarioRepository
from app.repositories.vantagens import VantagemRepository
from app.schemas.professor import (
    ExtratoAlunoResponse,
    ExtratoProfessorResponse,
    MovimentoAlunoResponse,
    ProfessorCreate,
    ProfessorResponse,
    ProfessorUpdate,
    TransferenciaCreate,
    TransferenciaResponse,
)

from .creditos import periodo_atual
from .email_service import notificar_transferencia
from .errors import ConflictError, NotFoundError


def professor_response(user: Usuario) -> ProfessorResponse:
    return ProfessorResponse(
        id=user.id,
        nome=user.nome,
        email=user.email,
        cpf=user.professor.cpf,
        departamento=user.professor.departamento,
        saldo=user.professor.saldo,
        instituicao=user.professor.instituicao,
        endereco=user.endereco,
    )


def transferencia_response(item) -> TransferenciaResponse:
    return TransferenciaResponse(
        id=item.id,
        professor_id=item.professor_id,
        professor_nome=item.professor.usuario.nome,
        aluno_id=item.aluno_id,
        aluno_nome=item.aluno.usuario.nome,
        quantidade=item.quantidade,
        justificativa=item.justificativa,
        criado_em=item.criado_em,
    )


class ProfessorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MoedasRepository(db)
        self.usuarios = UsuarioRepository(db)

    def list(self, busca: str | None = None) -> list[ProfessorResponse]:
        return [
            professor_response(item)
            for item in self.repo.list_professores(busca)
        ]

    def get(self, entity_id: int) -> ProfessorResponse:
        user = self.repo.get_professor(entity_id)

        if not user:
            raise NotFoundError("Professor não encontrado")

        return professor_response(user)

    def create(self, data: ProfessorCreate) -> ProfessorResponse:
        if not self.usuarios.instituicao(data.instituicao_id):
            raise NotFoundError(
                "Instituição de ensino não encontrada"
            )

        if self.usuarios.email_exists(str(data.email)):
            raise ConflictError("E-mail já cadastrado")

        if self.repo.cpf_professor_exists(data.cpf):
            raise ConflictError("CPF já cadastrado")

        user = Usuario(
            nome=data.nome.strip(),
            email=str(data.email).lower(),
            tipo="PROFESSOR",
        )

        user.endereco = Endereco(**data.endereco.model_dump())
        user.professor = Professor(
            cpf=data.cpf,
            departamento=data.departamento.strip(),
            instituicao_id=data.instituicao_id,
        )

        self.repo.add(user)

        try:
            self.db.flush()

            ano, semestre = periodo_atual()

            self.repo.registrar_credito_inicial(
                professor_id=user.id,
                ano=ano,
                semestre=semestre,
            )

            self._commit()

        except Exception:
            self.db.rollback()
            raise

        return self.get(user.id)

    def update(
        self,
        entity_id: int,
        data: ProfessorUpdate,
    ) -> ProfessorResponse:
        user = self.repo.get_professor(entity_id)

        if not user:
            raise NotFoundError("Professor não encontrado")

        if not self.usuarios.instituicao(data.instituicao_id):
            raise NotFoundError(
                "Instituição de ensino não encontrada"
            )

        if self.usuarios.email_exists(
            str(data.email),
            entity_id,
        ):
            raise ConflictError("E-mail já cadastrado")

        user.nome = data.nome.strip()
        user.email = str(data.email).lower()
        user.professor.departamento = data.departamento.strip()
        user.professor.instituicao_id = data.instituicao_id

        for key, value in data.endereco.model_dump().items():
            setattr(user.endereco, key, value)

        self._commit()
        return self.get(entity_id)

    def delete(self, entity_id: int) -> None:
        user = self.repo.get_professor(entity_id)

        if not user:
            raise NotFoundError("Professor não encontrado")

        self.repo.delete(user)
        self._commit()

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(
                "Dados já cadastrados ou professor possui histórico"
            ) from exc


class MoedasService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MoedasRepository(db)

    def transferir(
        self,
        data: TransferenciaCreate,
    ) -> TransferenciaResponse:
        professor = self.repo.get_professor(data.professor_id)

        if not professor:
            raise NotFoundError("Professor não encontrado")

        aluno = self.repo.get_aluno_user(data.aluno_id)

        if not aluno:
            raise NotFoundError("Aluno não encontrado")

        quantidade = Decimal(data.quantidade)

        try:
            item = self.repo.transferir(
                data.professor_id,
                data.aluno_id,
                quantidade,
                data.justificativa,
            )

            if item is None:
                self.db.rollback()
                raise ConflictError(
                    "Saldo insuficiente ou destinatário indisponível"
                )

            self.db.commit()

        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError(
                "Não foi possível concluir a transferência"
            ) from exc

        persisted = self.repo.get_transferencia(item.id)
        resposta = transferencia_response(persisted)

        notificar_transferencia(
            email_aluno=persisted.aluno.usuario.email,
            nome_aluno=persisted.aluno.usuario.nome,
            nome_professor=persisted.professor.usuario.nome,
            quantidade=persisted.quantidade,
            justificativa=persisted.justificativa,
        )

        return resposta

    def extrato_professor(
        self,
        professor_id: int,
    ) -> ExtratoProfessorResponse:
        professor = self.repo.get_professor(professor_id)

        if not professor:
            raise NotFoundError("Professor não encontrado")

        items = self.repo.list_transferencias_professor(
            professor_id
        )

        return ExtratoProfessorResponse(
            professor_id=professor_id,
            saldo=professor.professor.saldo,
            total_distribuido=self.repo.total_distribuido(
                professor_id
            ),
            transferencias=[
                transferencia_response(item)
                for item in items
            ],
        )

    def extrato_aluno(
        self,
        aluno_id: int,
    ) -> ExtratoAlunoResponse:
        aluno = self.repo.get_aluno_user(aluno_id)

        if not aluno:
            raise NotFoundError("Aluno não encontrado")

        items = self.repo.list_transferencias_aluno(
            aluno_id
        )

        movimentos_ordenaveis = [
            (
                item.criado_em,
                0,
                item.id,
                MovimentoAlunoResponse(
                    tipo="RECEBIMENTO",
                    data=item.criado_em,
                    quantidade=item.quantidade,
                    descricao=item.justificativa,
                    professor_nome=item.professor.usuario.nome,
                ),
            )
            for item in items
        ]

        resgates = VantagemRepository(
            self.db
        ).list_resgates_aluno(aluno_id)

        movimentos_ordenaveis.extend(
            (
                item.criado_em,
                1,
                item.id,
                MovimentoAlunoResponse(
                    tipo="RESGATE",
                    data=item.criado_em,
                    quantidade=item.custo,
                    descricao=f"Resgate: {item.vantagem.nome}",
                    vantagem_nome=item.vantagem.nome,
                    codigo_cupom=item.codigo_cupom,
                ),
            )
            for item in resgates
        )

        movimentos_ordenaveis.sort(
            key=lambda entry: (
                entry[0],
                entry[1],
                entry[2],
            ),
            reverse=True,
        )

        movimentos = [
            entry[3]
            for entry in movimentos_ordenaveis
        ]

        return ExtratoAlunoResponse(
            aluno_id=aluno_id,
            saldo=aluno.aluno.saldo,
            movimentos=movimentos,
        )

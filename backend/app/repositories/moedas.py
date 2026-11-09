
from decimal import Decimal

from sqlalchemy import func, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Aluno,
    CreditoSemestral,
    Professor,
    TransferenciaMoedas,
    Usuario,
)


class MoedasRepository:
    def __init__(self, db: Session):
        self.db = db

    def cpf_professor_exists(
        self,
        cpf: str,
        except_id: int | None = None,
    ) -> bool:
        stmt = select(Professor.usuario_id).where(Professor.cpf == cpf)
        if except_id is not None:
            stmt = stmt.where(Professor.usuario_id != except_id)
        return self.db.scalar(stmt) is not None

    def list_professores(
        self,
        busca: str | None = None,
    ) -> list[Usuario]:
        stmt = (
            select(Usuario)
            .join(Usuario.professor)
            .options(
                selectinload(Usuario.endereco),
                selectinload(Usuario.professor).selectinload(
                    Professor.instituicao
                ),
            )
            .order_by(Usuario.nome)
        )

        if busca:
            term = f"%{busca.strip()}%"
            digits = "".join(filter(str.isdigit, busca))
            filters = [
                Usuario.nome.ilike(term),
                Usuario.email.ilike(term),
                Professor.departamento.ilike(term),
            ]
            if digits:
                filters.append(Professor.cpf.like(f"%{digits}%"))
            stmt = stmt.where(or_(*filters))

        return list(self.db.scalars(stmt).all())

    def get_professor(self, user_id: int) -> Usuario | None:
        stmt = (
            select(Usuario)
            .join(Usuario.professor)
            .where(Usuario.id == user_id)
            .options(
                selectinload(Usuario.endereco),
                selectinload(Usuario.professor).selectinload(
                    Professor.instituicao
                ),
            )
        )
        return self.db.scalar(stmt)

    def add(self, entity: object) -> None:
        self.db.add(entity)

    def delete(self, entity: object) -> None:
        self.db.delete(entity)

    def get_aluno_user(self, user_id: int) -> Usuario | None:
        return self.db.scalar(
            select(Usuario)
            .join(Usuario.aluno)
            .where(Usuario.id == user_id)
        )

    def registrar_credito_inicial(
        self,
        professor_id: int,
        ano: int,
        semestre: int,
    ) -> None:
        credito = CreditoSemestral(
            professor_id=professor_id,
            ano=ano,
            semestre=semestre,
            quantidade=Decimal("1000.00"),
        )
        self.db.add(credito)

    def creditar_semestre(
        self,
        professor_id: int,
        ano: int,
        semestre: int,
    ) -> bool:
        stmt = (
            insert(CreditoSemestral)
            .values(
                professor_id=professor_id,
                ano=ano,
                semestre=semestre,
                quantidade=Decimal("1000.00"),
            )
            .on_conflict_do_nothing(
                constraint="uq_credito_professor_ano_semestre"
            )
            .returning(CreditoSemestral.id)
        )

        credito_id = self.db.scalar(stmt)

        if credito_id is None:
            return False

        resultado = self.db.execute(
            update(Professor)
            .where(Professor.usuario_id == professor_id)
            .values(
                saldo=Professor.saldo + Decimal("1000.00")
            )
        )

        if resultado.rowcount != 1:
            raise RuntimeError(
                "Professor não encontrado durante o crédito"
            )

        return True

    def list_creditos_professor(
        self,
        professor_id: int,
    ) -> list[CreditoSemestral]:
        stmt = (
            select(CreditoSemestral)
            .where(CreditoSemestral.professor_id == professor_id)
            .order_by(
                CreditoSemestral.ano.desc(),
                CreditoSemestral.semestre.desc(),
            )
        )
        return list(self.db.scalars(stmt).all())

    def transferir(
        self,
        professor_id: int,
        aluno_id: int,
        quantidade: Decimal,
        justificativa: str,
    ) -> TransferenciaMoedas | None:
        debit = self.db.execute(
            update(Professor)
            .where(
                Professor.usuario_id == professor_id,
                Professor.saldo >= quantidade,
            )
            .values(saldo=Professor.saldo - quantidade)
        )

        if debit.rowcount != 1:
            return None

        credit = self.db.execute(
            update(Aluno)
            .where(Aluno.usuario_id == aluno_id)
            .values(saldo=Aluno.saldo + quantidade)
        )

        if credit.rowcount != 1:
            return None

        transferencia = TransferenciaMoedas(
            professor_id=professor_id,
            aluno_id=aluno_id,
            quantidade=quantidade,
            justificativa=justificativa,
        )

        self.db.add(transferencia)
        self.db.flush()
        self.db.refresh(transferencia)

        return transferencia

    def list_transferencias_professor(
        self,
        professor_id: int,
    ) -> list[TransferenciaMoedas]:
        stmt = (
            select(TransferenciaMoedas)
            .where(TransferenciaMoedas.professor_id == professor_id)
            .options(
                selectinload(
                    TransferenciaMoedas.professor
                ).selectinload(Professor.usuario),
                selectinload(
                    TransferenciaMoedas.aluno
                ).selectinload(Aluno.usuario),
            )
            .order_by(
                TransferenciaMoedas.criado_em.desc(),
                TransferenciaMoedas.id.desc(),
            )
        )
        return list(self.db.scalars(stmt).all())

    def get_transferencia(
        self,
        transferencia_id: int,
    ) -> TransferenciaMoedas | None:
        stmt = (
            select(TransferenciaMoedas)
            .where(TransferenciaMoedas.id == transferencia_id)
            .options(
                selectinload(
                    TransferenciaMoedas.professor
                ).selectinload(Professor.usuario),
                selectinload(
                    TransferenciaMoedas.aluno
                ).selectinload(Aluno.usuario),
            )
        )
        return self.db.scalar(stmt)

    def list_transferencias_aluno(
        self,
        aluno_id: int,
    ) -> list[TransferenciaMoedas]:
        stmt = (
            select(TransferenciaMoedas)
            .where(TransferenciaMoedas.aluno_id == aluno_id)
            .options(
                selectinload(
                    TransferenciaMoedas.professor
                ).selectinload(Professor.usuario)
            )
            .order_by(
                TransferenciaMoedas.criado_em.desc(),
                TransferenciaMoedas.id.desc(),
            )
        )
        return list(self.db.scalars(stmt).all())

    def total_distribuido(self, professor_id: int) -> Decimal:
        return self.db.scalar(
            select(
                func.coalesce(
                    func.sum(TransferenciaMoedas.quantidade),
                    0,
                )
            ).where(
                TransferenciaMoedas.professor_id == professor_id
            )
        ) or Decimal("0.00")

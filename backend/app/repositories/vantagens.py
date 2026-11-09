from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Aluno,
    EmpresaParceira,
    ResgateVantagem,
    Usuario,
    Vantagem,
)


class VantagemRepository:
    def __init__(self, db: Session):
        self.db = db

    def empresa_exists(self, empresa_id: int) -> bool:
        return (
            self.db.scalar(
                select(EmpresaParceira.usuario_id).where(
                    EmpresaParceira.usuario_id == empresa_id
                )
            )
            is not None
        )

    def list(
        self,
        apenas_ativas: bool = False,
        empresa_id: int | None = None,
    ) -> list[Vantagem]:
        stmt = (
            select(Vantagem)
            .options(
                selectinload(Vantagem.empresa).selectinload(
                    EmpresaParceira.usuario
                )
            )
            .order_by(
                Vantagem.ativa.desc(),
                Vantagem.nome,
            )
        )

        if apenas_ativas:
            stmt = stmt.where(Vantagem.ativa.is_(True))

        if empresa_id is not None:
            stmt = stmt.where(Vantagem.empresa_id == empresa_id)

        return list(self.db.scalars(stmt).all())

    def count(self) -> int:
        return (
            self.db.scalar(
                select(func.count(Vantagem.id))
            )
            or 0
        )

    def get(self, vantagem_id: int) -> Vantagem | None:
        stmt = (
            select(Vantagem)
            .where(Vantagem.id == vantagem_id)
            .options(
                selectinload(Vantagem.empresa).selectinload(
                    EmpresaParceira.usuario
                )
            )
        )

        return self.db.scalar(stmt)

    def add(self, entity: object) -> None:
        self.db.add(entity)

    def resgate_by_key(
        self,
        key: str,
    ) -> ResgateVantagem | None:
        stmt = (
            select(ResgateVantagem)
            .where(
                ResgateVantagem.idempotency_key == key
            )
            .options(
                selectinload(ResgateVantagem.vantagem),
                selectinload(
                    ResgateVantagem.empresa
                ).selectinload(
                    EmpresaParceira.usuario
                ),
            )
        )

        return self.db.scalar(stmt)

    def get_resgate(
        self,
        resgate_id: int,
    ) -> ResgateVantagem | None:
        stmt = (
            select(ResgateVantagem)
            .where(
                ResgateVantagem.id == resgate_id
            )
            .options(
                selectinload(ResgateVantagem.vantagem),
                selectinload(
                    ResgateVantagem.empresa
                ).selectinload(
                    EmpresaParceira.usuario
                ),
            )
        )

        return self.db.scalar(stmt)

    def resgatar(
        self,
        aluno_id: int,
        vantagem: Vantagem,
        key: str,
        codigo: str,
    ) -> ResgateVantagem | None:
        custo = Decimal(vantagem.custo)

        debit = self.db.execute(
            update(Aluno)
            .where(
                Aluno.usuario_id == aluno_id,
                Aluno.saldo >= custo,
            )
            .values(
                saldo=Aluno.saldo - custo
            )
        )

        if debit.rowcount != 1:
            return None

        resgate = ResgateVantagem(
            aluno_id=aluno_id,
            vantagem_id=vantagem.id,
            empresa_id=vantagem.empresa_id,
            custo=custo,
            codigo_cupom=codigo,
            idempotency_key=key,
        )

        self.db.add(resgate)
        self.db.flush()

        return resgate

    def list_resgates_aluno(
        self,
        aluno_id: int,
    ) -> list[ResgateVantagem]:
        stmt = (
            select(ResgateVantagem)
            .where(
                ResgateVantagem.aluno_id == aluno_id
            )
            .options(
                selectinload(ResgateVantagem.vantagem)
            )
            .order_by(
                ResgateVantagem.criado_em.desc(),
                ResgateVantagem.id.desc(),
            )
        )

        return list(self.db.scalars(stmt).all())

    # ==========================================
    # CONSULTA DE CUPONS
    # ==========================================

    def get_cupom(
        self,
        codigo: str,
        empresa_id: int,
    ) -> ResgateVantagem | None:
        stmt = (
            select(ResgateVantagem)
            .where(
                ResgateVantagem.codigo_cupom == codigo,
                ResgateVantagem.empresa_id == empresa_id,
            )
            .options(
                selectinload(ResgateVantagem.vantagem)
            )
        )

        return self.db.scalar(stmt)

    # ==========================================
    # VALIDAÇÃO E UTILIZAÇÃO DE CUPONS
    # ==========================================

    def marcar_cupom_utilizado(
        self,
        codigo: str,
        empresa_id: int,
    ) -> int | None:
        stmt = (
            update(ResgateVantagem)
            .where(
                ResgateVantagem.codigo_cupom == codigo,
                ResgateVantagem.empresa_id == empresa_id,
                ResgateVantagem.utilizado_em.is_(None),
            )
            .values(
                utilizado_em=func.now()
            )
            .returning(
                ResgateVantagem.id
            )
        )

        return self.db.execute(
            stmt
        ).scalar_one_or_none()
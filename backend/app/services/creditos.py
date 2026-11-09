
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.moedas import MoedasRepository

from .errors import NotFoundError


QUANTIDADE_SEMESTRAL = Decimal("1000.00")


def periodo_atual() -> tuple[int, int]:
    agora = datetime.now(timezone.utc)
    semestre = 1 if agora.month <= 6 else 2
    return agora.year, semestre


class CreditoSemestralService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MoedasRepository(db)

    def executar(self) -> dict:
        ano, semestre = periodo_atual()
        professores = self.repo.list_professores()

        creditados = 0
        ja_creditados = 0

        try:
            for usuario in professores:
                realizado = self.repo.creditar_semestre(
                    usuario.id,
                    ano,
                    semestre,
                )

                if realizado:
                    creditados += 1
                else:
                    ja_creditados += 1

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise

        return {
            "ano": ano,
            "semestre": semestre,
            "quantidade_por_professor": QUANTIDADE_SEMESTRAL,
            "professores_creditados": creditados,
            "professores_ja_creditados": ja_creditados,
            "total_creditado": QUANTIDADE_SEMESTRAL * creditados,
            "mensagem": (
                "Crédito semestral processado com sucesso."
            ),
        }

    def historico(self, professor_id: int) -> dict:
        professor = self.repo.get_professor(professor_id)

        if professor is None:
            raise NotFoundError("Professor não encontrado")

        creditos = self.repo.list_creditos_professor(
            professor_id
        )

        return {
            "professor_id": professor_id,
            "professor_nome": professor.nome,
            "saldo_atual": professor.professor.saldo,
            "creditos": [
                {
                    "id": item.id,
                    "ano": item.ano,
                    "semestre": item.semestre,
                    "quantidade": item.quantidade,
                    "criado_em": item.criado_em,
                }
                for item in creditos
            ],
        }

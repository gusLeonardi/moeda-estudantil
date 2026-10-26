from sqlalchemy import select

from app.database.session import SessionLocal
from app.models import InstituicaoEnsino

INSTITUICOES = [("Pontifícia Universidade Católica de Minas Gerais", "PUC Minas"), ("Universidade Federal de Minas Gerais", "UFMG"), ("Centro Federal de Educação Tecnológica de Minas Gerais", "CEFET-MG")]

def seed():
    with SessionLocal() as db:
        existing = set(db.scalars(select(InstituicaoEnsino.sigla)).all())
        db.add_all([InstituicaoEnsino(nome=nome, sigla=sigla) for nome, sigla in INSTITUICOES if sigla not in existing])
        db.commit()

if __name__ == "__main__": seed()

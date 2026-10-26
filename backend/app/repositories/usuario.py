from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Aluno, EmpresaParceira, InstituicaoEnsino, Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def email_exists(self, email: str, except_id: int | None = None) -> bool:
        stmt = select(Usuario.id).where(Usuario.email == email.lower())
        if except_id is not None:
            stmt = stmt.where(Usuario.id != except_id)
        return self.db.scalar(stmt) is not None

    def list_alunos(self, busca: str | None = None) -> list[Usuario]:
        stmt = select(Usuario).join(Usuario.aluno).options(selectinload(Usuario.endereco), selectinload(Usuario.aluno).selectinload(Aluno.instituicao)).order_by(Usuario.nome)
        if busca:
            term = f"%{busca.strip()}%"
            stmt = stmt.where(or_(Usuario.nome.ilike(term), Usuario.email.ilike(term)))
        return list(self.db.scalars(stmt).all())

    def get_aluno(self, user_id: int) -> Usuario | None:
        stmt = select(Usuario).join(Usuario.aluno).where(Usuario.id == user_id).options(selectinload(Usuario.endereco), selectinload(Usuario.aluno).selectinload(Aluno.instituicao))
        return self.db.scalar(stmt)

    def list_empresas(self, busca: str | None = None) -> list[Usuario]:
        stmt = select(Usuario).join(Usuario.empresa).options(selectinload(Usuario.endereco), selectinload(Usuario.empresa)).order_by(Usuario.nome)
        if busca:
            term = f"%{busca.strip()}%"
            digits = "".join(filter(str.isdigit, busca))
            filters = [Usuario.nome.ilike(term)]
            if digits:
                filters.append(EmpresaParceira.cnpj.like(f"%{digits}%"))
            stmt = stmt.where(or_(*filters))
        return list(self.db.scalars(stmt).all())

    def get_empresa(self, user_id: int) -> Usuario | None:
        stmt = select(Usuario).join(Usuario.empresa).where(Usuario.id == user_id).options(selectinload(Usuario.endereco), selectinload(Usuario.empresa))
        return self.db.scalar(stmt)

    def instituicao(self, entity_id: int) -> InstituicaoEnsino | None:
        return self.db.get(InstituicaoEnsino, entity_id)

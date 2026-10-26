import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_sprint2.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.database.session import get_db
from app.main import create_app
from app.models import InstituicaoEnsino

TEST_DB = Path(__file__).parent / "test_sprint2.db"
engine = create_engine(f"sqlite:///{TEST_DB}", connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestingSession() as db:
        db.add(InstituicaoEnsino(nome="Pontifícia Universidade Católica de Minas Gerais", sigla="PUC Minas")); db.commit()
    app = create_app()
    def override_db():
        with TestingSession() as db: yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client: yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()
    TEST_DB.unlink(missing_ok=True)


@pytest.fixture()
def endereco():
    return {"logradouro":"Avenida Dom José Gaspar","numero":"500","complemento":None,"bairro":"Coração Eucarístico","cidade":"Belo Horizonte","estado":"MG","cep":"30535901"}

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
from app.core.config import get_settings

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
    get_settings().admin_cron_token = "test-only-admin-token"
    get_settings().app_env = "development"
    def override_db():
        with TestingSession() as db: yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        original_post = test_client.post
        tokens = {}
        def post_with_auth(url, *args, **kwargs):
            data = kwargs.get("json") or {}
            role = "PROFESSOR" if url.startswith("/api/moedas/") or "/professores" in url else "ALUNO" if url.startswith("/api/resgates") or "/alunos" in url else "EMPRESA" if "/cupons" in url or "/empresas" in url or "/vantagens" in url else None
            if role:
                headers = dict(kwargs.pop("headers", {}) or {})
                if "Authorization" not in headers:
                    if role in tokens: headers["Authorization"] = f"Bearer {tokens[role]}"
                kwargs["headers"] = headers
            response = original_post(url, *args, **kwargs)
            role_by_url = {"/api/alunos": "ALUNO", "/api/professores": "PROFESSOR", "/api/empresas": "EMPRESA"}
            created_role = role_by_url.get(url)
            if created_role and response.status_code == 201:
                login = original_post("/api/auth/login", json={"email": data["email"], "senha": data["senha"]})
                tokens[created_role] = login.json()["access_token"]
            return response
        original_get = test_client.get
        def get_with_auth(url, *args, **kwargs):
            role = "PROFESSOR" if "/professores" in url else "ALUNO" if "/alunos" in url else "EMPRESA" if "/empresas" in url or "/vantagens" in url else next(iter(tokens), None)
            if role and role in tokens:
                headers = dict(kwargs.pop("headers", {}) or {})
                if "Authorization" not in headers:
                    headers["Authorization"] = f"Bearer {tokens[role]}"
                kwargs["headers"] = headers
            return original_get(url, *args, **kwargs)
        original_put = test_client.put
        def put_with_auth(url, *args, **kwargs):
            role = "ALUNO" if "/alunos" in url else "PROFESSOR" if "/professores" in url else "EMPRESA"
            headers=dict(kwargs.pop("headers",{}) or {})
            if role in tokens: headers["Authorization"]=f"Bearer {tokens[role]}"
            kwargs["headers"]=headers
            return original_put(url,*args,**kwargs)
        original_delete=test_client.delete
        def delete_with_auth(url,*args,**kwargs):
            role = "ALUNO" if "/alunos" in url else "PROFESSOR" if "/professores" in url else "EMPRESA"
            headers=dict(kwargs.pop("headers",{}) or {})
            if role in tokens: headers["Authorization"]=f"Bearer {tokens[role]}"
            kwargs["headers"]=headers
            return original_delete(url,*args,**kwargs)
        test_client.post = post_with_auth
        test_client.get = get_with_auth
        test_client.put = put_with_auth
        test_client.delete = delete_with_auth
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()
    TEST_DB.unlink(missing_ok=True)


@pytest.fixture()
def endereco():
    return {"logradouro":"Avenida Dom José Gaspar","numero":"500","complemento":None,"bairro":"Coração Eucarístico","cidade":"Belo Horizonte","estado":"MG","cep":"30535901"}

from tests.test_moedas import aluno_payload, professor_payload, provisionar_professor
import re
from datetime import datetime, timedelta, timezone
import pytest


def test_login_argon2_and_bad_password(client, endereco):
    created = client.post("/api/alunos", json=aluno_payload(endereco))
    assert created.status_code == 201
    valid = client.post("/api/auth/login", json={"email": "aluno@example.com", "senha": "Senha-Forte-Teste-123!"})
    assert valid.status_code == 200
    assert valid.json()["tipo"] == "ALUNO"
    from app.services.auth import hash_password
    assert hash_password("Senha-Forte-Teste-123!").startswith("$argon2")
    assert client.post("/api/auth/login", json={"email": "aluno@example.com", "senha": "incorrect"}).status_code == 401


def test_transfer_requires_professor_identity_and_isolates_extratos(client, endereco):
    student = client.post("/api/alunos", json=aluno_payload(endereco)).json()
    prof = provisionar_professor(client, professor_payload(endereco)).json()
    student_token = client.post("/api/auth/login", json={"email": "aluno@example.com", "senha": "Senha-Forte-Teste-123!"}).json()["access_token"]
    payload = {"professor_id": prof["id"], "aluno_id": student["id"], "quantidade": 1, "justificativa": "Reconhecimento"}
    assert client.post("/api/moedas/transferencias", json=payload, headers={"Authorization": ""}).status_code == 401
    assert client.post("/api/moedas/transferencias", json=payload, headers={"Authorization": f"Bearer {student_token}"}).status_code == 403


def test_private_records_are_isolated_by_profile(client, endereco):
    a=client.post("/api/alunos",json=aluno_payload(endereco)).json()
    b=client.post("/api/alunos",json=aluno_payload(endereco,email="second@example.com",cpf="11144477735")).json()
    token=client.post("/api/auth/login",json={"email":"aluno@example.com","senha":"Senha-Forte-Teste-123!"}).json()["access_token"]
    h={"Authorization":f"Bearer {token}"}
    assert client.get(f"/api/alunos/{a['id']}",headers=h).status_code==200
    assert client.get(f"/api/alunos/{b['id']}",headers=h).status_code==403
    assert client.get(f"/api/alunos/{b['id']}/extrato",headers=h).status_code==403


def test_professor_provisioning_requires_admin_token_even_in_development(client, endereco):
    payload = professor_payload(endereco)
    assert client.post("/api/professores", json=payload).status_code == 404
    professor = provisionar_professor(client, payload)
    assert professor.status_code == 201
    login = client.post("/api/auth/login", json={"email":"professor@example.com", "senha":"Senha-Forte-Teste-123!"})
    assert login.status_code == 200


def test_professor_signup_is_not_public_in_production(client, endereco):
    from app.core.config import get_settings
    settings = get_settings()
    settings.app_env = "production"
    settings.admin_cron_token = ""
    response = client.post("/api/professores", json=professor_payload(endereco))
    assert response.status_code == 404


def test_production_configuration_requires_private_secrets_tls_and_https_cors(monkeypatch):
    from app.core.config import Settings

    monkeypatch.setenv("JWT_SECRET", "")
    settings = Settings(app_env="production", jwt_secret="", admin_cron_token="", database_url="", cors_origins="")
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        settings.validate_production()
    settings.jwt_secret = "j" * 40
    settings.admin_cron_token = "a" * 40
    settings.database_url = "postgresql+psycopg://app:pass@db.example.test/conquista?sslmode=require"
    settings.cors_origins = "https://conquista.example.test"
    settings.validate_production()
    settings.cors_origins = "*"
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        settings.validate_production()


def test_global_dashboard_indicators_are_professor_only(client, endereco):
    client.post("/api/alunos", json=aluno_payload(endereco))
    assert client.get("/api/dashboard/indicadores").status_code == 403
    professor = provisionar_professor(client, professor_payload(endereco))
    assert professor.status_code == 201
    token = client.post("/api/auth/login", json={"email": "professor@example.com", "senha": "Senha-Forte-Teste-123!"}).json()["access_token"]
    response = client.get("/api/dashboard/indicadores", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"total_alunos": 1}


def test_activation_request_does_not_reveal_accounts(client):
    unknown = client.post("/api/auth/activation/request", json={"email": "unknown@example.com"})
    assert unknown.status_code == 202
    assert "Se a conta" in unknown.json()["detail"]


def test_auth_endpoints_rate_limit_repeated_attempts(client, endereco):
    client.post("/api/alunos", json=aluno_payload(endereco))
    payload = {"email": "aluno@example.com", "senha": "senha-incorreta"}
    for _ in range(4):
        assert client.post("/api/auth/login", json=payload).status_code == 401
    blocked = client.post("/api/auth/login", json=payload)
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0

    activation = {"email": "missing@example.com"}
    for _ in range(3):
        assert client.post("/api/auth/activation/request", json=activation).status_code == 202
    assert client.post("/api/auth/activation/request", json=activation).status_code == 429


def test_activation_delivery_failure_invalidates_grant(client, monkeypatch, caplog):
    from conftest import TestingSession
    from sqlalchemy import text
    import app.services.auth as auth

    with TestingSession() as db:
        legacy_account(db, "undeliverable@example.com")
    monkeypatch.setattr(auth, "enviar_email", lambda *_: False)
    response = client.post("/api/auth/activation/request", json={"email": "undeliverable@example.com"})
    assert response.status_code == 202
    assert "Se a conta" in response.json()["detail"]
    assert "grant invalidado" in caplog.text
    with TestingSession() as db:
        count = db.execute(text("SELECT COUNT(*) FROM ativacoes_conta")).scalar_one()
    assert count == 0


def test_activation_reports_missing_migration_without_sql_traceback(client):
    from conftest import TestingSession
    from sqlalchemy import text
    with TestingSession() as db:
        legacy_account(db, "legacy@example.com")
        db.execute(text("DROP TABLE ativacoes_conta"))
        db.commit()
    response = client.post("/api/auth/activation/request", json={"email":"legacy@example.com"})
    assert response.status_code == 503
    assert "aplique as migrations" in response.json()["detail"]


def legacy_account(db_session, email):
    from app.models import Usuario
    user = Usuario(nome="Legacy User", email=email, tipo="ALUNO", senha_hash=None)
    db_session.add(user); db_session.commit(); return user


def test_activation_token_valid_once_and_already_activated(client, monkeypatch):
    from conftest import TestingSession
    from app import services as _services
    import app.services.auth as auth
    sent=[]
    monkeypatch.setattr(auth, "enviar_email", lambda to, subject, body: sent.append(body) or True)
    with TestingSession() as db: legacy_account(db, "legacy@example.com")
    client.post("/api/auth/activation/request", json={"email":"legacy@example.com"})
    assert "Ativação de conta" in sent[0]
    assert "token temporário" in sent[0]
    token=re.search(r"<p>([A-Za-z0-9_-]{40,})</p>", sent[0]).group(1)
    from conftest import TestingSession
    from sqlalchemy import text
    with TestingSession() as db:
        stored=db.execute(text("SELECT token_hash FROM ativacoes_conta")).scalar_one()
        assert stored != token
    payload={"email":"legacy@example.com","token":token,"senha":"Senha-Nova-Segura-123!"}
    assert client.post("/api/auth/activation/complete",json=payload).status_code==204
    assert client.post("/api/auth/activation/complete",json=payload).status_code==400
    client.post("/api/auth/activation/request",json={"email":"legacy@example.com"})
    assert len(sent)==1


@pytest.mark.parametrize("case", ["expired", "invalid", "third_party"])
def test_activation_rejects_expired_invalid_and_cross_account_tokens(client, monkeypatch, case):
    from conftest import TestingSession
    from sqlalchemy import text
    import app.services.auth as auth
    sent=[]
    monkeypatch.setattr(auth, "enviar_email", lambda to, subject, body: sent.append((to,body)) or True)
    with TestingSession() as db:
        legacy_account(db,"one@example.com"); legacy_account(db,"two@example.com")
    for email in ("one@example.com","two@example.com"):
        client.post("/api/auth/activation/request",json={"email":email})
    token1=re.search(r"<p>([A-Za-z0-9_-]{40,})</p>",sent[0][1]).group(1)
    token2=re.search(r"<p>([A-Za-z0-9_-]{40,})</p>",sent[1][1]).group(1)
    if case=="expired":
        with TestingSession() as db: db.execute(text("UPDATE ativacoes_conta SET expira_em=:v WHERE usuario_id=(SELECT id FROM usuarios WHERE email='one@example.com')"),{"v":datetime.now(timezone.utc)-timedelta(minutes=1)}); db.commit()
        email,token="one@example.com",token1
    elif case=="third_party": email,token="one@example.com",token2
    else: email,token="one@example.com","xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    assert client.post("/api/auth/activation/complete",json={"email":email,"token":token,"senha":"Senha-Nova-Segura-123!"}).status_code==400


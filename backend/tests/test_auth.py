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
    settings.admin_ui_username = "admin"
    from app.services.auth import hash_password
    settings.admin_ui_password_hash = hash_password("Senha-Administrativa-Segura-2026!")
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


def _admin_session(client):
    from conftest import TEST_ADMIN_PASSWORD
    response = client.post("/api/admin/auth/login", json={"username": "admin-teste", "senha": TEST_ADMIN_PASSWORD})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_login_and_professor_management_authorization(client, endereco):
    from tests.test_empresas import empresa_payload
    from tests.test_moedas import aluno_payload, professor_payload, provisionar_professor

    assert client.get("/api/admin/professores").status_code == 401
    assert client.post("/api/admin/auth/login", json={"username": "admin-teste", "senha": "senha-errada"}).status_code == 401
    admin_headers = _admin_session(client)

    student = client.post("/api/alunos", json=aluno_payload(endereco)).json()
    teacher = provisionar_professor(client, professor_payload(endereco)).json()
    company = client.post("/api/empresas", json=empresa_payload(endereco)).json()
    provision_payload = professor_payload(endereco, email="admin-check@example.com")
    provision_payload.pop("senha")
    update_payload = {
        "nome": "Tentativa de alteração", "email": "professor@example.com",
        "departamento": "Computação", "instituicao_id": 1, "endereco": endereco,
    }
    cases = [
        ("aluno@example.com", "ALUNO", student),
        ("professor@example.com", "PROFESSOR", teacher),
        ("contato@livraria.com", "EMPRESA", company),
    ]
    for email, _role, _person in cases:
        token = client.post("/api/auth/login", json={"email": email, "senha": "Senha-Forte-Teste-123!"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        assert client.get("/api/admin/professores", headers=headers).status_code == 403
        assert client.post("/api/admin/professores", headers=headers, json=provision_payload).status_code == 403
        assert client.put(f"/api/admin/professores/{teacher['id']}", headers=headers, json=update_payload).status_code == 403

    listed = client.get("/api/admin/professores", headers=admin_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["conta_ativada"] is True
    assert client.get(f"/api/admin/professores/{teacher['id']}", headers=admin_headers).status_code == 200
    assert client.put(f"/api/admin/professores/{teacher['id']}", headers=admin_headers, json={}).status_code == 422


def test_admin_provisions_professor_without_password_and_activation_is_one_time(client, endereco, monkeypatch):
    import re
    import app.services.auth as auth
    from conftest import TestingSession
    from app.models import Usuario
    from tests.test_moedas import professor_payload

    sent = {}
    def capture_email(email, subject, html):
        sent.update(email=email, subject=subject, html=html)
        return True
    monkeypatch.setattr(auth, "enviar_email", capture_email)

    payload = professor_payload(endereco, email="novo.professor@example.com")
    payload.pop("senha")
    response = client.post("/api/admin/professores", headers=_admin_session(client), json=payload)
    assert response.status_code == 201
    data = response.json()
    professor = data["professor"]
    assert data["activation_sent"] is True
    assert professor["saldo"] == "1000.00"
    assert professor["instituicao"]["id"] == 1
    assert professor["conta_ativada"] is False
    with TestingSession() as db:
        user = db.get(Usuario, professor["id"])
        assert user.senha_hash is None
        assert user.professor.instituicao_id == 1

    token_match = re.search(r"<p>([A-Za-z0-9_-]{40,})</p>", sent["html"])
    assert token_match
    token = token_match.group(1)
    activated = client.post("/api/auth/activation/complete", json={"email": professor["email"], "token": token, "senha": "Senha-Nova-Segura-2026!"})
    assert activated.status_code == 204
    assert client.post("/api/auth/activation/complete", json={"email": professor["email"], "token": token, "senha": "Senha-Outra-Segura-2026!"}).status_code == 400
    admin_headers = _admin_session(client)
    assert client.get(f"/api/admin/professores/{professor['id']}", headers=admin_headers).json()["conta_ativada"] is True
    assert client.post(f"/api/admin/professores/{professor['id']}/ativacao", headers=admin_headers).json()["accepted"] is False

    updated = {key: payload[key] for key in ("nome", "email", "departamento", "instituicao_id", "endereco")}
    updated["nome"] = "Professor Atualizado"
    changed = client.put(f"/api/admin/professores/{professor['id']}", headers=admin_headers, json=updated)
    assert changed.status_code == 200
    assert changed.json()["nome"] == "Professor Atualizado"


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


from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import logging
import secrets

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.models import Usuario
from app.services.email_service import enviar_email, estrutura_email

hasher = PasswordHash.recommended()
bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def _activation_schema_unavailable(exc: DBAPIError) -> HTTPException:
    original = exc.orig
    state = getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)
    detail = str(original).lower()
    if state == "42P01" or "no such table: ativacoes_conta" in detail:
        return HTTPException(503, "Ativacao indisponivel: aplique as migrations do backend e tente novamente.")
    raise exc


def hash_password(password: str) -> str:
    return hasher.hash(password)


def verify_password(password: str, hashed: str | None) -> bool:
    return bool(hashed and hasher.verify(password, hashed))


def issue_token(user: Usuario) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user.id), "role": user.tipo, "iat": now,
                       "exp": now + timedelta(minutes=30), "jti": secrets.token_hex(12)},
                      get_settings().signing_secret(), algorithm="HS256")


def issue_admin_token(username: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": username, "role": "ADMIN", "iat": now,
         "exp": now + timedelta(minutes=15), "jti": secrets.token_hex(12)},
        get_settings().signing_secret(), algorithm="HS256",
    )


def authenticate(email: str, password: str, db: Session) -> Usuario:
    user = db.scalar(select(Usuario).where(Usuario.email == email.lower()))
    if not user or not verify_password(password, user.senha_hash):
        raise HTTPException(401, "E-mail ou senha inválidos", headers={"WWW-Authenticate": "Bearer"})
    return user


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
                 db: Session = Depends(get_db)) -> Usuario:
    if credentials is None:
        raise HTTPException(401, "Autenticação necessária", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, get_settings().signing_secret(), algorithms=["HS256"])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(401, "Token inválido ou expirado")
    user = db.get(Usuario, user_id)
    if not user or payload.get("role") != user.tipo:
        raise HTTPException(401, "Token inválido")
    return user


def require_role(*roles: str):
    def dependency(user: Usuario = Depends(current_user)) -> Usuario:
        if user.tipo not in roles:
            raise HTTPException(403, "Perfil sem permissão para esta operação")
        return user
    return dependency


def require_admin(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    settings = get_settings()
    if credentials is None:
        raise HTTPException(401, "Autenticação administrativa necessária", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, settings.signing_secret(), algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Token inválido ou expirado", headers={"WWW-Authenticate": "Bearer"})
    username = payload.get("sub")
    if payload.get("role") != "ADMIN" or not isinstance(username, str) or not hmac.compare_digest(username, settings.admin_ui_username):
        raise HTTPException(403, "Perfil sem permissão para esta operação")
    return username


def require_anonymous_registration(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> None:
    """Allow public registration only when no valid Conquista JWT is presented."""
    if credentials is None:
        return
    try:
        jwt.decode(credentials.credentials, get_settings().signing_secret(), algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Token inválido ou expirado")
    raise HTTPException(403, "O cadastro público está disponível apenas para visitantes.")


def password_setup_token(email: str, secret: str) -> str:
    return hmac.new(secret.encode(), email.lower().encode(), hashlib.sha256).hexdigest()


def request_activation(email: str, db: Session) -> bool:
    """Email-bound, expiring, one-time activation; never reveals account existence."""
    user = db.scalar(select(Usuario).where(Usuario.email == email.lower()))
    if not user or user.senha_hash:
        return True
    now = datetime.now(timezone.utc)
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    try:
        db.execute(text("DELETE FROM ativacoes_conta WHERE usuario_id=:uid"), {"uid": user.id})
        db.execute(text("INSERT INTO ativacoes_conta (usuario_id, token_hash, expira_em) VALUES (:uid,:token,:exp)"), {"uid": user.id, "token": token_hash, "exp": now + timedelta(minutes=15)})
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        raise _activation_schema_unavailable(exc) from exc
    sent = enviar_email(user.email, "Conquista | Ative sua conta", estrutura_email("Ativação de conta", f"<p>Use este token temporário no fluxo seguro de ativação:</p><p>{raw}</p><p>Expira em 15 minutos e só pode ser usado uma vez.</p>"))
    if not sent:
        # Never leave an unusable grant active after delivery failure.
        db.execute(
            text("DELETE FROM ativacoes_conta WHERE usuario_id=:uid AND token_hash=:token"),
            {"uid": user.id, "token": token_hash},
        )
        db.commit()
        logger.error("Token de ativacao nao entregue; grant invalidado")
        return False
    return True


def activate_account(email: str, token: str, password: str, db: Session) -> None:
    user = db.scalar(select(Usuario).where(Usuario.email == email.lower()))
    if not user or user.senha_hash:
        raise HTTPException(400, "Ativação inválida ou expirada")
    digest = hashlib.sha256(token.encode()).hexdigest()
    try:
        row = db.execute(text("SELECT token_hash, expira_em FROM ativacoes_conta WHERE usuario_id=:uid"), {"uid": user.id}).first()
    except DBAPIError as exc:
        db.rollback()
        raise _activation_schema_unavailable(exc) from exc
    if not row or not hmac.compare_digest(row.token_hash, digest):
        raise HTTPException(400, "Ativação inválida ou expirada")
    expires_at = row.expira_em
    if isinstance(expires_at, str): expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None: expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        raise HTTPException(400, "Ativação inválida ou expirada")
    try:
        deleted = db.execute(text("DELETE FROM ativacoes_conta WHERE usuario_id=:uid AND token_hash=:token AND expira_em>:now"), {"uid": user.id, "token": digest, "now": datetime.now(timezone.utc)})
    except DBAPIError as exc:
        db.rollback()
        raise _activation_schema_unavailable(exc) from exc
    if deleted.rowcount != 1:
        db.rollback()
        raise HTTPException(400, "Ativação inválida ou expirada")
    user.senha_hash = hash_password(password)
    db.commit()



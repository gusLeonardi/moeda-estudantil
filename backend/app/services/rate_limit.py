"""Database-backed fixed-window limits for public authentication routes."""
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import secrets
import logging

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.config import get_settings

logger = logging.getLogger(__name__)


_UPSERT = text("""
    INSERT INTO auth_rate_limits (bucket_key, window_started_at, attempts)
    VALUES (:key, :now, 1)
    ON CONFLICT (bucket_key) DO UPDATE SET
      window_started_at = CASE
        WHEN auth_rate_limits.window_started_at <= :cutoff THEN :now
        ELSE auth_rate_limits.window_started_at
      END,
      attempts = CASE
        WHEN auth_rate_limits.window_started_at <= :cutoff THEN 1
        ELSE auth_rate_limits.attempts + 1
      END
    RETURNING attempts, window_started_at
""")


def enforce_auth_limits(
    db: Session,
    scope: str,
    identities: list[tuple[str, str, int]],
    window_seconds: int,
) -> None:
    """Count attempts atomically; identity tuples are (kind, value, limit)."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=window_seconds)
    secret = get_settings().signing_secret().encode()
    retry_after = 0

    try:
        for kind, value, limit in identities:
            material = f"{scope}:{kind}:{value.strip().lower()}".encode()
            key = hmac.new(secret, material, hashlib.sha256).hexdigest()
            attempts, started = db.execute(
                _UPSERT, {"key": key, "now": now, "cutoff": cutoff}
            ).one()
            if isinstance(started, str):
                started = datetime.fromisoformat(started)
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            if attempts > limit:
                retry_after = max(
                    retry_after,
                    int((started + timedelta(seconds=window_seconds) - now).total_seconds()) + 1,
                )

        # Keep abandoned address/email buckets bounded without storing raw identities.
        if secrets.randbelow(64) == 0:
            db.execute(
                text("DELETE FROM auth_rate_limits WHERE window_started_at < :old"),
                {"old": now - timedelta(days=2)},
            )
        db.commit()
    except DBAPIError as exc:
        db.rollback()
        logger.error("Auth rate limit storage unavailable (%s)", type(exc).__name__)
        raise HTTPException(503, "Autenticação temporariamente indisponível; verifique as migrations do backend.") from exc

    if retry_after:
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas. Aguarde antes de tentar novamente.",
            headers={"Retry-After": str(retry_after)},
        )

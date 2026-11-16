from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Sistema de Moeda Estudantil"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./moeda_estudantil.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    jwt_secret: str = ""
    admin_cron_token: str = ""
    admin_ui_username: str = ""
    admin_ui_password_hash: str = ""
    app_env: str = "development"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def signing_secret(self) -> str:
        import os

        secret = self.jwt_secret or os.getenv("JWT_SECRET", "")
        if not secret and self.app_env.lower() == "production":
            raise RuntimeError("JWT_SECRET precisa ser configurado em produção")
        return secret or "local-development-secret-change-before-deploy"

    def validate_production(self) -> None:
        if self.app_env.lower() != "production":
            return
        secret = self.jwt_secret or __import__("os").getenv("JWT_SECRET", "")
        if len(secret.encode()) < 32:
            raise RuntimeError("JWT_SECRET de pelo menos 32 bytes precisa ser configurado em produção")
        if len(self.admin_cron_token.encode()) < 32:
            raise RuntimeError("ADMIN_CRON_TOKEN de pelo menos 32 bytes precisa ser configurado em produção")
        if not self.admin_ui_username or not self.admin_ui_password_hash.startswith("$argon2"):
            raise RuntimeError("ADMIN_UI_USERNAME e ADMIN_UI_PASSWORD_HASH Argon2 precisam ser configurados em produção")
        if not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
            raise RuntimeError("DATABASE_URL de PostgreSQL precisa ser configurada em produção")
        sslmode = make_url(self.database_url).query.get("sslmode")
        if sslmode not in {"require", "verify-ca", "verify-full"}:
            raise RuntimeError("DATABASE_URL precisa exigir TLS com sslmode=require ou superior")
        if not self.cors_origin_list or any(
            origin == "*" or not origin.startswith("https://")
            for origin in self.cors_origin_list
        ):
            raise RuntimeError("CORS_ORIGINS precisa conter apenas origens HTTPS explícitas em produção")


@lru_cache
def get_settings() -> Settings:
    return Settings()

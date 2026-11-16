from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Sistema de Moeda Estudantil"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./moeda_estudantil.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    jwt_secret: str = ""
    admin_cron_token: str = ""
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


@lru_cache
def get_settings() -> Settings:
    return Settings()

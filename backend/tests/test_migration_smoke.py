"""Disposable SQLite migration smoke test; never reads the configured .env database."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from sqlalchemy import create_engine, text


def test_activation_migration_preserves_existing_passwordless_users():
    backend = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="conquista-migration-") as directory:
        database = Path(directory) / "migration.db"
        env = os.environ.copy()
        env["DATABASE_URL"] = f"sqlite:///{database.as_posix()}"
        for revision in ("20261109_0005", "head"):
            if revision == "head":
                engine = create_engine(env["DATABASE_URL"])
                with engine.begin() as connection:
                    connection.execute(text("INSERT INTO usuarios (nome,email,tipo,senha_hash) VALUES ('Legacy','legacy@example.com','ALUNO',NULL)"))
                engine.dispose()
            subprocess.run([sys.executable, "-m", "alembic", "upgrade", revision], cwd=backend, env=env, check=True, capture_output=True, text=True)
        engine = create_engine(env["DATABASE_URL"])
        with engine.connect() as connection:
            assert connection.execute(text("SELECT count(*) FROM usuarios WHERE email='legacy@example.com' AND senha_hash IS NULL")).scalar_one() == 1
            assert connection.execute(text("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='ativacoes_conta'")).scalar_one() == 1
        engine.dispose()

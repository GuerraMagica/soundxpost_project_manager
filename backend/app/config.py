"""Application configuration.

SQLite is the MVP datastore. The DATABASE_URL is intentionally
SQLAlchemy-standard so a future move to PostgreSQL only requires
changing this value (e.g. postgresql+psycopg://user:pass@host/db).
"""
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "SOUND X-POST"
    environment: str = os.getenv("ENVIRONMENT", "lab")
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'soundxpost.db'}"
    )
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

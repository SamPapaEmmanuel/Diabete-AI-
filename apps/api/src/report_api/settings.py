from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[4]


class ReportSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="REPORT_", env_file=PROJECT_ROOT / ".env", extra="ignore"
    )

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = (
        "postgresql+psycopg://report:local-report-password@127.0.0.1:5432/report_dev"
    )
    frontend_origin: str = "http://localhost:5173"
    cookie_secure: bool = False
    csrf_secret: str = "local-development-secret-change-before-hosting"
    mail_directory: Path = PROJECT_ROOT / ".runtime" / "mail"

    @model_validator(mode="after")
    def require_safe_environment(self) -> "ReportSettings":
        if not self.database_url.startswith("postgresql+psycopg://"):
            raise ValueError("This application requires PostgreSQL with psycopg")
        if self.environment == "production":
            raise ValueError("Hosted authentication requires a reviewed production mail transport")
        return self

    @property
    def session_cookie(self) -> str:
        return "__Host-report_session" if self.cookie_secure else "report_session"

    @property
    def csrf_cookie(self) -> str:
        return "__Host-report_csrf" if self.cookie_secure else "report_csrf"


from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root is the parent directory of core/
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "chinook-mcp-server"
    app_version: str = "0.1.0"
    app_env: str = "development"

    database_path: str = "data/chinook.db"
    sqlalchemy_echo: bool = False

    log_level: str = "INFO"
    log_to_file: bool = False
    log_file: str = "logs/chinook-mcp-server.log"

    @property
    def resolved_database_path(self) -> Path:
        """Return the absolute path to the SQLite database."""

        path = Path(self.database_path)

        if not path.is_absolute():
            path = PROJECT_ROOT / path

        return path.resolve()

    @property
    def database_url(self) -> str:
        """Build an asynchronous SQLite connection URL."""

        path = self.resolved_database_path

        return f"sqlite+aiosqlite:///{path.as_posix()}"


settings = Settings()

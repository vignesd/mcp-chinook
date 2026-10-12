
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

from core.config import settings


def create_database_engine() -> AsyncEngine:
    """Create the asynchronous SQLAlchemy engine."""

    database_path = settings.resolved_database_path

    if not database_path.is_file():
        raise FileNotFoundError(
            f"Chinook database not found: {database_path}"
        )

    return create_async_engine(
        settings.database_url,
        echo=settings.sqlalchemy_echo,
    )


# Shared engine used by services and MCP tools.
engine = create_database_engine()


async def check_database_connection() -> bool:
    """Return True if the database can execute a simple query."""

    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        return result.scalar_one() == 1


async def close_database() -> None:
    """Dispose of the engine and release its connections."""

    await engine.dispose()

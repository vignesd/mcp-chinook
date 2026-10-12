
from typing import Any
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from mcp.server.mcpserver.exceptions import ToolError
from core.config import settings
from core.database import (
    check_database_connection,
    engine,
)
from core.logging import logger

from models.album_models import (
    AlbumOutput,
    AlbumListOutput,
    AlbumSearchOutput,
    GetAlbumInput,
    AlbumCountOutput
)
from models.server_model import (
    HealthCheckOutput,
    ServerInfoOutput,
)
from services.album_services import (
    get_album as fetch_album,
    list_albums as fetch_albums,
    search_albums as find_albums_by_title,
    get_total_albums as get_total,
)


async def health_check() -> HealthCheckOutput:
    """Check whether the Chinook database is reachable."""

    try:
        is_connected = await check_database_connection()

        if is_connected:
            return HealthCheckOutput(
                status="healthy",
                database="Chinook",
                message="Database connection successful.",
            )

        return HealthCheckOutput(
            status="unhealthy",
            database="Chinook",
            message="Database health check failed.",
        )

    except Exception:
        logger.exception("Database health check failed.")

        return HealthCheckOutput(
            status="unhealthy",
            database="Chinook",
            message="Unable to connect to the database.",
        )


async def server_info() -> ServerInfoOutput:
    """Return metadata about the Chinook MCP server."""

    return ServerInfoOutput(
        server_name=settings.app_name,
        version=settings.app_version,
        transport="stdio",
        database_engine="sqlite",
        database_file=settings.resolved_database_path.name,
        tools=[
            "health_check",
            "server_info",
            "get_album",
            "list_albums",
            "search_albums",
        ],
    )


async def get_album(album_id: int) -> AlbumOutput:
    """Get an album by its ID. If the ID is invalid, correct the input before retrying. 
    If the album does not exist, do not retry the same ID. Retry database failures only when they are transient. """
    if album_id < 1:
        raise ToolError("INVALID_ARGUMENT: album_id must be a positive integer. "
                        "Provide an album_id greater than or equal to 1. "
                        "Do not retry with the same invalid value.")
    try:
        validated_input = GetAlbumInput(album_id=album_id)
        album = await fetch_album(engine, validated_input.album_id)

    except ValidationError:
        raise ToolError(
            "INVALID_ARGUMENT: album_id must be a positive integer."
        ) from None

    except SQLAlchemyError:
        logger.exception("Database failure fetching album_id=%s", album_id)
        raise ToolError("DATABASE_ERROR: Unable to retrieve the album because "
                        "a database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None
    if album is None:
        raise ToolError(f"NOT_FOUND: No album exists with album_id={album_id}. "
                        "Do not retry the same ID. If the user provided an album "
                        "title, use search_albums to find matching albums.")

    return AlbumOutput(found=True, album=album)


# async def list_albums() -> AlbumListOutput:
#     """Return all albums from the Chinook database."""

#     albums = await fetch_albums(engine)

#     return AlbumListOutput(
#         count=len(albums),
#         albums=albums,
#     )

async def list_albums(
    limit: int = 10,
    offset: int = 0,
) -> AlbumListOutput:
    """List albums using pagination.

    Args:
        limit: Number of albums to return, from 1 to 100.
        offset: Number of albums to skip, starting from 0.
    """
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100.")

    if offset < 0:
        raise ValueError("offset must be zero or greater.")

    result = await fetch_albums(
        engine=engine,
        limit=limit,
        offset=offset,
    )

    return AlbumListOutput(**result)


async def search_albums(title: str) -> AlbumSearchOutput:
    """Search albums by a partial match on the album title."""

    title = title.strip()

    if not title:
        raise ValueError("title must not be empty.")

    albums = await find_albums_by_title(engine, title)

    return AlbumSearchOutput(
        query=title,
        count=len(albums),
        albums=albums,
    )


async def get_albums_count() -> AlbumCountOutput:
    """Return total album count."""
    total = await get_total(engine,)

    return AlbumCountOutput(
        count=total
    )

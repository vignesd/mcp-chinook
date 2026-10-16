from sqlalchemy.exc import SQLAlchemyError
from mcp.server.mcpserver.exceptions import ToolError

from core.logging import logger
from models.artist_models import (
    ArtistDetailsOutput,
    ArtistListOutput,
    ArtistSearchOutput,
)
from services.artist_services import (
    get_artist_details as fetch_artist_details,
    list_artists as fetch_artists,
    search_artists as find_artists_by_name,
)


async def list_artists(
    limit: int = 10,
    offset: int = 0,
) -> ArtistListOutput:
    """List artists using pagination.

    Args:
        limit: Number of artists to return, from 1 to 100.
        offset: Number of artists to skip, starting from 0.
    """
    if not 1 <= limit <= 100:
        raise ToolError("INVALID_ARGUMENT: limit must be between 1 and 100. "
                        "Do not retry with the same invalid value.")

    if offset < 0:
        raise ToolError("INVALID_ARGUMENT: offset must be zero or greater. "
                        "Do not retry with the same invalid value.")

    try:
        result = await fetch_artists(limit=limit, offset=offset)

    except SQLAlchemyError:
        logger.exception(
            "Database failure listing artists limit=%s offset=%s",
            limit,
            offset,
        )
        raise ToolError("DATABASE_ERROR: Unable to list artists because a "
                        "database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None

    return ArtistListOutput(**result)


async def search_artists(name: str, limit: int = 10) -> ArtistSearchOutput:
    """Search artists by a partial match on the artist name.

    Args:
        name: All or part of the artist name.
        limit: Maximum number of artists to return, from 1 to 100.
    """
    name = name.strip()

    if not name:
        raise ToolError("INVALID_ARGUMENT: name must not be empty. "
                        "Provide all or part of an artist name.")

    if not 1 <= limit <= 100:
        raise ToolError("INVALID_ARGUMENT: limit must be between 1 and 100. "
                        "Do not retry with the same invalid value.")

    try:
        artists = await find_artists_by_name(name, limit)

    except SQLAlchemyError:
        logger.exception("Database failure searching artists name=%s", name)
        raise ToolError("DATABASE_ERROR: Unable to search artists because a "
                        "database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None

    return ArtistSearchOutput(
        query=name,
        count=len(artists),
        artists=artists,  # type:ignore
    )


async def get_artist_details(artist_id: int) -> ArtistDetailsOutput:
    """Get an artist and their albums by ArtistId. If the ID is invalid, correct
    the input before retrying. If the artist does not exist, do not retry the
    same ID. Retry database failures only when they are transient."""
    if artist_id < 1:
        raise ToolError("INVALID_ARGUMENT: artist_id must be a positive integer. "
                        "Provide an artist_id greater than or equal to 1. "
                        "Do not retry with the same invalid value.")

    try:
        details = await fetch_artist_details(artist_id)

    except SQLAlchemyError:
        logger.exception("Database failure fetching artist_id=%s", artist_id)
        raise ToolError("DATABASE_ERROR: Unable to retrieve the artist because "
                        "a database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None

    if details is None:
        raise ToolError(f"NOT_FOUND: No artist exists with artist_id={artist_id}. "
                        "Do not retry the same ID. If the user provided an artist "
                        "name, use search_artists to find matching artists.")

    return ArtistDetailsOutput(
        found=True,
        artist=details["artist"],
        album_count=len(details["albums"]),
        albums=details["albums"],
    )

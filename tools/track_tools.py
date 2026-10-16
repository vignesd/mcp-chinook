from sqlalchemy.exc import SQLAlchemyError
from mcp.server.mcpserver.exceptions import ToolError

from core.logging import logger
from models.track_models import (
    GenreListOutput,
    GenreTracksOutput,
    LongestTracksOutput,
    TrackDetailsOutput,
    TrackSearchOutput,
)
from services.track_services import (
    get_longest_tracks as fetch_longest_tracks,
    get_track_details as fetch_track_details,
    get_tracks_by_genre as fetch_tracks_by_genre,
    list_genres as fetch_genres,
    search_tracks as find_tracks,
)


async def search_tracks(
    query: str,
    limit: int = 10,
    offset: int = 0,
) -> TrackSearchOutput:
    """Search tracks by a partial match on track name or composer.

    Args:
        query: All or part of a track name or composer.
        limit: Number of tracks to return, from 1 to 100.
        offset: Number of tracks to skip, starting from 0.
    """
    query = query.strip()

    if not query:
        raise ToolError("INVALID_ARGUMENT: query must not be empty. "
                        "Provide all or part of a track name or composer.")

    if not 1 <= limit <= 100:
        raise ToolError("INVALID_ARGUMENT: limit must be between 1 and 100. "
                        "Do not retry with the same invalid value.")

    if offset < 0:
        raise ToolError("INVALID_ARGUMENT: offset must be zero or greater. "
                        "Do not retry with the same invalid value.")

    try:
        result = await find_tracks(query, limit, offset)

    except SQLAlchemyError:
        logger.exception("Database failure searching tracks query=%s", query)
        raise ToolError("DATABASE_ERROR: Unable to search tracks because a "
                        "database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None

    return TrackSearchOutput(query=query, **result)


async def get_track_details(track_id: int) -> TrackDetailsOutput:
    """Get a track by TrackId. If the ID is invalid, correct the input before
    retrying. If the track does not exist, do not retry the same ID. Retry
    database failures only when they are transient."""
    if track_id < 1:
        raise ToolError("INVALID_ARGUMENT: track_id must be a positive integer. "
                        "Provide a track_id greater than or equal to 1. "
                        "Do not retry with the same invalid value.")

    try:
        track = await fetch_track_details(track_id)

    except SQLAlchemyError:
        logger.exception("Database failure fetching track_id=%s", track_id)
        raise ToolError("DATABASE_ERROR: Unable to retrieve the track because "
                        "a database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None

    if track is None:
        raise ToolError(f"NOT_FOUND: No track exists with track_id={track_id}. "
                        "Do not retry the same ID. If the user provided a track "
                        "name, use search_tracks to find matching tracks.")

    return TrackDetailsOutput(found=True, track=track)  # type:ignore


async def list_genres() -> GenreListOutput:
    """List all music genres with the number of tracks in each."""

    try:
        genres = await fetch_genres()

    except SQLAlchemyError:
        logger.exception("Database failure listing genres")
        raise ToolError("DATABASE_ERROR: Unable to list genres because a "
                        "database operation failed. Retry at most twice with "
                        "a short delay. If the error persists, stop and report "
                        "the issue to the user.") from None

    return GenreListOutput(
        count=len(genres),
        genres=genres,  # type:ignore
    )


async def get_tracks_by_genre(
    genre_id: int,
    limit: int = 10,
    offset: int = 0,
) -> GenreTracksOutput:
    """List tracks in a genre using pagination.

    Args:
        genre_id: GenreId from list_genres.
        limit: Number of tracks to return, from 1 to 100.
        offset: Number of tracks to skip, starting from 0.
    """
    if genre_id < 1:
        raise ToolError("INVALID_ARGUMENT: genre_id must be a positive integer. "
                        "Use list_genres to find valid genre IDs.")

    if not 1 <= limit <= 100:
        raise ToolError("INVALID_ARGUMENT: limit must be between 1 and 100. "
                        "Do not retry with the same invalid value.")

    if offset < 0:
        raise ToolError("INVALID_ARGUMENT: offset must be zero or greater. "
                        "Do not retry with the same invalid value.")

    try:
        result = await fetch_tracks_by_genre(genre_id, limit, offset)

    except SQLAlchemyError:
        logger.exception(
            "Database failure fetching tracks for genre_id=%s", genre_id)
        raise ToolError("DATABASE_ERROR: Unable to retrieve tracks for the genre "
                        "because a database operation failed. Retry at most "
                        "twice with a short delay. If the error persists, stop "
                        "and report the issue to the user.") from None

    if result is None:
        raise ToolError(f"NOT_FOUND: No genre exists with genre_id={genre_id}. "
                        "Do not retry the same ID. Use list_genres to find "
                        "valid genre IDs.")

    return GenreTracksOutput(**result)


async def get_longest_tracks(limit: int = 10) -> LongestTracksOutput:
    """List the longest tracks by duration.

    Args:
        limit: Number of tracks to return, from 1 to 100.
    """
    if not 1 <= limit <= 100:
        raise ToolError("INVALID_ARGUMENT: limit must be between 1 and 100. "
                        "Do not retry with the same invalid value.")

    try:
        tracks = await fetch_longest_tracks(limit)

    except SQLAlchemyError:
        logger.exception("Database failure fetching longest tracks")
        raise ToolError("DATABASE_ERROR: Unable to retrieve the longest tracks "
                        "because a database operation failed. Retry at most "
                        "twice with a short delay. If the error persists, stop "
                        "and report the issue to the user.") from None

    return LongestTracksOutput(
        count=len(tracks),
        tracks=tracks,  # type:ignore
    )

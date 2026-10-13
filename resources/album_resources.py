"""Read-only MCP resources for the Chinook album catalogue."""

import json

from mcp.server import MCPServer

from core.database import engine
from services.album_services import (
    get_album as fetch_album,
    list_albums as fetch_albums,
)


def register_album_resources(mcp: MCPServer) -> None:
    """Register album resources on the existing MCP server."""

    @mcp.resource(
        uri="chinook://albums",
        name="album_catalogue",
        title="Album Catalogue",
        description=(
            "Retrieve the album catalogue from the Chinook music database. "
            "Provides a collection of albums with their album IDs, titles, and "
            "associated artist information. Use this resource when the user wants "
            "to explore or browse the available albums in the music library. "
            "For a specific album, use the album details resource. "
            "For aggregate information about albums, use the album statistics resource."
        ),
        mime_type="text/plain",
    )
    async def album_catalogue() -> str:
        """Return all albums in the Chinook database as JSON."""
        albums = await fetch_albums(engine)
        return json.dumps(
            {"count": len(albums), "albums": albums},
            default=str,
            indent=2,
        )

    @mcp.resource(
        uri="chinook://albums/{album_id}",
        name="album_details",
        title="Album Details",
        description=(
            "Retrieve detailed information about a specific album in the Chinook "
            "music database using its unique album ID. Provides the album title, "
            "album ID, associated artist information, and other available album "
            "metadata. Use this resource when the user asks about a particular "
            "album or wants to identify an album by its ID. The album_id URI "
            "parameter must be a valid integer. If the album does not exist, "
            "return a clear not-found message."
        ),
        mime_type="text/plain",
    )
    async def album_details(album_id: int) -> str:
        """Return an album record by its ID as JSON."""
        if album_id < 1:
            return json.dumps(
                {"error": "INVALID_ARGUMENT", "message": "album_id must be positive."}
            )

        album = await fetch_album(engine, album_id)

        if album is None:
            return json.dumps(
                {
                    "error": "NOT_FOUND",
                    "message": f"Album {album_id} was not found.",
                }
            )

        return json.dumps(album, default=str, indent=2)

    @mcp.resource(
        uri="chinook://albums/statistics",
        name="album_statistics",
        title="Album Statistics",
        description=(
            "Retrieve aggregate statistics about the album catalogue in the "
            "Chinook music database. Provides useful summary information, such as "
            "the total number of albums and, when supported by the implementation, "
            "the number of distinct artists represented in the album catalogue "
            "and the distribution of albums by artist. Use this resource when "
            "the user asks for album counts, catalogue summaries, or general "
            "statistical information rather than individual album records."
        ),
        mime_type="text/plain",
    )
    async def album_statistics() -> str:
        """Return basic album catalogue statistics."""
        albums = await fetch_albums(engine)
        return json.dumps(
            {"total_albums": len(albums)},
            indent=2,
        )

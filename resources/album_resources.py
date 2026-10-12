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

    @mcp.resource("chinook://albums")
    async def album_catalogue() -> str:
        """Return all albums in the Chinook database as JSON."""
        albums = await fetch_albums(engine)
        return json.dumps(
            {"count": len(albums), "albums": albums},
            default=str,
            indent=2,
        )

    @mcp.resource("chinook://albums/{album_id}")
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

    @mcp.resource("chinook://albums/statistics")
    async def album_statistics() -> str:
        """Return basic album catalogue statistics."""
        albums = await fetch_albums(engine)
        return json.dumps(
            {"total_albums": len(albums)},
            indent=2,
        )

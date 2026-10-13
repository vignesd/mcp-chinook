"""Reusable prompts for the Chinook album MCP server."""

from mcp.server import MCPServer


def register_album_prompts(mcp: MCPServer) -> None:
    """Register album prompts on the existing MCP server."""

    @mcp.prompt(
        name="list_albums",
        title="List albums",
        description="List albums from the Chinook database.",
    )
    def list_albums_prompt() -> str:
        return "List the albums available in the Chinook music database."

    @mcp.prompt(
        name="get_album",
        title="Get album",
        description="Retrieve an album by its ID.",
    )
    def get_album_prompt(album_id: int = 1) -> str:
        return f"Get the details of album ID {album_id}."

    @mcp.prompt(
        name="search_albums",
        title="Search albums",
        description="Search albums by a partial title.",
    )
    def search_albums_prompt(title: str = "Rock") -> str:
        return f"Search for albums whose titles contain '{title}'."

    @mcp.prompt(
        name="get_total_albums",
        title="Get total albums",
        description="Count albums in the database.",
    )
    def get_total_albums_prompt() -> str:
        return "How many albums are available in the Chinook database?"

    @mcp.prompt(
        name="album_search_and_details",
        title="Album search and details",
        description="Search albums and retrieve a matching album.",
    )
    def album_search_and_details_prompt(title: str = "Rock") -> str:
        return (
            f"Search for albums whose titles contain '{title}'. "
            "Then retrieve the details of one matching album by its ID."
        )

    @mcp.prompt(
        name="album_catalogue_summary",
        title="Album catalogue summary",
        description="Summarize the album catalogue using available tools.",
    )
    def album_catalogue_summary_prompt(title: str = "Rock") -> str:
        return (
            "Find the total number of albums and search for albums "
            f"containing '{title}'. Summarize the results."
        )

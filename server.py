from tools.album_tools import (
    get_album,
    health_check,
    list_albums,
    search_albums,
    server_info,
    get_albums_count,
)
from tools.customer_tools import (
    get_customer_by_email,
    get_customer_by_id,
    get_customers_count,
    search_customers_by_keyword
)

from tools.invoice_tools import (
    get_customer_purchase_tracks,
    get_customer_invoices,
    get_invoice_details,
)

from tools.artist_tools import (
    get_artist_details,
    list_artists,
    search_artists,
)

from tools.employee_tools import (
    get_employee_details,
    get_employee_sales_summary,
    list_employees,
)

from tools.track_tools import (
    get_longest_tracks,
    get_track_details,
    get_tracks_by_genre,
    list_genres,
    search_tracks,
)

from tools.sales_tools import (
    get_best_selling_tracks,
    get_customer_lifetime_value,
    get_revenue_by_country,
    get_sales_by_month,
    get_top_artists_by_revenue,
    get_top_customers,
    get_total_revenue,
)

import hmac
import os
from typing import Any

import uvicorn
from mcp.server.transport_security import TransportSecuritySettings

from core.logging import logger
from core.config import settings
from core.tool_annotations import READ, WRITE
from mcp.server import MCPServer
from prompts.album_prompts import register_album_prompts
from prompts.customer_prompts import register_customer_prompts
from resources.album_resources import register_album_resources
from resources.customer_resource import register_customer_resources


# Create the MCP server.
mcp = MCPServer(
    settings.app_name,
    version=settings.app_version,
    log_level=settings.log_level,  # type:ignore
)
# Register all prompts centrally.
register_album_prompts(mcp)
register_customer_prompts(mcp)

# Register all resources centrally.
register_album_resources(mcp)
register_customer_resources(mcp)

# Register all tools centrally.
mcp.add_tool(
    health_check,
    name="health_check",
    title="Database Health Check",
    description=(
        "Check whether the Chinook SQLite database is reachable. "
        "Use this tool to diagnose database connectivity issues."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    server_info,
    name="server_info",
    title="MCP Server Information",
    description=(
        "Get the Chinook MCP server name, version, transport, "
        "database information, and registered tool names."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_album,
    name="get_album",
    title="Get Album",
    description=("Retrieve an album by its exact AlbumId from the Chinook database. "
                 "Use when the user provides a specific album ID. "
                 "Returns the album record when found. "
                 "If no album exists, return found=false. "
                 "This tool is read-only."),
    annotations=READ, structured_output=True, )

mcp.add_tool(
    list_albums,
    name="list_albums",
    title="List Albums",
    description=(
        "Retrieve album records from the Chinook database. "
        "Use this tool when the user wants to browse albums. "
        "Returns the album records and their count."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    search_albums,
    name="search_albums",
    title="Search Albums",
    description=(
        "Search the Chinook database for albums by a partial title match. "
        "Use this tool when the user knows all or part of an album title. "
        "Provide the title text to search for. "
        "Returns matching albums and their count."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_albums_count,
    name="get_total_albums",
    title="Get Total Album Count",
    description=(
        "Return the total number of albums in the Chinook database. "
        "Use this tool when the user asks how many albums exist. "
        "Returns a count without retrieving every album record."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_customer_by_email,
    name="get_customer_by_email",
    title="Get Customer by Email",
    description=(
        "Retrieve a customer from the Chinook database using their email address. "
        "Use this tool when the user asks to find or view a customer by email. "
        "Returns the matching customer details."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_customer_by_id,
    name="get_customer_by_id",
    title="Get Customer by ID",
    description=(
        "Retrieve a customer from the Chinook database using their customer ID. "
        "Use this tool when the user asks to find or view a specific customer "
        "by ID. Returns the matching customer details."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_customers_count,
    name="get_customers_count",
    title="Get Total Customer Count",
    description=(
        "Return the total number of customers in the Chinook database. "
        "Use this tool when the user asks how many customers exist. "
        "Returns a count without retrieving every customer record."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    search_customers_by_keyword,
    name="search_customers_by_keyword",
    title="Search Customers by Keyword",
    description=(
        "Search customers in the Chinook database using a keyword. "
        "Use this tool when the user wants to find customers by name, "
        "company, email, city, or other supported customer fields. "
        "Returns matching customer records."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_customer_invoices,
    name="get_customer_invoices",
    title="Get Customer Invoices",
    description=(
        "Retrieve all invoices for a customer in the Chinook database using "
        "their CustomerId. Returns invoice details including invoice ID, "
        "invoice date, billing address, billing country, and invoice total. "
        "Use this tool when the user asks to view a customer's invoices or "
        "billing history. Requires a valid customer ID. If the customer does "
        "not exist, return a not-found error. An existing customer with no "
        "invoices should return an empty invoice list."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_customer_purchase_tracks,
    name="get_customer_purchase_tracks",
    title="Get Customer Purchase Tracks",
    description=(
        "Retrieve the tracks purchased by a customer in the Chinook database "
        "using their CustomerId. Returns purchase details including invoice ID, "
        "invoice date, customer name, billing country, track name, unit price, "
        "quantity, line total, and invoice total. Use this tool when the user "
        "asks about a customer's purchase history, purchased songs, or tracks "
        "included in their invoices. Requires a valid customer ID. If the "
        "customer does not exist, return a not-found error. An existing "
        "customer with no purchases should return an empty purchase list."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_invoice_details,
    name="get_invoice_details",
    title="Get Invoice Details",
    description=(
        "Retrieve a single invoice from the Chinook database by its InvoiceId, "
        "including the customer, billing details, invoice total, and every "
        "line item with track name, album, artist, unit price, quantity, and "
        "line total. Use this tool when the user provides an invoice ID or "
        "wants to see what was purchased on a specific invoice. If the invoice "
        "does not exist, return a not-found error; use get_customer_invoices "
        "to find valid invoice IDs."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    list_artists,
    name="list_artists",
    title="List Artists",
    description=(
        "Retrieve a page of artists from the Chinook database, each with the "
        "number of albums they have. Use this tool when the user wants to "
        "browse artists. Supports limit (1-100) and offset for pagination; "
        "use next_offset from the response to request the next page."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    search_artists,
    name="search_artists",
    title="Search Artists",
    description=(
        "Search the Chinook database for artists by a partial name match. "
        "Use this tool when the user knows all or part of an artist's name. "
        "Returns matching artists with their ArtistId and album count."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_artist_details,
    name="get_artist_details",
    title="Get Artist Details",
    description=(
        "Retrieve an artist from the Chinook database by ArtistId, including "
        "every album by the artist and the number of tracks on each album. "
        "Use this tool when the user provides an artist ID or wants to see an "
        "artist's discography. If the artist does not exist, return a "
        "not-found error; use search_artists to find artists by name."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    list_employees,
    name="list_employees",
    title="List Employees",
    description=(
        "Retrieve all Chinook employees with their EmployeeId, title, "
        "location, email, and manager. Use this tool when the user asks who "
        "works at Chinook, about the reporting structure, or needs a valid "
        "employee ID."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_employee_details,
    name="get_employee_details",
    title="Get Employee Details",
    description=(
        "Retrieve an employee from the Chinook database by EmployeeId, "
        "including title, manager, hire date, contact details, the number of "
        "customers they support, and their direct reports. Use this tool when "
        "the user asks about a specific employee. If the employee does not "
        "exist, return a not-found error; use list_employees to find valid IDs."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_employee_sales_summary,
    name="get_employee_sales_summary",
    title="Get Employee Sales Summary",
    description=(
        "Summarize sales for the customers an employee supports as their "
        "support representative: customer count, invoice count, total sales, "
        "average invoice value, and first and last sale dates. Use this tool "
        "when the user asks how much an employee or sales agent has sold. "
        "Employees with no assigned customers return zero totals. If the "
        "employee does not exist, return a not-found error."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    search_tracks,
    name="search_tracks",
    title="Search Tracks",
    description=(
        "Search the Chinook database for tracks by a partial match on the "
        "track name or composer. Use this tool when the user knows all or part "
        "of a song title or composer. Returns tracks with album, artist, genre, "
        "duration, and price. Supports limit (1-100) and offset for pagination."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_track_details,
    name="get_track_details",
    title="Get Track Details",
    description=(
        "Retrieve a track from the Chinook database by TrackId, including its "
        "album, artist, genre, media type, composer, duration, file size, "
        "price, and total units sold. Use this tool when the user provides a "
        "track ID. If the track does not exist, return a not-found error; use "
        "search_tracks to find tracks by name."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    list_genres,
    name="list_genres",
    title="List Genres",
    description=(
        "Retrieve all music genres in the Chinook database with the number of "
        "tracks in each. Use this tool when the user asks which genres exist "
        "or needs a GenreId for get_tracks_by_genre."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_tracks_by_genre,
    name="get_tracks_by_genre",
    title="Get Tracks by Genre",
    description=(
        "Retrieve a page of tracks in a genre using its GenreId. Use this tool "
        "when the user wants to browse tracks of a particular genre; call "
        "list_genres first to find the GenreId. Supports limit (1-100) and "
        "offset for pagination. If the genre does not exist, return a "
        "not-found error."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_longest_tracks,
    name="get_longest_tracks",
    title="Get Longest Tracks",
    description=(
        "Retrieve the longest tracks in the Chinook database, ordered by "
        "duration. Use this tool when the user asks for the longest songs or "
        "episodes. Returns up to limit tracks (1-100) with duration as m:ss."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_total_revenue,
    name="get_total_revenue",
    title="Get Total Revenue",
    description=(
        "Calculate total revenue, invoice count, customer count, and average "
        "invoice value from Chinook invoices. Optionally limit the result to "
        "an inclusive date range with start_date and end_date in YYYY-MM-DD "
        "format. Use this tool when the user asks how much the store has "
        "earned overall or within a period."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_sales_by_month,
    name="get_sales_by_month",
    title="Get Sales by Month",
    description=(
        "Retrieve invoice counts and revenue for each month of a given year, "
        "plus the yearly totals. Use this tool when the user asks about sales "
        "trends or monthly performance. Months without sales are omitted; a "
        "year with no sales returns an empty list."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_revenue_by_country,
    name="get_revenue_by_country",
    title="Get Revenue by Country",
    description=(
        "Rank billing countries by revenue, with customer and invoice counts "
        "for each. Use this tool when the user asks which countries generate "
        "the most sales. Returns up to limit countries (1-100)."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_best_selling_tracks,
    name="get_best_selling_tracks",
    title="Get Best-Selling Tracks",
    description=(
        "Rank tracks by the number of units sold, with artist and revenue for "
        "each. Use this tool when the user asks for the most popular or "
        "best-selling songs. Returns up to limit tracks (1-100)."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_top_artists_by_revenue,
    name="get_top_artists_by_revenue",
    title="Get Top Artists by Revenue",
    description=(
        "Rank artists by the revenue generated from sales of their tracks, "
        "with units sold for each. Use this tool when the user asks which "
        "artists earn the most. Returns up to limit artists (1-100)."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_top_customers,
    name="get_top_customers",
    title="Get Top Customers",
    description=(
        "Rank customers by total spend, with country and invoice count for "
        "each. Use this tool when the user asks who the best or biggest "
        "customers are. Returns up to limit customers (1-100)."
    ),
    annotations=READ,
    structured_output=True,
)

mcp.add_tool(
    get_customer_lifetime_value,
    name="get_customer_lifetime_value",
    title="Get Customer Lifetime Value",
    description=(
        "Calculate a customer's lifetime value by CustomerId: total spent, "
        "invoice count, average invoice value, tracks purchased, and first "
        "and last purchase dates. Use this tool when the user asks how much a "
        "specific customer has spent. Customers with no purchases return zero "
        "totals. If the customer does not exist, return a not-found error."
    ),
    annotations=READ,
    structured_output=True,
)


class ApiKeyMiddleware:
    """Protect the HTTP MCP endpoint with a Bearer API key."""

    def __init__(self, app: Any, api_key: str) -> None:
        self.app = app
        self._api_key = api_key

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        # Forward ASGI lifespan events so MCP session management works.
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # Minimal public liveness endpoint for Render.
        if path == "/health" and scope.get("method") == "GET":
            body = b'{"status":"ok"}'
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                    (b"cache-control", b"no-store"),
                ],
            })
            await send({"type": "http.response.body", "body": body})
            return

        headers = {
            key.lower(): value
            for key, value in scope.get("headers", [])
        }
        authorization = headers.get(b"authorization", b"")

        provided_key = ""
        if authorization.startswith(b"Bearer "):
            try:
                provided_key = authorization[len(b"Bearer "):].decode("utf-8")
            except UnicodeDecodeError:
                pass

        if not provided_key or not hmac.compare_digest(
            provided_key, self._api_key
        ):
            logger.warning(
                "Rejected unauthenticated HTTP request: method=%s path=%s",
                scope.get("method", "UNKNOWN"),
                path,
            )
            body = b'{"error":"Unauthorized"}'
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode("ascii")),
                    (b"cache-control", b"no-store"),
                    (b"www-authenticate", b"Bearer"),
                ],
            })
            await send({"type": "http.response.body", "body": body})
            return

        await self.app(scope, receive, send)


def _run_stdio() -> None:
    """Start the server for local STDIO clients."""
    logger.info(
        "Starting %s v%s using STDIO",
        settings.app_name,
        settings.app_version,
    )
    mcp.run(transport="stdio")


def _run_streamable_http() -> None:
    """Start authenticated Streamable HTTP for Render."""
    api_key = os.getenv("MCP_API_KEY", "").strip()

    if len(api_key) < 32:
        raise RuntimeError(
            "MCP_API_KEY must be set to a strong secret "
            "of at least 32 characters."
        )

    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    if not 1 <= port <= 65535:
        raise RuntimeError("PORT must be between 1 and 65535.")

    mcp_path = os.getenv("MCP_PATH", "/mcp").strip()
    if not mcp_path.startswith("/") or mcp_path == "/":
        raise RuntimeError("MCP_PATH must be a valid path such as /mcp.")

    allowed_hosts = [
        value.strip()
        for value in os.getenv("MCP_ALLOWED_HOSTS", "").split(",")
        if value.strip()
    ]

    if not allowed_hosts:
        raise RuntimeError(
            "Configure MCP_ALLOWED_HOSTS with your exact Render hostname."
        )

    allowed_origins = [
        value.strip()
        for value in os.getenv("MCP_ALLOWED_ORIGINS", "").split(",")
        if value.strip()
    ]

    security = TransportSecuritySettings(
        allowed_hosts=allowed_hosts,
        allowed_origins=allowed_origins,
    )

    # Keep the same MCPServer instance and all existing registrations.
    mcp_app = mcp.streamable_http_app(
        streamable_http_path=mcp_path,
        host="0.0.0.0",
        transport_security=security,
        max_request_body_size=1_048_576,
        session_idle_timeout=1800,
        max_sessions=1000,
    )

    app = ApiKeyMiddleware(mcp_app, api_key)

    logger.info(
        "Starting %s v%s using Streamable HTTP",
        settings.app_name,
        settings.app_version,
    )
    logger.info("MCP endpoint path: %s", mcp_path)
    logger.info("Health endpoint: /health")
    logger.info("HTTP authentication enabled.")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level=str(settings.log_level).lower(),
        log_config=None,
        access_log=False,
        server_header=False,
        date_header=False,
        timeout_keep_alive=5,
        limit_concurrency=100,
    )


def main() -> None:
    """Select STDIO or Streamable HTTP from the environment."""
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    try:
        if transport == "stdio":
            _run_stdio()
        elif transport == "streamable-http":
            _run_streamable_http()
        else:
            raise ValueError(
                "MCP_TRANSPORT must be 'stdio' or 'streamable-http'."
            )
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user.")
    except Exception:
        logger.exception("MCP server failed.")
        raise


if __name__ == "__main__":
    main()

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
    get_customer_invoices
)

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


def main() -> None:
    """Start the MCP server using STDIO transport."""
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    logger.info("Transport: STDIO")

    try:
        mcp.run(transport="stdio")

    except KeyboardInterrupt:
        logger.info("MCP server stopped by user.")


if __name__ == "__main__":
    main()

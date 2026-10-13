
from mcp.server import MCPServer


def register_customer_prompts(mcp: MCPServer) -> None:
    """Register customer prompts on the existing MCP server."""

    @mcp.prompt(
        name="get_customer_by_email",
        description="Find a customer by email address in the Chinook database.",
        title="Get Customer by Email",
    )
    def get_customer_by_email_prompt() -> str:
        return (
            "Find a customer by their email address in the Chinook database. "
            "Use the get_customer_by_email tool to retrieve the customer details."
        )

    @mcp.prompt(
        name="get_customer_by_id",
        description="Find a customer by ID in the Chinook database.",
        title="Get Customer by ID",
    )
    def get_customer_by_id_prompt() -> str:
        return (
            "Find a customer by their customer ID in the Chinook database. "
            "Use the get_customer_by_id tool to retrieve the customer details."
        )

    @mcp.prompt(
        name="get_customers_count",
        description="Get the total number of customers in the Chinook database.",
        title="Get Customer Count",
    )
    def get_customers_count_prompt() -> str:
        return (
            "Use the get_customers_count tool to retrieve the total number "
            "of customers in the Chinook database. "
            "Report the total count without retrieving individual customer records."
        )

    @mcp.prompt(
        name="search_customers_by_keyword",
        description="Search Chinook customers using a keyword.",
        title="Search Customers",
    )
    def search_customers_by_keyword_prompt() -> str:
        return (
            "Search for customers in the Chinook database using a keyword. "
            "Use the search_customers_by_keyword tool to retrieve matching customers. "
            "Present the results clearly, or state when no matching customers are found."
        )

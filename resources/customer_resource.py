from mcp.server import MCPServer


def register_customer_resources(mcp: MCPServer) -> None:
    """Register customer resources on the existing MCP server."""

    @mcp.resource(
        uri="chinook://customers/schema",
        name="customer_schema",
        title="Customer Schema",
        description=(
            "Provides the schema and field descriptions for the Customer table "
            "in the Chinook database."
        ),
        mime_type="text/plain",
    )
    def customer_schema_resource() -> str:
        return (
            "Chinook Customer Table Schema\n\n"
            "Table: Customer\n\n"
            "Fields:\n"
            "- CustomerId: INTEGER, primary key\n"
            "- FirstName: NVARCHAR(40), customer first name\n"
            "- LastName: NVARCHAR(20), customer last name\n"
            "- Company: NVARCHAR(80), company name (optional)\n"
            "- Address: NVARCHAR(70), street address (optional)\n"
            "- City: NVARCHAR(40), city (optional)\n"
            "- State: NVARCHAR(40), state or region (optional)\n"
            "- Country: NVARCHAR(40), country (optional)\n"
            "- PostalCode: NVARCHAR(10), postal code (optional)\n"
            "- Phone: NVARCHAR(24), phone number (optional)\n"
            "- Fax: NVARCHAR(24), fax number (optional)\n"
            "- Email: NVARCHAR(60), customer email address\n"
            "- SupportRepId: INTEGER, foreign key referencing Employee.EmployeeId\n\n"
            "Relationships:\n"
            "- Customer.CustomerId references Invoice.CustomerId.\n"
            "- Customer.SupportRepId references Employee.EmployeeId."
        )

    @mcp.resource(
        uri="chinook://customers/usage",
        name="customer_usage_guidelines",
        title="Customer Usage Guidelines",
        description=(
            "Provides guidance for querying customer records and related "
            "purchase information in the Chinook database."
        ),
        mime_type="text/plain",
    )
    def customer_usage_resource() -> str:
        return (
            "Customer Query Guidelines\n\n"
            "1. Use get_customer_by_id to retrieve a customer by CustomerId.\n"
            "2. Use get_customer_by_email to retrieve a customer by email.\n"
            "3. Use search_customers_by_keyword to find customers by a keyword.\n"
            "4. Use get_customers_count to retrieve the total customer count.\n"
            "5. Use list_albums for album listings; customers and albums are "
            "different entities.\n"
            "6. Use the Invoice table to retrieve customer purchase history.\n"
            "7. Use parameterized SQL queries for database access.\n"
            "8. Do not expose unnecessary customer contact information.\n"
            "9. A customer may have no invoices, so use LEFT JOIN or NOT EXISTS "
            "when querying customers without purchases."
        )

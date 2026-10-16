# Chinook MCP Server

A Python-based Model Context Protocol (MCP) server for querying the Chinook sample database using read-only tools.

## Overview

This project exposes the Chinook SQLite database through MCP-compatible clients using the official Python MCP SDK. It is designed for local development and secure HTTP deployments, with structured validation, logging, and read-only database access.

## Features

- Album lookup, listing, search, and counts
- Artist listing, search, and discography details
- Track search, track details, genres, and longest tracks
- Customer lookup by email or ID, keyword search, and counts
- Invoice details, customer invoices, and purchase history
- Employee directory, reporting structure, and sales summaries
- Sales analytics: revenue totals, monthly trends, country rankings, best sellers, top artists and customers, customer lifetime value
- Database health and server metadata tools
- MCP resources and reusable prompts for albums and customers
- Read-only access with Pydantic-validated structured output
- Support for both stdio and streamable HTTP transports

## Tech Stack

- Python 3.11+
- uv
- SQLAlchemy 2.x (async, with aiosqlite)
- Pydantic 2.x
- Official Python MCP SDK
- SQLite

## Prerequisites

- Python 3.11+
- uv installed
- Access to the included database in `data/chinook.db`

## Installation

```bash
git clone https://github.com/vignesd/mcp-chinook.git
cd mcp-chinook
uv sync
cp .env.example .env
```

## Configuration

Edit `.env` as needed:

```env
APP_NAME=chinook-mcp-server
APP_VERSION=0.1.0
APP_ENV=development
DATABASE_PATH=data/chinook.db
SQLALCHEMY_ECHO=false
LOG_LEVEL=INFO
LOG_TO_FILE=false
LOG_FILE=logs/chinook-mcp-server.log
MCP_TRANSPORT=stdio
MCP_PATH=/mcp
MCP_PORT=8000
MCP_API_KEY=replace-with-a-long-random-secret
MCP_ALLOWED_HOSTS=localhost,127.0.0.1
MCP_ALLOWED_ORIGINS=http://localhost:3000

# Used only by client.py
MCP_SERVER_URL=https://your-host.example.com/mcp
```

In streamable HTTP mode, `MCP_API_KEY` must be at least 32 characters and `MCP_ALLOWED_HOSTS` must be set, or the server refuses to start. `PORT` (set by hosts such as Render) takes precedence over `MCP_PORT`.

## Run the server

Run all commands from the project root.

### Local stdio mode

```bash
uv run python server.py
```

### Streamable HTTP mode

```bash
MCP_TRANSPORT=streamable-http uv run python server.py
```

The MCP endpoint is served at `MCP_PATH` (default `/mcp`) and requires an `Authorization: Bearer <MCP_API_KEY>` header. `GET /health` is public and returns `{"status":"ok"}`.

### MCP Inspector

```bash
uv run mcp dev server.py
```

### Connect to a hosted server

`client.py` connects to a deployed HTTP server using `MCP_SERVER_URL` (HTTPS only) and `MCP_API_KEY`. It lists the available tools and calls `health_check`:

```bash
uv run python client.py
```

## Tools

All tools are read-only and return structured output.

| Area | Tool | Description |
| --- | --- | --- |
| Server | `health_check` | Check database connectivity |
| | `server_info` | Server name, version, and database information |
| Albums | `get_album` | Album by `album_id` |
| | `list_albums` | Paginated album list (`limit`, `offset`) |
| | `search_albums` | Albums by partial title |
| | `get_total_albums` | Total album count |
| Artists | `list_artists` | Paginated artist list with album counts |
| | `search_artists` | Artists by partial name |
| | `get_artist_details` | Artist with all albums and track counts |
| Tracks | `search_tracks` | Paginated tracks by partial name or composer |
| | `get_track_details` | Track with album, artist, genre, media type, and units sold |
| | `list_genres` | All genres with track counts |
| | `get_tracks_by_genre` | Paginated tracks in a genre |
| | `get_longest_tracks` | Longest tracks by duration |
| Customers | `get_customer_by_email` | Customer by email address |
| | `get_customer_by_id` | Customer by `customer_id` |
| | `search_customers_by_keyword` | Customers by name, company, or country |
| | `get_customers_count` | Total customer count |
| Invoices | `get_customer_invoices` | All invoices for a customer |
| | `get_customer_purchase_tracks` | Tracks purchased by a customer |
| | `get_invoice_details` | Invoice header with line items (track, album, artist) |
| Employees | `list_employees` | All employees with title and manager |
| | `get_employee_details` | Employee with manager, direct reports, and customer count |
| | `get_employee_sales_summary` | Sales totals for the customers an employee supports |
| Sales analytics | `get_total_revenue` | Revenue totals, optionally for a date range (`YYYY-MM-DD`) |
| | `get_sales_by_month` | Monthly invoice counts and revenue for a year |
| | `get_revenue_by_country` | Billing countries ranked by revenue |
| | `get_best_selling_tracks` | Tracks ranked by units sold |
| | `get_top_artists_by_revenue` | Artists ranked by revenue |
| | `get_top_customers` | Customers ranked by total spend |
| | `get_customer_lifetime_value` | One customer's total spend, order count, and purchase dates |

Employee sales are attributed through the customer's assigned support representative (`Customer.SupportRepId`), because Chinook invoices do not record a salesperson.

Errors are returned as MCP tool errors prefixed with a code (`INVALID_ARGUMENT`, `NOT_FOUND`, `DATABASE_ERROR`, `INTERNAL_ERROR`) and a hint telling the client whether to retry.

## Resources and Prompts

| Type | Name |
| --- | --- |
| Resource | `chinook://albums`, `chinook://albums/{album_id}`, `chinook://albums/statistics` |
| Resource | `chinook://customers/schema`, `chinook://customers/usage` |
| Prompt | Album prompts: `list_albums`, `get_album`, `search_albums`, `get_total_albums`, `album_search_and_details`, `album_catalogue_summary` |
| Prompt | Customer prompts: `get_customer_by_email`, `get_customer_by_id`, `get_customers_count`, `search_customers_by_keyword` |

## Project Structure

```text
server.py      MCP server: registers all tools, resources, and prompts; selects transport
client.py      Example client for a hosted HTTP server
core/          Settings, database engine, logging, tool annotations
services/      SQL queries against the Chinook database
tools/         MCP tool functions (validation and error handling)
models/        Pydantic input and output models
resources/     MCP resources
prompts/       MCP prompts
data/          chinook.db
docs/          Requirements and database schema notes
```

To add a tool, write the query in `services/`, the output model in `models/`, and the tool function in `tools/`, then register it with `mcp.add_tool(...)` in `server.py`. Tools that are not registered there are not exposed.

## Security Notes

- Only read-only tools are exposed; no write operations exist in the current implementation
- HTTP access requires a bearer API key, compared in constant time
- Host and origin allowlists should be configured before external exposure
- Logs are written to stderr so they never interfere with the stdio transport

## Testing

There is no pytest suite yet. To check the server locally:

```bash
uv run python -m core.check_db        # verify the database connection
uv run mcp dev server.py              # exercise tools in MCP Inspector
```

`tests/inspect_tools.py` drives the server through an in-memory MCP client, but its expected tool list is out of date.

## Troubleshooting

- Verify `data/chinook.db` exists and is readable
- Ensure `.env` values are correctly set
- Run commands from the project root so imports such as `core.config` resolve
- Reinstall dependencies if needed:

```bash
uv sync --reinstall
```

## License

This project currently does not declare a license. Add a license before public distribution if required.

## Project Status

Production-oriented MCP server prototype for learning and experimentation with MCP, SQLAlchemy, and SQLite-backed tooling.

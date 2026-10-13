# Chinook MCP Server

A Python-based Model Context Protocol (MCP) server for the Chinook sample database. The project exposes a small set of read-only database tools for querying music catalog and customer billing data through MCP-compatible clients such as Claude Desktop, Cursor, or custom Python-based MCP clients.

## Overview

This project demonstrates how to build a production-oriented MCP server using the official Python MCP SDK with:

- Python 3.11+
- SQLAlchemy 2.x
- Pydantic 2.x
- SQLite database access
- Stdio transport and Streamable HTTP transport
- Read-only query patterns and structured error handling

The server is designed around the Chinook sample database, which models a digital music store with albums, customers, invoices, and purchased tracks.

## Why this project

The repository provides a practical example of:

- registering MCP tools, resources, and prompts
- validating inputs and outputs with Pydantic
- abstracting database access behind service functions
- exposing a safe read-only interface to a SQLite database
- running the same business logic across local and HTTP transports

## Features

### Current implementation

The server currently includes read-only tools for the following capabilities:

- Database health checks
- Server metadata discovery
- Album lookup, listing, searching, and counting
- Customer lookup by email or ID, keyword search, and counting
- Customer invoice retrieval
- Customer purchase-history retrieval

### Supported transports

- Stdio for local MCP clients
- Streamable HTTP for deployment and remote access scenarios

### Security model

- Database access is read-only
- Inputs are validated with Pydantic
- HTTP endpoint requires a bearer API key
- Health endpoint is intentionally lightweight and public
- Unsafe or invalid requests return structured errors instead of leaking stack traces

## Repository structure

```text
mcp-chinook/
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── helper.py
│   ├── logging.py
│   ├── tool_annotations.py
│   └── verify.py
├── data/
│   └── chinook.db
├── docs/
│   ├── Requirement.md
│   ├── Tables.txt
│   └── notes.txt
├── models/
│   ├── album_models.py
│   ├── customer_models.py
│   ├── invoice_models.py
│   └── server_model.py
├── prompts/
│   ├── album_prompts.py
│   └── customer_prompts.py
├── resources/
│   ├── album_resources.py
│   └── customer_resource.py
├── services/
│   ├── Invoice_services.py
│   ├── album_services.py
│   └── customer_services.py
├── tests/
│   ├── __init__.py
│   ├── inspect_tools.py
│   └── test_exception.py
├── tools/
│   ├── album_tools.py
│   ├── customer_tools.py
│   └── invoice_tools.py
├── .env.example
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
├── server.py
├── uv.lock
└── ...
```

## Prerequisites

- Python 3.11+
- uv package manager
- Access to the included SQLite database in `data/chinook.db`

## Installation

1. Clone the repository.
2. Install dependencies using uv:

```bash
uv sync
```

3. Copy the example environment file and adjust it if needed:

```bash
cp .env.example .env
```

## Configuration

The project loads settings from `.env` using `pydantic-settings`.

Example configuration:

```dotenv
APP_NAME=chinook-mcp-server
APP_VERSION=0.1.0
APP_ENV=development
DATABASE_PATH=data/chinook.db
LOG_LEVEL=INFO
MCP_TRANSPORT=stdio
MCP_PATH=/mcp
MCP_PORT=8000
MCP_API_KEY=replace-with-a-long-random-secret
MCP_ALLOWED_HOSTS=localhost,127.0.0.1
MCP_ALLOWED_ORIGINS=http://localhost:3000
```

Important notes:

- `MCP_TRANSPORT` can be set to `stdio` or `streamable-http`
- `MCP_API_KEY` is required for HTTP mode
- In production, configure host and origin allowlists carefully

## Running the server

### Local stdio mode

```bash
uv run python server.py
```

This starts the MCP server using standard input/output, which is suitable for local MCP clients.

### Streamable HTTP mode

```bash
MCP_TRANSPORT=streamable-http uv run python server.py
```

HTTP mode exposes the server over a configured port and path, protected by the bearer token defined in `MCP_API_KEY`.

## Available MCP tools

This project registers the following tool groups.

### Album tools

- `health_check`
- `server_info`
- `get_album`
- `list_albums`
- `search_albums`
- `get_total_albums`

### Customer tools

- `get_customer_by_email`
- `get_customer_by_id`
- `get_customers_count`
- `search_customers_by_keyword`

### Invoice tools

- `get_customer_invoices`
- `get_customer_purchase_tracks`

## Example usage

### Querying an album by ID

```python
await get_album(1)
```

### Listing albums with pagination

```python
await list_albums(limit=10, offset=0)
```

### Searching customers by keyword

```python
await search_customers_by_keyword("Luis")
```

### Getting customer invoices

```python
await get_customer_invoices(6)
```

## Development

### Run the app in development mode

```bash
uv run python server.py
```

### Run Python scripts directly

```bash
uv run python main.py
```

## Testing

The repository includes a few lightweight test files and validation scripts.

Run tests with:

```bash
uv run pytest
```

If you want to inspect available tool metadata or validate behavior manually, check the scripts under `tests/`.

## Data model

The project is based on the Chinook database, which includes tables such as:

- Albums
- Artists
- Customers
- Employees
- Invoices
- InvoiceLines
- Tracks
- Genres

The server intentionally exposes read-only queries and does not implement write operations.

## Security and operational notes

This project is intended for educational and local development use, with deliberate safeguards:

- no write capabilities are exposed
- HTTP requests require a bearer token
- host and origin allowlists should be configured before external exposure
- database access is constrained to read-only retrieval patterns

## Troubleshooting

### Database connection fails

Verify that the path in `.env` points to a valid SQLite database:

```bash
ls -l data/chinook.db
```

### HTTP server not starting

Confirm these are set:

```bash
MCP_TRANSPORT=streamable-http
MCP_API_KEY=<strong-secret>
MCP_ALLOWED_HOSTS=localhost,127.0.0.1
MCP_PATH=/mcp
MCP_PORT=8000
```

### Dependency issues

Reinstall project dependencies:

```bash
uv sync --reinstall
```

## License

This repository does not currently declare a license in `pyproject.toml`. If you plan to distribute or publish the project, add an appropriate license file and update the project metadata before release.

## Contributing

Contributions are welcome. For substantial changes, please:

1. open an issue describing the improvement or bug
2. create a branch with a focused change
3. validate the affected behavior with tests or targeted checks
4. open a pull request with a clear summary

## Project status

This project is a working MCP server prototype focused on safe, read-only access to the Chinook sample database. It is well suited for learning MCP architecture, SQLAlchemy querying, and structured tool design in Python.


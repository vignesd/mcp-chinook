# Chinook MCP Server

A Python-based Model Context Protocol (MCP) server for querying the Chinook sample database using read-only tools.

## Overview

This project exposes the Chinook SQLite database through MCP-compatible clients using the official Python MCP SDK. It is designed for local development and secure HTTP deployments, with structured validation, logging, and read-only database access.

## Features

- Album lookup, listing, and search
- Customer lookup by email or ID
- Customer search by keyword
- Invoice and purchase-history retrieval
- Database health and server metadata tools
- Read-only access with Pydantic validation
- Support for both stdio and streamable HTTP transports

## Tech Stack

- Python 3.11+
- uv
- SQLAlchemy 2.x
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
LOG_LEVEL=INFO
MCP_TRANSPORT=stdio
MCP_PATH=/mcp
MCP_PORT=8000
MCP_API_KEY=replace-with-a-long-random-secret
MCP_ALLOWED_HOSTS=localhost,127.0.0.1
MCP_ALLOWED_ORIGINS=http://localhost:3000
```

## Run the server

### Local stdio mode

```bash
uv run python server.py
```

### Streamable HTTP mode

```bash
MCP_TRANSPORT=streamable-http uv run python server.py
```

## Example tool usage

- `health_check`
- `server_info`
- `get_album`
- `list_albums`
- `search_albums`
- `get_customer_by_email`
- `get_customer_by_id`
- `search_customers_by_keyword`
- `get_customer_invoices`
- `get_customer_purchase_tracks`

## Security Notes

- Database access is read-only
- HTTP access requires a bearer API key
- Host and origin allowlists should be configured before external exposure
- No write operations are exposed in the initial implementation

## Testing

```bash
uv run pytest
```

## Troubleshooting

- Verify `data/chinook.db` exists and is readable
- Ensure `.env` values are correctly set
- Reinstall dependencies if needed:

```bash
uv sync --reinstall
```

## License

This project currently does not declare a license. Add a license before public distribution if required.

## Project Status

Production-oriented MCP server prototype for learning and experimentation with MCP, SQLAlchemy, and SQLite-backed tooling.

# Chinook Database MCP Server — Final Requirements Specification

## Chinook MCP Server

SRS v1.0 · Finalized requirements

Approved configuration

Language

Python 3.11+

IDE / package manager

VS Code / uv

MCP framework

Official Python MCP SDK

Database layer

SQLAlchemy 2.x

Transports

Stdio → Streamable HTTP

Initial operations

Read-only

The requirements are now finalized with your selected technology choices. No project files or implementation code have been created.

## 1. Project objectives and scope

Build an educational, production-oriented MCP server that exposes the existing `chinook.db` music-store database to MCP-compatible clients.

The project will teach you to:

- Develop an MCP server using the official Python SDK.

- Register and validate tools using Pydantic.

- Access SQLite through SQLAlchemy 2.x.

- Implement joins, filtering, pagination, and business analytics.

- Support Stdio first and Streamable HTTP second.

- Implement MCP resources and reusable prompts.

- Test the server using pytest and MCP Inspector.

- Apply structured error handling, logging, and read-only security controls.

The initial version will not include an AI agent, RAG, vector database, dashboard, write operations, or mandatory cloud deployment.

## 2. Final technology stack

| Component          | Final requirement                                  |
| ------------------ | -------------------------------------------------- |
| Python             | 3.11 or newer                                      |
| IDE                | Visual Studio Code                                 |
| Package management | `uv`                                               |
| MCP framework      | Official Python MCP SDK                            |
| Database           | Existing SQLite `chinook.db`                       |
| ORM / query layer  | SQLAlchemy 2.x                                     |
| Validation         | Pydantic 2.x                                       |
| Configuration      | Environment variables; `.env` support where useful |
| Logging            | Python standard `logging`                          |
| Testing            | pytest, with pytest-asyncio if required            |
| MCP client testing | MCP Inspector                                      |
| Transports         | Stdio and Streamable HTTP                          |
| Version control    | Git                                                |

Dependencies must be declared in `pyproject.toml`, with a committed `uv.lock` for reproducible installations. The exact SDK version and API signatures will be verified during implementation rather than assumed.

## 3. Architecture

MCP clients

MCP Inspector and compatible applications

Stdio

Phase 1

Streamable HTTP

Phase 6

Official Python MCP SDK

Tool registration · Resources · Prompts · Transport handling

Pydantic validation → Service layer

Validated inputs · Business logic · Structured outputs

SQLAlchemy 2.x → SQLite

Read-only connection to the existing Chinook database

### Architecture requirements

- MCP transport handlers must remain separate from business logic.

- MCP tools must delegate database operations to service functions.

- SQLAlchemy 2.x must handle query construction and database access.

- Pydantic must validate tool inputs and define structured output contracts where appropriate.

- The database connection must use SQLite read-only mode.

- The application must fail clearly if the configured database file is missing.

- The server must not create, update, or delete records in the initial version.

- The same tools and business capabilities must work through both transports.

## 4. Final tool catalogue

The initial implementation contains 32 read-only tools, divided into four functional groups.

### A. Foundation — 5 tools

| Tool                  | Responsibility                                    |
| --------------------- | ------------------------------------------------- |
| `health_check`        | Verify server operation and database connectivity |
| `server_info`         | Return server metadata and capabilities           |
| `list_tables`         | List database tables                              |
| `get_table_schema`    | Inspect columns, types, and key information       |
| `get_table_row_count` | Count records in an approved table                |

### B. Music catalogue — 10 tools

1. `search_artists`

2. `get_artist_details`

3. `list_albums`

4. `get_album_details`

5. `search_tracks`

6. `get_track_details`

7. `list_genres`

8. `get_tracks_by_genre`

9. `get_top_tracks_by_price`

10. `get_longest_tracks`

### C. Customers and employees — 7 tools

1. `search_customers`

2. `get_customer_details`

3. `list_customers_by_country`

4. `get_customer_invoices`

5. `get_customer_purchase_history`

6. `get_employee_details`

7. `get_employee_sales_summary`

### D. Invoices and sales analytics — 10 tools

1. `get_invoice_details`

2. `list_invoices`

3. `get_total_revenue`

4. `get_revenue_by_country`

5. `get_top_customers`

6. `get_best_selling_tracks`

7. `get_top_artists_by_revenue`

8. `get_sales_by_month`

9. `get_average_invoice_value`

10. `get_customer_lifetime_value`

All tools must have documented arguments, validation rules, return structures, and failure behavior. Search and list tools must apply sensible limits and support pagination wherever applicable.

## 5. Additional MCP capabilities

Beyond the 32 tools, the server should expose three resources and three prompts.

| Type     | Name                           | Purpose                              |
| -------- | ------------------------------ | ------------------------------------ |
| Resource | `chinook://database/schema`    | Database schema overview             |
| Resource | `chinook://catalog/genres`     | Available music genres               |
| Resource | `chinook://catalog/top-tracks` | Read-only track catalogue summary    |
| Prompt   | `music_research`               | Support music catalogue research     |
| Prompt   | `customer_sales_analysis`      | Guide sales analysis                 |
| Prompt   | `music_recommendation`         | Guide evidence-based recommendations |

The resource URIs and prompt names must be discoverable through the official SDK. Resources must not expose unrestricted database access, and prompts must not imply that database results are available unless the client retrieves them.

## 6. Final project structure requirements

The intended structure is deliberately small and easy to navigate in VS Code.

```
chinook-mcp-server/
├── data/
│   └── chinook.db
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── schemas.py
│   ├── services.py
│   ├── tools.py
│   ├── resources.py
│   ├── prompts.py
│   └── server.py
├── tests/
│   ├── conftest.py
│   ├── test_tools.py
│   └── test_services.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

`data/chinook.db` represents the supplied database location, not a file that should be generated or replaced. The actual file location will be confirmed during database inspection.

Responsibilities:

- `config.py`: settings and database path.

- `database.py`: SQLAlchemy engine, sessions, and read-only connection.

- `schemas.py`: Pydantic input/output models.

- `services.py`: query logic and business rules.

- `tools.py`: MCP tool registrations.

- `resources.py`: MCP resource registrations.

- `prompts.py`: MCP prompt templates.

- `server.py`: server initialization and transport startup.

- `tests/`: unit and integration tests.

## 7. Phase-wise implementation roadmap

## 0

Requirements and database verification

Inspect the actual database, tables, columns, relationships, indexes, and record counts. Finalize the tool contracts against the verified schema.

Deliverable: verified schema inventory and implementation checklist.

## 1

Project setup and foundation tools

Configure uv, dependencies, settings, logging, SQLAlchemy read-only access, and the five foundation tools. Start with Stdio.

Deliverable: working server and five tested tools.

## 2

Catalogue tools

Implement artist, album, track, and genre retrieval, including filters, sorting, joins, and pagination.

Deliverable: ten tested catalogue tools.

## 3

Customer and employee tools

Implement customer profiles, purchase history, invoice retrieval, employee information, and employee sales summaries.

Deliverable: seven tested tools.

## 4

Sales analytics

Implement revenue calculations, monthly sales, customer rankings, track rankings, and artist-level analytics. Validate calculations against independent SQL results.

Deliverable: ten tested analytics tools.

## 5

Resources and prompts

Add the three resources and three reusable prompts. Verify discovery and retrieval using an MCP client.

Deliverable: discoverable resources and prompts with tests.

## 6

Streamable HTTP transport

Add HTTP startup configuration and validate initialization, discovery, calls, and session behavior where applicable.

Deliverable: the same server capabilities over HTTP and Stdio.

## 7

Quality assurance and documentation

Run the full test suite, verify read-only enforcement, check errors and logs, and document setup, commands, tool contracts, and troubleshooting.

Deliverable: reproducible, documented, tested project.

## 8. Testing strategy — separate database copy

This is a mandatory design requirement.

- Keep the original `chinook.db` unchanged.

- Create a separate temporary copy for integration tests that require a file-backed database.

- Point the test SQLAlchemy engine exclusively at that copy.

- Dispose of the test engine and clean up temporary files after testing.

- Never silently fall back to the original database if the test database is missing.

- Use controlled test data or isolated fixtures for cases that require known results.

- Verify that the test database's contents are restored or recreated consistently between runs.

Unit tests should cover service logic and validation; integration tests should verify real SQLAlchemy queries, joins, constraints, and database behavior.

The production connection and test connection must be configured independently.

## 9. Read-only and security requirements

The application must use a read-only SQLite connection, with the actual database opened using SQLite's read-only URI mode or an equivalent verified configuration.

Additional controls:

- No arbitrary SQL execution tool.

- No write tools in the initial version.

- Parameterized queries or SQLAlchemy expressions for user-supplied filters.

- Allowlisted metadata access for table inspection.

- Bounded list results and pagination.

- Safe, consistent error responses.

- No secrets or unnecessary personal information in logs.

- Localhost binding for local HTTP development by default.

- Explicit security review before exposing HTTP access remotely.

Read-only behavior must be tested, not merely assumed.

## 10. Final acceptance criteria

The project will be considered complete when all of the following are satisfied:

- The project installs reproducibly through uv.

- The existing database is verified and is never silently replaced by an empty database.

- All 32 specified tools are implemented and documented.

- All three resources and three prompts are implemented and discoverable.

- Stdio works with MCP Inspector.

- Streamable HTTP works with MCP Inspector or another compatible MCP client.

- Both transports expose the same business capabilities.

- Pydantic validates tool arguments and output contracts are documented.

- SQLAlchemy queries are tested for correctness.

- Analytics are verified against independent SQL calculations.

- Integration tests use a separate temporary copy of the database.

- Tests cover invalid inputs, missing records, empty results, and database errors.

- Read-only enforcement is verified.

- Logging and error handling are consistent.

- The README explains installation, configuration, startup, testing, and troubleshooting.

## 11. Explicitly deferred features

The following are outside version 1.0 and must not be added without a scope change:

- LLM-powered agents and LangGraph workflows.

- RAG and vector databases.

- Database write operations.

- Playlist creation and modification.

- Cloud deployment as a mandatory requirement.

- User interfaces and dashboards.

- Authentication and multi-tenant access controls beyond the requirements needed for local operation and safe HTTP exposure.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A read-only MCP server built on the official Python MCP SDK (`mcp>=2.3`, which uses the `MCPServer` class rather than `FastMCP`). It exposes the bundled Chinook SQLite database (`data/chinook.db`) through async SQLAlchemy + aiosqlite. The original requirements are in `docs/Requirement.md`. The table DDL is in `docs/notes.txt` / `docs/Tables.txt`. You can also print the schema with `uv run python core/helper.py`.

## Commands

Uses `uv` and Python 3.11. Run everything from the repo root: modules import each other as top-level packages (`core.`, `services.`, ...), and the project isn't installed as a package.

```bash
uv sync                                   # install deps
cp .env.example .env                      # config (read by core/config.py via pydantic-settings)
uv run python server.py                   # run over stdio (default)
MCP_TRANSPORT=streamable-http uv run python server.py   # HTTP; needs MCP_API_KEY (>=32 chars) and MCP_ALLOWED_HOSTS
uv run mcp dev server.py                  # MCP Inspector (from mcp[cli])
uv run python -m core.check_db            # DB connectivity check
uv run python -m tests.inspect_tools      # in-memory client: list tools and call them
uv run python client.py                   # call a hosted HTTP server (needs MCP_SERVER_URL=https://... and MCP_API_KEY in .env)
```

Testing: the README says `uv run pytest`, but pytest isn't a declared dependency and `tests/` has no real pytest tests yet. `tests/inspect_tools.py` is a script that drives `server.mcp` through `mcp.client.Client`. Its `EXPECTED_TOOLS` set is out of date. To run one pytest test once some exist: `uv run --with pytest pytest tests/test_x.py::test_name`.

No linter or formatter is configured.

## Architecture

Each request passes through these layers, one module per domain (album / customer / invoice):

1. **`server.py`** is the single composition root. It creates the `MCPServer`, calls `register_*_prompts(mcp)` and `register_*_resources(mcp)`, and registers **every tool explicitly** with `mcp.add_tool(fn, name=..., title=..., description=..., annotations=READ, structured_output=True)`. The tool's public name and LLM-facing description are set here, not in the function, and the name can differ from the function name (e.g. `get_albums_count` is exposed as `get_total_albums`). A new tool must be added here or it won't be exposed.
2. **`tools/*_tools.py`** hold the async tool functions. They validate input, call services, and return Pydantic output models. Errors are raised as `ToolError` (from `mcp.server.mcpserver.exceptions`) with a `CODE: message` prefix (`INVALID_ARGUMENT`, `NOT_FOUND`, `DATABASE_ERROR`). The message also tells the LLM whether to retry. Use `from None` to hide internal tracebacks. `SQLAlchemyError` is logged with `logger.exception` before it's rewrapped.
3. **`services/*_services.py`** run raw parameterised SQL (`sqlalchemy.text`) and return `dict` / `list[dict]`, or `None` for not-found. Two conventions are in use: `album_services` takes `engine` as its first argument, while the customer and invoice services import the shared `engine` from `core.database` themselves.
4. **`models/*_models.py`** are Pydantic v2 input/output models, mostly with `extra="forbid"`. Output models become the tools' structured-output schema. `server_model.py` holds the health/server_info models.
5. **`resources/`** and **`prompts/`** expose `register_*(mcp)` functions that use the `@mcp.resource(uri="chinook://...")` and `@mcp.prompt` decorators inside them.

Shared infrastructure in `core/`:
- `config.py`: the `settings` singleton. `DATABASE_PATH` is resolved relative to the project root, and the async URL is `sqlite+aiosqlite:///...`.
- `database.py`: a module-level `engine`, created **at import time**. Importing it raises `FileNotFoundError` if the DB file is missing.
- `logging.py`: configures root logging to **stderr** on import (stdout is reserved for the stdio MCP transport, so never `print` in server code). Use `from core.logging import logger`.
- `tool_annotations.py`: preset `ToolAnnotations` (`READ`, `CREATE`, `DELETE`, ...). Every current tool uses `READ`.

HTTP mode (`_run_streamable_http` in `server.py`) reads `MCP_API_KEY`, `PORT`/`MCP_PORT`, `MCP_PATH`, `MCP_ALLOWED_HOSTS` and `MCP_ALLOWED_ORIGINS` straight from `os.getenv`, not from `settings`. It wraps the Streamable HTTP app in `ApiKeyMiddleware`, which checks the Bearer token with `hmac.compare_digest` and leaves `GET /health` public for Render.

## Notes

- The server is read-only by design. Don't add write tools unless asked.
- `main.py` and `core/OLD_server.py` are scratch/legacy files and aren't used by the server.
- `services.album_services.list_albums` now returns a pagination dict, but `resources/album_resources.py` still treats the result as a list (`len(albums)`), and `server_info` hardcodes an outdated tool list.

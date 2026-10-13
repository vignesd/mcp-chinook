
from __future__ import annotations

import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

load_dotenv()


def load_config() -> tuple[str, str]:
    """Load and validate MCP server configuration."""

    server_url = os.getenv("MCP_SERVER_URL", "").strip()
    api_key = os.getenv("MCP_API_KEY", "").strip()

    if not server_url:
        raise ValueError("MCP_SERVER_URL is missing from .env")

    if not api_key:
        raise ValueError("MCP_API_KEY is missing from .env")

    if not server_url.startswith("https://"):
        raise ValueError("MCP_SERVER_URL must use HTTPS")

    return server_url, api_key


async def main() -> None:
    """Connect to the hosted MCP server using Bearer authentication."""

    server_url, api_key = load_config()

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    print(f"Connecting to MCP server: {server_url}")

    try:
        async with httpx.AsyncClient(
            headers=headers,
            timeout=30.0,
        ) as http_client:

            async with streamable_http_client(
                server_url,
                http_client=http_client,  # type:ignore
            ) as (read_stream, write_stream):

                async with ClientSession(
                    read_stream,
                    write_stream,
                ) as session:

                    # Initialize the MCP session.
                    await session.initialize()
                    print("\nConnected successfully.")

                    # Discover available tools.
                    tools_result = await session.list_tools()

                    print("\nAvailable tools:")
                    for tool in tools_result.tools:
                        print(f"- {tool.name}: {tool.description}")

                    tool_names = {
                        tool.name for tool in tools_result.tools
                    }

                    # Test the health-check tool.
                    if "health_check" in tool_names:
                        print("\nCalling health_check...")

                        result = await session.call_tool(
                            "health_check",
                            {},
                        )

                        if result.is_error:
                            print("health_check returned an error.")
                        else:
                            for content in result.content:
                                if hasattr(content, "text"):
                                    print(content.text)  # type:ignore

                            if result.structured_content is not None:
                                print(result.structured_content)
                    else:
                        print(
                            "\nThe server does not expose health_check."
                        )

    except Exception as exc:
        print(
            f"\nMCP client error: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        raise


if __name__ == "__main__":
    asyncio.run(main())


"""Inspect tool definitions and test MCP tool responses."""

import asyncio
import json

from mcp.client import Client

from core.database import close_database
from server import mcp


EXPECTED_TOOLS = {
    "health_check",
    "server_info",
    "get_album",
    "list_albums",
    "search_albums",
    "sample"
}


async def main() -> None:
    try:
        async with Client(mcp) as client:
            # 1. Discover tools exactly as an MCP client does.
            response = await client.list_tools()
            tools = response.tools

            print("\n=== TOOL DEFINITIONS ===")

            received_names = {tool.name for tool in tools}
            assert received_names == EXPECTED_TOOLS, (
                f"Unexpected tools. Received: {received_names}"
            )

            for tool in tools:

                print(f"\nName: {tool.name}")
                print(f"Description: {tool.description}")

                print("Input schema:")
                print(json.dumps(tool.input_schema, indent=2))

                print("Output schema:")
                print(
                    json.dumps(
                        getattr(tool, "output_schema", None),
                        indent=2,
                    )
                )

            # 2. Call representative tools.
            test_calls = [
                ("health_check", {}),
                ("server_info", {}),
                ("get_album", {"album_id": 1}),
                ("list_albums", {}),
                ("search_albums", {"title": "rock"}),
            ]

            print("\n=== TOOL CALL RESULTS ===")

            for name, arguments in test_calls:
                result = await client.call_tool(name, arguments)

                print(f"\nTool: {name}")
                print(f"Arguments: {arguments}")
                print(f"Is error: {result.is_error}")

                print("Text content:")
                for block in result.content:
                    if hasattr(block, "text"):
                        print(block.text)  # type:ignore

                print("Structured content:")
                print(
                    json.dumps(
                        result.structured_content,
                        indent=2,
                        default=str,
                    )
                )

                assert not result.is_error, (
                    f"{name} returned an MCP tool error"
                )

            print("\nAll tool discovery and smoke tests passed.")

    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())

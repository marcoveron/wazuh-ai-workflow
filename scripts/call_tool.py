"""Dev helper: launch the MCP server over stdio, list its tools and optionally call one.

Usage:
    uv run scripts/call_tool.py                              # list tools
    uv run scripts/call_tool.py get_manager_info             # call a tool
    uv run scripts/call_tool.py list_agents '{"status": "active"}'
"""

import json
import sys

import anyio
from mcp.client import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main(tool: str | None, arguments: dict) -> None:
    server = StdioServerParameters(command="uv", args=["run", "wazuh-mcp"])
    async with stdio_client(server) as (read, write), ClientSession(read, write) as session:
        await session.initialize()

        if tool is None:
            for t in (await session.list_tools()).tools:
                print(f"- {t.name}: {t.description}")
                print(f"  args schema: {json.dumps(t.input_schema)}")
            return

        result = await session.call_tool(tool, arguments)
        if result.is_error:
            print("TOOL ERROR:", result.content[0].text)
        else:
            print(json.dumps(result.structured_content, indent=2))


if __name__ == "__main__":
    tool_name = sys.argv[1] if len(sys.argv) > 1 else None
    tool_args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    anyio.run(main, tool_name, tool_args)

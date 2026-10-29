"""MCP server exposing Wazuh as tools.

The server talks MCP over stdio: the client launches this process and exchanges
JSON-RPC messages through stdin/stdout. That means stdout is reserved for the
protocol. Never print() here; use logging, which writes to stderr.
"""

import logging
from typing import Any

from mcp.server.mcpserver import MCPServer

from wazuh_mcp.config import Settings
from wazuh_mcp.wazuh_client import WazuhAPIClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

mcp = MCPServer(
    name="wazuh",
    instructions="Read-only access to a Wazuh SIEM: manager status, agents and security alerts.",
)
wazuh = WazuhAPIClient(Settings())


# The docstring becomes the tool description the LLM reads to decide when to call it,
# and the type hints become the JSON schema of its arguments. Write both for the model.
@mcp.tool()
async def get_manager_info() -> dict[str, Any]:
    """Get information about the Wazuh manager: version, installation path, OS and node type."""
    data = await wazuh.get("/manager/info")
    return data["affected_items"][0]


# TODO(marco): your first tool, list_agents.
#   - Endpoint: GET /agents  (docs: https://documentation.wazuh.com/current/user-manual/api/reference.html#tag/Agents)
#   - Useful query params: status ("active", "disconnected", "never_connected", "pending"),
#     limit, and select (comma-separated fields, e.g. "id,name,ip,status,os.name,version,lastKeepAlive").
#   - Think about which arguments the LLM should be able to pass, and give them sensible defaults.
#   - Return only the fields that matter: every token you send back fills the local model's context.


def main() -> None:
    mcp.run()  # stdio transport by default

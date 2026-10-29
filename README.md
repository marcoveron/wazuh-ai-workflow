# wazuh-ai-workflow

Talk to your [Wazuh](https://wazuh.com) SIEM in natural language using a **local LLM** and the **Model Context Protocol (MCP)**. No data leaves your machine.

> 🚧 Work in progress. Built step by step. See the [roadmap](#roadmap).

## Architecture

```
 You (CLI)
    │  "Which critical alerts fired today on agent web-01?"
    ▼
┌────────────────────┐   question + tool list          ┌──────────────┐
│  Agent / MCP host   │ ──────────────────────────────▶ │ Ollama       │
│  (CLI)              │ ◀────────────────────────────── │ (qwen3:8b)   │
└────────────────────┘   "call get_alerts(level>=12)"  └──────────────┘
    │ executes the tool over MCP (stdio)
    ▼
┌────────────────────┐   HTTPS + JWT          ┌─────────────────────────┐
│  MCP server         │ ─────────────────────▶ │ Wazuh API (:55000)      │
│  wazuh-mcp          │                        │ Wazuh Indexer (:9200)   │
└────────────────────┘                        └─────────────────────────┘
```

- **MCP server**: exposes Wazuh capabilities as typed *tools*. It knows nothing about LLMs, so any MCP client can use it.
- **Agent (CLI)**: runs the tool-calling loop between the local model and the MCP server.
- **Wazuh data sources**: the manager API (agents, rules, status, vulnerabilities) and the indexer, an OpenSearch instance where alerts are stored.
- **Read-only first**: active responses (blocking an IP, restarting an agent) will come later, behind explicit confirmation.

## Local lab

Requirements: Docker with Compose, about 4 GB of free RAM, and `vm.max_map_count >= 262144`.

```bash
./lab/setup.sh
```

This deploys Wazuh 4.14.7 single-node (manager, indexer and dashboard). Admin ports are bound to `127.0.0.1` because the upstream stack ships with default credentials.

| Service   | URL                      |
|-----------|--------------------------|
| Dashboard | https://localhost        |
| API       | https://localhost:55000  |
| Indexer   | https://localhost:9200   |

## MCP server

Requirements: [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env        # then fill in your Wazuh API credentials
uv sync
uv run scripts/call_tool.py                    # list the available tools
uv run scripts/call_tool.py get_manager_info   # call one
```

Or explore it interactively with the [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```bash
npx @modelcontextprotocol/inspector uv run wazuh-mcp
```

### Tools

| Tool               | Source      | Description                                |
|--------------------|-------------|--------------------------------------------|
| `get_manager_info` | Manager API | Manager version, OS and installation info. |

## Roadmap

- [x] Reproducible local Wazuh lab
- [x] MCP server skeleton + Wazuh API client (JWT auth)
- [ ] Read-only tools: agents, alerts, rules
- [ ] CLI agent with Ollama tool calling
- [ ] Tests + CI
- [ ] HTTP API / dashboard

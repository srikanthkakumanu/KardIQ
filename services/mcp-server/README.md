# mcp-server

This service is an **HTTP adapter** that mirrors the shape of an MCP tool
contract (a `GET /tools` discovery endpoint and a `POST /tools/{name}/call`
invocation endpoint) — it does **not** implement the official MCP protocol
(stdio/SSE transport, the official `mcp` Python SDK's wire format, etc.).
It was built this way to keep the whole system reachable over plain HTTP
inside Docker Compose / Kubernetes, consistent with every other KardIQ
service.

The agent talks to it over HTTP via `MCP_SERVER_URL`, exactly like it talks
to any other internal service.

## Tools

| Tool | Calls | Description |
|---|---|---|
| `list_cards` | card-service | List knowledge cards |
| `create_card` | card-service | Create a knowledge card |
| `graph_search` | graph-rag | Keyword + one-hop graph search for relevant context |
| `health_report` | card-service + graph-rag | Aggregate downstream health |

## Endpoints

- `GET /health`
- `GET /tools` — lists every registered tool with its JSON input/output schema
- `POST /tools/{tool_name}/call` — validates arguments against the tool's
  input schema, executes it, and always returns HTTP 200 with
  `{tool, success, result|error, downstream, requestId}` (a genuinely
  unknown tool name returns HTTP 404 instead, since that is a routing
  error rather than a tool-execution failure).

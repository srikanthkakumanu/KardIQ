# CLAUDE.md

## Component Ownership

This directory contains the MCP server. It is the tool boundary between the AI agent and the rest of the system.

## Required Stack

- Python 3.12+.
- `uv` for dependency management and running scripts (`uv sync`, `uv run`).
- FastAPI or the official MCP Python SDK when practical.
- Pydantic models for tool schemas.
- `httpx` for downstream service calls.
- `pytest` for tests.

## Responsibilities

- Expose tools the agent can discover and call.
- Validate tool arguments.
- Call the card service and graph RAG service through typed clients.
- Normalize downstream errors into tool errors.
- Return tool results in a shape useful for the agent.

## Required Tools

Implement these tools:

- `list_cards`: list cards from the card service.
- `create_card`: create a card through the card service.
- `graph_search`: search graph context through the graph RAG service.
- `health_report`: report downstream health status.

Add internet/search tools only if the system needs them. If added, isolate provider code and make network/API keys configurable.

## Boundary Rules

- The MCP server may call the card service and graph RAG service.
- The MCP server must not directly connect to PostgreSQL.
- The MCP server must not directly connect to Neo4j.
- The MCP server must not perform LLM calls.
- The MCP server owns tool contracts, not business persistence.

## Implementation Rules

- Keep the tool registry explicit and easy to inspect.
- Define each tool's name, description, input schema, and output schema.
- Keep route handlers thin; put tool execution in a service layer.
- Put downstream HTTP calls in client classes/modules.
- Use timeouts on all downstream HTTP calls.
- Map downstream 4xx/5xx responses to structured tool errors.
- Include enough trace metadata for the agent to report what happened.
- If using an MCP-style HTTP adapter instead of the official protocol, document the adapter honestly in README.
- Propagate the inbound X-Request-Id to every downstream call to the card service and graph RAG service, and include it in tool call trace metadata.

## API Contract

Provide:

- `GET /health`
- endpoint to list tools
- endpoint to call a tool

Tool call responses should include:

- tool name
- success flag
- result or error
- downstream service metadata where useful

## Testing

Test at minimum:

- tool registry contents
- schema validation for every tool
- success and failure path for every tool
- downstream timeout/error handling
- health report behavior when dependencies are healthy or unhealthy


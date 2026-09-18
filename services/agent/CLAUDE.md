# CLAUDE.md

## Component Ownership

This directory contains the AI agent service. It is responsible for receiving user questions, choosing and invoking MCP tools, and returning grounded answers with an auditable trace.

## Required Stack

- Python 3.12+.
- `uv` for dependency management and running scripts (`uv sync`, `uv run`).
- FastAPI.
- LangChain current package style.
- `langchain-openai` for OpenAI chat models.
- `langchain-groq` for Groq chat models.
- Pydantic Settings for configuration.
- `python-dotenv` for local development.
- `httpx` for MCP server communication.
- `pytest` for tests.

## Configuration

Read all runtime values from environment variables:

- `LLM_PROVIDER`: `openai` or `groq`.
- `OPENAI_API_KEY`.
- `OPENAI_MODEL`.
- `GROQ_API_KEY`.
- `GROQ_MODEL`.
- `MCP_SERVER_URL`.
- `AGENT_PORT`.
- `LLM_REQUEST_TIMEOUT_SECONDS`: max seconds to wait for a provider response.
- `LLM_MAX_OUTPUT_TOKENS`: cap on generated tokens per response.
- `LLM_MAX_RETRIES`: max retry attempts on transient provider failures.

Fail fast with a clear configuration error when the selected provider lacks a required API key.

## Guardrails

- Enforce `LLM_REQUEST_TIMEOUT_SECONDS` on every LLM call; return a structured timeout error rather than hanging the request.
- Enforce `LLM_MAX_OUTPUT_TOKENS` on every LLM call to bound cost and latency.
- Retry transient provider failures (e.g. 429/5xx) up to `LLM_MAX_RETRIES` times with backoff; do not retry on invalid-request errors.
- Surface guardrail failures (timeout, retries exhausted) as structured errors in the `/chat` response, not as unhandled exceptions.

## Boundary Rules

- The agent calls only the MCP server for tools.
- The agent must not call PostgreSQL, Neo4j, the card service, or graph RAG directly.
- The agent must not embed service-specific URLs other than `MCP_SERVER_URL`.
- The frontend-facing response must include a trace of tool calls used.
- The agent propagates the X-Request-Id from the inbound /chat request (generating one if the frontend didn't send it) to every MCP server call, and includes it in the returned tool trace.

## Implementation Rules

- Keep FastAPI routes thin.
- Put orchestration in an `AgentService` or equivalent application class.
- Put model construction in an `llm_factory` module.
- Put MCP communication in an `mcp_client` module.
- Define request/response DTOs with Pydantic models.
- Use dependency injection or factory functions so tests can provide fake LLMs and fake MCP clients.
- Keep prompts short, explicit, and grounded in returned tool context.
- Prefer a simple deterministic tool sequence for the teaching version:
  - discover available tools
  - retrieve graph/card context
  - ask the selected LLM to answer using context
  - return answer and trace
- Do not create an unbounded autonomous loop.
- Do not silently answer from model knowledge when context is required; state when context is missing.

## API Contract

Provide:

- `GET /health`
- `POST /chat`

`POST /chat` accepts:

- user message
- optional conversation/session identifier

`POST /chat` returns:

- answer
- model provider
- model name
- tool calls
- context snippets or source references
- structured error information when applicable

## Testing

Test at minimum:

- provider selection
- missing API key behavior
- prompt/context assembly
- MCP client request/response mapping
- chat orchestration with fake MCP responses and fake LLM response
- route validation for invalid chat requests

Tests must not require real OpenAI or Groq API keys.


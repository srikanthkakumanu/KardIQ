# CLAUDE.md

## Component Ownership

This directory contains the graph RAG service. It owns Neo4j graph persistence and graph-based retrieval context for the agent.

## Required Stack

- Python 3.12+.
- `uv` for dependency management and running scripts (`uv sync`, `uv run`).
- FastAPI.
- Neo4j Python driver.
- Pydantic Settings.
- `pytest`.
- Optional LangChain graph utilities only when they clarify rather than hide the implementation.

## Responsibilities

- Store card nodes in Neo4j.
- Store relationships between cards.
- Retrieve graph neighborhoods relevant to a question.
- Return compact, source-aware context for the agent through the MCP server.
- Seed the demo relationship used in documentation and the tutorial: a `LangChain USES OpenAI` relationship between the seeded cards, via an idempotent seed script or startup routine.

## Boundary Rules

- This service talks to Neo4j.
- It does not talk to PostgreSQL directly.
- It does not talk to the frontend directly.
- It does not talk to the AI agent directly.
- It should receive card data through service APIs or synchronization calls, not by reading another service database.

## Graph Model

Use a simple, explicit graph model:

- Node label: `Card`
- Card properties: `id`, `title`, `body`, `tags`, `updatedAt`
- Relationship type: start with `RELATED_TO`
- Relationship properties: `label`, `weight`, `createdAt` when useful

Create uniqueness constraints for card IDs.

## Retrieval Rules

Start with transparent retrieval before adding complexity:

- keyword match card title/body/tags
- expand one hop to related cards
- rank exact title/tag matches above body matches
- return source IDs and relationship labels
- format a concise `contextText` for LLM prompts

Do not add embeddings until graph retrieval is working and documented. If embeddings are added later, keep graph traversal visible in the response.

## API Contract

Provide:

- `GET /health`
- `POST /graph/cards`
- `POST /graph/relations`
- `POST /rag/search`

`POST /rag/search` returns:

- matched cards
- relationships used
- context text
- source identifiers

## Implementation Rules

- Keep FastAPI routes thin.
- Put Cypher execution in a repository module.
- Put retrieval/ranking/context formatting in a service module.
- Use parameterized Cypher queries only.
- Do not assemble Cypher by string-concatenating user input.
- Use driver sessions safely and close resources.
- Use timeouts where supported.
- Return structured errors when Neo4j is unavailable.
- Include the inbound X-Request-Id (if present) in every log line and in error responses for that request.

## Testing

Test:

- graph repository query methods with mocks or test Neo4j
- retrieval ranking and context formatting
- API validation
- behavior when Neo4j connection fails
- Cypher parameters are passed separately from query text


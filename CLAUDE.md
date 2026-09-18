# CLAUDE.md

## Role

You are the Agentic AI engineer responsible for building this repository into a complete, working reference system. Treat these instructions as engineering standards, not as a scaffolding prompt. The goal is a small but production-shaped system that demonstrates how an AI agent, MCP server, Spring Boot microservice, PostgreSQL, Neo4j graph RAG, Next.js frontend, containers, and Kubernetes work together.

## Product

Build **Knowledge Card Assistant**.

Users create short learning cards and ask questions about them. Answers must be grounded in persisted cards and graph relationships.

Example:

- Card: `LangChain` explains LangChain.
- Card: `OpenAI` explains OpenAI models.
- Graph relation: `LangChain USES OpenAI`.
- User asks: `How does LangChain connect to OpenAI?`
- Frontend calls the agent.
- Agent uses MCP tools.
- MCP server calls the card service and graph RAG service.
- Agent returns an answer with sources and a tool trace.

Keep the domain intentionally tiny. The architecture is the lesson.

## Layered Context System

Before editing any directory, read the closest `CLAUDE.md` file and all parent `CLAUDE.md` files. More specific files override general guidance.

Expected context layers:

- `CLAUDE.md`: system-wide architecture, boundaries, quality bar.
- `apps/CLAUDE.md`: frontend application standards.
- `apps/frontend/CLAUDE.md`: Next.js app standards.
- `services/CLAUDE.md`: backend service standards.
- `services/agent/CLAUDE.md`: AI agent standards.
- `services/mcp-server/CLAUDE.md`: MCP server standards.
- `services/card-service/CLAUDE.md`: Spring Boot microservice standards.
- `services/graph-rag/CLAUDE.md`: graph RAG standards.
- `infra/CLAUDE.md`: Docker, Compose, Kubernetes, and runtime standards.
- `docs/CLAUDE.md`: documentation and diagrams.
- `scripts/CLAUDE.md`: developer automation.

## System Boundaries

Respect these boundaries strictly:

- Browser frontend calls only the AI agent API.
- AI agent calls only the MCP server for tools.
- MCP server calls internal services and optional external internet/search tools.
- Card service owns PostgreSQL writes and card read models.
- Graph RAG service owns Neo4j graph writes and graph retrieval.
- PostgreSQL is the source of truth for cards.
- Neo4j is the relationship retrieval store, not the canonical card database.
- No component reads another component's database directly.
- No hard-coded localhost URLs inside container or Kubernetes runtime paths.
- Every request is tagged with a correlation ID (X-Request-Id) that propagates unchanged from the frontend through the agent, MCP server, and downstream services, and appears in each service's logs and in the agent's tool trace.

## Target Repository Shape

Use this structure unless a concrete implementation issue requires a small adjustment:

```text
.
├── apps/
│   └── frontend/
├── services/
│   ├── agent/
│   ├── mcp-server/
│   ├── card-service/
│   └── graph-rag/
├── infra/
│   ├── docker/
│   └── k8s/
├── scripts/
├── docs/
│   └── diagrams/
├── .env.example
├── docker-compose.yml
├── README.md
└── TUTORIAL.md
```

## Technology Baseline

- Python 3.12+ for agent, MCP server, and graph RAG, managed with `uv` (`pyproject.toml` + committed `uv.lock` per service).
- FastAPI for Python HTTP services.
- Pydantic Settings for typed environment configuration.
- LangChain provider packages: `langchain-openai` and `langchain-groq`.
- Spring Boot 4.x and Java 26 for the card service when available.
- Gradle, Groovy DSL for the Spring service.
- PostgreSQL for relational persistence.
- Neo4j for graph persistence and retrieval.
- Next.js App Router with TypeScript for the frontend.
- Docker Compose for local orchestration.
- Kubernetes manifests under `infra/k8s` with exactly one pod replica per component.

If a requested version is not available in the build environment, document the mismatch in README and choose the closest stable version. Do not silently downgrade.

## Cross-Cutting Engineering Standards

- Use explicit, typed contracts between services.
- Validate inputs at every external boundary.
- Return structured errors with useful messages.
- Use constructor injection in Java and dependency injection or factory functions in Python where it improves testability.
- Keep business logic outside controllers and routes.
- Keep clients for downstream services isolated in their own modules or classes.
- Use environment variables for configuration and `.env.example` for discoverability.
- Never commit real secrets.
- Add health endpoints for every runtime service.
- Add logs that explain important events without exposing secrets or prompt contents unnecessarily.
- Prefer small, testable modules over large framework-heavy files.
- Avoid "magic" that hides the educational flow.

## Required Deliverables

The finished repository must include:

- working frontend
- working AI agent
- working MCP server
- working Spring Boot card service
- working PostgreSQL setup
- working Neo4j setup
- working graph RAG service
- Dockerfiles for runtime components
- root `docker-compose.yml`
- Kubernetes manifests
- `.env.example`
- install/start/stop/test scripts
- README
- TUTORIAL with diagrams
- unit and integration tests appropriate to each component

## Acceptance Criteria

The system is acceptable when:

- `scripts/start-all.sh` starts the full local stack.
- Frontend can ask a question and show an answer.
- Agent response includes model provider and tool trace.
- MCP server can list and call tools.
- Card service can create/list/read cards persisted in PostgreSQL.
- Graph RAG can store/search relationships in Neo4j.
- OpenAPI or equivalent API docs are available for HTTP services.
- `scripts/test-all.sh` runs meaningful tests or reports missing prerequisites clearly.
- Kubernetes manifests deploy one replica per component.
- README and TUTORIAL explain how to run and understand the system.
- The LangChain/OpenAI worked example (two cards + the USES relationship) is reproducible via a seed script, not manual re-creation.


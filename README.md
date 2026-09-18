# KardIQ - Knowledge Card Assistant

A small, production-shaped reference system: users create short learning
cards and ask questions about them, and answers are grounded in those
cards **and** the graph relationships between them. The domain is
intentionally tiny - the point is the architecture, not the app.

**Worked example:** a `LangChain` card, an `OpenAI` card, a graph relation
`LangChain USES OpenAI`. Ask *"How does LangChain connect to OpenAI?"* and
the agent discovers MCP tools, retrieves the graph context, and answers
with sources and a full tool-call trace - grounded, not guessed.

See [`docs/diagrams/architecture.md`](docs/diagrams/architecture.md) for
the full component diagram and [`docs/diagrams/sequence.md`](docs/diagrams/sequence.md)
for exactly how that question flows through the system. For a guided,
layer-by-layer walkthrough of the whole codebase, read
[`TUTORIAL.md`](TUTORIAL.md).

## Components

| Component | Tech | Port | Directory | API docs |
|---|---|---|---|---|
| Frontend | Next.js 16 (App Router), TypeScript | 3000 | `apps/frontend` | - |
| Agent | FastAPI + LangChain | 8000 | `services/agent` | `/docs` |
| MCP server | FastAPI (HTTP adapter) | 8010 | `services/mcp-server` | `/docs`, `/tools` |
| Card service | Spring Boot 4 + Java 26 | 8080 | `services/card-service` | `/swagger-ui.html` |
| Graph RAG | FastAPI + Neo4j driver | 8020 | `services/graph-rag` | `/docs` |
| PostgreSQL | 16-alpine | 5432 (internal) | - | - |
| Neo4j | 5-community | 7474 / 7687 | - | Neo4j Browser at `:7474` |

Strict call graph: browser → agent → MCP server → {card-service, graph-rag}
→ {PostgreSQL, Neo4j}. No component skips a layer or reads another
component's database directly.

## Prerequisites

- Docker (with Compose v2) - the only hard requirement for `scripts/start-all.sh`.
- For local (non-Docker) development: Java 26 (a Gradle wrapper is
  bundled), Python 3.12+ with [`uv`](https://docs.astral.sh/uv/), and
  Node.js 22+.
- Optional: `kubectl` and a local cluster (Docker Desktop's built-in
  Kubernetes, kind, or Minikube) for the Kubernetes quick start below.
- An OpenAI or Groq API key - the agent fails fast at startup without one
  matching whichever `LLM_PROVIDER` you configure.

## Environment setup

```bash
cp .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY` (or switch `LLM_PROVIDER=groq` and
set `GROQ_API_KEY`). Every variable is documented inline in `.env.example`.

## Running locally (Docker Compose)

```bash
scripts/install-all.sh   # optional: only needed for local (non-Docker) dev
scripts/start-all.sh     # builds images, starts the stack, waits for health
scripts/seed-data.sh     # optional: SEED_ON_STARTUP=true (default) already does this
scripts/test-all.sh      # runs every test suite
scripts/stop-all.sh      # stops the stack; data volumes are preserved
```

`scripts/start-all.sh` prints every service URL once the stack is
healthy:

- Frontend: http://localhost:3000
- Agent API docs: http://localhost:8000/docs
- MCP server tools: http://localhost:8010/tools
- Card service Swagger UI: http://localhost:8080/swagger-ui.html
- Graph RAG API docs: http://localhost:8020/docs
- Neo4j Browser: http://localhost:7474

## Kubernetes quick start

```bash
docker compose build
cp infra/k8s/secret.example.yaml infra/k8s/secret.yaml   # then edit with real values
scripts/k8s-apply.sh
kubectl -n kardiq port-forward svc/agent 8000:8000 &
kubectl -n kardiq port-forward svc/frontend 3000:3000 &
```

See [`infra/k8s/README.md`](infra/k8s/README.md) for why both ports need
forwarding and how to point this at a real image registry.
Tear down with `scripts/k8s-delete.sh` (deletes all data).

## Troubleshooting

- **Agent container keeps restarting / exits immediately.** It fails fast
  if the API key for its configured `LLM_PROVIDER` is missing. Check
  `docker compose logs agent` - the error names exactly which variable to
  set.
- **Neo4j container won't start.** Its password (`NEO4J_PASSWORD` in
  `.env`, or the `NEO4J_AUTH` value in a Kubernetes secret) must be at
  least 8 characters and different from the username `neo4j`.
- **A service reports "unhealthy" in `docker compose ps` but seems to
  work fine.** Give it longer - `start_period` allows extra time before a
  failing health check counts against a service; check
  `docker compose logs <service>` for the actual error if it never
  recovers.
- **`scripts/seed-data.sh` says it can't find LangChain/OpenAI cards.**
  Card-service seeds them via a Flyway migration on first startup against
  a fresh database. If you're pointing the script at a database that
  already existed before this project's migrations ran, create the two
  cards manually first (via the frontend or `POST /api/v1/cards`).
- **Frontend loads but every question fails with a network error.** Its
  `NEXT_PUBLIC_AGENT_URL` is baked in at image build time, not read at
  container runtime - rebuild the frontend image if the agent's
  host-reachable URL changes.

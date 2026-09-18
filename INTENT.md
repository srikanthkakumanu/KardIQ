# INTENT.md

This file exists because the repository currently has a complete governance layer (11 `CLAUDE.md` files) but no implementation yet. It captures, in one place, what the project is trying to become, what already exists, what to build next and in what order, and a set of best-practice gaps worth closing in the `CLAUDE.md` files themselves. Treat this as a living planning doc — update it as components move from "planned" to "built." It is not a replacement for the `README.md` / `TUTORIAL.md` required by `docs/CLAUDE.md`; those describe the system as it actually runs, once it runs.

## 1. Purpose

Build **Knowledge Card Assistant**: users create short learning cards and ask questions about them, and answers are grounded in persisted cards *and* graph relationships between them. The canonical worked example (from root `CLAUDE.md`): a `LangChain` card, an `OpenAI` card, a graph relation `LangChain USES OpenAI`, and a user question "How does LangChain connect to OpenAI?" that the agent answers by calling MCP tools, which call the card service and graph RAG service, returning an answer with sources and a tool trace.

The domain is intentionally tiny — the point of the repo is not the card-taking app, it's a small, production-shaped demonstration of how an AI agent, an MCP server, a Spring Boot microservice, PostgreSQL, Neo4j graph RAG, a Next.js frontend, containers, and Kubernetes fit together. Every implementation decision should optimize for that teaching goal (visible, inspectable flow) over cleverness.

## 2. Current State ("day zero")

Only the governance layer and an empty directory skeleton exist. No code, no config files, no Dockerfiles, no `docker-compose.yml`, no Kubernetes manifests, no scripts, no docs, and **no git repository** has been initialized.

| Path | Status |
|---|---|
| `CLAUDE.md` (root) + 10 nested `CLAUDE.md` files | Present, complete — all 11 layers the root file expects exist |
| `apps/frontend/` | Stub — empty `app/`, `src/components/` dirs only |
| `services/agent/` | Stub — empty `app/` dir only |
| `services/mcp-server/` | Stub — empty `app/` dir only |
| `services/card-service/` | Stub, but with a full empty Java package skeleton: `src/main/java/com/example/cards/{api,application,domain,infrastructure}`, `src/main/resources/db/migration`, `src/test/java/com/example/cards` |
| `services/graph-rag/` | Stub — empty `app/` dir only |
| `infra/k8s/` | Empty directory, no manifests |
| `infra/docker/` | **Does not exist yet** (referenced in root `CLAUDE.md`'s target tree) |
| `scripts/` | Only `CLAUDE.md`, no `.sh` files |
| `docs/diagrams/` | Empty |
| Root `.env.example`, `docker-compose.yml`, `README.md`, `TUTORIAL.md` | Do not exist |

## 3. System Boundaries (recap)

Strict call graph — do not violate this while implementing:

```
Browser (Next.js frontend)
   -> AI agent API only
Agent
   -> MCP server only
MCP server
   -> card-service, graph-rag, optional internet/search tools
card-service
   -> owns PostgreSQL writes + card read models
graph-rag
   -> owns Neo4j writes + graph retrieval
```

PostgreSQL is the source of truth for cards; Neo4j is a relationship-retrieval store, never canonical. No component reads another component's database directly. No hard-coded `localhost` in container/Kubernetes runtime paths — use service DNS names (e.g. `http://agent:8000`, `postgres:5432`, `neo4j:7687`).

## 4. Build Order / To-Do Roadmap

Recommended sequence, driven by dependency order rather than the order components are listed in the repo tree:

1. **`services/card-service`** — Spring Boot 4.x / Java 26 / Gradle, Postgres + Flyway, `/api/v1/cards` CRUD. Nothing downstream has real data without this.
2. **`services/graph-rag`** — FastAPI + Neo4j driver, store `Card` nodes + `RELATED_TO` relationships, keyword + one-hop retrieval. Independent of card-service; can be built in parallel with step 1.
3. **`services/mcp-server`** — FastAPI/MCP SDK, required tools `list_cards`, `create_card`, `graph_search`, `health_report`, typed clients to card-service and graph-rag. Depends on 1 and 2 existing (or at least their contracts).
4. **`services/agent`** — FastAPI + LangChain (`langchain-openai`, `langchain-groq`), calls MCP server only, `/chat` returns answer + provider + model + tool trace. Depends on 3.
5. **`apps/frontend`** — Next.js App Router + TypeScript, calls agent only via `NEXT_PUBLIC_AGENT_URL`, shows answer + tool trace/sources. Depends on 4.
6. **`infra/docker`** — Dockerfile per runtime component (multi-stage for Java/Next.js), root `docker-compose.yml` wiring all 7 runtime pieces (5 app components + Postgres + Neo4j), root `.env.example`.
7. **`scripts/`** — `install-all.sh`, `start-all.sh`, `stop-all.sh`, `test-all.sh` (wraps the Compose stack from step 6).
8. **`infra/k8s`** — namespace, configmap, secret template, deployment+service per component, 1 replica each, PVs for Postgres/Neo4j; `scripts/k8s-apply.sh` / `k8s-delete.sh`.
9. **`docs/`** — root `README.md`, `TUTORIAL.md` with diagrams (architecture, sequence, data-ownership, k8s deployment), written last so they describe what actually runs rather than aspirational behavior, per `docs/CLAUDE.md`.
10. **Seed/demo data** — a fixture or seed script that creates the `LangChain` / `OpenAI` cards and the `USES` relation from the root `CLAUDE.md` example, so the TUTORIAL's worked example is runnable end to end without manual setup.

## 5. Known Gaps to Resolve While Building

- `infra/docker/` is referenced in root `CLAUDE.md`'s target tree but doesn't exist yet — create it at step 6, not a blocker before then.
- No git repository has been initialized yet (a root `.gitignore` now exists, but `git init` + first commit still needs to happen) — needed before any real work accumulates, so it can be committed incrementally per component.

## 6. Best-Practice Observations (CLAUDE.md review)

Status as of the latest governance update — most items below have now been applied directly to the `CLAUDE.md` files (and one new root `.gitignore` was added); two remain open for a deliberate future decision:

- ~~No git/version-control guidance~~ — **partially resolved**: a root `.gitignore` now exists covering Node/Python/Java/env/OS patterns. Branch strategy and commit conventions are still undocumented, and the repo itself is not yet `git init`'d.
- **No CI/CD mention** — still open. Standards cover local testing (`scripts/test-all.sh`) but say nothing about automated build/test on push — even a one-line "out of scope for this reference app" would remove ambiguity.
- **No linter/formatter mandate** — still open. The standards describe *what* good code looks like (typed contracts, DI, small modules) but don't name enforcement tooling — ESLint/Prettier for the frontend, Ruff/Black for the Python services, Spotless/Checkstyle for Java — that would make those standards mechanically checkable instead of just aspirational.
- ~~Correlation/trace ID propagation is vague~~ — **resolved**. All service-layer, agent, MCP server, and frontend `CLAUDE.md` files now require an `X-Request-Id` header generated at the frontend and propagated unchanged through every hop, logged everywhere, and included in the agent's tool trace (root `CLAUDE.md` System Boundaries + `services/CLAUDE.md` API Standards).
- ~~No LLM call guardrails specified~~ — **resolved**. `services/agent/CLAUDE.md` now has a `Guardrails` section plus `LLM_REQUEST_TIMEOUT_SECONDS`, `LLM_MAX_OUTPUT_TOKENS`, and `LLM_MAX_RETRIES` config.
- ~~No secrets-to-Kubernetes mapping guidance~~ — **resolved**. `infra/CLAUDE.md` now has a "Secrets from `.env`" subsection documenting the `kubectl create secret generic ... --from-env-file` pattern and the key-name-parity rule.
- ~~No seed-data requirement for the worked example~~ — **resolved**. `services/card-service/CLAUDE.md` and `services/graph-rag/CLAUDE.md` now require seeding the LangChain/OpenAI cards and their `USES` relationship; `scripts/CLAUDE.md` adds a required `scripts/seed-data.sh`; root `CLAUDE.md` adds it to Acceptance Criteria.
- **New**: the three Python services now standardize on `uv` for dependency management (`pyproject.toml` + committed `uv.lock`, `uv sync`/`uv run`), reflected in root `CLAUDE.md`, each Python service's `CLAUDE.md`, `scripts/CLAUDE.md` (`install-all.sh` runs `uv sync`), and `infra/CLAUDE.md` (Dockerfiles use `uv sync --frozen`).

## 7. Acceptance Criteria (recap, from root `CLAUDE.md`)

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

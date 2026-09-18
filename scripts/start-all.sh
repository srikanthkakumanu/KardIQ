#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Missing prerequisite: docker (install Docker Desktop or the Docker Engine)" >&2
  exit 1
fi

if [ ! -f .env ]; then
  echo "No .env found - copying from .env.example."
  echo "Edit .env to set a real OPENAI_API_KEY or GROQ_API_KEY before the agent will answer questions - it fails fast at startup without one."
  cp .env.example .env
fi

echo "==> Starting the KardIQ stack (docker compose up -d --build)"
docker compose up -d --build

echo
echo "==> Waiting for all services to report healthy..."
services=(postgres neo4j card-service graph-rag mcp-server agent frontend)
for service in "${services[@]}"; do
  printf '    %-15s' "$service"
  status=""
  for _ in $(seq 1 60); do
    status="$(docker compose ps --format '{{.Health}}' "$service" 2>/dev/null || true)"
    if [ "$status" = "healthy" ]; then
      echo "healthy"
      break
    fi
    sleep 2
  done
  if [ "$status" != "healthy" ]; then
    echo "did not become healthy in time - check: docker compose logs $service"
  fi
done

# shellcheck disable=SC1091
set -a
source .env
set +a

cat <<EOF

KardIQ is up. Try it out:

  Frontend:        http://localhost:${FRONTEND_PORT:-3000}
  Agent API docs:  http://localhost:${AGENT_PORT:-8000}/docs
  MCP server:      http://localhost:${MCP_SERVER_PORT:-8010}/tools
  Card service:    http://localhost:${CARD_SERVICE_PORT:-8080}/swagger-ui.html
  Graph RAG docs:  http://localhost:${GRAPH_RAG_PORT:-8020}/docs
  Neo4j browser:   http://localhost:${NEO4J_HTTP_PORT:-7474}

The LangChain/OpenAI demo cards and relationship are seeded automatically
(SEED_ON_STARTUP=true by default). If you set it to false, or want to
re-seed against a different card-service/graph-rag pair, run:

  scripts/seed-data.sh

Run scripts/stop-all.sh to stop the stack (data is preserved).
EOF

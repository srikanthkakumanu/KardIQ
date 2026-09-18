#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILURES=0

run_step() {
  local name="$1"
  shift
  echo
  echo "==> $name"
  if ! ( "$@" ); then
    echo "FAILED: $name"
    FAILURES=$((FAILURES + 1))
  fi
}

if command -v uv >/dev/null 2>&1; then
  run_step "agent tests (uv run pytest)" bash -c "cd '$ROOT_DIR/services/agent' && uv run pytest -q"
  run_step "mcp-server tests (uv run pytest)" bash -c "cd '$ROOT_DIR/services/mcp-server' && uv run pytest -q"
  run_step "graph-rag tests (uv run pytest)" bash -c "cd '$ROOT_DIR/services/graph-rag' && uv run pytest -q"
else
  echo
  echo "SKIPPED Python service tests: uv is not installed (https://docs.astral.sh/uv/getting-started/installation/)"
fi

if command -v npm >/dev/null 2>&1; then
  run_step "frontend typecheck" bash -c "cd '$ROOT_DIR/apps/frontend' && npm run typecheck"
  run_step "frontend lint" bash -c "cd '$ROOT_DIR/apps/frontend' && npm run lint"
  run_step "frontend tests (vitest)" bash -c "cd '$ROOT_DIR/apps/frontend' && npm run test"
else
  echo
  echo "SKIPPED frontend checks: npm is not installed (https://nodejs.org/)"
fi

if [ -x "$ROOT_DIR/services/card-service/gradlew" ]; then
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    run_step "card-service tests (./gradlew test - Testcontainers needs Docker)" \
      bash -c "cd '$ROOT_DIR/services/card-service' && ./gradlew test --no-daemon"
  else
    echo
    echo "SKIPPED card-service tests: Docker is required (Testcontainers-backed integration tests) but is not running"
  fi
else
  echo
  echo "SKIPPED card-service tests: services/card-service/gradlew not found"
fi

echo
if [ "$FAILURES" -eq 0 ]; then
  echo "All test suites passed."
else
  echo "$FAILURES test suite(s) failed."
  exit 1
fi

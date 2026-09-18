#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log() { printf '\n==> %s\n' "$1"; }

require() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing prerequisite: $1 ($2)" >&2
    exit 1
  fi
}

require uv "install from https://docs.astral.sh/uv/getting-started/installation/"
require npm "install Node.js from https://nodejs.org/"
require java "install a JDK (Java 26 recommended) from https://adoptium.net/"

log "Installing agent dependencies (uv sync)"
(cd "$ROOT_DIR/services/agent" && uv sync)

log "Installing mcp-server dependencies (uv sync)"
(cd "$ROOT_DIR/services/mcp-server" && uv sync)

log "Installing graph-rag dependencies (uv sync)"
(cd "$ROOT_DIR/services/graph-rag" && uv sync)

log "Installing frontend dependencies (npm install)"
(cd "$ROOT_DIR/apps/frontend" && npm install)

log "Resolving card-service dependencies and compiling (./gradlew build -x test)"
(cd "$ROOT_DIR/services/card-service" && ./gradlew build -x test --no-daemon)

log "All dependencies installed."

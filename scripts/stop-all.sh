#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Missing prerequisite: docker (install Docker Desktop or the Docker Engine)" >&2
  exit 1
fi

echo "==> Stopping the KardIQ stack (data volumes are preserved)"
docker compose down

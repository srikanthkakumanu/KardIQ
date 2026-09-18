# CLAUDE.md

## Scope

This file governs developer automation scripts.

## Script Standards

- Use Bash.
- Start every Bash script with `set -euo pipefail`.
- Keep scripts explicit and readable.
- Use relative paths from the repository root where practical.
- Detect missing prerequisites and print actionable messages.
- Do not hide failures.
- Do not require real LLM API keys for tests that can run with mocks.

## Required Scripts

Provide:

- `scripts/install-all.sh`
- `scripts/start-all.sh`
- `scripts/stop-all.sh`
- `scripts/test-all.sh`

Add these if Kubernetes manifests are created:

- `scripts/k8s-apply.sh`
- `scripts/k8s-delete.sh`

Add this once card-service and graph-rag exist:

- `scripts/seed-data.sh`

Component-specific scripts are allowed when they reduce command complexity.

## Behavior

- `install-all.sh` installs dependencies or prints component-specific install commands, running `uv sync` in each Python service directory (agent, mcp-server, graph-rag) in addition to any frontend/Java install steps.
- `start-all.sh` starts the Docker Compose stack and prints useful URLs.
- `stop-all.sh` stops the Docker Compose stack without deleting persistent data.
- `test-all.sh` runs frontend, Python, and Java tests.
- `seed-data.sh` creates the demo LangChain/OpenAI cards and their relationship via the running card-service and graph-rag APIs; safe to re-run (idempotent).
- Kubernetes scripts should target the configured namespace and not affect unrelated namespaces.

## Safety

- Do not delete Docker volumes in normal stop scripts.
- Destructive reset scripts must be clearly named, such as `reset-local-data.sh`.
- Never embed secrets in scripts.
- Do not assume a user's shell profile or global environment is loaded.


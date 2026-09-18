# CLAUDE.md

## Scope

This file governs Docker, Docker Compose, Kubernetes, runtime configuration, and deployment assets.

## Local Runtime

The root Docker Compose stack must run:

- frontend
- agent
- MCP server
- card service
- graph RAG service
- PostgreSQL
- Neo4j

Use service DNS names for container communication:

- `http://agent:8000`
- `http://mcp-server:8010`
- `http://card-service:8080`
- `http://graph-rag:8020`
- `postgres:5432`
- `neo4j:7687`

Do not use `localhost` for container-to-container URLs.

## Docker Standards

- Every runtime component has a Dockerfile.
- Prefer multi-stage builds for Java and Next.js.
- Keep Python images simple and explicit.
- Run containers as non-root where practical.
- Install only runtime dependencies in final images.
- Expose only required ports.
- Add health checks in Compose where practical.
- Keep image build context scoped to the component directory.
- Python service Dockerfiles install dependencies with `uv sync --frozen` for reproducible, lockfile-pinned builds.

## Configuration

- Root `.env.example` must list all required environment variables.
- Compose should work with `.env` copied from `.env.example`.
- Secrets must not have real values in committed files.
- Use consistent variable names across local, Compose, and Kubernetes.
- Kubernetes Secret keys must reuse the exact variable names from `.env.example` so local and cluster config stay in sync.

## Kubernetes Standards

Place manifests under `infra/k8s`.

Required objects:

- namespace
- configmap
- secret template or example secret
- deployment and service for frontend
- deployment and service for agent
- deployment and service for MCP server
- deployment and service for card service
- deployment or stateful workload and service for PostgreSQL
- deployment or stateful workload and service for Neo4j
- deployment and service for graph RAG

Every workload must use one pod instance:

```yaml
replicas: 1
```

Use:

- readiness probes for HTTP services
- liveness probes where useful
- persistent volumes for PostgreSQL and Neo4j when practical
- ConfigMaps for non-secret config
- Secrets for API keys and passwords

### Secrets from `.env`

- The example Secret manifest lists the same keys as `.env.example`, with placeholder (non-real) values.
- Document one supported way to create the real cluster Secret from a local `.env` file, e.g.:
  `kubectl create secret generic app-secrets --from-env-file=.env -n <namespace>`
- Never commit a Secret manifest containing real values — only the placeholder template.

## Operational Expectations

- Local startup should be one command.
- Local shutdown should be one command.
- Kubernetes apply/delete should be scripted if manifests are numerous.
- Scripts should print the URLs needed to try the system.
- Health checks should make dependency failures visible.

## Safety

- Do not include destructive volume deletion in normal stop scripts.
- If a reset script is added, name it clearly and document data loss.
- Never commit real API keys or database passwords.


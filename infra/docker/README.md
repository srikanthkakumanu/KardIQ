# infra/docker

Per the Layered Context System's "more specific overrides general" rule,
each runtime component owns its own `Dockerfile` rather than this
directory holding them centrally:

- `apps/frontend/Dockerfile`
- `services/card-service/Dockerfile`
- `services/graph-rag/Dockerfile`
- `services/mcp-server/Dockerfile`
- `services/agent/Dockerfile`

This keeps each Dockerfile next to the build context it packages, and
matches `apps/frontend/CLAUDE.md`'s own Suggested Structure, which already
places `Dockerfile` inside `apps/frontend/`.

`infra/docker/` exists only to document that convention. The root
`docker-compose.yml` builds every image from its component's own
Dockerfile via a `build.context` pointing at that directory.

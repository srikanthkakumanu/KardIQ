# CLAUDE.md

## Scope

This file governs backend services under `services/`.

## Service Standards

- Each service owns one bounded responsibility.
- Every service exposes a health endpoint.
- Every service uses typed configuration loaded from environment variables.
- Every service documents its public endpoints.
- Business logic belongs in service/application modules, not route/controller handlers.
- Downstream calls belong in dedicated clients/adapters.
- External request and response bodies must use DTO/schema classes.
- Validate all inbound request payloads.
- Log service startup, important operations, and downstream failures.
- Do not log secrets, API keys, database passwords, or full LLM prompts by default.

## API Standards

- Use REST for normal service APIs.
- Use nouns for resources and verbs only where resource semantics are not a good fit.
- Return stable JSON shapes.
- Return useful error responses with an error code and message.
- Accept an inbound X-Request-Id header; if absent, generate one. Propagate it unchanged on every downstream HTTP call and include it in every log line for the request.
- Keep endpoint names consistent across services: `/health`, `/api/...`, `/docs` where supported.

## Dependency Rules

- Services communicate over HTTP unless a component-specific file says otherwise.
- No service directly accesses another service's database.
- Environment variables provide downstream URLs.
- Container runtime URLs must use Docker Compose or Kubernetes service names, not `localhost`.

## Testing Rules

- Unit test business logic with downstream dependencies mocked.
- Integration test HTTP boundaries where practical.
- Keep tests deterministic and independent of real API keys.
- Provide clear instructions for tests requiring Docker dependencies.


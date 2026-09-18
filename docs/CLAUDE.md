# CLAUDE.md

## Scope

This file governs documentation and diagrams. Documentation supports the working system; it does not replace the implementation.

## Documentation Standards

- Write for a capable engineer learning how the components fit together.
- Keep instructions copy-paste friendly.
- Document commands that were actually designed to work.
- Explain operational boundaries and data ownership.
- Avoid vague claims such as "production-ready" unless the system truly meets that bar.
- Keep docs in sync with filenames, ports, environment variables, and scripts.

## README Requirements

The root README must include:

- system purpose
- use case
- architecture overview
- component table with ports and directories
- prerequisites
- environment setup
- local start/stop/test commands
- service URLs
- Kubernetes quick start
- troubleshooting section

## Tutorial Requirements

`TUTORIAL.md` should explain the built system layer by layer:

- user journey
- request flow
- frontend
- agent
- MCP server
- card microservice
- PostgreSQL
- graph RAG
- Neo4j
- container runtime
- Kubernetes
- tests
- extension points

The tutorial should describe implementation decisions, not invent aspirational behavior that is absent from the code.

## Diagram Standards

Use infographic diagrams as PNG files embedded in Markdown unless a generated image is explicitly needed.

Include:

- high-level architecture diagram
- sequence diagram for a user question
- data ownership diagram
- Kubernetes deployment diagram

Diagrams should be:

- readable in GitHub Markdown
- visually balanced
- named consistently with the code
- small enough to understand quickly

## API Documentation

- Link to generated OpenAPI docs for HTTP services.
- Keep example requests and responses short.
- Ensure examples match DTO names and actual endpoints.


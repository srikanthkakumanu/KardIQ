# CLAUDE.md

## Scope

This file governs frontend applications under `apps/`.

## Frontend Engineering Standards

- Build product UI, not a marketing page.
- Keep browser code isolated from internal topology.
- Frontend applications call public application APIs only. For this repo, that means the AI agent API.
- Do not call the MCP server, card service, graph RAG service, PostgreSQL, or Neo4j from browser code.
- Use TypeScript strictly. Avoid `any` unless the boundary is genuinely unknown and narrowed immediately.
- Keep API clients in dedicated modules. UI components should not assemble raw fetch calls inline.
- Model API responses with explicit TypeScript types.
- Keep components small and named for their product responsibility.
- Separate stateful client components from presentational components when it improves readability.

## UX Standards

- The first screen must support the core workflow.
- Show loading, empty, success, and error states.
- Make errors understandable to a learner running the stack locally.
- Keep the interface responsive on mobile and desktop.
- Show agent trace/context in a compact inspectable panel so users can understand the architecture.
- Avoid decorative UI that obscures the system behavior.

## Configuration

- Use `NEXT_PUBLIC_*` only for values safe to expose in the browser.
- Never expose API keys, database credentials, or internal service secrets.
- Keep local configuration documented in `.env.example`.

## Testing

- Include type checking as a required quality gate.
- Add unit/component tests for non-trivial state and rendering behavior.
- Mock network calls in frontend tests.
- Keep fixtures small and close to the tests that use them.


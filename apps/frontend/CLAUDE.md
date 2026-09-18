# CLAUDE.md

## Component Ownership

This directory contains the Next.js frontend for Knowledge Card Assistant. It is the user's entry point and should make the system understandable through the UI.

## Required Stack

- Next.js App Router.
- TypeScript with strict mode.
- React functional components.
- A small typed agent API client.
- CSS Modules, Tailwind, or another lightweight styling approach. Do not introduce a large UI framework unless the app already uses one.

## Application Responsibilities

- Let the user ask the assistant a question.
- Show the assistant answer.
- Show tool calls, retrieved context, and source/card references when returned by the agent.
- Optionally provide a tiny card creation/viewing flow if it helps demonstrate the end-to-end system.

## Boundary Rules

- Call only `NEXT_PUBLIC_AGENT_URL`.
- Do not call internal service URLs from the browser.
- Do not duplicate backend business rules in the UI.
- Do not store secrets in frontend code or frontend environment variables.

## Implementation Rules

- Put API calls in `src/api/agentClient.ts` or equivalent.
- Put shared request/response types in `src/types.ts` or colocated type modules.
- Use controlled form inputs for the chat/question form.
- Disable submit while a request is in flight.
- Use `AbortController` or equivalent cancellation if requests can overlap.
- Render API errors from structured error responses when available.
- Keep page-level orchestration in `app/page.tsx`; extract reusable UI pieces into `src/components`.
- Use semantic HTML for forms, buttons, headings, and status messages.
- Ensure text does not overflow on small screens.
- Generate a per-request X-Request-Id (e.g. a UUID) when calling the agent, send it as a header, and display it in the trace/inspectable panel so users can correlate a UI answer with backend logs.

## Suggested Structure

```text
apps/frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── src/
│   ├── api/
│   ├── components/
│   └── types.ts
├── package.json
├── next.config.ts
├── tsconfig.json
└── Dockerfile
```

## Quality Gates

- `npm run typecheck` must pass.
- `npm run lint` should pass when linting is configured.
- `npm run build` must pass for production image creation.
- Tests should cover the chat form, loading state, error state, and successful answer rendering.


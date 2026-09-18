import type { ApiErrorBody, ChatRequest, ChatResponse } from "@/src/types";

// The sole network boundary for the browser: only ever calls the agent,
// never an internal service URL, per apps/frontend/CLAUDE.md.
const AGENT_URL = process.env.NEXT_PUBLIC_AGENT_URL ?? "http://localhost:8000";

export class AgentApiError extends Error {
  readonly code: string;
  readonly requestId: string;

  constructor(body: ApiErrorBody) {
    super(body.message);
    this.name = "AgentApiError";
    this.code = body.code;
    this.requestId = body.requestId;
  }
}

function generateRequestId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `req-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export async function postChat(request: ChatRequest, signal?: AbortSignal): Promise<ChatResponse> {
  const requestId = generateRequestId();

  const response = await fetch(`${AGENT_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Request-Id": requestId,
    },
    body: JSON.stringify(request),
    signal,
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as ApiErrorBody | null;
    if (body && typeof body.code === "string" && typeof body.message === "string") {
      throw new AgentApiError(body);
    }
    throw new AgentApiError({
      code: "UNKNOWN_ERROR",
      message: `Request failed with status ${response.status}`,
      requestId,
    });
  }

  return (await response.json()) as ChatResponse;
}

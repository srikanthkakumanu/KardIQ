import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AgentApiError } from "@/src/api/agentClient";
import type { ChatResponse } from "@/src/types";

import Home from "../page";

vi.mock("@/src/api/agentClient", async () => {
  const actual = await vi.importActual<typeof import("@/src/api/agentClient")>("@/src/api/agentClient");
  return {
    ...actual,
    postChat: vi.fn(),
  };
});

const { postChat } = await import("@/src/api/agentClient");
const postChatMock = vi.mocked(postChat);

function successResponse(overrides: Partial<ChatResponse> = {}): ChatResponse {
  return {
    answer: "LangChain uses OpenAI as its LLM provider.",
    provider: "openai",
    model: "gpt-4o-mini",
    toolCalls: [{ tool: "graph_search", success: true, latencyMs: 12.0 }],
    sources: [{ cardId: "1", title: "LangChain" }],
    contextSnippets: ["LangChain USES OpenAI"],
    requestId: "req-1",
    error: null,
    ...overrides,
  };
}

describe("Home page", () => {
  beforeEach(() => {
    postChatMock.mockReset();
  });

  async function askQuestion(question = "How does LangChain connect to OpenAI?") {
    const user = userEvent.setup();
    render(<Home />);
    await user.type(screen.getByLabelText(/ask a question/i), question);
    await user.click(screen.getByRole("button", { name: /ask/i }));
    return user;
  }

  it("shows a loading state while the request is in flight", async () => {
    let resolveRequest!: (value: ChatResponse) => void;
    postChatMock.mockReturnValue(new Promise((resolve) => (resolveRequest = resolve)));

    await askQuestion();

    expect(screen.getByRole("status")).toHaveTextContent(/thinking/i);
    expect(screen.getByRole("button", { name: /asking/i })).toBeDisabled();

    resolveRequest(successResponse());
    await waitFor(() => expect(screen.queryByRole("status")).not.toBeInTheDocument());
  });

  it("renders the answer, sources, and trace on success", async () => {
    postChatMock.mockResolvedValue(successResponse());

    await askQuestion();

    expect(await screen.findByText("LangChain uses OpenAI as its LLM provider.")).toBeInTheDocument();
    expect(screen.getByText("LangChain")).toBeInTheDocument();
    expect(screen.getByText(/how this answer was produced/i)).toBeInTheDocument();
  });

  it("renders a structured error banner when the agent returns a chat-level error", async () => {
    postChatMock.mockResolvedValue(
      successResponse({ answer: "", error: { code: "LLM_TIMEOUT", message: "The LLM provider timed out" } }),
    );

    await askQuestion();

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("LLM_TIMEOUT");
    expect(alert).toHaveTextContent("The LLM provider timed out");
  });

  it("renders a network error banner when the request itself fails", async () => {
    postChatMock.mockRejectedValue(new AgentApiError({ code: "MCP_UNAVAILABLE", message: "down", requestId: "r" }));

    await askQuestion();

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("MCP_UNAVAILABLE");
    expect(alert).toHaveTextContent("down");
  });
});

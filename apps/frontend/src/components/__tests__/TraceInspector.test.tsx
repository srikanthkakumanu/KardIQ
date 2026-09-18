import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { TraceInspector } from "@/src/components/TraceInspector";
import type { ChatResponse } from "@/src/types";

const result: ChatResponse = {
  answer: "LangChain uses OpenAI.",
  provider: "openai",
  model: "gpt-4o-mini",
  toolCalls: [
    { tool: "list_tools", success: true, latencyMs: null },
    { tool: "graph_search", success: true, latencyMs: 12.3 },
  ],
  sources: [],
  contextSnippets: ["LangChain USES OpenAI"],
  requestId: "req-abc-123",
  error: null,
};

describe("TraceInspector", () => {
  it("shows provider, model, and request id", () => {
    render(<TraceInspector result={result} />);

    expect(screen.getByText("openai")).toBeInTheDocument();
    expect(screen.getByText("gpt-4o-mini")).toBeInTheDocument();
    expect(screen.getByText("req-abc-123")).toBeInTheDocument();
  });

  it("shows every tool call with its outcome", () => {
    render(<TraceInspector result={result} />);

    expect(screen.getByText(/list_tools - ok/)).toBeInTheDocument();
    expect(screen.getByText(/graph_search - ok \(12\.3ms\)/)).toBeInTheDocument();
  });

  it("shows a failed tool call distinctly", () => {
    render(
      <TraceInspector
        result={{ ...result, toolCalls: [{ tool: "graph_search", success: false, latencyMs: null }] }}
      />,
    );

    expect(screen.getByText(/graph_search - failed/)).toBeInTheDocument();
  });

  it("shows context snippets when present", () => {
    render(<TraceInspector result={result} />);

    expect(screen.getByText("LangChain USES OpenAI")).toBeInTheDocument();
  });
});

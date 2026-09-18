import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AnswerPanel } from "@/src/components/AnswerPanel";
import type { ChatResponse } from "@/src/types";

const baseResult: ChatResponse = {
  answer: "LangChain uses OpenAI as its LLM provider.",
  provider: "openai",
  model: "gpt-4o-mini",
  toolCalls: [],
  sources: [{ cardId: "1", title: "LangChain" }],
  contextSnippets: [],
  requestId: "req-1",
  error: null,
};

describe("AnswerPanel", () => {
  it("renders the answer text", () => {
    render(<AnswerPanel result={baseResult} />);

    expect(screen.getByText(baseResult.answer)).toBeInTheDocument();
  });

  it("renders sources when present", () => {
    render(<AnswerPanel result={baseResult} />);

    expect(screen.getByText("Sources")).toBeInTheDocument();
    expect(screen.getByText("LangChain")).toBeInTheDocument();
  });

  it("omits the sources section when there are none", () => {
    render(<AnswerPanel result={{ ...baseResult, sources: [] }} />);

    expect(screen.queryByText("Sources")).not.toBeInTheDocument();
  });
});

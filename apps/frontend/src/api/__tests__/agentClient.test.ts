import { afterEach, describe, expect, it, vi } from "vitest";

import { AgentApiError, postChat } from "@/src/api/agentClient";

describe("postChat", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends the message and an X-Request-Id header, and returns the parsed response", async () => {
    const fetchMock = vi.fn(async (_url: string, init?: RequestInit) => {
      expect(init?.headers).toMatchObject({ "X-Request-Id": expect.any(String) });
      expect(JSON.parse(init?.body as string)).toEqual({ message: "hi" });
      return new Response(
        JSON.stringify({
          answer: "hello",
          provider: "openai",
          model: "gpt-4o-mini",
          toolCalls: [],
          sources: [],
          contextSnippets: [],
          requestId: "req-1",
          error: null,
        }),
        { status: 200 },
      );
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await postChat({ message: "hi" });

    expect(result.answer).toBe("hello");
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("throws AgentApiError with the structured error body on a non-ok response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(JSON.stringify({ code: "VALIDATION_ERROR", message: "bad input", requestId: "req-2" }), {
            status: 422,
          }),
      ),
    );

    await expect(postChat({ message: "" })).rejects.toMatchObject({
      code: "VALIDATION_ERROR",
      message: "bad input",
    });
  });

  it("throws a generic AgentApiError when the error body cannot be parsed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("not json", { status: 500 })),
    );

    await expect(postChat({ message: "hi" })).rejects.toBeInstanceOf(AgentApiError);
  });
});

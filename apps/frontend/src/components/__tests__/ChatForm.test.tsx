import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ChatForm } from "@/src/components/ChatForm";

describe("ChatForm", () => {
  it("calls onSubmit with the trimmed message when submitted", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ChatForm onSubmit={onSubmit} disabled={false} />);

    await user.type(screen.getByLabelText(/ask a question/i), "  How does LangChain connect to OpenAI?  ");
    await user.click(screen.getByRole("button", { name: /ask/i }));

    expect(onSubmit).toHaveBeenCalledWith("How does LangChain connect to OpenAI?");
  });

  it("does not call onSubmit for a blank message", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<ChatForm onSubmit={onSubmit} disabled={false} />);

    await user.click(screen.getByRole("button", { name: /ask/i }));

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("disables the textarea and button while a request is in flight", () => {
    render(<ChatForm onSubmit={vi.fn()} disabled />);

    expect(screen.getByLabelText(/ask a question/i)).toBeDisabled();
    expect(screen.getByRole("button", { name: /asking/i })).toBeDisabled();
  });
});

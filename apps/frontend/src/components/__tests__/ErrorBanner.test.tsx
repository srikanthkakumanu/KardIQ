import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ErrorBanner } from "@/src/components/ErrorBanner";

describe("ErrorBanner", () => {
  it("renders the error code and message with an alert role", () => {
    render(<ErrorBanner code="LLM_TIMEOUT" message="The LLM provider did not respond in time" />);

    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("LLM_TIMEOUT");
    expect(alert).toHaveTextContent("The LLM provider did not respond in time");
  });
});

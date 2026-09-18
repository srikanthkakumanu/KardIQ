class ConfigurationError(Exception):
    """Raised at startup when required configuration (e.g. a provider API
    key) is missing - the agent must fail fast, per services/agent/CLAUDE.md."""


class LlmGuardrailError(Exception):
    """Raised by app.llm.guardrails when a provider call times out, fails
    non-retryably, or exhausts its retry budget."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class DownstreamError(Exception):
    """Normalizes an MCP server HTTP error or connectivity failure."""

    def __init__(self, code: str, message: str, status_code: int | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"{code}: {message}")

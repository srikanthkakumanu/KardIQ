class DownstreamError(Exception):
    """Normalizes a card-service/graph-rag HTTP error (or connectivity failure)
    into a tool error, per services/mcp-server/CLAUDE.md's "normalize
    downstream errors into tool errors" rule."""

    def __init__(self, service: str, code: str, message: str, status_code: int | None = None):
        self.service = service
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"{service}: {code} - {message}")

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.logging import request_id_var

HEADER_NAME = "X-Request-Id"


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Accepts an inbound X-Request-Id, generating one if absent, and makes it
    available to every log line, downstream call, and tool-call trace for
    the request, per the correlation-ID propagation rule in
    services/CLAUDE.md and services/mcp-server/CLAUDE.md."""

    async def dispatch(self, request: Request, call_next):
        incoming = request.headers.get(HEADER_NAME)
        request_id = incoming if incoming else str(uuid.uuid4())
        # Intentionally not reset after the request: if a route raises, the
        # exception propagates out of call_next before this dispatch resumes,
        # so registered exception handlers (further up the ASGI stack) still
        # need request_id_var to hold this request's id. Each request runs in
        # its own asyncio Task, so there is no cross-request leakage from
        # skipping the reset.
        request_id_var.set(request_id)
        response = await call_next(request)
        response.headers[HEADER_NAME] = request_id
        return response

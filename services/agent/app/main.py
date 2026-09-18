import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.api.schemas import ErrorResponse
from app.config import get_settings
from app.llm.llm_factory import build_chat_model
from app.logging import configure_logging, request_id_var
from app.middleware import HEADER_NAME, RequestIdMiddleware
from app.mcp.mcp_client import McpClient
from app.services.agent_service import AgentService

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    # Fails fast per services/agent/CLAUDE.md if the selected provider is
    # missing its API key - the process should not start half-configured.
    chat_model = build_chat_model(settings)
    mcp_client = McpClient(settings.mcp_server_url, settings.mcp_request_timeout_seconds)
    app.state.agent_service = AgentService(mcp_client, chat_model, settings)
    logger.info("agent started on port %s (provider=%s)", settings.agent_port, settings.llm_provider)
    yield


app = FastAPI(title="KardIQ Agent", lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)
app.include_router(router)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    request_id = request_id_var.get()
    body = ErrorResponse(code=code, message=message, request_id=request_id)
    response = JSONResponse(status_code=status_code, content=body.model_dump(by_alias=True))
    # The RequestIdMiddleware never resumes on this path (the exception
    # propagated out of call_next), so the header has to be set here too.
    response.headers[HEADER_NAME] = request_id
    return response


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    message = "; ".join(f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors())
    return _error_response(422, "VALIDATION_ERROR", message)


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error")
    return _error_response(500, "INTERNAL_ERROR", "An unexpected error occurred")

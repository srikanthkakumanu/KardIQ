import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from neo4j.exceptions import ServiceUnavailable

from app.api.routes import router
from app.api.schemas import ErrorResponse
from app.config import get_settings
from app.db.neo4j_driver import create_driver, ensure_constraints
from app.errors import CardNotFoundError
from app.logging import configure_logging, request_id_var
from app.middleware import HEADER_NAME, RequestIdMiddleware
from app.seed.seed_demo_data import seed_demo_data
from app.util import now_iso

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    driver = create_driver(settings)
    app.state.driver = driver
    ensure_constraints(driver)
    logger.info("graph-rag service started on port %s", settings.graph_rag_port)
    if settings.seed_on_startup:
        seed_demo_data(driver)
    try:
        yield
    finally:
        driver.close()


app = FastAPI(title="KardIQ Graph RAG Service", lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)
app.include_router(router)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    request_id = request_id_var.get()
    body = ErrorResponse(code=code, message=message, request_id=request_id, timestamp=now_iso())
    response = JSONResponse(status_code=status_code, content=body.model_dump(by_alias=True))
    # The RequestIdMiddleware never resumes on this path (the exception
    # propagated out of call_next), so the header has to be set here too.
    response.headers[HEADER_NAME] = request_id
    return response


@app.exception_handler(CardNotFoundError)
def handle_card_not_found(request: Request, exc: CardNotFoundError) -> JSONResponse:
    return _error_response(404, "CARD_NOT_FOUND", str(exc))


@app.exception_handler(ServiceUnavailable)
def handle_neo4j_unavailable(request: Request, exc: ServiceUnavailable) -> JSONResponse:
    logger.error("Neo4j unavailable: %s", exc)
    return _error_response(503, "NEO4J_UNAVAILABLE", "Graph database is currently unavailable")


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    message = "; ".join(f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors())
    return _error_response(422, "VALIDATION_ERROR", message)


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error")
    return _error_response(500, "INTERNAL_ERROR", "An unexpected error occurred")

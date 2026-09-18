import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import tools as _tools  # noqa: F401  (import populates TOOL_REGISTRY as a side effect)
from app.api.routes import router
from app.clients.card_service_client import CardServiceClient
from app.clients.graph_rag_client import GraphRagClient
from app.config import get_settings
from app.logging import configure_logging
from app.middleware import RequestIdMiddleware
from app.tools.clients import Clients

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.clients = Clients(
        card_service=CardServiceClient(settings.card_service_url, settings.downstream_timeout_seconds),
        graph_rag=GraphRagClient(settings.graph_rag_url, settings.downstream_timeout_seconds),
    )
    logger.info("mcp-server started on port %s", settings.mcp_server_port)
    yield


app = FastAPI(title="KardIQ MCP Server", lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)
app.include_router(router)

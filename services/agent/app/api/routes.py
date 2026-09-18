from fastapi import APIRouter, Depends, Request

from app.api.schemas import (
    ChatErrorOut,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SourceOut,
    ToolCallTraceOut,
)
from app.logging import request_id_var
from app.services.agent_service import AgentService

router = APIRouter()


def get_agent_service(request: Request) -> AgentService:
    return request.app.state.agent_service


@router.get("/health", response_model=HealthResponse)
def health(agent_service: AgentService = Depends(get_agent_service)) -> HealthResponse:
    reachable = agent_service.check_mcp_server_reachable(request_id_var.get())
    status = "UP" if reachable else "DOWN"
    return HealthResponse(status=status, dependencies={"mcp-server": status})


@router.post("/chat", response_model=ChatResponse)
def chat(chat_request: ChatRequest, agent_service: AgentService = Depends(get_agent_service)) -> ChatResponse:
    request_id = request_id_var.get()
    result = agent_service.chat(chat_request.message, request_id)
    return ChatResponse(
        answer=result.answer,
        provider=result.provider,
        model=result.model,
        tool_calls=[
            ToolCallTraceOut(tool=trace.tool, success=trace.success, latency_ms=trace.latency_ms)
            for trace in result.tool_calls
        ],
        sources=[SourceOut(card_id=source["cardId"], title=source["title"]) for source in result.sources],
        context_snippets=result.context_snippets,
        request_id=request_id,
        error=ChatErrorOut(**result.error) if result.error else None,
    )

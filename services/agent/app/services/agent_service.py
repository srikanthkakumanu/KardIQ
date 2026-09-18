from dataclasses import dataclass, field

from langchain_core.messages import HumanMessage, SystemMessage

from app.config import Settings
from app.errors import DownstreamError, LlmGuardrailError
from app.llm.guardrails import invoke_with_guardrails
from app.mcp.mcp_client import McpClient

SYSTEM_PROMPT_TEMPLATE = (
    "You are the Knowledge Card Assistant. Answer the user's question using ONLY the "
    "context below - it comes from the user's own knowledge cards and graph "
    "relationships. If the context does not contain enough information to answer, "
    "say so explicitly instead of guessing.\n\nContext:\n{context}"
)

NO_CONTEXT_ANSWER = (
    "I don't have enough grounded context to answer that yet. Try creating cards and "
    "graph relationships for the topics you're asking about."
)


@dataclass
class ToolCallTrace:
    tool: str
    success: bool
    latency_ms: float | None = None


@dataclass
class ChatResult:
    answer: str
    provider: str
    model: str
    tool_calls: list[ToolCallTrace] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)
    context_snippets: list[str] = field(default_factory=list)
    error: dict | None = None


class AgentService:
    """Deterministic teaching pipeline per services/agent/CLAUDE.md: discover
    tools -> retrieve graph/card context -> ask the LLM using that context
    (or say context is missing) -> return answer + trace. No unbounded
    autonomous loop."""

    def __init__(self, mcp_client: McpClient, chat_model, settings: Settings):
        self._mcp_client = mcp_client
        self._chat_model = chat_model
        self._settings = settings

    def check_mcp_server_reachable(self, request_id: str) -> bool:
        try:
            self._mcp_client.list_tools(request_id)
            return True
        except DownstreamError:
            return False

    def chat(self, message: str, request_id: str) -> ChatResult:
        tool_calls: list[ToolCallTrace] = []

        try:
            self._mcp_client.list_tools(request_id)
        except DownstreamError as exc:
            tool_calls.append(ToolCallTrace(tool="list_tools", success=False))
            return self._failure(tool_calls, {"code": exc.code, "message": exc.message})
        tool_calls.append(ToolCallTrace(tool="list_tools", success=True))

        try:
            search_response = self._mcp_client.call_tool("graph_search", {"query": message}, request_id)
        except DownstreamError as exc:
            tool_calls.append(ToolCallTrace(tool="graph_search", success=False))
            return self._failure(tool_calls, {"code": exc.code, "message": exc.message})

        downstream = search_response.get("downstream") or {}
        tool_success = bool(search_response.get("success"))
        tool_calls.append(
            ToolCallTrace(tool="graph_search", success=tool_success, latency_ms=downstream.get("latencyMs"))
        )

        if not tool_success:
            error = search_response.get("error") or {"code": "GRAPH_SEARCH_FAILED", "message": "graph_search failed"}
            return self._failure(tool_calls, error)

        result = search_response.get("result") or {}
        context_text = result.get("context_text") or ""
        matched_cards = result.get("matched_cards") or []
        sources = [{"cardId": card["id"], "title": card["title"]} for card in matched_cards]
        context_snippets = [context_text] if context_text else []

        if not context_text:
            return ChatResult(
                answer=NO_CONTEXT_ANSWER,
                provider=self._settings.llm_provider,
                model=self._model_name(),
                tool_calls=tool_calls,
                sources=sources,
                context_snippets=context_snippets,
            )

        try:
            answer = self._ask_llm(message, context_text)
        except LlmGuardrailError as exc:
            return self._failure(
                tool_calls, {"code": exc.code, "message": exc.message}, sources=sources,
                context_snippets=context_snippets,
            )

        return ChatResult(
            answer=answer,
            provider=self._settings.llm_provider,
            model=self._model_name(),
            tool_calls=tool_calls,
            sources=sources,
            context_snippets=context_snippets,
        )

    def _ask_llm(self, message: str, context_text: str) -> str:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT_TEMPLATE.format(context=context_text)),
            HumanMessage(content=message),
        ]
        response = invoke_with_guardrails(self._chat_model, messages, self._settings)
        return response.content

    def _model_name(self) -> str:
        return self._settings.openai_model if self._settings.llm_provider == "openai" else self._settings.groq_model

    def _failure(
        self, tool_calls: list[ToolCallTrace], error: dict, sources: list[dict] | None = None,
        context_snippets: list[str] | None = None,
    ) -> ChatResult:
        return ChatResult(
            answer="",
            provider=self._settings.llm_provider,
            model=self._model_name(),
            tool_calls=tool_calls,
            sources=sources or [],
            context_snippets=context_snippets or [],
            error=error,
        )

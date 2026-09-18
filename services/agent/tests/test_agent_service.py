from app.config import Settings
from app.errors import DownstreamError
from app.services.agent_service import AgentService


class FakeMcpClient:
    def __init__(self):
        self.tools_response = [{"name": "graph_search"}]
        self.call_responses: dict[str, dict] = {}
        self.raise_on_list_tools: Exception | None = None
        self.raise_on_call: dict[str, Exception] = {}

    def list_tools(self, request_id):
        if self.raise_on_list_tools:
            raise self.raise_on_list_tools
        return self.tools_response

    def call_tool(self, tool_name, arguments, request_id):
        if tool_name in self.raise_on_call:
            raise self.raise_on_call[tool_name]
        return self.call_responses[tool_name]


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeChatModel:
    def __init__(self, content="LangChain uses OpenAI as its LLM provider.", error=None):
        self._content = content
        self._error = error

    def invoke(self, messages):
        if self._error:
            raise self._error
        return FakeResponse(self._content)


def _settings(**overrides):
    return Settings(llm_provider="openai", openai_api_key="test-key", **overrides)


def _graph_search_success(context_text="LangChain USES OpenAI", matched_cards=None):
    return {
        "tool": "graph_search",
        "success": True,
        "result": {
            "matched_cards": matched_cards if matched_cards is not None else [{"id": "1", "title": "LangChain"}],
            "relationships": [],
            "context_text": context_text,
            "source_ids": [],
        },
        "downstream": {"service": "graph-rag", "latencyMs": 12.0},
    }


def test_chat_returns_grounded_answer_with_trace_and_sources():
    mcp_client = FakeMcpClient()
    mcp_client.call_responses["graph_search"] = _graph_search_success()
    agent = AgentService(mcp_client, FakeChatModel(), _settings())

    result = agent.chat("How does LangChain connect to OpenAI?", "req-1")

    assert result.answer == "LangChain uses OpenAI as its LLM provider."
    assert result.provider == "openai"
    assert result.model == "gpt-4o-mini"
    assert [t.tool for t in result.tool_calls] == ["list_tools", "graph_search"]
    assert all(t.success for t in result.tool_calls)
    assert result.sources == [{"cardId": "1", "title": "LangChain"}]
    assert result.context_snippets == ["LangChain USES OpenAI"]
    assert result.error is None


def test_chat_states_missing_context_instead_of_calling_the_llm():
    mcp_client = FakeMcpClient()
    mcp_client.call_responses["graph_search"] = _graph_search_success(context_text="", matched_cards=[])
    chat_model = FakeChatModel()
    agent = AgentService(mcp_client, chat_model, _settings())

    result = agent.chat("Tell me about something unrelated", "req-1")

    assert "don't have enough" in result.answer.lower()
    assert result.error is None


def test_chat_short_circuits_when_tool_discovery_fails():
    mcp_client = FakeMcpClient()
    mcp_client.raise_on_list_tools = DownstreamError("MCP_UNAVAILABLE", "down")
    agent = AgentService(mcp_client, FakeChatModel(), _settings())

    result = agent.chat("question", "req-1")

    assert result.error == {"code": "MCP_UNAVAILABLE", "message": "down"}
    assert [t.tool for t in result.tool_calls] == ["list_tools"]
    assert result.tool_calls[0].success is False


def test_chat_surfaces_mcp_downstream_error_from_graph_search():
    mcp_client = FakeMcpClient()
    mcp_client.raise_on_call["graph_search"] = DownstreamError("MCP_UNAVAILABLE", "down")
    agent = AgentService(mcp_client, FakeChatModel(), _settings())

    result = agent.chat("question", "req-1")

    assert result.error == {"code": "MCP_UNAVAILABLE", "message": "down"}
    assert result.tool_calls[-1].tool == "graph_search"
    assert result.tool_calls[-1].success is False


def test_chat_surfaces_tool_level_failure_from_graph_search():
    mcp_client = FakeMcpClient()
    mcp_client.call_responses["graph_search"] = {
        "tool": "graph_search",
        "success": False,
        "error": {"code": "NEO4J_UNAVAILABLE", "message": "graph db down"},
        "downstream": {"service": "graph-rag", "latencyMs": 5.0},
    }
    agent = AgentService(mcp_client, FakeChatModel(), _settings())

    result = agent.chat("question", "req-1")

    assert result.error == {"code": "NEO4J_UNAVAILABLE", "message": "graph db down"}
    assert result.tool_calls[-1].success is False


def test_chat_surfaces_llm_guardrail_error(monkeypatch):
    monkeypatch.setattr("app.llm.guardrails.time.sleep", lambda _s: None)
    mcp_client = FakeMcpClient()
    mcp_client.call_responses["graph_search"] = _graph_search_success()
    chat_model = FakeChatModel(error=Exception("boom"))
    agent = AgentService(mcp_client, chat_model, _settings())

    result = agent.chat("question", "req-1")

    assert result.error["code"] == "LLM_REQUEST_FAILED"
    assert result.answer == ""
    # context was already retrieved before the LLM call failed, so it's not lost from the trace
    assert result.sources == [{"cardId": "1", "title": "LangChain"}]


def test_check_mcp_server_reachable_reflects_downstream_health():
    mcp_client = FakeMcpClient()
    agent = AgentService(mcp_client, FakeChatModel(), _settings())
    assert agent.check_mcp_server_reachable("req-1") is True

    mcp_client.raise_on_list_tools = DownstreamError("MCP_UNAVAILABLE", "down")
    assert agent.check_mcp_server_reachable("req-1") is False

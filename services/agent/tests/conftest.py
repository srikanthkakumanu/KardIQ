import pytest
from fastapi.testclient import TestClient

from app.api.routes import get_agent_service
from app.main import app
from app.services.agent_service import ChatResult, ToolCallTrace


class FakeAgentService:
    def __init__(self):
        self.chat_result = ChatResult(
            answer="LangChain uses OpenAI.",
            provider="openai",
            model="gpt-4o-mini",
            tool_calls=[
                ToolCallTrace(tool="list_tools", success=True),
                ToolCallTrace(tool="graph_search", success=True, latency_ms=12.0),
            ],
            sources=[{"cardId": "1", "title": "LangChain"}],
            context_snippets=["LangChain USES OpenAI"],
        )
        self.reachable = True

    def chat(self, message: str, request_id: str) -> ChatResult:
        return self.chat_result

    def check_mcp_server_reachable(self, request_id: str) -> bool:
        return self.reachable


@pytest.fixture()
def fake_agent_service() -> FakeAgentService:
    return FakeAgentService()


@pytest.fixture()
def client(fake_agent_service: FakeAgentService):
    app.dependency_overrides[get_agent_service] = lambda: fake_agent_service
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

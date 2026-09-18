def test_health_returns_up_when_mcp_reachable(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP", "dependencies": {"mcp-server": "UP"}}


def test_health_returns_down_when_mcp_unreachable(client, fake_agent_service):
    fake_agent_service.reachable = False

    response = client.get("/health")

    assert response.json() == {"status": "DOWN", "dependencies": {"mcp-server": "DOWN"}}


def test_chat_returns_grounded_answer_with_trace_and_sources(client):
    response = client.post("/chat", json={"message": "How does LangChain connect to OpenAI?"})
    body = response.json()

    assert response.status_code == 200
    assert body["answer"] == "LangChain uses OpenAI."
    assert body["provider"] == "openai"
    assert body["model"] == "gpt-4o-mini"
    assert [t["tool"] for t in body["toolCalls"]] == ["list_tools", "graph_search"]
    assert body["sources"] == [{"cardId": "1", "title": "LangChain"}]
    assert body["contextSnippets"] == ["LangChain USES OpenAI"]
    assert body["error"] is None


def test_chat_rejects_blank_message(client):
    response = client.post("/chat", json={"message": ""})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_chat_rejects_missing_message_field(client):
    response = client.post("/chat", json={})

    assert response.status_code == 422


def test_chat_echoes_the_inbound_x_request_id(client):
    response = client.post("/chat", json={"message": "hi"}, headers={"X-Request-Id": "trace-1"})

    assert response.headers["x-request-id"] == "trace-1"
    assert response.json()["requestId"] == "trace-1"


def test_chat_surfaces_a_chat_level_error_when_present(client, fake_agent_service):
    fake_agent_service.chat_result.answer = ""
    fake_agent_service.chat_result.error = {"code": "MCP_UNAVAILABLE", "message": "down"}

    response = client.post("/chat", json={"message": "hi"})
    body = response.json()

    assert response.status_code == 200
    assert body["error"] == {"code": "MCP_UNAVAILABLE", "message": "down"}

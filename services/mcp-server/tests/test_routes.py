from app.errors import DownstreamError


def test_list_tools_returns_all_four_required_tools_with_schemas(client):
    response = client.get("/tools")

    assert response.status_code == 200
    tools = response.json()
    names = {tool["name"] for tool in tools}
    assert names == {"list_cards", "create_card", "graph_search", "health_report"}
    for tool in tools:
        assert tool["inputSchema"]["type"] == "object"
        assert tool["outputSchema"]["type"] == "object"


def test_call_unknown_tool_returns_404(client):
    response = client.post("/tools/does_not_exist/call", json={})

    assert response.status_code == 404


def test_call_list_cards_success_includes_downstream_trace(client, fake_clients):
    fake_clients.card_service.list_response = {
        "items": [{"id": "1", "title": "LangChain", "tags": []}],
        "page": 0,
        "size": 20,
        "totalElements": 1,
    }

    response = client.post("/tools/list_cards/call", json={})
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is True
    assert body["result"]["items"][0]["id"] == "1"
    assert body["downstream"]["service"] == "card-service"
    assert body["error"] is None


def test_call_tool_with_invalid_arguments_returns_success_false_with_structured_error(client):
    response = client.post("/tools/create_card/call", json={"title": ""})
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_ARGUMENTS"


def test_call_tool_maps_downstream_error_into_the_response_body(client, fake_clients):
    fake_clients.card_service.raise_error = DownstreamError("card-service", "DOWNSTREAM_UNAVAILABLE", "down", 503)

    response = client.post("/tools/list_cards/call", json={})
    body = response.json()

    assert response.status_code == 200
    assert body["success"] is False
    assert body["error"]["code"] == "DOWNSTREAM_UNAVAILABLE"
    assert body["downstream"]["status"] == 503


def test_call_tool_echoes_the_inbound_x_request_id(client):
    response = client.post(
        "/tools/list_cards/call", json={}, headers={"X-Request-Id": "regression-test-id"}
    )

    assert response.headers["x-request-id"] == "regression-test-id"
    assert response.json()["requestId"] == "regression-test-id"


def test_health_endpoint_aggregates_dependency_status(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP", "dependencies": {"card-service": "UP", "graph-rag": "UP"}}


def test_health_endpoint_reports_down_when_a_dependency_fails(client, fake_clients):
    fake_clients.graph_rag.raise_error = DownstreamError("graph-rag", "NEO4J_UNAVAILABLE", "down", 503)

    response = client.get("/health")

    assert response.json() == {"status": "DOWN", "dependencies": {"card-service": "UP", "graph-rag": "DOWN"}}

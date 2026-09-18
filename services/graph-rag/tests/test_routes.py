def test_health_returns_up_when_neo4j_reachable(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP", "dependencies": {"neo4j": "UP"}}


def test_rag_search_rejects_missing_query(client):
    response = client.post("/rag/search", json={})

    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_create_relation_returns_404_when_a_card_is_missing(client):
    response = client.post(
        "/graph/relations",
        json={"sourceId": "missing-1", "targetId": "missing-2", "label": "USES"},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "CARD_NOT_FOUND"


def test_error_responses_echo_the_inbound_x_request_id(client):
    response = client.post(
        "/graph/relations",
        json={"sourceId": "missing-1", "targetId": "missing-2", "label": "USES"},
        headers={"X-Request-Id": "regression-test-id"},
    )

    assert response.headers["x-request-id"] == "regression-test-id"
    assert response.json()["requestId"] == "regression-test-id"


def test_upsert_card_then_search_finds_it(client):
    create = client.post(
        "/graph/cards",
        json={
            "id": "1",
            "title": "LangChain",
            "body": "Framework for building LLM apps",
            "tags": ["framework"],
            "updatedAt": "2024-01-01T00:00:00Z",
        },
    )
    assert create.status_code == 200
    assert create.json() == {"id": "1", "upserted": True}

    search = client.post("/rag/search", json={"query": "LangChain"})

    assert search.status_code == 200
    body = search.json()
    assert body["matchedCards"][0]["id"] == "1"
    assert body["sourceIds"] == ["1"]


def test_full_flow_creates_relation_and_search_includes_it(client):
    client.post(
        "/graph/cards",
        json={"id": "1", "title": "LangChain", "body": "Framework", "tags": [], "updatedAt": "2024-01-01T00:00:00Z"},
    )
    client.post(
        "/graph/cards",
        json={"id": "2", "title": "OpenAI", "body": "LLM provider", "tags": [], "updatedAt": "2024-01-01T00:00:00Z"},
    )

    relation = client.post(
        "/graph/relations",
        json={"sourceId": "1", "targetId": "2", "label": "USES"},
    )
    assert relation.status_code == 200
    assert relation.json() == {"sourceId": "1", "targetId": "2", "label": "USES", "created": True}

    search = client.post("/rag/search", json={"query": "LangChain"})
    body = search.json()

    assert body["relationships"] == [{"sourceId": "1", "targetId": "2", "label": "USES"}]
    assert set(body["sourceIds"]) == {"1", "2"}
    assert "OpenAI" in body["contextText"]

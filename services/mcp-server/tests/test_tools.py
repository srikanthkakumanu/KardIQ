import pytest

from app.errors import DownstreamError
from app.tools import create_card as create_card_tool
from app.tools import graph_search as graph_search_tool
from app.tools import health_report as health_report_tool
from app.tools import list_cards as list_cards_tool
from app.tools.clients import Clients
from tests.fakes import FakeCardServiceClient, FakeGraphRagClient


@pytest.fixture()
def clients() -> Clients:
    return Clients(card_service=FakeCardServiceClient(), graph_rag=FakeGraphRagClient())


def test_list_cards_maps_card_service_response(clients):
    clients.card_service.list_response = {
        "items": [{"id": "1", "title": "LangChain", "tags": ["framework"]}],
        "page": 0,
        "size": 20,
        "totalElements": 1,
    }

    output = list_cards_tool.handle(list_cards_tool.ListCardsInput(), "req-1", clients)

    assert output.items[0].id == "1"
    assert output.total_elements == 1


def test_list_cards_propagates_downstream_error(clients):
    clients.card_service.raise_error = DownstreamError("card-service", "DOWNSTREAM_UNAVAILABLE", "down")

    with pytest.raises(DownstreamError):
        list_cards_tool.handle(list_cards_tool.ListCardsInput(), "req-1", clients)


def test_create_card_maps_response(clients):
    clients.card_service.create_response = {"id": "1", "title": "T", "body": "B", "tags": ["a"]}

    output = create_card_tool.handle(
        create_card_tool.CreateCardInput(title="T", body="B", tags=["a"]), "req-1", clients
    )

    assert output.id == "1"
    assert output.tags == ["a"]


def test_create_card_propagates_downstream_error(clients):
    clients.card_service.raise_error = DownstreamError("card-service", "VALIDATION_ERROR", "bad request", 400)

    with pytest.raises(DownstreamError):
        create_card_tool.handle(create_card_tool.CreateCardInput(title="T", body="B"), "req-1", clients)


def test_graph_search_maps_response_preserving_relationship_direction(clients):
    clients.graph_rag.search_response = {
        "matchedCards": [{"id": "1", "title": "LangChain", "tags": []}],
        "relationships": [{"sourceId": "1", "targetId": "2", "label": "USES"}],
        "contextText": "LangChain USES OpenAI",
        "sourceIds": ["1", "2"],
    }

    output = graph_search_tool.handle(graph_search_tool.GraphSearchInput(query="LangChain"), "req-1", clients)

    assert output.relationships[0].source_id == "1"
    assert output.relationships[0].target_id == "2"
    assert output.source_ids == ["1", "2"]


def test_graph_search_propagates_downstream_error(clients):
    clients.graph_rag.raise_error = DownstreamError("graph-rag", "NEO4J_UNAVAILABLE", "down", 503)

    with pytest.raises(DownstreamError):
        graph_search_tool.handle(graph_search_tool.GraphSearchInput(query="x"), "req-1", clients)


def test_health_report_reports_up_when_both_dependencies_healthy(clients):
    output = health_report_tool.handle(health_report_tool.HealthReportInput(), "req-1", clients)

    assert output.status == "UP"
    assert output.dependencies == {"card-service": "UP", "graph-rag": "UP"}


def test_health_report_reports_down_when_a_dependency_is_unreachable(clients):
    clients.card_service.raise_error = DownstreamError("card-service", "DOWNSTREAM_UNAVAILABLE", "down")

    output = health_report_tool.handle(health_report_tool.HealthReportInput(), "req-1", clients)

    assert output.status == "DOWN"
    assert output.dependencies == {"card-service": "DOWN", "graph-rag": "UP"}


def test_health_report_reports_down_when_a_dependency_reports_down_status(clients):
    clients.graph_rag.health_response = {"status": "DOWN"}

    output = health_report_tool.handle(health_report_tool.HealthReportInput(), "req-1", clients)

    assert output.status == "DOWN"
    assert output.dependencies["graph-rag"] == "DOWN"

import pytest
from fastapi.testclient import TestClient

from app.api.routes import get_clients
from app.main import app
from app.tools.clients import Clients
from tests.fakes import FakeCardServiceClient, FakeGraphRagClient


@pytest.fixture()
def fake_clients() -> Clients:
    return Clients(card_service=FakeCardServiceClient(), graph_rag=FakeGraphRagClient())


@pytest.fixture()
def client(fake_clients: Clients):
    app.dependency_overrides[get_clients] = lambda: fake_clients
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

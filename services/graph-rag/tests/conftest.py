import pytest
from fastapi.testclient import TestClient
from neo4j.exceptions import ServiceUnavailable

from app.api.routes import get_driver, get_repository
from app.main import app


class FakeDriver:
    def __init__(self, healthy: bool = True):
        self.healthy = healthy

    def verify_connectivity(self) -> None:
        if not self.healthy:
            raise ServiceUnavailable("down")


class FakeRepository:
    def __init__(self):
        self.cards: dict[str, object] = {}
        self.relationships: list[object] = []

    def upsert_card(self, card) -> None:
        self.cards[card.id] = card

    def card_exists(self, card_id: str) -> bool:
        return card_id in self.cards

    def upsert_relationship(self, relationship) -> None:
        self.relationships.append(relationship)

    def keyword_match(self, query: str, limit: int) -> list[dict]:
        needle = query.lower()
        matches = [
            {
                "id": card.id,
                "title": card.title,
                "tags": card.tags,
                "exact_match": card.title.lower() == needle,
            }
            for card in self.cards.values()
            if needle in card.title.lower() or needle in card.body.lower()
        ]
        return matches[:limit]

    def one_hop_expand(self, card_ids: list[str]) -> list[dict]:
        return [
            {
                "source_id": rel.source_id,
                "source_title": self.cards[rel.source_id].title,
                "target_id": rel.target_id,
                "target_title": self.cards[rel.target_id].title,
                "label": rel.label,
            }
            for rel in self.relationships
            if (rel.source_id in card_ids or rel.target_id in card_ids)
            and rel.source_id in self.cards
            and rel.target_id in self.cards
        ]


@pytest.fixture()
def repository() -> FakeRepository:
    return FakeRepository()


@pytest.fixture()
def client(repository: FakeRepository):
    app.dependency_overrides[get_driver] = lambda: FakeDriver()
    app.dependency_overrides[get_repository] = lambda: repository
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()

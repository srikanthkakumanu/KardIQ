from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.domain.models import CardNode, GraphRelationship


class CamelModel(BaseModel):
    """Base for every request/response schema so the JSON wire shape is
    camelCase (matching the Java card-service's naturally camelCase DTOs)
    while Python code stays snake_case."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CardNodeIn(CamelModel):
    id: str
    title: str
    body: str
    tags: list[str] = Field(default_factory=list)
    updated_at: str

    def to_domain(self) -> CardNode:
        return CardNode(id=self.id, title=self.title, body=self.body, tags=self.tags, updated_at=self.updated_at)


class CardUpsertResponse(CamelModel):
    id: str
    upserted: bool = True


class RelationIn(CamelModel):
    source_id: str
    target_id: str
    label: str
    weight: float | None = None

    def to_domain(self, created_at: str) -> GraphRelationship:
        return GraphRelationship(
            source_id=self.source_id,
            target_id=self.target_id,
            label=self.label,
            weight=self.weight,
            created_at=created_at,
        )


class RelationUpsertResponse(CamelModel):
    source_id: str
    target_id: str
    label: str
    created: bool = True


class RagSearchRequest(CamelModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=50)


class MatchedCard(CamelModel):
    id: str
    title: str
    tags: list[str] = Field(default_factory=list)


class MatchedRelationship(CamelModel):
    source_id: str
    target_id: str
    label: str


class RagSearchResponse(CamelModel):
    matched_cards: list[MatchedCard]
    relationships: list[MatchedRelationship]
    context_text: str
    source_ids: list[str]


class HealthResponse(CamelModel):
    status: str
    dependencies: dict[str, str]


class ErrorResponse(CamelModel):
    code: str
    message: str
    request_id: str
    timestamp: str

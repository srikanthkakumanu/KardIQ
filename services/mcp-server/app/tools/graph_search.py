from pydantic import BaseModel, Field

from app.tools.clients import Clients
from app.tools.registry import ToolSpec, register


class GraphSearchInput(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=50)


class MatchedCard(BaseModel):
    id: str
    title: str
    tags: list[str] = Field(default_factory=list)


class MatchedRelationship(BaseModel):
    source_id: str
    target_id: str
    label: str


class GraphSearchOutput(BaseModel):
    matched_cards: list[MatchedCard]
    relationships: list[MatchedRelationship]
    context_text: str
    source_ids: list[str]


def handle(input_data: GraphSearchInput, request_id: str, clients: Clients) -> GraphSearchOutput:
    result = clients.graph_rag.search(input_data.query, input_data.limit, request_id)
    return GraphSearchOutput(
        matched_cards=[MatchedCard(**card) for card in result["matchedCards"]],
        relationships=[
            MatchedRelationship(source_id=r["sourceId"], target_id=r["targetId"], label=r["label"])
            for r in result["relationships"]
        ],
        context_text=result["contextText"],
        source_ids=result["sourceIds"],
    )


register(
    ToolSpec(
        name="graph_search",
        description="Search graph context (matched cards and relationships) relevant to a question.",
        input_model=GraphSearchInput,
        output_model=GraphSearchOutput,
        primary_service="graph-rag",
        handler=handle,
    )
)

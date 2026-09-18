from pydantic import BaseModel, Field

from app.tools.clients import Clients
from app.tools.registry import ToolSpec, register


class ListCardsInput(BaseModel):
    page: int = Field(default=0, ge=0)
    size: int = Field(default=20, ge=1, le=100)


class CardSummary(BaseModel):
    id: str
    title: str
    tags: list[str] = Field(default_factory=list)


class ListCardsOutput(BaseModel):
    items: list[CardSummary]
    page: int
    size: int
    total_elements: int


def handle(input_data: ListCardsInput, request_id: str, clients: Clients) -> ListCardsOutput:
    result = clients.card_service.list_cards(input_data.page, input_data.size, request_id)
    items = [CardSummary(id=c["id"], title=c["title"], tags=c.get("tags", [])) for c in result["items"]]
    return ListCardsOutput(
        items=items, page=result["page"], size=result["size"], total_elements=result["totalElements"]
    )


register(
    ToolSpec(
        name="list_cards",
        description="List knowledge cards persisted in the card service.",
        input_model=ListCardsInput,
        output_model=ListCardsOutput,
        primary_service="card-service",
        handler=handle,
    )
)

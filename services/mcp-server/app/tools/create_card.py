from pydantic import BaseModel, Field

from app.tools.clients import Clients
from app.tools.registry import ToolSpec, register


class CreateCardInput(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(min_length=1, max_length=4000)
    tags: list[str] = Field(default_factory=list, max_length=8)


class CreateCardOutput(BaseModel):
    id: str
    title: str
    body: str
    tags: list[str]


def handle(input_data: CreateCardInput, request_id: str, clients: Clients) -> CreateCardOutput:
    result = clients.card_service.create_card(
        {"title": input_data.title, "body": input_data.body, "tags": input_data.tags}, request_id
    )
    return CreateCardOutput(id=result["id"], title=result["title"], body=result["body"], tags=result.get("tags", []))


register(
    ToolSpec(
        name="create_card",
        description="Create a new knowledge card through the card service.",
        input_model=CreateCardInput,
        output_model=CreateCardOutput,
        primary_service="card-service",
        handler=handle,
    )
)

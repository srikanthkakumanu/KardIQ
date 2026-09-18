from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ChatRequest(CamelModel):
    message: str = Field(min_length=1)
    session_id: str | None = None


class ToolCallTraceOut(CamelModel):
    tool: str
    success: bool
    latency_ms: float | None = None


class SourceOut(CamelModel):
    card_id: str
    title: str


class ChatErrorOut(CamelModel):
    code: str
    message: str


class ChatResponse(CamelModel):
    answer: str
    provider: str
    model: str
    tool_calls: list[ToolCallTraceOut]
    sources: list[SourceOut]
    context_snippets: list[str]
    request_id: str
    error: ChatErrorOut | None = None


class HealthResponse(CamelModel):
    status: str
    dependencies: dict[str, str]


class ErrorResponse(CamelModel):
    code: str
    message: str
    request_id: str

from pydantic import BaseModel

from app.tools.clients import Clients
from app.tools.registry import ToolSpec, register


class HealthReportInput(BaseModel):
    pass


class HealthReportOutput(BaseModel):
    status: str
    dependencies: dict[str, str]


def handle(input_data: HealthReportInput, request_id: str, clients: Clients) -> HealthReportOutput:
    dependencies = {
        "card-service": _status(lambda: clients.card_service.health(request_id)),
        "graph-rag": _status(lambda: clients.graph_rag.health(request_id)),
    }
    overall = "UP" if all(status == "UP" for status in dependencies.values()) else "DOWN"
    return HealthReportOutput(status=overall, dependencies=dependencies)


def _status(check) -> str:
    try:
        result = check()
    except Exception:
        return "DOWN"
    return "UP" if result.get("status") == "UP" else "DOWN"


register(
    ToolSpec(
        name="health_report",
        description="Report the health of downstream dependencies (card-service, graph-rag).",
        input_model=HealthReportInput,
        output_model=HealthReportOutput,
        primary_service="card-service+graph-rag",
        handler=handle,
    )
)

import time

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

from app.errors import DownstreamError
from app.logging import request_id_var
from app.tools import TOOL_REGISTRY
from app.tools.clients import Clients

router = APIRouter()


def get_clients(request: Request) -> Clients:
    return request.app.state.clients


@router.get("/health")
def health(clients: Clients = Depends(get_clients)) -> dict:
    request_id = request_id_var.get()
    dependencies = {
        "card-service": _dependency_status(lambda: clients.card_service.health(request_id)),
        "graph-rag": _dependency_status(lambda: clients.graph_rag.health(request_id)),
    }
    status = "UP" if all(value == "UP" for value in dependencies.values()) else "DOWN"
    return {"status": status, "dependencies": dependencies}


def _dependency_status(check) -> str:
    try:
        result = check()
    except Exception:
        return "DOWN"
    return "UP" if result.get("status") == "UP" else "DOWN"


@router.get("/tools")
def list_tools() -> list[dict]:
    return [
        {
            "name": spec.name,
            "description": spec.description,
            "inputSchema": spec.input_model.model_json_schema(),
            "outputSchema": spec.output_model.model_json_schema(),
        }
        for spec in TOOL_REGISTRY.values()
    ]


@router.post("/tools/{tool_name}/call")
def call_tool(tool_name: str, payload: dict, clients: Clients = Depends(get_clients)) -> dict:
    request_id = request_id_var.get()
    spec = TOOL_REGISTRY.get(tool_name)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")

    try:
        validated_input = spec.input_model.model_validate(payload)
    except ValidationError as exc:
        return _tool_response(
            tool_name,
            request_id,
            success=False,
            error={"code": "INVALID_ARGUMENTS", "message": _format_validation_error(exc)},
            downstream={"service": spec.primary_service, "latencyMs": 0},
        )

    start = time.monotonic()
    try:
        output = spec.handler(validated_input, request_id, clients)
    except DownstreamError as exc:
        return _tool_response(
            tool_name,
            request_id,
            success=False,
            error={"code": exc.code, "message": exc.message},
            downstream={"service": exc.service, "status": exc.status_code, "latencyMs": _elapsed_ms(start)},
        )

    return _tool_response(
        tool_name,
        request_id,
        success=True,
        result=output.model_dump(by_alias=True),
        downstream={"service": spec.primary_service, "latencyMs": _elapsed_ms(start)},
    )


def _tool_response(
    tool: str, request_id: str, *, success: bool, result: dict | None = None, error: dict | None = None,
    downstream: dict | None = None,
) -> dict:
    return {
        "tool": tool,
        "success": success,
        "result": result,
        "error": error,
        "downstream": downstream,
        "requestId": request_id,
    }


def _format_validation_error(exc: ValidationError) -> str:
    return "; ".join(f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors())


def _elapsed_ms(start: float) -> float:
    return round((time.monotonic() - start) * 1000, 1)

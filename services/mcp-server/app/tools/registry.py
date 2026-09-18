from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel

# The explicit, inspectable tool registry required by
# services/mcp-server/CLAUDE.md: every tool's name, description, and
# input/output schema is declared here rather than discovered dynamically.


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    primary_service: str
    handler: Callable[[BaseModel, str, object], BaseModel]


TOOL_REGISTRY: dict[str, ToolSpec] = {}


def register(spec: ToolSpec) -> None:
    TOOL_REGISTRY[spec.name] = spec

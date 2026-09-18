from dataclasses import dataclass, field


@dataclass
class CardNode:
    id: str
    title: str
    body: str
    tags: list[str] = field(default_factory=list)
    updated_at: str = ""


@dataclass
class GraphRelationship:
    source_id: str
    target_id: str
    label: str
    weight: float | None = None
    created_at: str | None = None

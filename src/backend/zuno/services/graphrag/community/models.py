from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class GraphCommunity:
    community_id: str
    knowledge_id: str
    level: int
    entities: list[str]
    relation_count: int
    supporting_chunks: list[str]
    relations: list[dict[str, Any]] = field(default_factory=list)
    report: str = ""
    community_version: str = "v0"
    status: str = "ready"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


__all__ = ["GraphCommunity"]

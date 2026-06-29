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

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "GraphCommunity":
        return cls(
            community_id=str(payload.get("community_id") or ""),
            knowledge_id=str(payload.get("knowledge_id") or ""),
            level=int(payload.get("level") or 0),
            entities=list(payload.get("entities") or []),
            relation_count=int(payload.get("relation_count") or 0),
            supporting_chunks=list(payload.get("supporting_chunks") or []),
            relations=list(payload.get("relations") or []),
            report=str(payload.get("report") or ""),
            community_version=str(payload.get("community_version") or "v0"),
            status=str(payload.get("status") or "ready"),
        )


__all__ = ["GraphCommunity"]

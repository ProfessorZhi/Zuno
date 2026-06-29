from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GraphRAGVersionState:
    index_version: str = "v1"
    community_version: str = "v0"
    document_hash: str | None = None
    chunk_hash: str | None = None
    status: str = "active"

    def to_trace(self) -> dict[str, str | None]:
        return {
            "index_version": self.index_version,
            "community_version": self.community_version,
            "document_hash": self.document_hash,
            "chunk_hash": self.chunk_hash,
            "status": self.status,
        }


def detect_stale_index_reasons(
    *,
    index_health: dict,
    scope_policy: dict,
) -> list[str]:
    reasons: list[str] = []
    for name, status in sorted((index_health or {}).items()):
        normalized = str(status or "").strip().lower()
        if normalized in {"stale", "failed", "unavailable"}:
            reasons.append(f"{name} index health is {normalized}")

    knowledge_status = str((scope_policy or {}).get("status") or "active").strip().lower()
    if knowledge_status != "active":
        reasons.append(f"knowledge status is {knowledge_status}")
    return reasons


__all__ = ["GraphRAGVersionState", "detect_stale_index_reasons"]

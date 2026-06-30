from typing import Literal

from pydantic import BaseModel, Field


class GraphRAGProjectContract(BaseModel):
    graphrag_project_id: str = Field(min_length=1, max_length=64)
    settings_path: str | None = Field(default=None, min_length=1, max_length=512)
    prompt_version: str = Field(default="default", min_length=1, max_length=128)
    index_version: str = Field(default="v1", min_length=1, max_length=64)
    query_method: Literal["auto", "basic", "local", "global", "drift"] = "auto"
    query_prompt_version: str = Field(default="default", min_length=1, max_length=128)
    community_version: str = Field(default="v0", min_length=1, max_length=64)
    document_hash: str | None = Field(default=None, min_length=1, max_length=128)
    chunk_hash: str | None = Field(default=None, min_length=1, max_length=128)
    status: Literal["not_configured", "ready", "stale", "failed", "disabled"] = "not_configured"


RETRIEVAL_MODES = {
    "default",
    "rag",
    "standard_retrieval",
    "normal",
    "graphrag",
    "hybrid",
    "hybrid_rag",
    "rag_graph",
    "rag_graph_deep",
    "enhanced_retrieval",
    "enhanced",
    "local_graphrag",
    "community_global",
    "drift_like",
    "auto",
}


def normalize_retrieval_mode(mode: str | None) -> str:
    normalized = (mode or "auto").strip().lower()
    if normalized not in RETRIEVAL_MODES:
        return "auto"
    if normalized == "rag_graph":
        return "rag_graph_deep"
    if normalized == "standard_retrieval":
        return "rag"
    if normalized == "normal":
        return "rag"
    if normalized == "enhanced_retrieval":
        return "rag_graph_deep"
    if normalized == "enhanced":
        return "rag_graph_deep"
    if normalized == "hybrid":
        return "hybrid_rag"
    if normalized == "graphrag":
        return "local_graphrag"
    if normalized == "default":
        return "auto"
    return normalized


__all__ = [
    "GraphRAGProjectContract",
    "RETRIEVAL_MODES",
    "normalize_retrieval_mode",
]

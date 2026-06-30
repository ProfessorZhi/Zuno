from typing import Any, Literal

from pydantic import BaseModel, Field


class GraphRAGExtractorConfig(BaseModel):
    requested_mode: str = "llm"
    resolved_mode: Literal["llm", "rule", "structured", "fixture"] = "llm"
    fallback_mode: str | None = "rule"
    model_ref: str | None = None
    prompt_ref: str | None = None
    schema_version: str = "default"
    cost_latency_profile: str = "balanced"
    eval_profile: str | None = None
    llm_first: bool = True

    @classmethod
    def from_knowledge_config(
        cls,
        *,
        graph_index_settings: dict[str, Any] | None = None,
        model_refs: dict[str, Any] | None = None,
        prompt_refs: dict[str, Any] | None = None,
        schema_refs: dict[str, Any] | None = None,
        policy_refs: dict[str, Any] | None = None,
        eval_refs: dict[str, Any] | None = None,
    ) -> "GraphRAGExtractorConfig":
        graph_settings = dict(graph_index_settings or {})
        model_refs = dict(model_refs or {})
        prompt_refs = dict(prompt_refs or {})
        schema_refs = dict(schema_refs or {})
        policy_refs = dict(policy_refs or {})
        eval_refs = dict(eval_refs or {})
        requested_mode = str(graph_settings.get("entity_extraction_mode") or "llm").strip().lower()
        mode_aliases = {
            "rule_llm": "llm",
            "llm_rule": "llm",
            "mock": "fixture",
            "regex": "rule",
        }
        resolved_mode = mode_aliases.get(requested_mode, requested_mode)
        if resolved_mode not in {"llm", "rule", "structured", "fixture"}:
            resolved_mode = "llm"
        fallback_mode = graph_settings.get("entity_extraction_fallback_mode")
        if fallback_mode is None and resolved_mode == "llm":
            fallback_mode = "rule"
        return cls(
            requested_mode=requested_mode,
            resolved_mode=resolved_mode,
            fallback_mode=str(fallback_mode) if fallback_mode else None,
            model_ref=(
                graph_settings.get("entity_extraction_llm_id")
                or model_refs.get("entity_extraction_llm_id")
                or model_refs.get("graph_extraction_llm_id")
            ),
            prompt_ref=(
                graph_settings.get("entity_extraction_prompt_id")
                or prompt_refs.get("entity_extraction_prompt_id")
                or prompt_refs.get("extract_graph")
            ),
            schema_version=str(
                graph_settings.get("entity_extraction_schema_version")
                or schema_refs.get("entity_extraction_schema_version")
                or schema_refs.get("graph_schema_version")
                or "default"
            ),
            cost_latency_profile=str(
                graph_settings.get("entity_extraction_cost_latency_profile")
                or policy_refs.get("entity_extraction_cost_latency_profile")
                or "balanced"
            ),
            eval_profile=(
                graph_settings.get("entity_extraction_eval_profile")
                or eval_refs.get("entity_extraction_eval_profile")
            ),
            llm_first=resolved_mode == "llm",
        )

    def to_trace(self) -> dict[str, Any]:
        return self.model_dump()


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
    "GraphRAGExtractorConfig",
    "GraphRAGProjectContract",
    "RETRIEVAL_MODES",
    "normalize_retrieval_mode",
]

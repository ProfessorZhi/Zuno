from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class QueryStrategy(StrEnum):
    DIRECT = "direct"
    REWRITE = "rewrite"
    MULTI_QUERY = "multi_query"
    STEP_BACK = "step_back"
    HYDE = "hyde"
    ENTITY_DECOMPOSITION = "entity_decomposition"
    RELATION_QUERY = "relation_query"


class RetrievalQualityVerdict(StrEnum):
    RELEVANT = "relevant"
    AMBIGUOUS = "ambiguous"
    IRRELEVANT = "irrelevant"
    CONFLICTING = "conflicting"
    INSUFFICIENT_SPAN = "insufficient_span"


class CorrectiveAction(StrEnum):
    CONTINUE = "continue"
    QUERY_REWRITE = "query_rewrite"
    MULTI_QUERY = "multi_query"
    STEP_BACK = "step_back"
    HYDE = "hyde"
    PARENT_EXPAND = "parent_expand"
    GRAPH_EXPAND = "graph_expand"
    FOCUSED_CITATION_RETRIEVE = "focused_citation_retrieve"
    USE_EXTERNAL_TOOL = "use_external_tool"
    ASK_USER = "ask_user"
    ABSTAIN = "abstain"


class EvidenceLedgerRecord(BaseModel):
    evidence_id: str
    document_id: str
    document_version: str = ""
    source_span: dict[str, Any] = Field(default_factory=dict)
    retrieval_round: int
    query_id: str
    query_strategy: QueryStrategy
    retriever: str
    raw_score: float = 0.0
    fusion_score: float = 0.0
    rerank_score: float = 0.0
    graph_path: list[str] = Field(default_factory=list)
    selection_reason: str = ""
    claim_refs: list[str] = Field(default_factory=list)
    contradiction_group: str = ""
    freshness_version: str = ""
    trace_span: str = ""
    text_hash: str = ""
    text: str = ""
    strict_citation_allowed: bool = True


__all__ = [
    "CorrectiveAction",
    "EvidenceLedgerRecord",
    "QueryStrategy",
    "RetrievalQualityVerdict",
]

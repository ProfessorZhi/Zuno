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


class KnowledgeRetrievalGraphNode(StrEnum):
    VALIDATE = "validate"
    PIN_SNAPSHOT = "pin_snapshot"
    SCOPE = "scope"
    INTERPRET = "interpret"
    SELECT_PROFILE = "select_profile"
    PLAN_ROUND = "plan_round"
    ADMIT = "admit"
    DISPATCH = "dispatch"
    NORMALIZE = "normalize"
    FUSE_RERANK = "fuse_rerank"
    EVIDENCE_LEDGER = "evidence_ledger"
    EVALUATE = "evaluate"
    CORRECTIVE_DECISION = "corrective_decision"


class KnowledgeRetrievalProfile(StrEnum):
    STANDARD = "standard"
    LOCAL = "local"
    GLOBAL = "global"
    DRIFT = "drift"
    DEEP = "deep"
    AGENTIC = "agentic"


class KnowledgeControlProposalType(StrEnum):
    ACCEPT_EVIDENCE = "accept_evidence"
    CORRECTIVE_RETRIEVAL = "corrective_retrieval"
    REQUEST_AGENT_REPLAN = "request_agent_replan"
    REQUEST_USER_CLARIFICATION = "request_user_clarification"
    REQUEST_EXTERNAL_TOOL = "request_external_tool"
    ABSTAIN = "abstain"


class RetrieverKind(StrEnum):
    BM25 = "bm25"
    VECTOR = "vector"
    ENTITY = "entity"
    RELATION = "relation"
    PATH = "path"
    COMMUNITY = "community"


class RetrieverAttemptStatus(StrEnum):
    SUCCEEDED = "succeeded"
    TIMEOUT = "timeout"
    INDEX_UNAVAILABLE = "index_unavailable"
    BUDGET_EXHAUSTED = "budget_exhausted"
    LATE_RESULT_FENCED = "late_result_fenced"


class EvidenceLedgerRecord(BaseModel):
    evidence_id: str
    document_id: str
    chunk_id: str = ""
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


class EvidenceCoverageSummary(BaseModel):
    claim_count: int = 0
    covered_claim_count: int = 0
    strict_citation_count: int = 0
    authority_count: int = 0
    temporal_version_count: int = 0
    conflict_group_count: int = 0
    coverage_ratio: float = 0.0
    strict_citation_ratio: float = 0.0


class EvidenceFrontier(BaseModel):
    total_records: int = 0
    newest_round: int = 0
    novelty: float = 0.0
    uncovered_claim_refs: list[str] = Field(default_factory=list)
    missing_strict_citation_ids: list[str] = Field(default_factory=list)
    conflict_groups: dict[str, list[str]] = Field(default_factory=dict)
    authority_refs: list[str] = Field(default_factory=list)
    temporal_versions: list[str] = Field(default_factory=list)
    stop_reasons: list[str] = Field(default_factory=list)
    coverage: EvidenceCoverageSummary = Field(default_factory=EvidenceCoverageSummary)


class RetrieverDispatchPlan(BaseModel):
    retriever: RetrieverKind
    knowledge_space_ids: list[str] = Field(default_factory=list)
    budget_tokens: int = 0
    timeout_ms: int = 0
    parallel_group: str = ""


class RetrievalPlan(BaseModel):
    round: int
    query: str
    query_strategy: QueryStrategy
    profile: KnowledgeRetrievalProfile
    retrievers: list[RetrieverDispatchPlan] = Field(default_factory=list)
    round_budget_tokens: int = 0
    deadline_ms: int = 0
    admitted: bool = True
    admission_reason: str = "admitted"


class RetrieverAttemptResult(BaseModel):
    retriever: RetrieverKind
    status: RetrieverAttemptStatus
    candidate_count: int = 0
    failure_reason: str = ""
    late_result: bool = False
    accepted: bool = True
    round: int
    parallel_group: str = ""


class KnowledgeRetrievalGraphNodeEvent(BaseModel):
    node: KnowledgeRetrievalGraphNode
    status: str = "completed"
    round: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class KnowledgeControlProposal(BaseModel):
    proposal_type: KnowledgeControlProposalType
    final_action: CorrectiveAction
    reason: str
    requires_agent_core_decision: bool = True
    accepted_by_knowledge: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)


class KnowledgeRetrievalGraphTrace(BaseModel):
    fixed_graph: list[KnowledgeRetrievalGraphNode] = Field(
        default_factory=lambda: list(KnowledgeRetrievalGraphNode)
    )
    profile: KnowledgeRetrievalProfile = KnowledgeRetrievalProfile.STANDARD
    requested_profile: str = "standard"
    snapshot_id: str | None = None
    node_events: list[KnowledgeRetrievalGraphNodeEvent] = Field(default_factory=list)
    proposal: KnowledgeControlProposal | None = None

    def add(
        self,
        node: KnowledgeRetrievalGraphNode,
        *,
        status: str = "completed",
        round: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.node_events.append(
            KnowledgeRetrievalGraphNodeEvent(
                node=node,
                status=status,
                round=round,
                payload=payload or {},
            )
        )

    def node_sequence(self) -> list[str]:
        return [event.node.value for event in self.node_events]


__all__ = [
    "CorrectiveAction",
    "EvidenceCoverageSummary",
    "EvidenceFrontier",
    "EvidenceLedgerRecord",
    "KnowledgeControlProposal",
    "KnowledgeControlProposalType",
    "KnowledgeRetrievalGraphNode",
    "KnowledgeRetrievalGraphNodeEvent",
    "KnowledgeRetrievalGraphTrace",
    "KnowledgeRetrievalProfile",
    "QueryStrategy",
    "RetrievalPlan",
    "RetrievalQualityVerdict",
    "RetrieverAttemptResult",
    "RetrieverAttemptStatus",
    "RetrieverDispatchPlan",
    "RetrieverKind",
]

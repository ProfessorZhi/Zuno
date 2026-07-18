from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from typing import Any


def _hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class KnowledgeVersionState(StrEnum):
    BUILDING = "BUILDING"
    VERIFIED = "VERIFIED"
    ACCEPTED = "ACCEPTED"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class RetrievalRoundStatus(StrEnum):
    PLANNED = "PLANNED"
    RUNNING = "RUNNING"
    REDUCED = "REDUCED"
    SUFFICIENT = "SUFFICIENT"
    NO_PROGRESS = "NO_PROGRESS"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True, slots=True)
class KnowledgeQueryRequest:
    request_ref: str
    agent_core_decision_ref: str
    evidence_requirement_refs: tuple[str, ...]
    snapshot_ref: str
    security_filter_ref: str
    budget_ref: str


@dataclass(frozen=True, slots=True)
class KnowledgeVersionRecord:
    version_ref: str
    state: KnowledgeVersionState
    source_span_manifest_hash: str
    document_version_ref: str
    security_metadata_ref: str
    index_manifest_hash: str
    visibility_receipt_ref: str
    accepted: bool


@dataclass(frozen=True, slots=True)
class RetrievalPlanRecord:
    plan_ref: str
    fixed_graph_ref: str
    dynamic_round_refs: tuple[str, ...]
    retriever_refs: tuple[str, ...]
    idempotent_reducer_ref: str


@dataclass(frozen=True, slots=True)
class RetrievalRoundRecord:
    round_ref: str
    status: RetrievalRoundStatus
    snapshot_ref: str
    security_filter_ref: str
    result_hash: str
    deadline_ref: str
    generation: int


@dataclass(frozen=True, slots=True)
class EvidenceRequirementRecord:
    requirement_ref: str
    evidence_goal: str
    unresolved_hops: tuple[str, ...]
    citation_fix_target_ref: str | None


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    evidence_ref: str
    requirement_ref: str
    source_span_ref: str
    document_version_ref: str
    content_hash: str
    strict_citation_eligible: bool
    tainted: bool


@dataclass(frozen=True, slots=True)
class EvidenceLedgerRecord:
    ledger_ref: str
    evidence_refs: tuple[str, ...]
    frontier_ref: str
    append_only_generation: int
    deduplicated: bool


@dataclass(frozen=True, slots=True)
class FusionDecision:
    fusion_ref: str
    normalized_score_ref: str
    rrf_version_ref: str
    rerank_candidate_count: int
    model_slot_ref: str


@dataclass(frozen=True, slots=True)
class GraphEvidenceDecision:
    graph_ref: str
    graph_capability_available: bool
    source_span_backlink_ref: str
    auxiliary_only_without_source_span: bool
    reason_code: str


@dataclass(frozen=True, slots=True)
class EvidenceQualityDecision:
    quality_ref: str
    authority_policy_ref: str
    temporal_policy_ref: str
    conflict_refs: tuple[str, ...]
    citation_eligible: bool


@dataclass(frozen=True, slots=True)
class CorrectiveRetrievalDecision:
    corrective_ref: str
    gap_ref: str
    next_action_ref: str
    retry_kind: str
    replan_required: bool


@dataclass(frozen=True, slots=True)
class StopBudgetDecision:
    decision_ref: str
    sufficient: bool
    no_progress: bool
    budget_reserved: int
    budget_settled: int
    overrun: bool


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    recovery_ref: str
    cancellation_signal_ref: str
    late_result_rejected: bool
    domain_commit_ref: str
    checkpoint_ref: str
    reconciled: bool


@dataclass(frozen=True, slots=True)
class DeletionPropagationRecord:
    delete_ref: str
    revoked_evidence_refs: tuple[str, ...]
    retrieval_paths_blocked: bool
    taint_propagated: bool


@dataclass(frozen=True, slots=True)
class KnowledgeEventRecord:
    event_ref: str
    event_type: str
    schema_version: str
    payload_hash: str
    redacted: bool


@dataclass(frozen=True, slots=True)
class EvalReleaseDecision:
    eval_ref: str
    pinned_profile_ref: str
    case_set_ref: str
    measured: bool
    comparable: bool
    release_gate_passed: bool


@dataclass(frozen=True, slots=True)
class ConfigSeparationRecord:
    config_ref: str
    intent_ref: str
    spec_ref: str
    projection_api_ref: str
    config_owns_runtime_fact: bool


@dataclass(frozen=True, slots=True)
class KnowledgeReadinessEvidence:
    requirement_ids: tuple[str, ...]
    code_refs: tuple[str, ...]
    test_refs: tuple[str, ...]
    verifier_ref: str
    evidence_ref: str
    implementation_available: bool


class KnowledgeRuntimeBatch:
    requirement_ids = tuple(f"ARCH-KNOW-{index:03d}" for index in range(1, 31))

    def query_request(self, *, request_ref: str, agent_core_decision_ref: str, evidence_requirement_refs: tuple[str, ...], snapshot_ref: str, security_filter_ref: str, budget_ref: str) -> KnowledgeQueryRequest:
        return KnowledgeQueryRequest(request_ref, agent_core_decision_ref, evidence_requirement_refs, snapshot_ref, security_filter_ref, budget_ref)

    def knowledge_version(self, *, version_ref: str, state: KnowledgeVersionState, source_span_manifest: dict[str, Any], document_version_ref: str, security_metadata_ref: str, index_manifest: dict[str, Any], visibility_receipt_ref: str) -> KnowledgeVersionRecord:
        accepted = state in {KnowledgeVersionState.ACCEPTED, KnowledgeVersionState.ACTIVE} and bool(source_span_manifest and document_version_ref and security_metadata_ref and visibility_receipt_ref)
        return KnowledgeVersionRecord(version_ref, state, _hash(source_span_manifest), document_version_ref, security_metadata_ref, _hash(index_manifest), visibility_receipt_ref, accepted)

    def retrieval_plan(self, *, plan_ref: str, dynamic_round_refs: tuple[str, ...], retriever_refs: tuple[str, ...]) -> RetrievalPlanRecord:
        return RetrievalPlanRecord(plan_ref, fixed_graph_ref="knowledge-retrieval-graph:v1", dynamic_round_refs=dynamic_round_refs, retriever_refs=retriever_refs, idempotent_reducer_ref="reducer:idempotent-rrf")

    def retrieval_round(self, *, round_ref: str, status: RetrievalRoundStatus, snapshot_ref: str, security_filter_ref: str, results: tuple[dict[str, Any], ...], deadline_ref: str, generation: int) -> RetrievalRoundRecord:
        return RetrievalRoundRecord(round_ref, status, snapshot_ref, security_filter_ref, _hash(results), deadline_ref, generation)

    def evidence_requirement(self, *, requirement_ref: str, evidence_goal: str, unresolved_hops: tuple[str, ...], citation_fix_target_ref: str | None = None) -> EvidenceRequirementRecord:
        return EvidenceRequirementRecord(requirement_ref, evidence_goal, unresolved_hops, citation_fix_target_ref)

    def evidence_record(self, *, evidence_ref: str, requirement_ref: str, source_span_ref: str, document_version_ref: str, content: dict[str, Any], strict: bool, tainted: bool = False) -> EvidenceRecord:
        return EvidenceRecord(evidence_ref, requirement_ref, source_span_ref, document_version_ref, _hash(content), strict_citation_eligible=bool(strict and source_span_ref and document_version_ref), tainted=tainted)

    def evidence_ledger(self, *, ledger_ref: str, evidence_refs: tuple[str, ...], frontier_ref: str, generation: int) -> EvidenceLedgerRecord:
        return EvidenceLedgerRecord(ledger_ref, tuple(dict.fromkeys(evidence_refs)), frontier_ref, generation, deduplicated=len(set(evidence_refs)) == len(tuple(dict.fromkeys(evidence_refs))))

    def fusion(self, *, fusion_ref: str, rerank_candidate_count: int) -> FusionDecision:
        return FusionDecision(fusion_ref, normalized_score_ref="score:normalized", rrf_version_ref="rrf:v1", rerank_candidate_count=rerank_candidate_count, model_slot_ref="model-slot:rerank")

    def graph_evidence(self, *, graph_ref: str, graph_capability_available: bool, source_span_backlink_ref: str | None, reason_code: str) -> GraphEvidenceDecision:
        return GraphEvidenceDecision(graph_ref, graph_capability_available, source_span_backlink_ref or "", auxiliary_only_without_source_span=not bool(source_span_backlink_ref), reason_code=reason_code)

    def quality(self, *, quality_ref: str, conflict_refs: tuple[str, ...], citation_eligible: bool) -> EvidenceQualityDecision:
        return EvidenceQualityDecision(quality_ref, authority_policy_ref="authority-policy:v1", temporal_policy_ref="temporal-policy:v1", conflict_refs=conflict_refs, citation_eligible=citation_eligible)

    def corrective(self, *, corrective_ref: str, gap_ref: str, retry_kind: str) -> CorrectiveRetrievalDecision:
        return CorrectiveRetrievalDecision(corrective_ref, gap_ref, next_action_ref=f"next-action:{gap_ref}", retry_kind=retry_kind, replan_required=retry_kind == "replan")

    def stop_budget(self, *, decision_ref: str, sufficient: bool, no_progress: bool, budget_reserved: int, budget_settled: int) -> StopBudgetDecision:
        return StopBudgetDecision(decision_ref, sufficient, no_progress, budget_reserved, budget_settled, overrun=budget_settled > budget_reserved)

    def recovery(self, *, recovery_ref: str, cancellation_signal_ref: str, domain_commit_ref: str, checkpoint_ref: str) -> RecoveryDecision:
        return RecoveryDecision(recovery_ref, cancellation_signal_ref, late_result_rejected=True, domain_commit_ref=domain_commit_ref, checkpoint_ref=checkpoint_ref, reconciled=domain_commit_ref != checkpoint_ref)

    def deletion_propagation(self, *, delete_ref: str, revoked_evidence_refs: tuple[str, ...]) -> DeletionPropagationRecord:
        return DeletionPropagationRecord(delete_ref, revoked_evidence_refs, retrieval_paths_blocked=bool(revoked_evidence_refs), taint_propagated=True)

    def event(self, *, event_ref: str, event_type: str, payload: dict[str, Any]) -> KnowledgeEventRecord:
        return KnowledgeEventRecord(event_ref, event_type, schema_version="knowledge.event.v1", payload_hash=_hash(payload), redacted=True)

    def eval_release(self, *, eval_ref: str, pinned_profile_ref: str, case_set_ref: str, measured: bool, comparable: bool) -> EvalReleaseDecision:
        return EvalReleaseDecision(eval_ref, pinned_profile_ref, case_set_ref, measured, comparable, release_gate_passed=measured and comparable)

    def config_separation(self, *, config_ref: str, intent_ref: str, spec_ref: str, projection_api_ref: str) -> ConfigSeparationRecord:
        return ConfigSeparationRecord(config_ref, intent_ref, spec_ref, projection_api_ref, config_owns_runtime_fact=False)

    def readiness_evidence(self, *, code_refs: tuple[str, ...], test_refs: tuple[str, ...], verifier_ref: str, evidence_ref: str) -> KnowledgeReadinessEvidence:
        return KnowledgeReadinessEvidence(self.requirement_ids, code_refs, test_refs, verifier_ref, evidence_ref, bool(code_refs and test_refs and verifier_ref and evidence_ref and len(self.requirement_ids) == 30))


__all__ = [
    "ConfigSeparationRecord",
    "CorrectiveRetrievalDecision",
    "DeletionPropagationRecord",
    "EvalReleaseDecision",
    "EvidenceLedgerRecord",
    "EvidenceQualityDecision",
    "EvidenceRecord",
    "EvidenceRequirementRecord",
    "FusionDecision",
    "GraphEvidenceDecision",
    "KnowledgeEventRecord",
    "KnowledgeQueryRequest",
    "KnowledgeReadinessEvidence",
    "KnowledgeRuntimeBatch",
    "KnowledgeVersionRecord",
    "KnowledgeVersionState",
    "RecoveryDecision",
    "RetrievalPlanRecord",
    "RetrievalRoundRecord",
    "RetrievalRoundStatus",
    "StopBudgetDecision",
]

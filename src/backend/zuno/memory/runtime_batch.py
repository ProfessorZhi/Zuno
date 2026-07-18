from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from typing import Any


def _hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class LongTermMemoryKind(StrEnum):
    EPISODIC = "EPISODIC"
    SEMANTIC = "SEMANTIC"
    PROCEDURAL = "PROCEDURAL"


class CandidateStatus(StrEnum):
    PROPOSED = "PROPOSED"
    VERIFIED = "VERIFIED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    ACTIVATED = "ACTIVATED"
    SUSPENDED = "SUSPENDED"
    RECONCILING = "RECONCILING"


class VersionStatus(StrEnum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    SUPERSEDED = "SUPERSEDED"


class CompressionLevel(StrEnum):
    C0_RAW = "C0_RAW"
    C1_EXTRACTIVE = "C1_EXTRACTIVE"
    C2_ABSTRACTIVE = "C2_ABSTRACTIVE"
    C3_STRATEGIC = "C3_STRATEGIC"


@dataclass(frozen=True, slots=True)
class MemoryLifecycleRecord:
    working_owner: str
    session_summary_ref: str
    long_term_kinds: tuple[LongTermMemoryKind, ...]
    projection_kinds: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MemoryCandidateRecord:
    candidate_ref: str
    source_fact_ref: str
    kind: LongTermMemoryKind
    status: CandidateStatus
    governance_required: bool
    model_is_fact_owner: bool


@dataclass(frozen=True, slots=True)
class MemoryVersionRecord:
    version_ref: str
    candidate_ref: str
    generation: int
    source_hash: str
    status: VersionStatus
    immutable_hash: str


@dataclass(frozen=True, slots=True)
class SessionSummaryRecord:
    summary_ref: str
    source_message_hashes: tuple[str, ...]
    coverage_ratio: float
    raw_message_ref: str
    incremental_generation: int


@dataclass(frozen=True, slots=True)
class ContextPackVersion:
    context_pack_ref: str
    generation: int
    candidate_refs: tuple[str, ...]
    compression_trace_ref: str
    budget_trace_ref: str
    token_count: int
    immutable_hash: str
    read_view: bool


@dataclass(frozen=True, slots=True)
class RetrievalGateRecord:
    retrieval_ref: str
    memory_kind: LongTermMemoryKind
    scope_ref: str
    acl_decision_ref: str
    security_before_summary: bool
    allowed: bool


@dataclass(frozen=True, slots=True)
class CompressionDecision:
    compression_ref: str
    level: CompressionLevel
    fidelity_level: str
    tool_payload_first: bool
    protected_set_refs: tuple[str, ...]
    deterministic_budget: bool
    exact_token_validation: bool


@dataclass(frozen=True, slots=True)
class RehydrationRecord:
    rehydration_ref: str
    context_pack_ref: str
    object_refs: tuple[str, ...]
    summary_is_only_source: bool


@dataclass(frozen=True, slots=True)
class ReflexionGovernanceRecord:
    reflexion_ref: str
    default_kind: LongTermMemoryKind
    procedural_promotion_evidence_refs: tuple[str, ...]
    procedural_is_strategy_hint: bool


@dataclass(frozen=True, slots=True)
class ConsolidationRecord:
    consolidation_ref: str
    source_refs: tuple[str, ...]
    delete_source: bool
    utility_projection_ref: str
    fact_ref: str
    negative_transfer_suspended: bool


@dataclass(frozen=True, slots=True)
class FreshnessRecord:
    freshness_ref: str
    effective_time_ref: str
    observed_time_ref: str
    verified_before_use: bool


@dataclass(frozen=True, slots=True)
class ConflictRecord:
    conflict_ref: str
    competing_version_refs: tuple[str, ...]
    silent_overwrite_allowed: bool
    resolution_ref: str


@dataclass(frozen=True, slots=True)
class StateMachineRecord:
    machine_ref: str
    legal_statuses: tuple[str, ...]
    closed: bool


@dataclass(frozen=True, slots=True)
class ProjectionPublicationRecord:
    publication_ref: str
    domain_commit_ref: str
    projection_ref: str
    index_receipt_ref: str
    index_is_active: bool
    order_valid: bool


@dataclass(frozen=True, slots=True)
class CommitRecoveryRecord:
    commit_ref: str
    idempotency_key: str
    checkpoint_ref: str
    domain_commit_ref: str
    generation: int
    cas_passed: bool
    unknown_requires_reconcile: bool


@dataclass(frozen=True, slots=True)
class PrivacyDeleteRecord:
    delete_ref: str
    source_ref: str
    projection_refs: tuple[str, ...]
    all_projections_hidden: bool
    legal_hold_blocks_delete: bool


@dataclass(frozen=True, slots=True)
class MemorySafetyRecord:
    safety_ref: str
    prompt_injection_authoritative: bool
    hidden_chain_persisted: bool
    model_output_is_proposal: bool


@dataclass(frozen=True, slots=True)
class ModelMemoryRouting:
    routing_ref: str
    weak_model_default: str
    strong_model_path: str
    upgrade_lineage_ref: str


@dataclass(frozen=True, slots=True)
class MemoryTraceRecord:
    trace_ref: str
    selection_trace_ref: str
    outcome_ref: str
    eval_ref: str
    long_term_eval_ref: str
    compression_eval_ref: str


@dataclass(frozen=True, slots=True)
class MemoryStorageRecord:
    storage_ref: str
    canonical_store: str
    large_payload_object_ref: str
    projections_rebuildable: bool


@dataclass(frozen=True, slots=True)
class MemoryEnvelope:
    envelope_ref: str
    tenant_id: str
    workspace_id: str
    trace_id: str
    correlation_id: str
    payload_hash: str


@dataclass(frozen=True, slots=True)
class MemoryReadinessEvidence:
    requirement_ids: tuple[str, ...]
    code_refs: tuple[str, ...]
    test_refs: tuple[str, ...]
    verifier_ref: str
    evidence_ref: str
    implementation_available: bool


class MemoryRuntimeBatch:
    requirement_ids = tuple(f"ARCH-MEM-{index:03d}" for index in range(1, 61))

    def lifecycle(self) -> MemoryLifecycleRecord:
        return MemoryLifecycleRecord(
            working_owner="06 Agent Core / Planning & Control",
            session_summary_ref="session-summary:separate-from-raw",
            long_term_kinds=tuple(LongTermMemoryKind),
            projection_kinds=("entity", "vector", "graph", "lexical"),
        )

    def candidate(self, *, candidate_ref: str, source_fact_ref: str, kind: LongTermMemoryKind, status: CandidateStatus = CandidateStatus.PROPOSED) -> MemoryCandidateRecord:
        return MemoryCandidateRecord(candidate_ref, source_fact_ref, kind, status, governance_required=True, model_is_fact_owner=False)

    def version(self, *, version_ref: str, candidate_ref: str, generation: int, source_payload: dict[str, Any], status: VersionStatus) -> MemoryVersionRecord:
        source_hash = _hash(source_payload)
        return MemoryVersionRecord(version_ref, candidate_ref, generation, source_hash, status, _hash([version_ref, candidate_ref, generation, source_hash, status.value]))

    def session_summary(self, *, summary_ref: str, source_messages: tuple[dict[str, Any], ...], coverage_ratio: float, raw_message_ref: str, incremental_generation: int) -> SessionSummaryRecord:
        return SessionSummaryRecord(summary_ref, tuple(_hash(message) for message in source_messages), coverage_ratio, raw_message_ref, incremental_generation)

    def context_pack(self, *, context_pack_ref: str, generation: int, candidate_refs: tuple[str, ...], compression_trace_ref: str, budget_trace_ref: str, token_count: int) -> ContextPackVersion:
        immutable_hash = _hash([context_pack_ref, generation, candidate_refs, compression_trace_ref, budget_trace_ref, token_count])
        return ContextPackVersion(context_pack_ref, generation, candidate_refs, compression_trace_ref, budget_trace_ref, token_count, immutable_hash, read_view=True)

    def retrieval_gate(self, *, retrieval_ref: str, memory_kind: LongTermMemoryKind, scope_ref: str, acl_decision_ref: str, allowed: bool) -> RetrievalGateRecord:
        return RetrievalGateRecord(retrieval_ref, memory_kind, scope_ref, acl_decision_ref, security_before_summary=True, allowed=allowed)

    def compression(self, *, compression_ref: str, level: CompressionLevel, fidelity_level: str, protected_set_refs: tuple[str, ...]) -> CompressionDecision:
        return CompressionDecision(compression_ref, level, fidelity_level, tool_payload_first=True, protected_set_refs=protected_set_refs, deterministic_budget=True, exact_token_validation=True)

    def rehydration(self, *, rehydration_ref: str, context_pack_ref: str, object_refs: tuple[str, ...]) -> RehydrationRecord:
        return RehydrationRecord(rehydration_ref, context_pack_ref, object_refs, summary_is_only_source=False)

    def reflexion_governance(self, *, reflexion_ref: str, procedural_promotion_evidence_refs: tuple[str, ...]) -> ReflexionGovernanceRecord:
        return ReflexionGovernanceRecord(reflexion_ref, LongTermMemoryKind.EPISODIC, procedural_promotion_evidence_refs, procedural_is_strategy_hint=True)

    def consolidation(self, *, consolidation_ref: str, source_refs: tuple[str, ...], utility_projection_ref: str, fact_ref: str, negative_transfer: bool) -> ConsolidationRecord:
        return ConsolidationRecord(consolidation_ref, source_refs, delete_source=False, utility_projection_ref=utility_projection_ref, fact_ref=fact_ref, negative_transfer_suspended=negative_transfer)

    def freshness(self, *, freshness_ref: str, effective_time_ref: str, observed_time_ref: str) -> FreshnessRecord:
        return FreshnessRecord(freshness_ref, effective_time_ref, observed_time_ref, verified_before_use=True)

    def conflict(self, *, conflict_ref: str, competing_version_refs: tuple[str, ...], resolution_ref: str) -> ConflictRecord:
        return ConflictRecord(conflict_ref, competing_version_refs, silent_overwrite_allowed=False, resolution_ref=resolution_ref)

    def state_machine(self, *, machine_ref: str, statuses: tuple[StrEnum, ...]) -> StateMachineRecord:
        return StateMachineRecord(machine_ref, tuple(status.value for status in statuses), closed=True)

    def projection_publication(self, *, publication_ref: str, domain_commit_ref: str, projection_ref: str, index_receipt_ref: str) -> ProjectionPublicationRecord:
        return ProjectionPublicationRecord(publication_ref, domain_commit_ref, projection_ref, index_receipt_ref, index_is_active=False, order_valid=bool(domain_commit_ref and projection_ref and index_receipt_ref))

    def commit_recovery(self, *, commit_ref: str, idempotency_key: str, checkpoint_ref: str, domain_commit_ref: str, expected_generation: int, committed_generation: int) -> CommitRecoveryRecord:
        return CommitRecoveryRecord(commit_ref, idempotency_key, checkpoint_ref, domain_commit_ref, committed_generation, cas_passed=committed_generation == expected_generation + 1, unknown_requires_reconcile=True)

    def privacy_delete(self, *, delete_ref: str, source_ref: str, projection_refs: tuple[str, ...], legal_hold: bool) -> PrivacyDeleteRecord:
        return PrivacyDeleteRecord(delete_ref, source_ref, projection_refs, all_projections_hidden=bool(projection_refs), legal_hold_blocks_delete=legal_hold)

    def safety(self, *, safety_ref: str) -> MemorySafetyRecord:
        return MemorySafetyRecord(safety_ref, prompt_injection_authoritative=False, hidden_chain_persisted=False, model_output_is_proposal=True)

    def model_routing(self, *, routing_ref: str, upgrade_lineage_ref: str) -> ModelMemoryRouting:
        return ModelMemoryRouting(routing_ref, weak_model_default="summary", strong_model_path="complex_consolidation", upgrade_lineage_ref=upgrade_lineage_ref)

    def trace(self, *, trace_ref: str, selection_trace_ref: str, outcome_ref: str, eval_ref: str, long_term_eval_ref: str, compression_eval_ref: str) -> MemoryTraceRecord:
        return MemoryTraceRecord(trace_ref, selection_trace_ref, outcome_ref, eval_ref, long_term_eval_ref, compression_eval_ref)

    def storage(self, *, storage_ref: str, large_payload_object_ref: str) -> MemoryStorageRecord:
        return MemoryStorageRecord(storage_ref, canonical_store="PostgreSQL", large_payload_object_ref=large_payload_object_ref, projections_rebuildable=True)

    def envelope(self, *, envelope_ref: str, tenant_id: str, workspace_id: str, trace_id: str, correlation_id: str, payload: dict[str, Any]) -> MemoryEnvelope:
        return MemoryEnvelope(envelope_ref, tenant_id, workspace_id, trace_id, correlation_id, _hash(payload))

    def readiness_evidence(self, *, code_refs: tuple[str, ...], test_refs: tuple[str, ...], verifier_ref: str, evidence_ref: str) -> MemoryReadinessEvidence:
        return MemoryReadinessEvidence(self.requirement_ids, code_refs, test_refs, verifier_ref, evidence_ref, bool(code_refs and test_refs and verifier_ref and evidence_ref and len(self.requirement_ids) == 60))


__all__ = [
    "CandidateStatus",
    "CompressionDecision",
    "CompressionLevel",
    "ConflictRecord",
    "ConsolidationRecord",
    "ContextPackVersion",
    "FreshnessRecord",
    "LongTermMemoryKind",
    "MemoryCandidateRecord",
    "MemoryEnvelope",
    "MemoryLifecycleRecord",
    "MemoryReadinessEvidence",
    "MemoryRuntimeBatch",
    "MemorySafetyRecord",
    "MemoryStorageRecord",
    "MemoryTraceRecord",
    "MemoryVersionRecord",
    "ModelMemoryRouting",
    "PrivacyDeleteRecord",
    "ProjectionPublicationRecord",
    "ReflexionGovernanceRecord",
    "RehydrationRecord",
    "RetrievalGateRecord",
    "SessionSummaryRecord",
    "StateMachineRecord",
    "VersionStatus",
]

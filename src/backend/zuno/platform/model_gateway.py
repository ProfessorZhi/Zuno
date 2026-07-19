from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import StrEnum
import hashlib
import json
import time
from typing import Any, Iterable, Literal, Protocol

from langchain_core.language_models import BaseChatModel

from zuno.platform.model_roles import ModelRole, ROLE_DEFAULT_SLOT
from zuno.platform.security import redact_sensitive_payload, redact_sensitive_text
from zuno.platform.services.llm.providers import EchoLLMProvider, LLMProvider


class ModelCategory(StrEnum):
    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANKER = "reranker"
    VLM = "vlm"
    EVAL_JUDGE = "eval_judge"


class ModelOperation(StrEnum):
    GENERATE = "generate"
    EMBED = "embed"
    RERANK = "rerank"
    VISION = "vision"
    TRANSCRIBE = "transcribe"
    CLASSIFY = "classify"
    JUDGE = "judge"


class ModelCallState(StrEnum):
    DECLARED = "DECLARED"
    BUDGET_BLOCKED = "BUDGET_BLOCKED"
    DISPATCHING = "DISPATCHING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    UNKNOWN_RECONCILE = "UNKNOWN_RECONCILE"


class ModelAttemptState(StrEnum):
    DECLARED = "DECLARED"
    DISPATCHED = "DISPATCHED"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"
    CANCELLED = "CANCELLED"
    UNKNOWN_RECONCILE = "UNKNOWN_RECONCILE"


class ModelUsageKind(StrEnum):
    ESTIMATE = "ESTIMATE"
    OBSERVED = "OBSERVED"
    SETTLED = "SETTLED"
    CORRECTION = "CORRECTION"


class ModelProviderHealthStatus(StrEnum):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class ModelCircuitStatus(StrEnum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"


class ModelCapabilityStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    REVOKED = "REVOKED"


class ModelProviderSignalStatus(StrEnum):
    ACCEPTED = "ACCEPTED"
    UNKNOWN_FAIL_CLOSED = "UNKNOWN_FAIL_CLOSED"


class ModelConfigActivationGate(StrEnum):
    VALIDATION = "VALIDATION"
    REPLAY = "REPLAY"
    CANARY = "CANARY"
    CAS = "CAS"
    ROLLBACK = "ROLLBACK"


class ModelProviderLifecycleState(StrEnum):
    PROBE = "PROBE"
    ENABLED = "ENABLED"
    DEPRECATED = "DEPRECATED"
    DRAINING = "DRAINING"
    DISABLED = "DISABLED"
    RETIRED = "RETIRED"


class ModelAdmissionLayer(StrEnum):
    GLOBAL = "GLOBAL"
    PROVIDER = "PROVIDER"
    MODEL = "MODEL"
    OPERATION = "OPERATION"
    ROLE = "ROLE"


class ModelOverloadState(StrEnum):
    NORMAL = "NORMAL"
    BACKPRESSURE = "BACKPRESSURE"
    LOAD_SHEDDING = "LOAD_SHEDDING"


class ModelCacheKind(StrEnum):
    PROVIDER_PROMPT = "PROVIDER_PROMPT"
    METADATA = "METADATA"
    RESULT = "RESULT"


class ModelOperationalCommandKind(StrEnum):
    ENABLE_PROVIDER = "ENABLE_PROVIDER"
    DISABLE_PROVIDER = "DISABLE_PROVIDER"
    RETIRE_MODEL = "RETIRE_MODEL"
    UPDATE_CONFIG = "UPDATE_CONFIG"


class ModelRetentionSubject(StrEnum):
    PROMPT = "PROMPT"
    RESPONSE = "RESPONSE"
    STREAM = "STREAM"
    USAGE = "USAGE"
    FAILURE = "FAILURE"
    DECISION = "DECISION"


class ModelDeletionStep(StrEnum):
    TOMBSTONE = "TOMBSTONE"
    VISIBILITY_REVOCATION = "VISIBILITY_REVOCATION"
    PHYSICAL_CLEANUP = "PHYSICAL_CLEANUP"
    VERIFICATION = "VERIFICATION"


class ModelReadinessStatus(StrEnum):
    READY = "READY"
    NOT_READY = "NOT_READY"


class ModelAdapterRolloutMode(StrEnum):
    PARALLEL = "PARALLEL"
    CANARY = "CANARY"
    DRAIN = "DRAIN"
    ROLLBACK = "ROLLBACK"


class ModelUnknownSignalDisposition(StrEnum):
    FAIL_CLOSED = "FAIL_CLOSED"
    QUARANTINE = "QUARANTINE"


class ModelControlActionType(StrEnum):
    RETRY = "retry"
    REPAIR = "repair"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    REPLAN_PROPOSAL = "replan_proposal"
    RECONCILE = "reconcile"


class ModelDomainWrite(StrEnum):
    NONE = "none"
    PLAN_VERSION_ACTIVATION = "plan_version_activation"
    RUN_OUTCOME_UPDATE = "run_outcome_update"


class ModelGatewayProviderError(RuntimeError):
    pass


class ModelGatewayTimeoutError(TimeoutError):
    pass


class ModelGatewayCancellationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ModelGatewayBinding:
    role: ModelRole
    operation: ModelOperation
    model_slot: str
    config_version: str
    prompt_version: str
    schema_version: str
    model_version: str
    adapter_version: str
    pricing_version: str
    security_epoch_ref: str

    @property
    def binding_hash(self) -> str:
        return _stable_hash(
            {
                "role": self.role.value,
                "operation": self.operation.value,
                "model_slot": self.model_slot,
                "config_version": self.config_version,
                "prompt_version": self.prompt_version,
                "schema_version": self.schema_version,
                "model_version": self.model_version,
                "adapter_version": self.adapter_version,
                "pricing_version": self.pricing_version,
                "security_epoch_ref": self.security_epoch_ref,
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role.value,
            "operation": self.operation.value,
            "model_slot": self.model_slot,
            "config_version": self.config_version,
            "prompt_version": self.prompt_version,
            "schema_version": self.schema_version,
            "model_version": self.model_version,
            "adapter_version": self.adapter_version,
            "pricing_version": self.pricing_version,
            "security_epoch_ref": self.security_epoch_ref,
            "binding_hash": self.binding_hash,
        }


@dataclass(frozen=True, slots=True)
class ModelAttemptReceipt:
    attempt_id: str
    provider_id: str
    model_id: str
    adapter_version: str
    state: ModelAttemptState
    dispatch_index: int
    failure_code: str | None = None
    original_error_ref: str | None = None
    usage_receipt_id: str | None = None
    reconcile_required: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt_id": self.attempt_id,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "adapter_version": self.adapter_version,
            "state": self.state.value,
            "dispatch_index": self.dispatch_index,
            "failure_code": self.failure_code,
            "original_error_ref": self.original_error_ref,
            "usage_receipt_id": self.usage_receipt_id,
            "reconcile_required": self.reconcile_required,
        }


@dataclass(frozen=True, slots=True)
class ModelUsageReceipt:
    usage_receipt_id: str
    call_id: str
    attempt_id: str | None
    kind: ModelUsageKind
    pricing_version: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    immutable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "usage_receipt_id": self.usage_receipt_id,
            "call_id": self.call_id,
            "attempt_id": self.attempt_id,
            "kind": self.kind.value,
            "pricing_version": self.pricing_version,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "immutable": self.immutable,
        }


@dataclass(frozen=True, slots=True)
class ModelQuotaPolicy:
    quota_scope: str
    token_limit: int
    reserved_tokens: int
    generation: int = 0


@dataclass(frozen=True, slots=True)
class ModelQuotaReservation:
    reservation_id: str
    quota_scope: str
    reserved_tokens: int
    expected_generation: int
    committed_generation: int
    accepted: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ModelProviderHealthWindow:
    provider_id: str
    model_id: str
    region: str
    operation: ModelOperation
    adapter_version: str
    window_started_at: float
    window_ended_at: float
    success_count: int
    failure_count: int
    evidence_ref: str | None
    status: ModelProviderHealthStatus

    @property
    def evidence_count(self) -> int:
        return self.success_count + self.failure_count

    @property
    def is_healthy(self) -> bool:
        return self.status == ModelProviderHealthStatus.HEALTHY and self.evidence_count > 0


@dataclass(frozen=True, slots=True)
class ModelCircuitKey:
    provider_id: str
    model_id: str
    region: str
    operation: ModelOperation
    adapter_version: str

    @property
    def isolation_key(self) -> str:
        return _stable_hash(
            [
                self.provider_id,
                self.model_id,
                self.region,
                self.operation.value,
                self.adapter_version,
            ]
        )


@dataclass(frozen=True, slots=True)
class ModelCircuitDecision:
    key: ModelCircuitKey
    status: ModelCircuitStatus
    reason: str
    health_evidence_ref: str | None


@dataclass(frozen=True, slots=True)
class ModelCapabilityProfile:
    capability_id: str
    provider_id: str
    model_id: str
    operation: ModelOperation
    status: ModelCapabilityStatus
    evidence_ref: str
    dispatch_allowed: bool
    requires_operator_review: bool


@dataclass(frozen=True, slots=True)
class ModelAdapterConformanceSuite:
    suite_id: str
    operation: ModelOperation
    adapter_version: str
    sdk_api_version: str
    model_mapping_version: str
    evidence_ref: str
    passed: bool

    @property
    def conformance_hash(self) -> str:
        return _stable_hash(
            [
                self.suite_id,
                self.operation.value,
                self.adapter_version,
                self.sdk_api_version,
                self.model_mapping_version,
                self.evidence_ref,
                self.passed,
            ]
        )


@dataclass(frozen=True, slots=True)
class ModelAdapterConformanceVerdict:
    suite_id: str
    valid: bool
    requires_revalidation: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ModelProviderSignalVerdict:
    signal_kind: Literal["enum", "event", "error"]
    raw_value: str
    status: ModelProviderSignalStatus
    success: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ModelGatewayConfigSnapshot:
    config_version: str
    generation: int
    content_sha256: str
    payload_canonical_json: str

    @property
    def snapshot_id(self) -> str:
        return "config_snapshot_" + _stable_hash([self.config_version, self.generation, self.content_sha256])[:16]


@dataclass(frozen=True, slots=True)
class ModelConfigActivationDecision:
    snapshot: ModelGatewayConfigSnapshot
    expected_generation: int
    committed_generation: int
    accepted: bool
    completed_gates: tuple[ModelConfigActivationGate, ...]
    rollback_snapshot_ref: str | None
    reason: str


@dataclass(frozen=True, slots=True)
class ModelCallConfigBinding:
    call_id: str
    config_snapshot_id: str
    config_version: str
    config_hash: str
    immutable: bool = True


@dataclass(frozen=True, slots=True)
class ModelProviderLifecycleRecord:
    provider_id: str
    model_id: str
    state: ModelProviderLifecycleState
    generation: int
    evidence_ref: str
    accepts_new_dispatch: bool
    preserves_history: bool = True


@dataclass(frozen=True, slots=True)
class ModelEmergencyDisableDecision:
    provider_id: str
    model_id: str
    generation: int
    blocks_new_dispatch: bool
    late_results_isolated: bool
    quarantine_ref: str


@dataclass(frozen=True, slots=True)
class ModelAdmissionLayerCheck:
    layer: ModelAdmissionLayer
    capacity_key: str
    requested_units: int
    available_units: int
    accepted: bool


@dataclass(frozen=True, slots=True)
class ModelAdmissionDecision:
    admission_id: str
    tenant_id: str
    role: ModelRole
    accepted: bool
    reason: str
    layer_checks: tuple[ModelAdmissionLayerCheck, ...]
    reserved_capacity_used: int
    fairness_limited: bool
    starvation_prevention_applied: bool


@dataclass(frozen=True, slots=True)
class ModelQueuedRequestBinding:
    queue_entry_id: str
    call_id: str
    deadline_at: float
    security_epoch_ref: str
    budget_verdict: BudgetVerdict
    config_binding: ModelCallConfigBinding


@dataclass(frozen=True, slots=True)
class ModelOverloadDecision:
    state: ModelOverloadState
    backpressure: bool
    load_shedding: bool
    reason: str
    preserved_gates: tuple[str, ...]
    bypass_allowed: bool = False


@dataclass(frozen=True, slots=True)
class ModelCachePolicy:
    cache_kind: ModelCacheKind
    enabled: bool
    tenant_id: str
    config_version: str
    schema_version: str
    model_version: str
    adapter_version: str
    security_epoch_ref: str


@dataclass(frozen=True, slots=True)
class ModelCacheKey:
    cache_kind: ModelCacheKind
    tenant_id: str
    cache_key: str
    version_scope: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ModelCacheLookup:
    cache_kind: ModelCacheKind
    key: ModelCacheKey
    hit: bool
    provider_attempt_allowed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ModelCacheReuseReceipt:
    reuse_receipt_id: str
    cache_key: str
    source_result_ref: str
    call_id: str
    creates_provider_attempt: bool = False


@dataclass(frozen=True, slots=True)
class ModelCacheInvalidationDecision:
    cache_key: str
    invalidated: bool
    reason: Literal["revocation", "deletion", "model_retirement", "validity_changed"]
    tombstone_ref: str


@dataclass(frozen=True, slots=True)
class ModelOperationalCommand:
    command_id: str
    command_kind: ModelOperationalCommandKind
    command_version: str
    target_ref: str
    expected_generation: int
    payload_hash: str
    high_risk: bool
    authorized_by: str | None
    approval_ref: str | None
    audit_ref: str | None


@dataclass(frozen=True, slots=True)
class ModelOperationalCommandVerdict:
    command_id: str
    accepted: bool
    reason: str
    committed_generation: int


@dataclass(frozen=True, slots=True)
class ModelRetentionBinding:
    subject: ModelRetentionSubject
    retention_policy_ref: str
    retention_until: float
    legal_hold: bool = False


@dataclass(frozen=True, slots=True)
class ModelDeletionWorkflow:
    object_ref: str
    steps: tuple[ModelDeletionStep, ...]
    tombstone_ref: str
    visibility_revoked: bool
    physical_cleanup_allowed: bool
    verified: bool
    legal_hold: bool = False


@dataclass(frozen=True, slots=True)
class ModelSliSloDimension:
    call_id: str
    attempt_id: str
    operation: ModelOperation
    role: ModelRole
    tenant_id: str
    provider_id: str
    config_version: str
    slo_ref: str


@dataclass(frozen=True, slots=True)
class ModelReadinessProbe:
    adapter_evidence_ref: str | None
    security_evidence_ref: str | None
    persistence_evidence_ref: str | None
    usage_evidence_ref: str | None
    reconcile_evidence_ref: str | None
    capacity_evidence_ref: str | None
    deletion_evidence_ref: str | None
    mock_only: bool = False


@dataclass(frozen=True, slots=True)
class ModelReadinessVerdict:
    status: ModelReadinessStatus
    missing_evidence: tuple[str, ...]
    mock_only: bool
    reason: str


@dataclass(frozen=True, slots=True)
class ModelAdapterRolloutPlan:
    active_adapter_version: str
    candidate_adapter_version: str
    sdk_api_version: str
    modes: tuple[ModelAdapterRolloutMode, ...]
    rollback_adapter_version: str


@dataclass(frozen=True, slots=True)
class ModelProviderApiSunsetPlan:
    provider_id: str
    retiring_api_version: str
    replacement_api_version: str
    migration_evidence_ref: str
    rollback_evidence_ref: str
    compatibility_evidence_ref: str


@dataclass(frozen=True, slots=True)
class ModelExperimentGateVerdict:
    experiment_id: str
    allowed: bool
    gates: tuple[str, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class ModelExperimentAssignment:
    experiment_id: str
    sticky_scope: str
    subject_ref: str
    variant: str
    assignment_hash: str


@dataclass(frozen=True, slots=True)
class ModelShadowCallRecord:
    shadow_call_id: str
    security_ref: str
    budget_ref: str
    usage_ref: str
    trace_ref: str
    retention_ref: str
    independent: bool = True


@dataclass(frozen=True, slots=True)
class ModelShadowResult:
    shadow_call_id: str
    result_ref: str
    enters_business_output: bool = False


@dataclass(frozen=True, slots=True)
class ModelResultValidityEvent:
    event_id: str
    result_ref: str
    previous_validity: str
    new_validity: str
    fact_owner: str
    propagation_owner: str
    propagation_allowed: bool


@dataclass(frozen=True, slots=True)
class ModelFailureClassification:
    provider_id: str
    raw_error_ref: str
    provider_neutral_code: str
    stable: bool = True


@dataclass(frozen=True, slots=True)
class ModelSuggestedControlAction:
    action: ModelControlActionType
    suggested_by: str
    decision_owner: str = "AGENT_CORE"
    replaces_agent_core_decision: bool = False


@dataclass(frozen=True, slots=True)
class ModelDomainEvent:
    event_id: str
    event_version: str
    sequence: int
    idempotency_key: str
    replayable: bool
    redacted_payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ModelProjectionBoundary:
    source_fact_ref: str
    trace_projection_ref: str
    audit_projection_ref: str
    eval_projection_ref: str
    projections_replace_source_fact: bool = False


@dataclass(frozen=True, slots=True)
class ModelOwnershipBoundary:
    module: str
    owned_facts: tuple[str, ...]
    foreign_facts: tuple[str, ...]
    cross_owner_write_allowed: bool = False


@dataclass(frozen=True, slots=True)
class ModelVersionedEnvelope:
    envelope_type: str
    major_version: int
    minor_version: int
    payload_ref: str
    idempotency_key: str
    correlation_id: str
    causation_id: str


@dataclass(frozen=True, slots=True)
class ModelStorageLayeringBoundary:
    domain_fact_ref: str
    object_payload_ref: str
    projection_ref: str
    layers_collapsed: bool = False


@dataclass(frozen=True, slots=True)
class ModelCompatibilityFacadeBoundary:
    facade_id: str
    bypass_inventory_ref: str
    new_bypass_allowed: bool
    migration_deadline_ref: str


@dataclass(frozen=True, slots=True)
class ModelMigrationIntegrityVerdict:
    migration_id: str
    preserves_history_versions: bool
    preserves_usage_receipts: bool
    preserves_implementation_status: bool
    accepted: bool


@dataclass(frozen=True, slots=True)
class ModelUnknownSignalVerdict:
    signal_kind: str
    raw_value: str
    disposition: ModelUnknownSignalDisposition
    accepted: bool = False


@dataclass(frozen=True, slots=True)
class ModelFaultRecoveryEvidence:
    fault_id: str
    high_risk: bool
    fault_injection_ref: str
    recovery_evidence_ref: str


@dataclass(frozen=True, slots=True)
class ModelCurrentEvidenceGate:
    requirement_id: str
    code_ref: str
    migration_ref: str
    test_ref: str
    trace_ref: str
    eval_ref: str
    runtime_evidence_ref: str

    @property
    def implementation_available(self) -> bool:
        return all(
            [
                self.code_ref,
                self.migration_ref,
                self.test_ref,
                self.trace_ref,
                self.eval_ref,
                self.runtime_evidence_ref,
            ]
        )


@dataclass(frozen=True, slots=True)
class ModelControlAction:
    action_id: str
    action_type: ModelControlActionType
    owner: Literal["MODEL_GATEWAY", "AGENT_CORE", "OBSERVABILITY"]
    reason: str
    attempt_id: str | None = None
    activates_plan_version: bool = False
    modifies_run_outcome: bool = False

    def __post_init__(self) -> None:
        if self.activates_plan_version or self.modifies_run_outcome:
            raise ModelGatewayProviderError("model gateway cannot mutate Agent Core domain state")

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "owner": self.owner,
            "reason": self.reason,
            "attempt_id": self.attempt_id,
            "activates_plan_version": self.activates_plan_version,
            "modifies_run_outcome": self.modifies_run_outcome,
        }


@dataclass(frozen=True, slots=True)
class ModelRepairRecord:
    repair_record_id: str
    original_output_sha256: str
    repaired_output_sha256: str
    schema_version: str
    failure_code: str
    deterministic: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "repair_record_id": self.repair_record_id,
            "original_output_sha256": self.original_output_sha256,
            "repaired_output_sha256": self.repaired_output_sha256,
            "schema_version": self.schema_version,
            "failure_code": self.failure_code,
            "deterministic": self.deterministic,
        }


@dataclass(frozen=True, slots=True)
class ProviderStreamChunk:
    provider_chunk_id: str
    sequence: int
    content: str
    final: bool = False


@dataclass(frozen=True, slots=True)
class GatewayStreamChunk:
    gateway_chunk_id: str
    provider_chunk_id: str
    sequence: int
    content: str
    content_sha256: str
    provisional: bool
    duplicate: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "gateway_chunk_id": self.gateway_chunk_id,
            "provider_chunk_id": self.provider_chunk_id,
            "sequence": self.sequence,
            "content": self.content,
            "content_sha256": self.content_sha256,
            "provisional": self.provisional,
            "duplicate": self.duplicate,
        }


@dataclass(frozen=True, slots=True)
class ProductStreamEvent:
    event_id: str
    event_type: Literal["model_stream_delta", "model_stream_completed"]
    sequence: int
    content: str
    provisional: bool
    gateway_chunk_ref: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "sequence": self.sequence,
            "content": self.content,
            "provisional": self.provisional,
            "gateway_chunk_ref": self.gateway_chunk_ref,
        }


@dataclass(frozen=True, slots=True)
class ModelStreamResult:
    call_id: str
    binding: ModelGatewayBinding
    attempt: ModelAttemptReceipt
    gateway_chunks: tuple[GatewayStreamChunk, ...]
    product_events: tuple[ProductStreamEvent, ...]
    usage_receipts: tuple[ModelUsageReceipt, ...]


@dataclass(frozen=True, slots=True)
class ModelEmbeddingResult:
    embedding_id: str
    text_ref: str
    vector: tuple[float, ...]
    revision: str
    dimension: int
    normalization: Literal["NONE", "L2", "UNIT"]
    index_generation: str
    state: Literal["SUCCEEDED", "FAILED"]
    failure_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ModelRerankItem:
    item_id: str
    score: float
    rank: int


@dataclass(frozen=True, slots=True)
class ModelVisionRegion:
    page_number: int
    bbox: tuple[float, float, float, float]
    text: str
    source_lineage_ref: str


@dataclass(frozen=True, slots=True)
class ModelTranscriptionSegment:
    segment_id: str
    start_ms: int
    end_ms: int
    text: str
    partial: bool


@dataclass(frozen=True, slots=True)
class ModelClassificationResult:
    label: str | None
    score: float
    threshold: float
    calibration_ref: str
    abstained: bool


@dataclass(frozen=True, slots=True)
class ModelJudgeResult:
    score: float
    rationale_ref: str
    budget_verdict: BudgetVerdict
    gateway_audited: bool
    sole_quality_proof_allowed: bool = False
    requires_external_evidence: bool = True


@dataclass(frozen=True, slots=True)
class ModelCompressedContext:
    compression_id: str
    summary: str
    lineage_refs: tuple[str, ...]
    preserved_constraints: tuple[str, ...]
    conflict_refs: tuple[str, ...]
    distortion_risks: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.lineage_refs:
            raise ModelGatewayProviderError("compressed context must preserve lineage")
        if not self.preserved_constraints:
            raise ModelGatewayProviderError("compressed context must preserve constraints")


@dataclass(frozen=True, slots=True)
class ModelOutputCandidate:
    candidate_id: str
    target_owner: Literal["MEMORY"]
    payload: dict[str, Any]
    source_model_call_ref: str
    requires_owner_review: bool = True
    directly_committable: bool = False


@dataclass(frozen=True, slots=True)
class ModelRiskProposal:
    proposal_id: str
    target_owner: Literal["SECURITY"]
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "BLOCK"]
    evidence_refs: tuple[str, ...]
    source_model_call_ref: str
    requires_owner_review: bool = True
    directly_enforced: bool = False


@dataclass(frozen=True, slots=True)
class ModelActionProposal:
    proposal_id: str
    target_owner: Literal["AGENT_CORE", "TOOL_RUNTIME"]
    action_name: str
    args_hash: str
    source_model_call_ref: str
    requires_owner_binding: bool = True
    directly_executable: bool = False


@dataclass(frozen=True, slots=True)
class BudgetPolicy:
    max_cost: float | None = None
    max_latency_ms: float | None = None


@dataclass(frozen=True, slots=True)
class BudgetVerdict:
    allowed: bool
    reason: str
    estimated_cost: float
    max_cost: float | None = None
    estimated_latency_ms: float | None = None
    max_latency_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "estimated_cost": self.estimated_cost,
            "max_cost": self.max_cost,
            "estimated_latency_ms": self.estimated_latency_ms,
            "max_latency_ms": self.max_latency_ms,
        }


@dataclass(slots=True)
class ModelGatewayRequest:
    category: ModelCategory | str
    prompt: str
    role: ModelRole | str = ModelRole.EXECUTOR
    operation: ModelOperation | str | None = None
    run_id: str | None = None
    provider_id: str | None = None
    fallback_provider_ids: list[str] = field(default_factory=list)
    trace_id: str | None = None
    task_id: str | None = None
    workspace_id: str | None = None
    user_id: str | None = None
    model_slot: str | None = None
    timeout_ms: int | None = None
    max_output_tokens: int = 128
    budget: BudgetPolicy | None = None
    config_version: str = "config:local:1"
    prompt_version: str = "prompt:inline:1"
    schema_version: str = "schema:none:1"
    model_version: str | None = None
    adapter_version: str = "adapter:mock:1"
    pricing_version: str = "pricing:local:1"
    security_epoch_ref: str = "security:local:1"
    output_schema: dict[str, type] | None = None
    repair_output: str | None = None
    requested_domain_writes: tuple[ModelDomainWrite | str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.category = ModelCategory(self.category)
        self.role = ModelRole(self.role)
        self.operation = ModelOperation(self.operation) if self.operation else _default_operation(self.category)
        self.requested_domain_writes = tuple(ModelDomainWrite(value) for value in self.requested_domain_writes)


@dataclass(frozen=True, slots=True)
class ModelCallMetrics:
    category: ModelCategory
    role: ModelRole
    provider_id: str
    model_id: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost_estimate: float
    retry_count: int = 0
    timeout_count: int = 0
    fallback_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category.value,
            "role": self.role.value,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "token_count": self.total_tokens,
            "latency_ms": self.latency_ms,
            "cost_estimate": self.cost_estimate,
            "retry_count": self.retry_count,
            "timeout_count": self.timeout_count,
            "fallback_reason": self.fallback_reason,
        }


@dataclass(frozen=True, slots=True)
class ModelGatewayResult:
    status: Literal["succeeded", "blocked", "failed", "cancelled"]
    output: str
    metrics: ModelCallMetrics
    budget_verdict: BudgetVerdict
    trace_event: dict[str, Any]
    call_id: str
    call_state: ModelCallState
    binding: ModelGatewayBinding
    attempts: tuple[ModelAttemptReceipt, ...] = ()
    usage_receipts: tuple[ModelUsageReceipt, ...] = ()
    control_actions: tuple[ModelControlAction, ...] = ()
    selected_attempt_id: str | None = None
    structured_output: dict[str, Any] | None = None
    repair_record: ModelRepairRecord | None = None


ModelCallRequest = ModelGatewayRequest
ModelCallResponse = ModelGatewayResult


class ModelProvider(Protocol):
    provider_id: str
    model_id: str

    def supports(self, category: ModelCategory) -> bool:
        ...

    def estimate_completion_tokens(self, prompt_tokens: int, max_output_tokens: int) -> int:
        ...

    def invoke(self, request: ModelGatewayRequest) -> str:
        ...


@dataclass(slots=True)
class MockModelProvider:
    provider_id: str = "local_mock_chat"
    model_id: str = "zuno-local-mock-chat"
    categories: Iterable[ModelCategory | str] | None = None
    fail_mode: Literal["timeout", "error", "cancel"] | None = None
    response: str | None = None
    call_count: int = 0

    def __post_init__(self) -> None:
        raw_categories = self.categories or list(ModelCategory)
        self.categories = tuple(ModelCategory(category) for category in raw_categories)

    def supports(self, category: ModelCategory) -> bool:
        return category in set(self.categories or ())

    def estimate_completion_tokens(self, prompt_tokens: int, max_output_tokens: int) -> int:
        return max(1, min(max_output_tokens, max(4, prompt_tokens // 2)))

    def invoke(self, request: ModelGatewayRequest) -> str:
        self.call_count += 1
        if self.fail_mode == "timeout":
            raise ModelGatewayTimeoutError(f"provider timed out: {self.provider_id}")
        if self.fail_mode == "error":
            raise ModelGatewayProviderError(f"provider failed: {self.provider_id}")
        if self.fail_mode == "cancel":
            raise ModelGatewayCancellationError(f"provider cancelled: {self.provider_id}")
        if self.response is not None:
            return self.response
        if request.category == ModelCategory.EMBEDDING:
            return "[0.13, 0.21, 0.34]"
        if request.category == ModelCategory.RERANKER:
            return "rerank_score=0.87"
        if request.category == ModelCategory.VLM:
            return "local mock vlm boundary: text-only diagnostic"
        if request.category == ModelCategory.EVAL_JUDGE:
            return "eval_judge_score=0.82; rationale=local deterministic judge"
        return f"local mock chat response from {self.model_id}"


class OpenAIEmbeddingGatewayAdapter:
    """Provider SDK adapter for OpenAI-compatible embeddings inside the Gateway boundary."""

    def __init__(self, *, api_key: str | None, base_url: str | None, model: str):
        from openai import AsyncOpenAI, OpenAI

        self.model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    def embed(self, query: str) -> list[float]:
        responses = self._client.embeddings.create(
            model=self.model,
            input=query,
            encoding_format="float",
        )
        return responses.data[0].embedding

    async def embed_async(self, query: str | list[str]) -> list[float] | list[list[float]]:
        if isinstance(query, str) or len(query) <= 10:
            return await self._embed_batch(query)

        semaphore = asyncio.Semaphore(5)

        async def process_batch(batch: list[str]) -> list[list[float]]:
            async with semaphore:
                batch_result = await self._embed_batch(batch)
                return batch_result if isinstance(batch_result[0], list) else [batch_result]

        batches = [query[index : index + 10] for index in range(0, len(query), 10)]
        results = await asyncio.gather(*(process_batch(batch) for batch in batches))
        return [embedding for batch_result in results for embedding in batch_result]

    async def _embed_batch(self, query: str | list[str]) -> list[float] | list[list[float]]:
        responses = await self._async_client.embeddings.create(
            model=self.model,
            input=query,
            encoding_format="float",
        )
        if isinstance(query, str):
            return responses.data[0].embedding
        return [response.embedding for response in responses.data]


def build_openai_chat_gateway_model(
    *,
    model: str | None,
    api_key: str | None,
    base_url: str | None,
    stream_usage: bool = True,
) -> BaseChatModel:
    """Build an OpenAI-compatible LangChain chat model inside the Gateway boundary."""
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        stream_usage=stream_usage,
        model=model,
        api_key=api_key,
        base_url=base_url,
        **_standard_openai_chat_kwargs(model, base_url),
    )


def _standard_openai_chat_kwargs(model_name: str | None, base_url: str | None) -> dict[str, Any]:
    base_url_lower = str(base_url or "").lower()
    model_lower = str(model_name or "").lower()
    if "deepseek.com" in base_url_lower and model_lower.startswith("deepseek-v4"):
        return {"extra_body": {"thinking": {"type": "disabled"}}}
    return {}


_CATEGORY_COST_PER_TOKEN = {
    ModelCategory.CHAT: 0.00001,
    ModelCategory.EMBEDDING: 0.000001,
    ModelCategory.RERANKER: 0.000002,
    ModelCategory.VLM: 0.00002,
    ModelCategory.EVAL_JUDGE: 0.00001,
}


class ModelGateway:
    def __init__(
        self,
        *,
        providers: Iterable[ModelProvider],
        default_budget: BudgetPolicy | None = None,
    ) -> None:
        self._providers = {provider.provider_id: provider for provider in providers}
        self.default_budget = default_budget or BudgetPolicy()
        self._quota_generations: dict[str, int] = {}
        self._quota_reserved_tokens: dict[str, int] = {}

    def invoke(self, request: ModelGatewayRequest) -> ModelGatewayResult:
        _ensure_gateway_domain_boundary(request)
        provider = self._select_provider(request.category, request.provider_id)
        binding = self._build_binding(request, provider)
        call_id = "model_call_" + binding.binding_hash[:16]
        prompt_tokens = _estimate_tokens(request.prompt)
        completion_tokens = provider.estimate_completion_tokens(prompt_tokens, request.max_output_tokens)
        budget_verdict = self._evaluate_budget(
            request=request,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        blocked_metrics = self._build_metrics(
            request=request,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=0.0,
            retry_count=0,
            timeout_count=0,
            fallback_reason=None,
        )
        estimate_receipt = self._build_usage_receipt(
            request=request,
            call_id=call_id,
            attempt_id=None,
            kind=ModelUsageKind.ESTIMATE,
            pricing_version=binding.pricing_version,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        if not budget_verdict.allowed:
            trace_event = self._build_trace_event(
                event_type="model_call_blocked",
                request=request,
                metrics=blocked_metrics,
                budget_verdict=budget_verdict,
                call_id=call_id,
                call_state=ModelCallState.BUDGET_BLOCKED,
                binding=binding,
                attempts=(),
                usage_receipts=(estimate_receipt,),
                control_actions=(),
            )
            return ModelGatewayResult(
                status="blocked",
                output="",
                metrics=blocked_metrics,
                budget_verdict=budget_verdict,
                trace_event=trace_event,
                call_id=call_id,
                call_state=ModelCallState.BUDGET_BLOCKED,
                binding=binding,
                usage_receipts=(estimate_receipt,),
                control_actions=(),
            )

        if request.metadata.get("cancel_before_dispatch") is True:
            cancel_receipt = self._build_usage_receipt(
                request=request,
                call_id=call_id,
                attempt_id=None,
                kind=ModelUsageKind.OBSERVED,
                pricing_version=binding.pricing_version,
                prompt_tokens=prompt_tokens,
                completion_tokens=0,
            )
            trace_event = self._build_trace_event(
                event_type="model_call_cancelled",
                request=request,
                metrics=blocked_metrics,
                budget_verdict=budget_verdict,
                call_id=call_id,
                call_state=ModelCallState.CANCELLED,
                binding=binding,
                attempts=(),
                usage_receipts=(estimate_receipt, cancel_receipt),
                control_actions=(),
            )
            return ModelGatewayResult(
                status="cancelled",
                output="",
                metrics=blocked_metrics,
                budget_verdict=budget_verdict,
                trace_event=trace_event,
                call_id=call_id,
                call_state=ModelCallState.CANCELLED,
                binding=binding,
                usage_receipts=(estimate_receipt, cancel_receipt),
                control_actions=(),
            )

        candidate_ids = [provider.provider_id, *request.fallback_provider_ids]
        retry_count = 0
        timeout_count = 0
        fallback_reason: str | None = None
        last_error: str | None = None
        attempts: list[ModelAttemptReceipt] = []
        usage_receipts: list[ModelUsageReceipt] = [estimate_receipt]
        control_actions: list[ModelControlAction] = []

        for attempt_index, provider_id in enumerate(candidate_ids):
            active_provider = self._select_provider(request.category, provider_id)
            attempt_id = _build_attempt_id(call_id, active_provider.provider_id, attempt_index)
            start = time.perf_counter()
            try:
                output = active_provider.invoke(request)
                output, structured_output, repair_record = _validate_structured_output(request, output)
            except ModelGatewayTimeoutError as exc:
                retry_count += 1
                timeout_count += 1
                fallback_reason = fallback_reason or f"timeout:{active_provider.provider_id}"
                last_error = str(exc)
                receipt = self._build_usage_receipt(
                    request=request,
                    call_id=call_id,
                    attempt_id=attempt_id,
                    kind=ModelUsageKind.OBSERVED,
                    pricing_version=binding.pricing_version,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=0,
                )
                usage_receipts.append(receipt)
                control_actions.append(
                    _control_action(
                        call_id=call_id,
                        action_type=ModelControlActionType.RECONCILE,
                        reason="provider_may_have_executed_after_timeout",
                        attempt_id=attempt_id,
                    )
                )
                control_actions.append(
                    _control_action(
                        call_id=call_id,
                        action_type=ModelControlActionType.FALLBACK if attempt_index + 1 < len(candidate_ids) else ModelControlActionType.ESCALATE,
                        reason="timeout_boundary_after_attempt",
                        attempt_id=attempt_id,
                    )
                )
                attempts.append(
                    ModelAttemptReceipt(
                        attempt_id=attempt_id,
                        provider_id=active_provider.provider_id,
                        model_id=active_provider.model_id,
                        adapter_version=binding.adapter_version,
                        state=ModelAttemptState.UNKNOWN_RECONCILE,
                        dispatch_index=attempt_index,
                        failure_code="MODEL_TIMEOUT_UNKNOWN",
                        original_error_ref=_error_ref(exc),
                        usage_receipt_id=receipt.usage_receipt_id,
                        reconcile_required=True,
                    )
                )
                continue
            except ModelGatewayProviderError as exc:
                retry_count += 1
                fallback_reason = fallback_reason or f"error:{active_provider.provider_id}"
                last_error = str(exc)
                receipt = self._build_usage_receipt(
                    request=request,
                    call_id=call_id,
                    attempt_id=attempt_id,
                    kind=ModelUsageKind.OBSERVED,
                    pricing_version=binding.pricing_version,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=0,
                )
                usage_receipts.append(receipt)
                control_actions.append(
                    _control_action(
                        call_id=call_id,
                        action_type=ModelControlActionType.FALLBACK if attempt_index + 1 < len(candidate_ids) else ModelControlActionType.ESCALATE,
                        reason="provider_error_boundary_after_attempt",
                        attempt_id=attempt_id,
                    )
                )
                attempts.append(
                    ModelAttemptReceipt(
                        attempt_id=attempt_id,
                        provider_id=active_provider.provider_id,
                        model_id=active_provider.model_id,
                        adapter_version=binding.adapter_version,
                        state=ModelAttemptState.FAILED,
                        dispatch_index=attempt_index,
                        failure_code="MODEL_PROVIDER_ERROR",
                        original_error_ref=_error_ref(exc),
                        usage_receipt_id=receipt.usage_receipt_id,
                    )
                )
                continue
            except ModelGatewayCancellationError as exc:
                retry_count += 1
                last_error = str(exc)
                receipt = self._build_usage_receipt(
                    request=request,
                    call_id=call_id,
                    attempt_id=attempt_id,
                    kind=ModelUsageKind.OBSERVED,
                    pricing_version=binding.pricing_version,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=0,
                )
                usage_receipts.append(receipt)
                attempts.append(
                    ModelAttemptReceipt(
                        attempt_id=attempt_id,
                        provider_id=active_provider.provider_id,
                        model_id=active_provider.model_id,
                        adapter_version=binding.adapter_version,
                        state=ModelAttemptState.CANCELLED,
                        dispatch_index=attempt_index,
                        failure_code="MODEL_CANCELLED",
                        original_error_ref=_error_ref(exc),
                        usage_receipt_id=receipt.usage_receipt_id,
                    )
                )
                break

            latency_ms = round((time.perf_counter() - start) * 1000, 3)
            active_prompt_tokens = _estimate_tokens(request.prompt)
            active_completion_tokens = active_provider.estimate_completion_tokens(
                active_prompt_tokens,
                request.max_output_tokens,
            )
            metrics = self._build_metrics(
                request=request,
                provider=active_provider,
                prompt_tokens=active_prompt_tokens,
                completion_tokens=active_completion_tokens,
                latency_ms=latency_ms,
                retry_count=retry_count if attempt_index else 0,
                timeout_count=timeout_count,
                fallback_reason=fallback_reason,
            )
            receipt = self._build_usage_receipt(
                request=request,
                call_id=call_id,
                attempt_id=attempt_id,
                kind=ModelUsageKind.OBSERVED,
                pricing_version=binding.pricing_version,
                prompt_tokens=active_prompt_tokens,
                completion_tokens=active_completion_tokens,
            )
            usage_receipts.append(receipt)
            if repair_record is not None:
                control_actions.append(
                    _control_action(
                        call_id=call_id,
                        action_type=ModelControlActionType.REPAIR,
                        reason=repair_record.failure_code,
                        attempt_id=attempt_id,
                    )
                )
            attempts.append(
                ModelAttemptReceipt(
                    attempt_id=attempt_id,
                    provider_id=active_provider.provider_id,
                    model_id=active_provider.model_id,
                    adapter_version=binding.adapter_version,
                    state=ModelAttemptState.SUCCEEDED,
                    dispatch_index=attempt_index,
                    usage_receipt_id=receipt.usage_receipt_id,
                )
            )
            trace_event = self._build_trace_event(
                event_type="model_call_completed",
                request=request,
                metrics=metrics,
                budget_verdict=budget_verdict,
                call_id=call_id,
                call_state=ModelCallState.SUCCEEDED,
                binding=binding,
                attempts=tuple(attempts),
                usage_receipts=tuple(usage_receipts),
                control_actions=tuple(control_actions),
            )
            return ModelGatewayResult(
                status="succeeded",
                output=output,
                metrics=metrics,
                budget_verdict=budget_verdict,
                trace_event=trace_event,
                call_id=call_id,
                call_state=ModelCallState.SUCCEEDED,
                binding=binding,
                attempts=tuple(attempts),
                usage_receipts=tuple(usage_receipts),
                control_actions=tuple(control_actions),
                selected_attempt_id=attempt_id,
                structured_output=structured_output,
                repair_record=repair_record,
            )

        failed_metrics = self._build_metrics(
            request=request,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=0.0,
            retry_count=retry_count,
            timeout_count=timeout_count,
            fallback_reason=fallback_reason,
        )
        final_state = ModelCallState.CANCELLED if attempts and attempts[-1].state == ModelAttemptState.CANCELLED else ModelCallState.FAILED
        if final_state == ModelCallState.FAILED:
            if not any(action.action_type == ModelControlActionType.ESCALATE for action in control_actions):
                control_actions.append(
                    _control_action(
                        call_id=call_id,
                        action_type=ModelControlActionType.ESCALATE,
                        reason="all_model_attempts_failed",
                        attempt_id=attempts[-1].attempt_id if attempts else None,
                    )
                )
            control_actions.append(
                _control_action(
                    call_id=call_id,
                    action_type=ModelControlActionType.REPLAN_PROPOSAL,
                    reason="agent_core_may_replan_after_model_failure",
                    attempt_id=attempts[-1].attempt_id if attempts else None,
                    owner="AGENT_CORE",
                )
            )
        trace_event = self._build_trace_event(
            event_type="model_call_failed",
            request=request,
            metrics=failed_metrics,
            budget_verdict=budget_verdict,
            error=last_error,
            call_id=call_id,
            call_state=final_state,
            binding=binding,
            attempts=tuple(attempts),
            usage_receipts=tuple(usage_receipts),
            control_actions=tuple(control_actions),
        )
        return ModelGatewayResult(
            status="cancelled" if final_state == ModelCallState.CANCELLED else "failed",
            output="",
            metrics=failed_metrics,
            budget_verdict=budget_verdict,
            trace_event=trace_event,
            call_id=call_id,
            call_state=final_state,
            binding=binding,
            attempts=tuple(attempts),
            usage_receipts=tuple(usage_receipts),
            control_actions=tuple(control_actions),
        )

    def stream(self, request: ModelGatewayRequest) -> ModelStreamResult:
        _ensure_gateway_domain_boundary(request)
        provider = self._select_provider(request.category, request.provider_id)
        binding = self._build_binding(request, provider)
        call_id = "model_call_" + binding.binding_hash[:16]
        attempt_id = _build_attempt_id(call_id, provider.provider_id, 0)
        provider_chunks = _provider_stream(provider, request)
        gateway_chunks = _normalize_stream_chunks(call_id, provider_chunks)
        product_events = _build_product_stream_events(call_id, gateway_chunks)
        prompt_tokens = _estimate_tokens(request.prompt)
        completion_tokens = _estimate_tokens(" ".join(chunk.content for chunk in gateway_chunks if not chunk.duplicate))
        usage_receipt = self._build_usage_receipt(
            request=request,
            call_id=call_id,
            attempt_id=attempt_id,
            kind=ModelUsageKind.OBSERVED,
            pricing_version=binding.pricing_version,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        attempt = ModelAttemptReceipt(
            attempt_id=attempt_id,
            provider_id=provider.provider_id,
            model_id=provider.model_id,
            adapter_version=binding.adapter_version,
            state=ModelAttemptState.SUCCEEDED,
            dispatch_index=0,
            usage_receipt_id=usage_receipt.usage_receipt_id,
        )
        return ModelStreamResult(
            call_id=call_id,
            binding=binding,
            attempt=attempt,
            gateway_chunks=tuple(gateway_chunks),
            product_events=tuple(product_events),
            usage_receipts=(usage_receipt,),
        )

    def embed_batch(
        self,
        *,
        texts: tuple[str, ...],
        revision: str,
        dimension: int,
        normalization: Literal["NONE", "L2", "UNIT"],
        index_generation: str,
    ) -> tuple[ModelEmbeddingResult, ...]:
        results: list[ModelEmbeddingResult] = []
        for index, text in enumerate(texts):
            if not text.strip():
                results.append(
                    ModelEmbeddingResult(
                        embedding_id=f"embedding_{index}",
                        text_ref=f"text:{index}",
                        vector=(),
                        revision=revision,
                        dimension=dimension,
                        normalization=normalization,
                        index_generation=index_generation,
                        state="FAILED",
                        failure_reason="empty_text",
                    )
                )
                continue
            vector = _deterministic_vector(text, dimension, normalization)
            results.append(
                ModelEmbeddingResult(
                    embedding_id=f"embedding_{_stable_hash([text, revision, index_generation])[:12]}",
                    text_ref=f"text:{index}",
                    vector=vector,
                    revision=revision,
                    dimension=dimension,
                    normalization=normalization,
                    index_generation=index_generation,
                    state="SUCCEEDED",
                )
            )
        return tuple(results)

    def rerank(self, items: tuple[tuple[str, float], ...]) -> tuple[ModelRerankItem, ...]:
        ranked = sorted((ModelRerankItem(item_id=item_id, score=score, rank=0) for item_id, score in items), key=lambda item: (-item.score, item.item_id))
        return tuple(ModelRerankItem(item_id=item.item_id, score=item.score, rank=index + 1) for index, item in enumerate(ranked))

    def analyze_vision(
        self,
        *,
        source_lineage_ref: str,
        page_number: int,
        bbox: tuple[float, float, float, float],
        text: str,
    ) -> ModelVisionRegion:
        return ModelVisionRegion(
            page_number=page_number,
            bbox=bbox,
            text=text,
            source_lineage_ref=source_lineage_ref,
        )

    def transcribe(self, segments: tuple[tuple[int, int, str, bool], ...]) -> tuple[ModelTranscriptionSegment, ...]:
        return tuple(
            ModelTranscriptionSegment(
                segment_id=f"segment_{index}",
                start_ms=start_ms,
                end_ms=end_ms,
                text=text,
                partial=partial,
            )
            for index, (start_ms, end_ms, text, partial) in enumerate(segments)
        )

    def classify(
        self,
        *,
        label_scores: dict[str, float],
        threshold: float,
        calibration_ref: str,
    ) -> ModelClassificationResult:
        label, score = max(label_scores.items(), key=lambda item: item[1])
        abstained = score < threshold
        return ModelClassificationResult(
            label=None if abstained else label,
            score=score,
            threshold=threshold,
            calibration_ref=calibration_ref,
            abstained=abstained,
        )

    def judge(
        self,
        request: ModelGatewayRequest,
        *,
        score: float,
        rationale: str,
    ) -> ModelJudgeResult:
        provider = self._select_provider(ModelCategory.EVAL_JUDGE, request.provider_id)
        prompt_tokens = _estimate_tokens(request.prompt)
        completion_tokens = provider.estimate_completion_tokens(prompt_tokens, request.max_output_tokens)
        budget_verdict = self._evaluate_budget(
            request=request,
            provider=provider,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        return ModelJudgeResult(
            score=score,
            rationale_ref="judge_rationale_" + _stable_hash([request.prompt, rationale])[:16],
            budget_verdict=budget_verdict,
            gateway_audited=True,
        )

    def compress_context(
        self,
        *,
        source_text: str,
        lineage_refs: tuple[str, ...],
        constraints: tuple[str, ...],
        conflict_refs: tuple[str, ...],
        distortion_risks: tuple[str, ...],
    ) -> ModelCompressedContext:
        return ModelCompressedContext(
            compression_id="ctx_compress_" + _stable_hash([source_text, lineage_refs, constraints])[:16],
            summary=source_text[:240],
            lineage_refs=lineage_refs,
            preserved_constraints=constraints,
            conflict_refs=conflict_refs,
            distortion_risks=distortion_risks,
        )

    def memory_candidate(self, *, payload: dict[str, Any], source_model_call_ref: str) -> ModelOutputCandidate:
        return ModelOutputCandidate(
            candidate_id="memory_candidate_" + _stable_hash([payload, source_model_call_ref])[:16],
            target_owner="MEMORY",
            payload=dict(payload),
            source_model_call_ref=source_model_call_ref,
        )

    def security_risk_proposal(
        self,
        *,
        risk_level: Literal["LOW", "MEDIUM", "HIGH", "BLOCK"],
        evidence_refs: tuple[str, ...],
        source_model_call_ref: str,
    ) -> ModelRiskProposal:
        return ModelRiskProposal(
            proposal_id="risk_proposal_" + _stable_hash([risk_level, evidence_refs, source_model_call_ref])[:16],
            target_owner="SECURITY",
            risk_level=risk_level,
            evidence_refs=evidence_refs,
            source_model_call_ref=source_model_call_ref,
        )

    def tool_action_proposal(
        self,
        *,
        action_name: str,
        args: dict[str, Any],
        source_model_call_ref: str,
        target_owner: Literal["AGENT_CORE", "TOOL_RUNTIME"] = "AGENT_CORE",
    ) -> ModelActionProposal:
        return ModelActionProposal(
            proposal_id="action_proposal_" + _stable_hash([action_name, args, source_model_call_ref, target_owner])[:16],
            target_owner=target_owner,
            action_name=action_name,
            args_hash=_stable_hash(args),
            source_model_call_ref=source_model_call_ref,
        )

    def settle_usage(self, receipt: ModelUsageReceipt) -> ModelUsageReceipt:
        return ModelUsageReceipt(
            usage_receipt_id="usage_settled_" + _stable_hash([receipt.usage_receipt_id, receipt.pricing_version])[:16],
            call_id=receipt.call_id,
            attempt_id=receipt.attempt_id,
            kind=ModelUsageKind.SETTLED,
            pricing_version=receipt.pricing_version,
            prompt_tokens=receipt.prompt_tokens,
            completion_tokens=receipt.completion_tokens,
            total_tokens=receipt.total_tokens,
            estimated_cost=receipt.estimated_cost,
        )

    def correct_usage(
        self,
        receipt: ModelUsageReceipt,
        *,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> ModelUsageReceipt:
        total_tokens = prompt_tokens + completion_tokens
        return ModelUsageReceipt(
            usage_receipt_id="usage_correction_" + _stable_hash([receipt.usage_receipt_id, total_tokens])[:16],
            call_id=receipt.call_id,
            attempt_id=receipt.attempt_id,
            kind=ModelUsageKind.CORRECTION,
            pricing_version=receipt.pricing_version,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=_estimate_cost(ModelCategory.CHAT, total_tokens),
        )

    def reserve_quota(
        self,
        *,
        policy: ModelQuotaPolicy,
        requested_tokens: int,
        expected_generation: int,
    ) -> ModelQuotaReservation:
        current_generation = self._quota_generations.get(policy.quota_scope, policy.generation)
        current_reserved = self._quota_reserved_tokens.get(policy.quota_scope, policy.reserved_tokens)
        if expected_generation != current_generation:
            return ModelQuotaReservation(
                reservation_id="quota_rejected_" + _stable_hash([policy.quota_scope, requested_tokens, expected_generation])[:16],
                quota_scope=policy.quota_scope,
                reserved_tokens=0,
                expected_generation=expected_generation,
                committed_generation=current_generation,
                accepted=False,
                reason="generation_mismatch",
            )
        if current_reserved + requested_tokens > policy.token_limit:
            return ModelQuotaReservation(
                reservation_id="quota_rejected_" + _stable_hash([policy.quota_scope, requested_tokens, current_generation, "limit"])[:16],
                quota_scope=policy.quota_scope,
                reserved_tokens=0,
                expected_generation=expected_generation,
                committed_generation=current_generation,
                accepted=False,
                reason="quota_exhausted",
            )
        committed_generation = current_generation + 1
        self._quota_generations[policy.quota_scope] = committed_generation
        self._quota_reserved_tokens[policy.quota_scope] = current_reserved + requested_tokens
        return ModelQuotaReservation(
            reservation_id="quota_" + _stable_hash([policy.quota_scope, requested_tokens, committed_generation])[:16],
            quota_scope=policy.quota_scope,
            reserved_tokens=requested_tokens,
            expected_generation=expected_generation,
            committed_generation=committed_generation,
            accepted=True,
            reason="reserved",
        )

    def evaluate_provider_health(
        self,
        *,
        provider_id: str,
        model_id: str,
        region: str,
        operation: ModelOperation | str,
        adapter_version: str,
        window_started_at: float,
        window_ended_at: float,
        success_count: int,
        failure_count: int,
        evidence_ref: str | None,
        unhealthy_failure_rate: float = 0.5,
    ) -> ModelProviderHealthWindow:
        total = success_count + failure_count
        if success_count < 0 or failure_count < 0:
            raise ModelGatewayProviderError("provider health counts must be non-negative")
        if window_ended_at < window_started_at:
            raise ModelGatewayProviderError("provider health window end must not precede start")
        if total == 0 or not evidence_ref:
            status = ModelProviderHealthStatus.UNKNOWN
        elif failure_count / total > unhealthy_failure_rate:
            status = ModelProviderHealthStatus.UNHEALTHY
        else:
            status = ModelProviderHealthStatus.HEALTHY
        return ModelProviderHealthWindow(
            provider_id=provider_id,
            model_id=model_id,
            region=region,
            operation=ModelOperation(operation),
            adapter_version=adapter_version,
            window_started_at=window_started_at,
            window_ended_at=window_ended_at,
            success_count=success_count,
            failure_count=failure_count,
            evidence_ref=evidence_ref,
            status=status,
        )

    def evaluate_circuit(self, health: ModelProviderHealthWindow) -> ModelCircuitDecision:
        key = ModelCircuitKey(
            provider_id=health.provider_id,
            model_id=health.model_id,
            region=health.region,
            operation=health.operation,
            adapter_version=health.adapter_version,
        )
        if health.status == ModelProviderHealthStatus.HEALTHY:
            return ModelCircuitDecision(
                key=key,
                status=ModelCircuitStatus.CLOSED,
                reason="provider_health_window_healthy",
                health_evidence_ref=health.evidence_ref,
            )
        return ModelCircuitDecision(
            key=key,
            status=ModelCircuitStatus.OPEN,
            reason=f"provider_health_window_{health.status.value.lower()}",
            health_evidence_ref=health.evidence_ref,
        )

    def capability_profile(
        self,
        *,
        capability_id: str,
        provider_id: str,
        model_id: str,
        operation: ModelOperation | str,
        status: ModelCapabilityStatus | str,
        evidence_ref: str,
    ) -> ModelCapabilityProfile:
        normalized_status = ModelCapabilityStatus(status)
        return ModelCapabilityProfile(
            capability_id=capability_id,
            provider_id=provider_id,
            model_id=model_id,
            operation=ModelOperation(operation),
            status=normalized_status,
            evidence_ref=evidence_ref,
            dispatch_allowed=normalized_status != ModelCapabilityStatus.REVOKED,
            requires_operator_review=normalized_status
            in {ModelCapabilityStatus.DEGRADED, ModelCapabilityStatus.STALE, ModelCapabilityStatus.REVOKED},
        )

    def adapter_conformance_suite(
        self,
        *,
        operation: ModelOperation | str,
        adapter_version: str,
        sdk_api_version: str,
        model_mapping_version: str,
        evidence_ref: str,
        passed: bool,
    ) -> ModelAdapterConformanceSuite:
        normalized_operation = ModelOperation(operation)
        return ModelAdapterConformanceSuite(
            suite_id="conformance_"
            + _stable_hash(
                [
                    normalized_operation.value,
                    adapter_version,
                    sdk_api_version,
                    model_mapping_version,
                    evidence_ref,
                ]
            )[:16],
            operation=normalized_operation,
            adapter_version=adapter_version,
            sdk_api_version=sdk_api_version,
            model_mapping_version=model_mapping_version,
            evidence_ref=evidence_ref,
            passed=passed,
        )

    def validate_adapter_conformance(
        self,
        suite: ModelAdapterConformanceSuite,
        *,
        operation: ModelOperation | str,
        adapter_version: str,
        sdk_api_version: str,
        model_mapping_version: str,
    ) -> ModelAdapterConformanceVerdict:
        if not suite.passed:
            return ModelAdapterConformanceVerdict(
                suite_id=suite.suite_id,
                valid=False,
                requires_revalidation=True,
                reason="suite_failed",
            )
        if suite.operation != ModelOperation(operation):
            return ModelAdapterConformanceVerdict(
                suite_id=suite.suite_id,
                valid=False,
                requires_revalidation=True,
                reason="operation_changed",
            )
        if suite.adapter_version != adapter_version:
            return ModelAdapterConformanceVerdict(
                suite_id=suite.suite_id,
                valid=False,
                requires_revalidation=True,
                reason="adapter_changed",
            )
        if suite.sdk_api_version != sdk_api_version:
            return ModelAdapterConformanceVerdict(
                suite_id=suite.suite_id,
                valid=False,
                requires_revalidation=True,
                reason="sdk_api_changed",
            )
        if suite.model_mapping_version != model_mapping_version:
            return ModelAdapterConformanceVerdict(
                suite_id=suite.suite_id,
                valid=False,
                requires_revalidation=True,
                reason="model_mapping_changed",
            )
        return ModelAdapterConformanceVerdict(
            suite_id=suite.suite_id,
            valid=True,
            requires_revalidation=False,
            reason="current",
        )

    def interpret_provider_signal(
        self,
        *,
        signal_kind: Literal["enum", "event", "error"],
        raw_value: str,
        known_values: Iterable[str],
    ) -> ModelProviderSignalVerdict:
        normalized_known = {str(value) for value in known_values}
        if raw_value not in normalized_known:
            return ModelProviderSignalVerdict(
                signal_kind=signal_kind,
                raw_value=raw_value,
                status=ModelProviderSignalStatus.UNKNOWN_FAIL_CLOSED,
                success=False,
                reason="unknown_provider_signal",
            )
        return ModelProviderSignalVerdict(
            signal_kind=signal_kind,
            raw_value=raw_value,
            status=ModelProviderSignalStatus.ACCEPTED,
            success=True,
            reason="known_provider_signal",
        )

    def create_config_snapshot(
        self,
        *,
        config_version: str,
        generation: int,
        payload: dict[str, Any],
    ) -> ModelGatewayConfigSnapshot:
        canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return ModelGatewayConfigSnapshot(
            config_version=config_version,
            generation=generation,
            content_sha256=hashlib.sha256(canonical_json.encode("utf-8")).hexdigest(),
            payload_canonical_json=canonical_json,
        )

    def activate_config_snapshot(
        self,
        snapshot: ModelGatewayConfigSnapshot,
        *,
        expected_generation: int,
        active_generation: int,
        validation_passed: bool,
        replay_passed: bool,
        canary_passed: bool,
        rollback_snapshot_ref: str | None,
    ) -> ModelConfigActivationDecision:
        completed: list[ModelConfigActivationGate] = []
        if validation_passed:
            completed.append(ModelConfigActivationGate.VALIDATION)
        else:
            return _config_activation_rejected(snapshot, expected_generation, active_generation, tuple(completed), rollback_snapshot_ref, "validation_failed")
        if replay_passed:
            completed.append(ModelConfigActivationGate.REPLAY)
        else:
            return _config_activation_rejected(snapshot, expected_generation, active_generation, tuple(completed), rollback_snapshot_ref, "replay_failed")
        if canary_passed:
            completed.append(ModelConfigActivationGate.CANARY)
        else:
            return _config_activation_rejected(snapshot, expected_generation, active_generation, tuple(completed), rollback_snapshot_ref, "canary_failed")
        if expected_generation != active_generation:
            return _config_activation_rejected(snapshot, expected_generation, active_generation, tuple(completed), rollback_snapshot_ref, "generation_mismatch")
        completed.append(ModelConfigActivationGate.CAS)
        if rollback_snapshot_ref is None:
            return _config_activation_rejected(snapshot, expected_generation, active_generation, tuple(completed), rollback_snapshot_ref, "missing_rollback_snapshot")
        completed.append(ModelConfigActivationGate.ROLLBACK)
        return ModelConfigActivationDecision(
            snapshot=snapshot,
            expected_generation=expected_generation,
            committed_generation=active_generation + 1,
            accepted=True,
            completed_gates=tuple(completed),
            rollback_snapshot_ref=rollback_snapshot_ref,
            reason="activated",
        )

    def bind_call_config_snapshot(
        self,
        *,
        call_id: str,
        snapshot: ModelGatewayConfigSnapshot,
    ) -> ModelCallConfigBinding:
        return ModelCallConfigBinding(
            call_id=call_id,
            config_snapshot_id=snapshot.snapshot_id,
            config_version=snapshot.config_version,
            config_hash=snapshot.content_sha256,
        )

    def provider_lifecycle_record(
        self,
        *,
        provider_id: str,
        model_id: str,
        state: ModelProviderLifecycleState | str,
        generation: int,
        evidence_ref: str,
    ) -> ModelProviderLifecycleRecord:
        normalized_state = ModelProviderLifecycleState(state)
        return ModelProviderLifecycleRecord(
            provider_id=provider_id,
            model_id=model_id,
            state=normalized_state,
            generation=generation,
            evidence_ref=evidence_ref,
            accepts_new_dispatch=normalized_state in {
                ModelProviderLifecycleState.ENABLED,
                ModelProviderLifecycleState.DEPRECATED,
            },
        )

    def emergency_disable_provider(
        self,
        *,
        provider_id: str,
        model_id: str,
        generation: int,
        reason: str,
    ) -> ModelEmergencyDisableDecision:
        return ModelEmergencyDisableDecision(
            provider_id=provider_id,
            model_id=model_id,
            generation=generation,
            blocks_new_dispatch=True,
            late_results_isolated=True,
            quarantine_ref="provider_disable_quarantine_" + _stable_hash([provider_id, model_id, generation, reason])[:16],
        )

    def evaluate_admission(
        self,
        *,
        tenant_id: str,
        role: ModelRole | str,
        provider_id: str,
        model_id: str,
        operation: ModelOperation | str,
        requested_units: int,
        capacity_by_key: dict[str, int],
        tenant_inflight: int,
        tenant_fairness_limit: int,
        reserved_capacity_units: int,
        waiting_age_ms: int,
        starvation_threshold_ms: int,
    ) -> ModelAdmissionDecision:
        normalized_role = ModelRole(role)
        normalized_operation = ModelOperation(operation)
        keys = {
            ModelAdmissionLayer.GLOBAL: "global",
            ModelAdmissionLayer.PROVIDER: f"provider:{provider_id}",
            ModelAdmissionLayer.MODEL: f"model:{provider_id}:{model_id}",
            ModelAdmissionLayer.OPERATION: f"operation:{normalized_operation.value}",
            ModelAdmissionLayer.ROLE: f"role:{normalized_role.value}",
        }
        checks = tuple(
            ModelAdmissionLayerCheck(
                layer=layer,
                capacity_key=key,
                requested_units=requested_units,
                available_units=int(capacity_by_key.get(key, 0)),
                accepted=int(capacity_by_key.get(key, 0)) >= requested_units,
            )
            for layer, key in keys.items()
        )
        if any(not check.accepted for check in checks):
            return ModelAdmissionDecision(
                admission_id="admission_" + _stable_hash([tenant_id, normalized_role.value, provider_id, model_id, requested_units, "capacity"])[:16],
                tenant_id=tenant_id,
                role=normalized_role,
                accepted=False,
                reason="capacity_exhausted",
                layer_checks=checks,
                reserved_capacity_used=0,
                fairness_limited=False,
                starvation_prevention_applied=False,
            )
        starvation_prevention = waiting_age_ms >= starvation_threshold_ms
        fairness_limited = tenant_inflight >= tenant_fairness_limit and reserved_capacity_units <= 0 and not starvation_prevention
        if fairness_limited:
            return ModelAdmissionDecision(
                admission_id="admission_" + _stable_hash([tenant_id, normalized_role.value, provider_id, model_id, requested_units, "fairness"])[:16],
                tenant_id=tenant_id,
                role=normalized_role,
                accepted=False,
                reason="tenant_fairness_limited",
                layer_checks=checks,
                reserved_capacity_used=0,
                fairness_limited=True,
                starvation_prevention_applied=False,
            )
        reserved_used = min(requested_units, reserved_capacity_units) if tenant_inflight >= tenant_fairness_limit else 0
        return ModelAdmissionDecision(
            admission_id="admission_" + _stable_hash([tenant_id, normalized_role.value, provider_id, model_id, requested_units, reserved_used, waiting_age_ms])[:16],
            tenant_id=tenant_id,
            role=normalized_role,
            accepted=True,
            reason="reserved_capacity" if reserved_used else "admitted",
            layer_checks=checks,
            reserved_capacity_used=reserved_used,
            fairness_limited=False,
            starvation_prevention_applied=starvation_prevention,
        )

    def queue_request_binding(
        self,
        *,
        call_id: str,
        deadline_at: float,
        security_epoch_ref: str,
        budget_verdict: BudgetVerdict,
        config_binding: ModelCallConfigBinding,
    ) -> ModelQueuedRequestBinding:
        return ModelQueuedRequestBinding(
            queue_entry_id="model_queue_" + _stable_hash([call_id, deadline_at, security_epoch_ref, config_binding.config_snapshot_id])[:16],
            call_id=call_id,
            deadline_at=deadline_at,
            security_epoch_ref=security_epoch_ref,
            budget_verdict=budget_verdict,
            config_binding=config_binding,
        )

    def evaluate_overload(
        self,
        *,
        current_load_units: int,
        capacity_units: int,
        required_gates: Iterable[str] = ("security", "validation", "usage", "audit", "budget"),
    ) -> ModelOverloadDecision:
        gate_tuple = tuple(str(gate) for gate in required_gates)
        if current_load_units <= capacity_units:
            return ModelOverloadDecision(
                state=ModelOverloadState.NORMAL,
                backpressure=False,
                load_shedding=False,
                reason="within_capacity",
                preserved_gates=gate_tuple,
            )
        if current_load_units <= capacity_units * 2:
            return ModelOverloadDecision(
                state=ModelOverloadState.BACKPRESSURE,
                backpressure=True,
                load_shedding=False,
                reason="over_capacity_backpressure",
                preserved_gates=gate_tuple,
            )
        return ModelOverloadDecision(
            state=ModelOverloadState.LOAD_SHEDDING,
            backpressure=True,
            load_shedding=True,
            reason="over_capacity_load_shedding",
            preserved_gates=gate_tuple,
        )

    def cache_policy(
        self,
        *,
        cache_kind: ModelCacheKind | str,
        tenant_id: str,
        config_version: str,
        schema_version: str,
        model_version: str,
        adapter_version: str,
        security_epoch_ref: str,
        enabled: bool | None = None,
    ) -> ModelCachePolicy:
        normalized_kind = ModelCacheKind(cache_kind)
        return ModelCachePolicy(
            cache_kind=normalized_kind,
            enabled=False if enabled is None and normalized_kind == ModelCacheKind.RESULT else bool(enabled),
            tenant_id=tenant_id,
            config_version=config_version,
            schema_version=schema_version,
            model_version=model_version,
            adapter_version=adapter_version,
            security_epoch_ref=security_epoch_ref,
        )

    def cache_key(
        self,
        *,
        policy: ModelCachePolicy,
        prompt_hash: str,
    ) -> ModelCacheKey:
        version_scope = (
            policy.config_version,
            policy.schema_version,
            policy.model_version,
            policy.adapter_version,
            policy.security_epoch_ref,
        )
        return ModelCacheKey(
            cache_kind=policy.cache_kind,
            tenant_id=policy.tenant_id,
            version_scope=version_scope,
            cache_key="cache_"
            + _stable_hash(
                [
                    policy.cache_kind.value,
                    policy.tenant_id,
                    *version_scope,
                    prompt_hash,
                ]
            )[:24],
        )

    def lookup_cache(
        self,
        *,
        policy: ModelCachePolicy,
        key: ModelCacheKey,
        stored_result_ref: str | None,
    ) -> ModelCacheLookup:
        if key.cache_kind != policy.cache_kind or key.tenant_id != policy.tenant_id:
            return ModelCacheLookup(
                cache_kind=policy.cache_kind,
                key=key,
                hit=False,
                provider_attempt_allowed=True,
                reason="cache_scope_mismatch",
            )
        if key.version_scope != (
            policy.config_version,
            policy.schema_version,
            policy.model_version,
            policy.adapter_version,
            policy.security_epoch_ref,
        ):
            return ModelCacheLookup(
                cache_kind=policy.cache_kind,
                key=key,
                hit=False,
                provider_attempt_allowed=True,
                reason="cache_version_mismatch",
            )
        if not policy.enabled or stored_result_ref is None:
            return ModelCacheLookup(
                cache_kind=policy.cache_kind,
                key=key,
                hit=False,
                provider_attempt_allowed=True,
                reason="cache_disabled_or_empty",
            )
        return ModelCacheLookup(
            cache_kind=policy.cache_kind,
            key=key,
            hit=True,
            provider_attempt_allowed=False,
            reason="cache_hit",
        )

    def cache_reuse_receipt(
        self,
        *,
        lookup: ModelCacheLookup,
        source_result_ref: str,
        call_id: str,
    ) -> ModelCacheReuseReceipt:
        if not lookup.hit:
            raise ModelGatewayProviderError("cache reuse receipt requires cache hit")
        return ModelCacheReuseReceipt(
            reuse_receipt_id="cache_reuse_" + _stable_hash([lookup.key.cache_key, source_result_ref, call_id])[:16],
            cache_key=lookup.key.cache_key,
            source_result_ref=source_result_ref,
            call_id=call_id,
        )

    def invalidate_cache(
        self,
        *,
        key: ModelCacheKey,
        reason: Literal["revocation", "deletion", "model_retirement", "validity_changed"],
    ) -> ModelCacheInvalidationDecision:
        return ModelCacheInvalidationDecision(
            cache_key=key.cache_key,
            invalidated=True,
            reason=reason,
            tombstone_ref="cache_tombstone_" + _stable_hash([key.cache_key, reason])[:16],
        )

    def operational_command(
        self,
        *,
        command_kind: ModelOperationalCommandKind | str,
        command_version: str,
        target_ref: str,
        expected_generation: int,
        payload: dict[str, Any],
        high_risk: bool,
        authorized_by: str | None = None,
        approval_ref: str | None = None,
        audit_ref: str | None = None,
    ) -> ModelOperationalCommand:
        normalized_kind = ModelOperationalCommandKind(command_kind)
        payload_hash = _stable_hash(payload)
        return ModelOperationalCommand(
            command_id="model_op_cmd_" + _stable_hash([normalized_kind.value, command_version, target_ref, expected_generation, payload_hash])[:16],
            command_kind=normalized_kind,
            command_version=command_version,
            target_ref=target_ref,
            expected_generation=expected_generation,
            payload_hash=payload_hash,
            high_risk=high_risk,
            authorized_by=authorized_by,
            approval_ref=approval_ref,
            audit_ref=audit_ref,
        )

    def evaluate_operational_command(
        self,
        command: ModelOperationalCommand,
        *,
        active_generation: int,
    ) -> ModelOperationalCommandVerdict:
        if not command.command_version:
            return ModelOperationalCommandVerdict(
                command_id=command.command_id,
                accepted=False,
                reason="missing_command_version",
                committed_generation=active_generation,
            )
        if command.expected_generation != active_generation:
            return ModelOperationalCommandVerdict(
                command_id=command.command_id,
                accepted=False,
                reason="generation_mismatch",
                committed_generation=active_generation,
            )
        if command.high_risk and not (command.authorized_by and command.approval_ref and command.audit_ref):
            return ModelOperationalCommandVerdict(
                command_id=command.command_id,
                accepted=False,
                reason="missing_high_risk_controls",
                committed_generation=active_generation,
            )
        return ModelOperationalCommandVerdict(
            command_id=command.command_id,
            accepted=True,
            reason="accepted",
            committed_generation=active_generation + 1,
        )

    def retention_bindings(
        self,
        *,
        retention_until_by_subject: dict[ModelRetentionSubject | str, float],
        policy_ref_by_subject: dict[ModelRetentionSubject | str, str],
    ) -> tuple[ModelRetentionBinding, ...]:
        bindings: list[ModelRetentionBinding] = []
        for subject in ModelRetentionSubject:
            retention_until = retention_until_by_subject.get(subject, retention_until_by_subject.get(subject.value))
            policy_ref = policy_ref_by_subject.get(subject, policy_ref_by_subject.get(subject.value))
            if retention_until is None or policy_ref is None:
                raise ModelGatewayProviderError(f"missing retention binding for {subject.value}")
            bindings.append(
                ModelRetentionBinding(
                    subject=subject,
                    retention_policy_ref=str(policy_ref),
                    retention_until=float(retention_until),
                )
            )
        return tuple(bindings)

    def deletion_workflow(
        self,
        *,
        object_ref: str,
        tombstone: bool,
        visibility_revoked: bool,
        physical_cleanup_requested: bool,
        verification_passed: bool,
        legal_hold: bool = False,
    ) -> ModelDeletionWorkflow:
        steps: list[ModelDeletionStep] = []
        if tombstone:
            steps.append(ModelDeletionStep.TOMBSTONE)
        if visibility_revoked:
            steps.append(ModelDeletionStep.VISIBILITY_REVOCATION)
        cleanup_allowed = tombstone and visibility_revoked and physical_cleanup_requested and not legal_hold
        if cleanup_allowed:
            steps.append(ModelDeletionStep.PHYSICAL_CLEANUP)
        verified = cleanup_allowed and verification_passed
        if verified:
            steps.append(ModelDeletionStep.VERIFICATION)
        return ModelDeletionWorkflow(
            object_ref=object_ref,
            steps=tuple(steps),
            tombstone_ref="model_delete_tombstone_" + _stable_hash([object_ref])[:16],
            visibility_revoked=visibility_revoked,
            physical_cleanup_allowed=cleanup_allowed,
            verified=verified,
            legal_hold=legal_hold,
        )

    def sli_slo_dimension(
        self,
        *,
        call_id: str,
        attempt_id: str,
        operation: ModelOperation | str,
        role: ModelRole | str,
        tenant_id: str,
        provider_id: str,
        config_version: str,
        slo_ref: str,
    ) -> ModelSliSloDimension:
        return ModelSliSloDimension(
            call_id=call_id,
            attempt_id=attempt_id,
            operation=ModelOperation(operation),
            role=ModelRole(role),
            tenant_id=tenant_id,
            provider_id=provider_id,
            config_version=config_version,
            slo_ref=slo_ref,
        )

    def readiness_verdict(self, probe: ModelReadinessProbe) -> ModelReadinessVerdict:
        evidence = {
            "adapter": probe.adapter_evidence_ref,
            "security": probe.security_evidence_ref,
            "persistence": probe.persistence_evidence_ref,
            "usage": probe.usage_evidence_ref,
            "reconcile": probe.reconcile_evidence_ref,
            "capacity": probe.capacity_evidence_ref,
            "deletion": probe.deletion_evidence_ref,
        }
        missing = tuple(name for name, ref in evidence.items() if not ref)
        if probe.mock_only:
            return ModelReadinessVerdict(
                status=ModelReadinessStatus.NOT_READY,
                missing_evidence=missing,
                mock_only=True,
                reason="mock_only_not_ready",
            )
        if missing:
            return ModelReadinessVerdict(
                status=ModelReadinessStatus.NOT_READY,
                missing_evidence=missing,
                mock_only=False,
                reason="missing_evidence",
            )
        return ModelReadinessVerdict(
            status=ModelReadinessStatus.READY,
            missing_evidence=(),
            mock_only=False,
            reason="ready",
        )

    def adapter_rollout_plan(
        self,
        *,
        active_adapter_version: str,
        candidate_adapter_version: str,
        sdk_api_version: str,
        rollback_adapter_version: str,
    ) -> ModelAdapterRolloutPlan:
        return ModelAdapterRolloutPlan(
            active_adapter_version=active_adapter_version,
            candidate_adapter_version=candidate_adapter_version,
            sdk_api_version=sdk_api_version,
            modes=(
                ModelAdapterRolloutMode.PARALLEL,
                ModelAdapterRolloutMode.CANARY,
                ModelAdapterRolloutMode.DRAIN,
                ModelAdapterRolloutMode.ROLLBACK,
            ),
            rollback_adapter_version=rollback_adapter_version,
        )

    def provider_api_sunset_plan(
        self,
        *,
        provider_id: str,
        retiring_api_version: str,
        replacement_api_version: str,
        migration_evidence_ref: str,
        rollback_evidence_ref: str,
        compatibility_evidence_ref: str,
    ) -> ModelProviderApiSunsetPlan:
        if not (migration_evidence_ref and rollback_evidence_ref and compatibility_evidence_ref):
            raise ModelGatewayProviderError("provider api sunset requires migration, rollback, and compatibility evidence")
        return ModelProviderApiSunsetPlan(
            provider_id=provider_id,
            retiring_api_version=retiring_api_version,
            replacement_api_version=replacement_api_version,
            migration_evidence_ref=migration_evidence_ref,
            rollback_evidence_ref=rollback_evidence_ref,
            compatibility_evidence_ref=compatibility_evidence_ref,
        )

    def experiment_gate_verdict(
        self,
        *,
        experiment_id: str,
        security_passed: bool,
        capability_passed: bool,
        budget_passed: bool,
        deadline_passed: bool,
    ) -> ModelExperimentGateVerdict:
        gates = ("security", "capability", "budget", "deadline")
        if not security_passed:
            return ModelExperimentGateVerdict(experiment_id=experiment_id, allowed=False, gates=gates, reason="security_gate_failed")
        if not capability_passed:
            return ModelExperimentGateVerdict(experiment_id=experiment_id, allowed=False, gates=gates, reason="capability_gate_failed")
        if not budget_passed:
            return ModelExperimentGateVerdict(experiment_id=experiment_id, allowed=False, gates=gates, reason="budget_gate_failed")
        if not deadline_passed:
            return ModelExperimentGateVerdict(experiment_id=experiment_id, allowed=False, gates=gates, reason="deadline_gate_failed")
        return ModelExperimentGateVerdict(experiment_id=experiment_id, allowed=True, gates=gates, reason="allowed")

    def experiment_assignment(
        self,
        *,
        experiment_id: str,
        sticky_scope: str,
        subject_ref: str,
        variants: tuple[str, ...],
    ) -> ModelExperimentAssignment:
        if not variants:
            raise ModelGatewayProviderError("experiment assignment requires at least one variant")
        assignment_hash = _stable_hash([experiment_id, sticky_scope, subject_ref])
        variant = variants[int(assignment_hash[:8], 16) % len(variants)]
        return ModelExperimentAssignment(
            experiment_id=experiment_id,
            sticky_scope=sticky_scope,
            subject_ref=subject_ref,
            variant=variant,
            assignment_hash=assignment_hash,
        )

    def shadow_call_record(
        self,
        *,
        shadow_call_id: str,
        security_ref: str,
        budget_ref: str,
        usage_ref: str,
        trace_ref: str,
        retention_ref: str,
    ) -> ModelShadowCallRecord:
        return ModelShadowCallRecord(
            shadow_call_id=shadow_call_id,
            security_ref=security_ref,
            budget_ref=budget_ref,
            usage_ref=usage_ref,
            trace_ref=trace_ref,
            retention_ref=retention_ref,
        )

    def shadow_result(
        self,
        *,
        shadow_call_id: str,
        result_ref: str,
    ) -> ModelShadowResult:
        return ModelShadowResult(shadow_call_id=shadow_call_id, result_ref=result_ref)

    def result_validity_event(
        self,
        *,
        result_ref: str,
        previous_validity: str,
        new_validity: str,
        fact_owner: str,
        propagation_owner: str,
    ) -> ModelResultValidityEvent:
        event_id = "model_result_validity_" + _stable_hash([result_ref, previous_validity, new_validity, fact_owner])[:16]
        return ModelResultValidityEvent(
            event_id=event_id,
            result_ref=result_ref,
            previous_validity=previous_validity,
            new_validity=new_validity,
            fact_owner=fact_owner,
            propagation_owner=propagation_owner,
            propagation_allowed=fact_owner == propagation_owner,
        )

    def classify_failure(self, *, provider_id: str, raw_error_ref: str, raw_error_code: str) -> ModelFailureClassification:
        normalized = raw_error_code.strip().lower().replace(" ", "_").replace("-", "_")
        mapping = {
            "rate_limit": "PROVIDER_RATE_LIMIT",
            "timeout": "PROVIDER_TIMEOUT",
            "invalid_request": "PROVIDER_INVALID_REQUEST",
            "auth_error": "PROVIDER_AUTHENTICATION_FAILED",
        }
        return ModelFailureClassification(
            provider_id=provider_id,
            raw_error_ref=raw_error_ref,
            provider_neutral_code=mapping.get(normalized, "PROVIDER_UNKNOWN_FAILURE"),
        )

    def suggested_control_action(
        self,
        *,
        action: ModelControlActionType | str,
        suggested_by: str,
    ) -> ModelSuggestedControlAction:
        return ModelSuggestedControlAction(action=ModelControlActionType(action), suggested_by=suggested_by)

    def domain_event(
        self,
        *,
        event_type: str,
        event_version: str,
        sequence: int,
        idempotency_key: str,
        payload: dict[str, Any],
    ) -> ModelDomainEvent:
        redacted_payload = redact_sensitive_payload(payload)
        event_id = "model_event_" + _stable_hash([event_type, event_version, sequence, idempotency_key, redacted_payload])[:16]
        return ModelDomainEvent(
            event_id=event_id,
            event_version=event_version,
            sequence=sequence,
            idempotency_key=idempotency_key,
            replayable=True,
            redacted_payload=redacted_payload,
        )

    def projection_boundary(
        self,
        *,
        source_fact_ref: str,
        trace_projection_ref: str,
        audit_projection_ref: str,
        eval_projection_ref: str,
    ) -> ModelProjectionBoundary:
        return ModelProjectionBoundary(
            source_fact_ref=source_fact_ref,
            trace_projection_ref=trace_projection_ref,
            audit_projection_ref=audit_projection_ref,
            eval_projection_ref=eval_projection_ref,
        )

    def ownership_boundary(self, *, owned_facts: tuple[str, ...], foreign_facts: tuple[str, ...]) -> ModelOwnershipBoundary:
        return ModelOwnershipBoundary(module="Model Gateway", owned_facts=owned_facts, foreign_facts=foreign_facts)

    def versioned_envelope(
        self,
        *,
        envelope_type: str,
        major_version: int,
        minor_version: int,
        payload_ref: str,
        idempotency_key: str,
        correlation_id: str,
        causation_id: str,
    ) -> ModelVersionedEnvelope:
        if major_version <= 0:
            raise ModelGatewayProviderError("versioned envelope requires a known positive major version")
        return ModelVersionedEnvelope(
            envelope_type=envelope_type,
            major_version=major_version,
            minor_version=minor_version,
            payload_ref=payload_ref,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
            causation_id=causation_id,
        )

    def storage_layering_boundary(
        self,
        *,
        domain_fact_ref: str,
        object_payload_ref: str,
        projection_ref: str,
    ) -> ModelStorageLayeringBoundary:
        return ModelStorageLayeringBoundary(
            domain_fact_ref=domain_fact_ref,
            object_payload_ref=object_payload_ref,
            projection_ref=projection_ref,
        )

    def compatibility_facade_boundary(
        self,
        *,
        facade_id: str,
        bypass_inventory_ref: str,
        migration_deadline_ref: str,
    ) -> ModelCompatibilityFacadeBoundary:
        if not (bypass_inventory_ref and migration_deadline_ref):
            raise ModelGatewayProviderError("compatibility facade requires bypass inventory and migration deadline")
        return ModelCompatibilityFacadeBoundary(
            facade_id=facade_id,
            bypass_inventory_ref=bypass_inventory_ref,
            new_bypass_allowed=False,
            migration_deadline_ref=migration_deadline_ref,
        )

    def migration_integrity_verdict(
        self,
        *,
        migration_id: str,
        preserves_history_versions: bool,
        preserves_usage_receipts: bool,
        preserves_implementation_status: bool,
    ) -> ModelMigrationIntegrityVerdict:
        accepted = preserves_history_versions and preserves_usage_receipts and preserves_implementation_status
        return ModelMigrationIntegrityVerdict(
            migration_id=migration_id,
            preserves_history_versions=preserves_history_versions,
            preserves_usage_receipts=preserves_usage_receipts,
            preserves_implementation_status=preserves_implementation_status,
            accepted=accepted,
        )

    def unknown_signal_verdict(self, *, signal_kind: str, raw_value: str, quarantine: bool = False) -> ModelUnknownSignalVerdict:
        return ModelUnknownSignalVerdict(
            signal_kind=signal_kind,
            raw_value=raw_value,
            disposition=ModelUnknownSignalDisposition.QUARANTINE if quarantine else ModelUnknownSignalDisposition.FAIL_CLOSED,
        )

    def fault_recovery_evidence(
        self,
        *,
        fault_id: str,
        high_risk: bool,
        fault_injection_ref: str,
        recovery_evidence_ref: str,
    ) -> ModelFaultRecoveryEvidence:
        if high_risk and not (fault_injection_ref and recovery_evidence_ref):
            raise ModelGatewayProviderError("high-risk fault requires fault injection and recovery evidence")
        return ModelFaultRecoveryEvidence(
            fault_id=fault_id,
            high_risk=high_risk,
            fault_injection_ref=fault_injection_ref,
            recovery_evidence_ref=recovery_evidence_ref,
        )

    def current_evidence_gate(
        self,
        *,
        requirement_id: str,
        code_ref: str,
        migration_ref: str,
        test_ref: str,
        trace_ref: str,
        eval_ref: str,
        runtime_evidence_ref: str,
    ) -> ModelCurrentEvidenceGate:
        return ModelCurrentEvidenceGate(
            requirement_id=requirement_id,
            code_ref=code_ref,
            migration_ref=migration_ref,
            test_ref=test_ref,
            trace_ref=trace_ref,
            eval_ref=eval_ref,
            runtime_evidence_ref=runtime_evidence_ref,
        )

    def _select_provider(self, category: ModelCategory, provider_id: str | None = None) -> ModelProvider:
        if provider_id:
            provider = self._providers.get(provider_id)
            if provider is None:
                raise ModelGatewayProviderError(f"unknown model provider: {provider_id}")
            if not provider.supports(category):
                raise ModelGatewayProviderError(f"provider does not support {category.value}: {provider_id}")
            return provider

        for provider in self._providers.values():
            if provider.supports(category):
                return provider
        raise ModelGatewayProviderError(f"no model provider supports {category.value}")

    def get_chat_model(
        self,
        binding: dict[str, Any] | None = None,
        *,
        role: ModelRole | str = ModelRole.EXECUTOR,
    ) -> BaseChatModel:
        """Return a LangChain chat model through the gateway boundary."""
        normalized_role = ModelRole(role)
        binding_payload = dict(binding or {})
        from zuno.core.models.manager import ModelManager

        if binding_payload.get("model") or binding_payload.get("model_name"):
            if "model" not in binding_payload and "model_name" in binding_payload:
                binding_payload["model"] = binding_payload["model_name"]
            return ModelManager.get_user_model(**binding_payload)

        slot = str(binding_payload.get("model_slot") or ROLE_DEFAULT_SLOT[normalized_role])
        if slot == "tool_call_model":
            return ModelManager.get_tool_invocation_model()
        return ModelManager.get_conversation_model()

    def _evaluate_budget(
        self,
        *,
        request: ModelGatewayRequest,
        provider: ModelProvider,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> BudgetVerdict:
        budget = request.budget or self.default_budget
        cost_estimate = _estimate_cost(request.category, prompt_tokens + completion_tokens)
        estimated_latency_ms = _estimate_latency_ms(request.category, prompt_tokens + completion_tokens)

        if budget.max_cost is not None and cost_estimate > budget.max_cost:
            return BudgetVerdict(
                allowed=False,
                reason="estimated_cost_exceeds_budget",
                estimated_cost=cost_estimate,
                max_cost=budget.max_cost,
                estimated_latency_ms=estimated_latency_ms,
                max_latency_ms=budget.max_latency_ms,
            )
        if budget.max_latency_ms is not None and estimated_latency_ms > budget.max_latency_ms:
            return BudgetVerdict(
                allowed=False,
                reason="estimated_latency_exceeds_budget",
                estimated_cost=cost_estimate,
                max_cost=budget.max_cost,
                estimated_latency_ms=estimated_latency_ms,
                max_latency_ms=budget.max_latency_ms,
            )
        return BudgetVerdict(
            allowed=True,
            reason="within_budget",
            estimated_cost=cost_estimate,
            max_cost=budget.max_cost,
            estimated_latency_ms=estimated_latency_ms,
            max_latency_ms=budget.max_latency_ms,
        )

    def _build_metrics(
        self,
        *,
        request: ModelGatewayRequest,
        provider: ModelProvider,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        retry_count: int,
        timeout_count: int,
        fallback_reason: str | None,
    ) -> ModelCallMetrics:
        total_tokens = prompt_tokens + completion_tokens
        return ModelCallMetrics(
            category=request.category,
            role=request.role,
            provider_id=provider.provider_id,
            model_id=provider.model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            cost_estimate=_estimate_cost(request.category, total_tokens),
            retry_count=retry_count,
            timeout_count=timeout_count,
            fallback_reason=fallback_reason,
        )

    def _build_binding(self, request: ModelGatewayRequest, provider: ModelProvider) -> ModelGatewayBinding:
        return ModelGatewayBinding(
            role=request.role,
            operation=request.operation,
            model_slot=request.model_slot or ROLE_DEFAULT_SLOT[request.role],
            config_version=request.config_version,
            prompt_version=request.prompt_version,
            schema_version=request.schema_version,
            model_version=request.model_version or provider.model_id,
            adapter_version=request.adapter_version,
            pricing_version=request.pricing_version,
            security_epoch_ref=request.security_epoch_ref,
        )

    def _build_usage_receipt(
        self,
        *,
        request: ModelGatewayRequest,
        call_id: str,
        attempt_id: str | None,
        kind: ModelUsageKind,
        pricing_version: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> ModelUsageReceipt:
        total_tokens = prompt_tokens + completion_tokens
        return ModelUsageReceipt(
            usage_receipt_id="usage_" + _stable_hash([call_id, attempt_id, kind.value, pricing_version, total_tokens])[:16],
            call_id=call_id,
            attempt_id=attempt_id,
            kind=kind,
            pricing_version=pricing_version,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=_estimate_cost(request.category, total_tokens),
        )

    def _build_trace_event(
        self,
        *,
        event_type: str,
        request: ModelGatewayRequest,
        metrics: ModelCallMetrics,
        budget_verdict: BudgetVerdict,
        call_id: str,
        call_state: ModelCallState,
        binding: ModelGatewayBinding,
        attempts: tuple[ModelAttemptReceipt, ...],
        usage_receipts: tuple[ModelUsageReceipt, ...],
        control_actions: tuple[ModelControlAction, ...],
        error: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "call_id": call_id,
            "call_state": call_state.value,
            "binding": binding.to_dict(),
            "attempts": [attempt.to_dict() for attempt in attempts],
            "usage_receipts": [receipt.to_dict() for receipt in usage_receipts],
            "control_actions": [action.to_dict() for action in control_actions],
            **metrics.to_dict(),
            "budget_verdict": budget_verdict.to_dict(),
            "run_id": request.run_id,
            "workspace_id": request.workspace_id,
            "user_id": request.user_id,
            "model_slot": request.model_slot or ROLE_DEFAULT_SLOT[request.role],
            "timeout_ms": request.timeout_ms,
            "prompt_sha256": hashlib.sha256(request.prompt.encode("utf-8")).hexdigest(),
            "prompt_preview": redact_sensitive_text(request.prompt[:160]),
            "metadata": redact_sensitive_payload(request.metadata),
        }
        if error is not None:
            payload["error"] = error
        return {
            "event_id": _build_event_id(request, event_type),
            "task_id": request.task_id or "",
            "trace_id": request.trace_id or "",
            "event_type": event_type,
            "payload": payload,
        }


def build_default_model_gateway() -> ModelGateway:
    providers = [
        MockModelProvider(
            provider_id=f"local_mock_{category.value}",
            model_id=f"zuno-local-mock-{category.value}",
            categories=[category],
        )
        for category in ModelCategory
    ]
    return ModelGateway(providers=providers)


def _estimate_tokens(text: str) -> int:
    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, len(stripped.split()))


def _estimate_cost(category: ModelCategory, token_count: int) -> float:
    return round(token_count * _CATEGORY_COST_PER_TOKEN[category], 8)


def _estimate_latency_ms(category: ModelCategory, token_count: int) -> float:
    base_latency = {
        ModelCategory.CHAT: 30.0,
        ModelCategory.EMBEDDING: 12.0,
        ModelCategory.RERANKER: 18.0,
        ModelCategory.VLM: 75.0,
        ModelCategory.EVAL_JUDGE: 35.0,
    }[category]
    return round(base_latency + token_count * 0.8, 3)


def _deterministic_vector(text: str, dimension: int, normalization: Literal["NONE", "L2", "UNIT"]) -> tuple[float, ...]:
    if dimension <= 0:
        raise ModelGatewayProviderError("embedding dimension must be positive")
    seed = hashlib.sha256(text.encode("utf-8")).digest()
    values = tuple(round(((seed[index % len(seed)] / 255.0) * 2.0) - 1.0, 6) for index in range(dimension))
    if normalization in {"L2", "UNIT"}:
        norm = sum(value * value for value in values) ** 0.5 or 1.0
        return tuple(round(value / norm, 6) for value in values)
    return values


def _default_operation(category: ModelCategory) -> ModelOperation:
    return {
        ModelCategory.CHAT: ModelOperation.GENERATE,
        ModelCategory.EMBEDDING: ModelOperation.EMBED,
        ModelCategory.RERANKER: ModelOperation.RERANK,
        ModelCategory.VLM: ModelOperation.VISION,
        ModelCategory.EVAL_JUDGE: ModelOperation.JUDGE,
    }[category]


def _build_attempt_id(call_id: str, provider_id: str, attempt_index: int) -> str:
    return "model_attempt_" + _stable_hash([call_id, provider_id, attempt_index])[:16]


def _build_event_id(request: ModelGatewayRequest, event_type: str) -> str:
    source = "|".join(
        [
            request.trace_id or "",
            request.task_id or "",
            request.category.value,
            request.role.value,
            event_type,
            hashlib.sha256(request.prompt.encode("utf-8")).hexdigest()[:12],
        ]
    )
    return "evt_model_" + hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _config_activation_rejected(
    snapshot: ModelGatewayConfigSnapshot,
    expected_generation: int,
    active_generation: int,
    completed_gates: tuple[ModelConfigActivationGate, ...],
    rollback_snapshot_ref: str | None,
    reason: str,
) -> ModelConfigActivationDecision:
    return ModelConfigActivationDecision(
        snapshot=snapshot,
        expected_generation=expected_generation,
        committed_generation=active_generation,
        accepted=False,
        completed_gates=completed_gates,
        rollback_snapshot_ref=rollback_snapshot_ref,
        reason=reason,
    )


def _error_ref(exc: BaseException) -> str:
    return "error_" + _stable_hash({"type": type(exc).__name__, "message": str(exc)})[:16]


def _ensure_gateway_domain_boundary(request: ModelGatewayRequest) -> None:
    forbidden = {
        ModelDomainWrite.PLAN_VERSION_ACTIVATION,
        ModelDomainWrite.RUN_OUTCOME_UPDATE,
    }
    requested = set(request.requested_domain_writes)
    if requested & forbidden:
        raise ModelGatewayProviderError("model gateway cannot activate PlanVersion or modify RunOutcome")


def _control_action(
    *,
    call_id: str,
    action_type: ModelControlActionType,
    reason: str,
    attempt_id: str | None,
    owner: Literal["MODEL_GATEWAY", "AGENT_CORE", "OBSERVABILITY"] = "MODEL_GATEWAY",
) -> ModelControlAction:
    return ModelControlAction(
        action_id="model_action_" + _stable_hash([call_id, action_type.value, reason, attempt_id, owner])[:16],
        action_type=action_type,
        owner=owner,
        reason=reason,
        attempt_id=attempt_id,
    )


def _validate_structured_output(request: ModelGatewayRequest, output: str) -> tuple[str, dict[str, Any] | None, ModelRepairRecord | None]:
    if not request.output_schema:
        return output, None, None
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as exc:
        if request.repair_output is None:
            raise ModelGatewayProviderError("structured output is not valid json") from exc
        repaired_output = request.repair_output
        repaired, _structured_output, repair_record = _validate_repaired_output(
            request=request,
            original_output=output,
            repaired_output=repaired_output,
            failure_code="MODEL_STRUCTURED_OUTPUT_INVALID_JSON",
        )
        return repaired, _structured_output, repair_record

    missing = [field for field in request.output_schema if field not in parsed]
    if missing:
        if request.repair_output is None:
            raise ModelGatewayProviderError(f"structured output missing fields: {','.join(sorted(missing))}")
        repaired_output = request.repair_output
        repaired, _structured_output, repair_record = _validate_repaired_output(
            request=request,
            original_output=output,
            repaired_output=repaired_output,
            failure_code="MODEL_STRUCTURED_OUTPUT_MISSING_FIELDS",
        )
        return repaired, _structured_output, repair_record
    for field, expected_type in request.output_schema.items():
        if not isinstance(parsed[field], expected_type):
            if request.repair_output is None:
                raise ModelGatewayProviderError(f"structured output field has wrong type: {field}")
            repaired_output = request.repair_output
            repaired, _structured_output, repair_record = _validate_repaired_output(
                request=request,
                original_output=output,
                repaired_output=repaired_output,
                failure_code="MODEL_STRUCTURED_OUTPUT_TYPE_MISMATCH",
            )
            return repaired, _structured_output, repair_record
    return output, parsed, None


def _validate_repaired_output(
    *,
    request: ModelGatewayRequest,
    original_output: str,
    repaired_output: str,
    failure_code: str,
) -> tuple[str, dict[str, Any], ModelRepairRecord]:
    try:
        parsed = json.loads(repaired_output)
    except json.JSONDecodeError as exc:
        raise ModelGatewayProviderError("repair output is not valid json") from exc
    for field, expected_type in request.output_schema.items() if request.output_schema else ():
        if field not in parsed:
            raise ModelGatewayProviderError(f"repair output missing field: {field}")
        if not isinstance(parsed[field], expected_type):
            raise ModelGatewayProviderError(f"repair output field has wrong type: {field}")
    repair_record = ModelRepairRecord(
        repair_record_id="repair_" + _stable_hash([original_output, repaired_output, request.schema_version, failure_code])[:16],
        original_output_sha256=hashlib.sha256(original_output.encode("utf-8")).hexdigest(),
        repaired_output_sha256=hashlib.sha256(repaired_output.encode("utf-8")).hexdigest(),
        schema_version=request.schema_version,
        failure_code=failure_code,
    )
    return repaired_output, parsed, repair_record


def _provider_stream(provider: ModelProvider, request: ModelGatewayRequest) -> list[ProviderStreamChunk]:
    raw_chunks = request.metadata.get("provider_stream_chunks")
    if raw_chunks is None:
        text = provider.invoke(request)
        parts = [part for part in text.split(" ") if part]
        return [
            ProviderStreamChunk(
                provider_chunk_id=f"{provider.provider_id}:{index}",
                sequence=index,
                content=part,
                final=index == len(parts) - 1,
            )
            for index, part in enumerate(parts)
        ]
    chunks: list[ProviderStreamChunk] = []
    for item in raw_chunks:
        chunks.append(
            ProviderStreamChunk(
                provider_chunk_id=str(item["provider_chunk_id"]),
                sequence=int(item["sequence"]),
                content=str(item["content"]),
                final=bool(item.get("final", False)),
            )
        )
    return chunks


def _normalize_stream_chunks(call_id: str, provider_chunks: list[ProviderStreamChunk]) -> list[GatewayStreamChunk]:
    ordered = sorted(provider_chunks, key=lambda chunk: (chunk.sequence, chunk.provider_chunk_id))
    seen: set[tuple[int, str]] = set()
    normalized: list[GatewayStreamChunk] = []
    for chunk in ordered:
        key = (chunk.sequence, chunk.content)
        duplicate = key in seen
        seen.add(key)
        content_sha256 = hashlib.sha256(chunk.content.encode("utf-8")).hexdigest()
        normalized.append(
            GatewayStreamChunk(
                gateway_chunk_id="gw_chunk_" + _stable_hash([call_id, chunk.provider_chunk_id, chunk.sequence, content_sha256])[:16],
                provider_chunk_id=chunk.provider_chunk_id,
                sequence=chunk.sequence,
                content=chunk.content,
                content_sha256=content_sha256,
                provisional=not chunk.final,
                duplicate=duplicate,
            )
        )
    return normalized


def _build_product_stream_events(call_id: str, gateway_chunks: list[GatewayStreamChunk]) -> list[ProductStreamEvent]:
    events: list[ProductStreamEvent] = []
    visible_chunks = [chunk for chunk in gateway_chunks if not chunk.duplicate]
    for chunk in visible_chunks:
        event_type: Literal["model_stream_delta", "model_stream_completed"] = (
            "model_stream_completed" if not chunk.provisional else "model_stream_delta"
        )
        events.append(
            ProductStreamEvent(
                event_id="product_stream_" + _stable_hash([call_id, chunk.gateway_chunk_id, event_type])[:16],
                event_type=event_type,
                sequence=chunk.sequence,
                content=chunk.content,
                provisional=chunk.provisional,
                gateway_chunk_ref=chunk.gateway_chunk_id,
            )
        )
    return events


__all__ = [
    "EchoLLMProvider",
    "LLMProvider",
    "BudgetPolicy",
    "BudgetVerdict",
    "MockModelProvider",
    "ModelAdapterRolloutMode",
    "ModelAdapterRolloutPlan",
    "ModelAdmissionDecision",
    "ModelAdmissionLayer",
    "ModelAdmissionLayerCheck",
    "ModelAttemptReceipt",
    "ModelAttemptState",
    "ModelCallRequest",
    "ModelCallMetrics",
    "ModelCallResponse",
    "ModelCallState",
    "ModelCategory",
    "ModelActionProposal",
    "ModelAdapterConformanceSuite",
    "ModelAdapterConformanceVerdict",
    "ModelCompressedContext",
    "ModelCallConfigBinding",
    "ModelCacheInvalidationDecision",
    "ModelCacheKey",
    "ModelCacheKind",
    "ModelCacheLookup",
    "ModelCachePolicy",
    "ModelCacheReuseReceipt",
    "ModelCompatibilityFacadeBoundary",
    "ModelControlAction",
    "ModelControlActionType",
    "ModelCapabilityProfile",
    "ModelCapabilityStatus",
    "ModelCircuitDecision",
    "ModelCircuitKey",
    "ModelCircuitStatus",
    "ModelConfigActivationDecision",
    "ModelConfigActivationGate",
    "ModelDomainWrite",
    "ModelDomainEvent",
    "ModelEmbeddingResult",
    "ModelExperimentAssignment",
    "ModelExperimentGateVerdict",
    "ModelFailureClassification",
    "ModelFaultRecoveryEvidence",
    "ModelGateway",
    "ModelGatewayBinding",
    "ModelGatewayConfigSnapshot",
    "ModelGatewayCancellationError",
    "ModelGatewayProviderError",
    "ModelGatewayRequest",
    "ModelGatewayResult",
    "ModelGatewayTimeoutError",
    "ModelOperation",
    "OpenAIEmbeddingGatewayAdapter",
    "ModelOperationalCommand",
    "ModelOperationalCommandKind",
    "ModelOperationalCommandVerdict",
    "ModelOverloadDecision",
    "ModelOverloadState",
    "ModelProjectionBoundary",
    "ModelClassificationResult",
    "ModelJudgeResult",
    "ModelOutputCandidate",
    "ModelEmergencyDisableDecision",
    "ModelProviderLifecycleRecord",
    "ModelProviderLifecycleState",
    "ModelProviderSignalStatus",
    "ModelProviderSignalVerdict",
    "ModelProviderApiSunsetPlan",
    "ModelProviderHealthStatus",
    "ModelProviderHealthWindow",
    "ModelQueuedRequestBinding",
    "ModelQuotaPolicy",
    "ModelQuotaReservation",
    "ModelCurrentEvidenceGate",
    "ModelRepairRecord",
    "ModelRerankItem",
    "ModelRetentionBinding",
    "ModelRetentionSubject",
    "ModelReadinessProbe",
    "ModelReadinessStatus",
    "ModelReadinessVerdict",
    "ModelSliSloDimension",
    "ModelShadowCallRecord",
    "ModelShadowResult",
    "ModelMigrationIntegrityVerdict",
    "ModelOwnershipBoundary",
    "ModelResultValidityEvent",
    "ModelStorageLayeringBoundary",
    "ModelSuggestedControlAction",
    "ModelUnknownSignalDisposition",
    "ModelUnknownSignalVerdict",
    "ModelVersionedEnvelope",
    "ModelDeletionStep",
    "ModelDeletionWorkflow",
    "ModelRiskProposal",
    "ModelRole",
    "ModelStreamResult",
    "ModelTranscriptionSegment",
    "ModelVisionRegion",
    "GatewayStreamChunk",
    "ModelUsageKind",
    "ModelUsageReceipt",
    "ProductStreamEvent",
    "ProviderStreamChunk",
    "build_default_model_gateway",
    "build_openai_chat_gateway_model",
]

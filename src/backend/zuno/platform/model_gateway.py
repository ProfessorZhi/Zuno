from __future__ import annotations

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
    "ModelControlAction",
    "ModelControlActionType",
    "ModelCapabilityProfile",
    "ModelCapabilityStatus",
    "ModelCircuitDecision",
    "ModelCircuitKey",
    "ModelCircuitStatus",
    "ModelDomainWrite",
    "ModelEmbeddingResult",
    "ModelGateway",
    "ModelGatewayBinding",
    "ModelGatewayCancellationError",
    "ModelGatewayProviderError",
    "ModelGatewayRequest",
    "ModelGatewayResult",
    "ModelGatewayTimeoutError",
    "ModelOperation",
    "ModelClassificationResult",
    "ModelJudgeResult",
    "ModelOutputCandidate",
    "ModelProviderHealthStatus",
    "ModelProviderHealthWindow",
    "ModelQuotaPolicy",
    "ModelQuotaReservation",
    "ModelRepairRecord",
    "ModelRerankItem",
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
]

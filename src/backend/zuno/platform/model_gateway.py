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
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.category = ModelCategory(self.category)
        self.role = ModelRole(self.role)
        self.operation = ModelOperation(self.operation) if self.operation else _default_operation(self.category)


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
    selected_attempt_id: str | None = None
    structured_output: dict[str, Any] | None = None
    repair_record: dict[str, Any] | None = None


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

    def invoke(self, request: ModelGatewayRequest) -> ModelGatewayResult:
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
            )

        candidate_ids = [provider.provider_id, *request.fallback_provider_ids]
        retry_count = 0
        timeout_count = 0
        fallback_reason: str | None = None
        last_error: str | None = None
        attempts: list[ModelAttemptReceipt] = []
        usage_receipts: list[ModelUsageReceipt] = [estimate_receipt]

        for attempt_index, provider_id in enumerate(candidate_ids):
            active_provider = self._select_provider(request.category, provider_id)
            attempt_id = _build_attempt_id(call_id, active_provider.provider_id, attempt_index)
            start = time.perf_counter()
            try:
                output = active_provider.invoke(request)
                structured_output, repair_record = _validate_structured_output(request, output)
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
        error: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "call_id": call_id,
            "call_state": call_state.value,
            "binding": binding.to_dict(),
            "attempts": [attempt.to_dict() for attempt in attempts],
            "usage_receipts": [receipt.to_dict() for receipt in usage_receipts],
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


def _validate_structured_output(request: ModelGatewayRequest, output: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not request.output_schema:
        return None, None
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError as exc:
        raise ModelGatewayProviderError("structured output is not valid json") from exc

    missing = [field for field in request.output_schema if field not in parsed]
    if missing:
        raise ModelGatewayProviderError(f"structured output missing fields: {','.join(sorted(missing))}")
    for field, expected_type in request.output_schema.items():
        if not isinstance(parsed[field], expected_type):
            raise ModelGatewayProviderError(f"structured output field has wrong type: {field}")
    return parsed, None


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
    "ModelGateway",
    "ModelGatewayBinding",
    "ModelGatewayCancellationError",
    "ModelGatewayProviderError",
    "ModelGatewayRequest",
    "ModelGatewayResult",
    "ModelGatewayTimeoutError",
    "ModelOperation",
    "ModelRole",
    "ModelUsageKind",
    "ModelUsageReceipt",
    "build_default_model_gateway",
]

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
import hashlib
import time
from typing import Any, Iterable, Literal, Protocol

from zuno.platform.security import redact_sensitive_payload, redact_sensitive_text
from zuno.platform.services.llm.providers import EchoLLMProvider, LLMProvider


class ModelCategory(StrEnum):
    CHAT = "chat"
    EMBEDDING = "embedding"
    RERANKER = "reranker"
    VLM = "vlm"
    EVAL_JUDGE = "eval_judge"


class ModelGatewayProviderError(RuntimeError):
    pass


class ModelGatewayTimeoutError(TimeoutError):
    pass


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
    provider_id: str | None = None
    fallback_provider_ids: list[str] = field(default_factory=list)
    trace_id: str | None = None
    task_id: str | None = None
    workspace_id: str | None = None
    user_id: str | None = None
    max_output_tokens: int = 128
    budget: BudgetPolicy | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.category = ModelCategory(self.category)


@dataclass(frozen=True, slots=True)
class ModelCallMetrics:
    category: ModelCategory
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
    status: Literal["succeeded", "blocked", "failed"]
    output: str
    metrics: ModelCallMetrics
    budget_verdict: BudgetVerdict
    trace_event: dict[str, Any]


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
    fail_mode: Literal["timeout", "error"] | None = None
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

        if not budget_verdict.allowed:
            trace_event = self._build_trace_event(
                event_type="model_call_blocked",
                request=request,
                metrics=blocked_metrics,
                budget_verdict=budget_verdict,
            )
            return ModelGatewayResult(
                status="blocked",
                output="",
                metrics=blocked_metrics,
                budget_verdict=budget_verdict,
                trace_event=trace_event,
            )

        candidate_ids = [provider.provider_id, *request.fallback_provider_ids]
        retry_count = 0
        timeout_count = 0
        fallback_reason: str | None = None
        last_error: str | None = None

        for attempt_index, provider_id in enumerate(candidate_ids):
            active_provider = self._select_provider(request.category, provider_id)
            start = time.perf_counter()
            try:
                output = active_provider.invoke(request)
            except ModelGatewayTimeoutError as exc:
                retry_count += 1
                timeout_count += 1
                fallback_reason = fallback_reason or f"timeout:{active_provider.provider_id}"
                last_error = str(exc)
                continue
            except ModelGatewayProviderError as exc:
                retry_count += 1
                fallback_reason = fallback_reason or f"error:{active_provider.provider_id}"
                last_error = str(exc)
                continue

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
            trace_event = self._build_trace_event(
                event_type="model_call_completed",
                request=request,
                metrics=metrics,
                budget_verdict=budget_verdict,
            )
            return ModelGatewayResult(
                status="succeeded",
                output=output,
                metrics=metrics,
                budget_verdict=budget_verdict,
                trace_event=trace_event,
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
        trace_event = self._build_trace_event(
            event_type="model_call_failed",
            request=request,
            metrics=failed_metrics,
            budget_verdict=budget_verdict,
            error=last_error,
        )
        return ModelGatewayResult(
            status="failed",
            output="",
            metrics=failed_metrics,
            budget_verdict=budget_verdict,
            trace_event=trace_event,
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

    def _build_trace_event(
        self,
        *,
        event_type: str,
        request: ModelGatewayRequest,
        metrics: ModelCallMetrics,
        budget_verdict: BudgetVerdict,
        error: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            **metrics.to_dict(),
            "budget_verdict": budget_verdict.to_dict(),
            "workspace_id": request.workspace_id,
            "user_id": request.user_id,
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


def _build_event_id(request: ModelGatewayRequest, event_type: str) -> str:
    source = "|".join(
        [
            request.trace_id or "",
            request.task_id or "",
            request.category.value,
            event_type,
            hashlib.sha256(request.prompt.encode("utf-8")).hexdigest()[:12],
        ]
    )
    return "evt_model_" + hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


__all__ = [
    "EchoLLMProvider",
    "LLMProvider",
    "BudgetPolicy",
    "BudgetVerdict",
    "MockModelProvider",
    "ModelCallMetrics",
    "ModelCategory",
    "ModelGateway",
    "ModelGatewayProviderError",
    "ModelGatewayRequest",
    "ModelGatewayResult",
    "ModelGatewayTimeoutError",
    "build_default_model_gateway",
]

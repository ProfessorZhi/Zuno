from __future__ import annotations

from zuno.platform.model_gateway import (
    BudgetPolicy,
    ModelCategory,
    ModelGateway,
    ModelGatewayRequest,
    MockModelProvider,
    build_default_model_gateway,
)


def test_model_gateway_records_redacted_cost_latency_trace() -> None:
    provider = MockModelProvider(provider_id="local", model_id="mock-chat")
    gateway = ModelGateway(providers=[provider])

    result = gateway.invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt="Draft the answer with secret token sk-phase08-secret.",
            provider_id="local",
            trace_id="trace_08",
            task_id="task_08",
            workspace_id="workspace_08",
        )
    )

    assert result.status == "succeeded"
    assert result.output
    assert result.metrics.category == ModelCategory.CHAT
    assert result.metrics.provider_id == "local"
    assert result.metrics.model_id == "mock-chat"
    assert result.metrics.prompt_tokens > 0
    assert result.metrics.completion_tokens > 0
    assert result.metrics.total_tokens == result.metrics.prompt_tokens + result.metrics.completion_tokens
    assert result.metrics.cost_estimate > 0
    assert result.metrics.latency_ms >= 0
    assert result.metrics.retry_count == 0
    assert result.metrics.timeout_count == 0
    assert result.budget_verdict.allowed is True

    assert result.trace_event["event_type"] == "model_call_completed"
    assert result.trace_event["payload"]["category"] == "chat"
    assert result.trace_event["payload"]["token_count"] == result.metrics.total_tokens
    assert "sk-phase08-secret" not in repr(result.trace_event)


def test_model_gateway_cost_guard_blocks_without_calling_provider() -> None:
    provider = MockModelProvider(provider_id="local", model_id="mock-chat")
    gateway = ModelGateway(providers=[provider], default_budget=BudgetPolicy(max_cost=0.000001))

    result = gateway.invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt=" ".join(["expensive"] * 200),
            provider_id="local",
            trace_id="trace_budget",
            task_id="task_budget",
            workspace_id="workspace_budget",
        )
    )

    assert result.status == "blocked"
    assert result.output == ""
    assert result.budget_verdict.allowed is False
    assert result.budget_verdict.reason == "estimated_cost_exceeds_budget"
    assert result.metrics.cost_estimate > result.budget_verdict.max_cost
    assert provider.call_count == 0
    assert result.trace_event["event_type"] == "model_call_blocked"
    assert result.trace_event["payload"]["budget_verdict"]["allowed"] is False


def test_model_gateway_timeout_fallback_enters_trace() -> None:
    primary = MockModelProvider(provider_id="primary", model_id="mock-primary", fail_mode="timeout")
    fallback = MockModelProvider(provider_id="fallback", model_id="mock-fallback")
    gateway = ModelGateway(providers=[primary, fallback])

    result = gateway.invoke(
        ModelGatewayRequest(
            category=ModelCategory.CHAT,
            prompt="Use fallback after timeout.",
            provider_id="primary",
            fallback_provider_ids=["fallback"],
            trace_id="trace_fallback",
            task_id="task_fallback",
            workspace_id="workspace_fallback",
        )
    )

    assert result.status == "succeeded"
    assert result.metrics.provider_id == "fallback"
    assert result.metrics.model_id == "mock-fallback"
    assert result.metrics.retry_count == 1
    assert result.metrics.timeout_count == 1
    assert result.metrics.fallback_reason == "timeout:primary"
    assert result.trace_event["payload"]["fallback_reason"] == "timeout:primary"
    assert primary.call_count == 1
    assert fallback.call_count == 1


def test_default_gateway_supports_phase08_model_categories() -> None:
    gateway = build_default_model_gateway()

    for category in [
        ModelCategory.CHAT,
        ModelCategory.EMBEDDING,
        ModelCategory.RERANKER,
        ModelCategory.VLM,
        ModelCategory.EVAL_JUDGE,
    ]:
        result = gateway.invoke(
            ModelGatewayRequest(
                category=category,
                prompt=f"Run local mock {category.value}.",
                trace_id=f"trace_{category.value}",
                task_id=f"task_{category.value}",
                workspace_id="workspace_categories",
            )
        )

        assert result.status == "succeeded"
        assert result.metrics.category == category
        assert result.metrics.provider_id.startswith("local_mock")
        assert result.trace_event["payload"]["category"] == category.value

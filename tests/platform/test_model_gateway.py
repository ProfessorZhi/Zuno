from __future__ import annotations

from types import SimpleNamespace

from zuno.platform.model_gateway import (
    BudgetPolicy,
    ModelCallRequest,
    ModelCategory,
    ModelGateway,
    ModelGatewayRequest,
    MockModelProvider,
)
from zuno.platform.model_roles import ModelRole


def test_model_gateway_routes_roles_and_records_trace_metadata() -> None:
    provider = MockModelProvider(provider_id="primary", model_id="mock-chat")
    gateway = ModelGateway(providers=[provider])

    result = gateway.invoke(
        ModelCallRequest(
            category=ModelCategory.CHAT,
            role=ModelRole.PLANNER,
            run_id="run-1",
            task_id="task-1",
            trace_id="trace-1",
            workspace_id="workspace-1",
            user_id="user-1",
            model_slot="reasoning_model",
            timeout_ms=1500,
            prompt="Plan with api_key sk-secret.",
            provider_id="primary",
            metadata={"api_key": "sk-secret", "safe": "yes"},
        )
    )

    assert result.status == "succeeded"
    assert result.metrics.role == ModelRole.PLANNER
    assert result.trace_event["payload"]["role"] == "planner"
    assert result.trace_event["payload"]["run_id"] == "run-1"
    assert result.trace_event["payload"]["model_slot"] == "reasoning_model"
    assert result.trace_event["payload"]["timeout_ms"] == 1500
    assert "sk-secret" not in repr(result.trace_event)


def test_model_call_request_alias_preserves_old_gateway_request() -> None:
    request = ModelGatewayRequest(
        category="chat",
        role="tool_call",
        prompt="Pick a tool.",
    )

    assert isinstance(request, ModelCallRequest)
    assert request.category == ModelCategory.CHAT
    assert request.role == ModelRole.TOOL_CALL


def test_gateway_get_chat_model_uses_legacy_model_manager_adapter(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []
    fake_model = SimpleNamespace(model_name="fake-chat")

    def fake_get_user_model(**kwargs):
        calls.append(("user", kwargs))
        return fake_model

    def fake_get_conversation_model():
        calls.append(("conversation", None))
        return fake_model

    def fake_get_tool_invocation_model():
        calls.append(("tool", None))
        return fake_model

    monkeypatch.setattr("zuno.core.models.manager.ModelManager.get_user_model", fake_get_user_model)
    monkeypatch.setattr(
        "zuno.core.models.manager.ModelManager.get_conversation_model",
        fake_get_conversation_model,
    )
    monkeypatch.setattr(
        "zuno.core.models.manager.ModelManager.get_tool_invocation_model",
        fake_get_tool_invocation_model,
    )

    gateway = ModelGateway(providers=[MockModelProvider()])

    assert gateway.get_chat_model({"model": "deepseek-chat"}, role=ModelRole.EXECUTOR) is fake_model
    assert gateway.get_chat_model({"model_slot": "conversation_model"}, role=ModelRole.SYNTHESIS) is fake_model
    assert gateway.get_chat_model(role=ModelRole.TOOL_CALL) is fake_model

    assert calls == [
        ("user", {"model": "deepseek-chat"}),
        ("conversation", None),
        ("tool", None),
    ]


def test_model_gateway_budget_block_includes_role_without_provider_call() -> None:
    provider = MockModelProvider(provider_id="primary", model_id="mock-chat")
    gateway = ModelGateway(providers=[provider], default_budget=BudgetPolicy(max_cost=0.000001))

    result = gateway.invoke(
        ModelCallRequest(
            category="chat",
            role="critic",
            prompt=" ".join(["expensive"] * 200),
            provider_id="primary",
        )
    )

    assert result.status == "blocked"
    assert result.metrics.role == ModelRole.CRITIC
    assert result.trace_event["payload"]["role"] == "critic"
    assert provider.call_count == 0

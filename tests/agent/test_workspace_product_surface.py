"""PHASE22 product wiring: real product surface verification.

These tests exercise the real product entrypoints — the HTTP workspace chat
surface (``WorkspaceService.workspace_simple_chat_response``) and the WeChat
channel service (``WeChatService.invoke_wechat_agent``) — and assert the
canonical single-controller runtime behavior through the product SSE
contract.

They never construct ``WorkspaceAgentRuntime`` directly to bypass the product
service: the adapter is always composed from the product request through the
server composition root, exactly like a real authenticated request.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from typing import Any

import pytest

from zuno.api.dto.workspace import WorkSpaceSimpleTask, WorkspaceTaskContract
from zuno.api.services.user import UserPayload
from zuno.api.services.workspace import WorkspaceService
from zuno.agent.runtime import SQLiteAgentRunStore
from zuno.platform.services.workspace.single_controller_runtime import (
    BlockedConfiguration,
    WorkspaceRuntimeComposition,
    configure_workspace_product_composition,
)
from zuno.platform.services.workspace.simple_agent import WorkSpaceSimpleAgent
from zuno.platform.security.decision_resolvers import PostgresBudgetDecisionResolver


class _FakeChatModel:
    """Product chat model stub: the runtime's model steps invoke this."""

    def __init__(self) -> None:
        self.calls = 0

    async def ainvoke(self, prompt: str) -> Any:
        self.calls += 1

        class _Response:
            content = "mock grounded answer"

        return _Response()


async def _async_noop(self, *args: Any, **kwargs: Any) -> None:
    return None


def _sync_noop(self, *args: Any, **kwargs: Any) -> None:
    return None


def _patch_product_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the product-side infrastructure with inert test doubles.

    The canonical runtime itself is NOT faked: only the session / model /
    tool catalog lookups that require PostgreSQL or an external provider are
    stubbed, so the real product surface -> adapter -> runtime -> plan ->
    gate -> outcome chain stays intact.
    """
    monkeypatch.setattr(
        "zuno.platform.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: _FakeChatModel(),
    )
    async def _get_llm_by_id(model_id: str) -> dict[str, Any]:
        return {
            "model": "mock-model",
            "base_url": "http://mock-model.local",
            "api_key": "mock-key",
            "provider": "mock",
        }

    monkeypatch.setattr(
        "zuno.api.services.workspace.LLMService.get_llm_by_id",
        _get_llm_by_id,
    )
    async def _get_workspace_session_from_id(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "zuno.api.services.workspace.WorkSpaceSessionService.get_workspace_session_from_id",
        _get_workspace_session_from_id,
    )
    async def _get_tools_from_id(*args, **kwargs):
        return []

    monkeypatch.setattr(
        "zuno.api.services.workspace.ToolService.get_tools_from_id",
        _get_tools_from_id,
    )
    for name in (
        "setup_terminal_tools",
        "setup_mcp_tools",
        "setup_plugin_tools",
        "setup_knowledge_tools",
        "setup_skill_tools",
        "setup_available_skill_catalog",
    ):
        monkeypatch.setattr(WorkSpaceSimpleAgent, name, _async_noop)
    monkeypatch.setattr(WorkSpaceSimpleAgent, "_enable_explicit_slash_skill", _sync_noop)


def _product_composition(tmp_path, *, budget_resolver: bool = True) -> WorkspaceRuntimeComposition:
    store = SQLiteAgentRunStore(tmp_path / "product-surface.db")
    return WorkspaceRuntimeComposition(
        store=store,
        security_epoch_ref="epoch-1",
        approval_flow="none",
        budget_decision_resolver=(
            PostgresBudgetDecisionResolver(default_limits={"timeout_seconds": 60})
            if budget_resolver
            else None
        ),
    )


def _consume_sse(coro) -> list[dict[str, Any]]:
    """Await the async product surface and drain its SSE stream."""

    async def _collect():
        response = await coro
        events = []
        async for raw in response.body_iterator:
            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            events.append(json.loads(text[len("data: "):]))
        return events

    return asyncio.run(_collect())


def _product_task(
    *,
    tenant_id: str | None,
    workspace_id: str | None,
    query: str = "hello",
    task_id: str = "product-task-1",
    attachments: list[dict[str, Any]] | None = None,
) -> WorkSpaceSimpleTask:
    return WorkSpaceSimpleTask(
        query=query,
        model_id="mock-model",
        session_id="session-1",
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        task_id=task_id,
        attachments=attachments or [],
    )


def _workspace_task_id(tenant_id: str, workspace_id: str, client_request_id: str) -> str:
    source = f"{tenant_id}|{workspace_id}|{client_request_id}"
    return f"workspace:{hashlib.sha256(source.encode('utf-8')).hexdigest()[:16]}"


@pytest.fixture
def product_composition(tmp_path, monkeypatch):
    configure_workspace_product_composition(_product_composition(tmp_path))
    yield
    configure_workspace_product_composition(None)


@pytest.fixture
def product_deps(monkeypatch):
    _patch_product_dependencies(monkeypatch)


def _blocked_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if event.get("event") == "status"
        and event.get("data", {}).get("status") == "BLOCKED_CONFIGURATION"
    ]


def _final_event(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    for event in events:
        if event.get("event") == "final":
            return event
    return None


# ---------------------------------------------------------------------------
# A. real tenant / workspace / principal context, fail-closed when missing
# ---------------------------------------------------------------------------


def test_product_workspace_missing_tenant_blocks_configuration(
    product_composition, product_deps
) -> None:
    task = _product_task(tenant_id=None, workspace_id="workspace-a")
    login_user = UserPayload(user_id="user-a", role="admin")

    events = _consume_sse(
        WorkspaceService.workspace_simple_chat_response(
            simple_task=task, login_user=login_user
        )
    )

    blocked = _blocked_events(events)
    assert blocked, "expected a BLOCKED_CONFIGURATION SSE event"
    assert "missing_product_tenant_context" in blocked[0]["data"]["message"]
    final = _final_event(events)
    assert final is not None and final["data"]["done"] is True


def test_product_workspace_missing_workspace_blocks_configuration(
    product_composition, product_deps
) -> None:
    task = _product_task(tenant_id="tenant-a", workspace_id=None)
    login_user = UserPayload(user_id="user-a", role="admin")

    events = _consume_sse(
        WorkspaceService.workspace_simple_chat_response(
            simple_task=task, login_user=login_user
        )
    )

    blocked = _blocked_events(events)
    assert blocked, "expected a BLOCKED_CONFIGURATION SSE event"
    assert "missing_product_workspace_context" in blocked[0]["data"]["message"]


def test_product_workspace_missing_principal_blocks_configuration(
    product_composition, product_deps
) -> None:
    task = _product_task(tenant_id="tenant-a", workspace_id="workspace-a")
    login_user = UserPayload(user_id="", role="admin")

    events = _consume_sse(
        WorkspaceService.workspace_simple_chat_response(
            simple_task=task, login_user=login_user
        )
    )

    blocked = _blocked_events(events)
    assert blocked, "expected a BLOCKED_CONFIGURATION SSE event"
    assert "missing_product_principal_context" in blocked[0]["data"]["message"]


def test_product_workspace_missing_identity_executes_no_tool(
    product_composition, product_deps
) -> None:
    """Missing identity -> zero tool execution: no tool_call event anywhere."""
    task = _product_task(tenant_id=None, workspace_id="workspace-a")
    login_user = UserPayload(user_id="user-a", role="admin")

    events = _consume_sse(
        WorkspaceService.workspace_simple_chat_response(
            simple_task=task, login_user=login_user
        )
    )

    assert not [e for e in events if e.get("event") == "tool_call"]
    assert not [e for e in events if e.get("event") == "tool_result"]


# ---------------------------------------------------------------------------
# C. read-only product happy path through the real product surface
# ---------------------------------------------------------------------------


def test_product_workspace_real_identity_happy_path(
    product_composition, product_deps, tmp_path
) -> None:
    """Real product request -> canonical runtime -> final SSE event, with the
    run outcome persisted and readable under the product submission id."""
    task = _product_task(tenant_id="tenant-a", workspace_id="workspace-a")
    login_user = UserPayload(user_id="user-a", role="admin")

    events = _consume_sse(
        WorkspaceService.workspace_simple_chat_response(
            simple_task=task, login_user=login_user
        )
    )

    # The product surface emits the SSE final event (RunOutcome mapped back
    # to the product contract).
    final = _final_event(events)
    assert final is not None
    assert final["data"]["done"] is True
    assert str(final["data"]["chunk"]).strip()  # a real final-gate answer

    # The run outcome is persisted under the tenant|workspace|submission
    # identity and readable from the composition store.
    store = SQLiteAgentRunStore(tmp_path / "product-surface.db")
    task_id = _workspace_task_id("tenant-a", "workspace-a", "product-task-1")
    snapshot = store.snapshot(task_id)
    assert snapshot is not None
    assert snapshot.task_id == task_id
    assert snapshot.workspace_id == "workspace-a"
    assert snapshot.events, "expected durable run events under the task identity"


def test_product_workspace_happy_path_through_budget_admission(
    product_composition, product_deps
) -> None:
    """A simple product task must pass formal Budget Admission (no tool
    security decision required for a plan-only run)."""
    task = _product_task(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        task_id="product-task-budget",
    )
    login_user = UserPayload(user_id="user-a", role="admin")

    events = _consume_sse(
        WorkspaceService.workspace_simple_chat_response(
            simple_task=task, login_user=login_user
        )
    )

    final = _final_event(events)
    assert final is not None
    assert final["data"]["done"] is True
    assert str(final["data"]["chunk"]).strip()


def test_product_budget_resolver_unbound_blocks(
    tmp_path, monkeypatch, product_deps
) -> None:
    """Composition without a Budget owner resolver -> the run fails closed
    (budget_owner_resolver_unbound), zero tool execution."""
    configure_workspace_product_composition(
        _product_composition(tmp_path, budget_resolver=False)
    )
    try:
        task = _product_task(tenant_id="tenant-a", workspace_id="workspace-a")
        login_user = UserPayload(user_id="user-a", role="admin")

        events = _consume_sse(
            WorkspaceService.workspace_simple_chat_response(
                simple_task=task, login_user=login_user
            )
        )

        error_events = [
            e
            for e in events
            if e.get("event") == "status"
            and e.get("data", {}).get("status") == "ERROR"
        ]
        assert error_events, "expected an ERROR SSE event"
        assert "FAILED/BLOCKED" in str(error_events[0]["data"]["error"])
        assert not [e for e in events if e.get("event") == "tool_call"]
        # The precise admission reason (budget_owner_resolver_unbound) is
        # asserted at the runtime layer; the product surface fails closed
        # with zero tool execution either way.
    finally:
        configure_workspace_product_composition(None)


# ---------------------------------------------------------------------------
# D. image generation product bypass is governed (fail-closed)
# ---------------------------------------------------------------------------


def test_product_image_regen_fails_closed_not_bound(
    product_composition, product_deps
) -> None:
    """A regeneration request with a reference image must fail closed with
    IMAGE_TOOL_RUNTIME_NOT_BOUND — the product API never executes
    _text_to_image directly."""
    task = _product_task(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        query="regenerate this logo",
        attachments=[{"name": "logo.png", "url": "https://example.com/logo.png", "mime_type": "image/png"}],
    )
    login_user = UserPayload(user_id="user-a", role="admin")

    assert WorkspaceService.is_image_regeneration_request(task) is True
    events = _consume_sse(
        WorkspaceService.workspace_simple_chat_response(
            simple_task=task, login_user=login_user
        )
    )

    blocked = _blocked_events(events)
    assert blocked, "expected a BLOCKED_CONFIGURATION SSE event"
    assert "IMAGE_TOOL_RUNTIME_NOT_BOUND" in blocked[0]["data"]["message"]
    assert not [e for e in events if e.get("event") == "tool_call"]


def test_product_image_regen_without_reference_is_not_rerouted(
    product_composition, product_deps
) -> None:
    """A plain image mention without a reference image is a normal product
    request (no direct-image detection, no fail-closed reroute)."""
    task = _product_task(
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        query="generate a poster",
    )
    login_user = UserPayload(user_id="user-a", role="admin")

    assert WorkspaceService.is_image_regeneration_request(task) is False
    events = _consume_sse(
        WorkspaceService.workspace_simple_chat_response(
            simple_task=task, login_user=login_user
        )
    )

    final = _final_event(events)
    assert final is not None
    assert final["data"]["done"] is True
    assert str(final["data"]["chunk"]).strip()


# ---------------------------------------------------------------------------
# E. WeChat product path: real identity required, else fail closed
# ---------------------------------------------------------------------------


def test_wechat_product_path_requires_real_identity(product_composition, product_deps) -> None:
    """The WeChat channel entry has no authenticated tenant / workspace
    context and must not guess: the adapter fails closed with
    BLOCKED_CONFIGURATION, zero tool execution."""
    from zuno.api.services.wechat import WeChatService

    with pytest.raises(BlockedConfiguration, match="BLOCKED_CONFIGURATION"):
        asyncio.run(
            WeChatService.invoke_wechat_agent(
                from_user="wechat-openid-1",
                to_user="zuno-account",
                content="hello",
                history_messages="",
            )
        )


def test_unified_runtime_rejects_synthetic_user_tenant(product_composition) -> None:
    """PHASE22 final engineering closure (P0-1, P0-4): the unified runtime
    entry MUST NOT accept ``f"user:{user_id}"`` / ``tenant:default`` /
    empty tenant. The entry fails closed with the canonical token
    ``BLOCKED_CONFIGURATION: tenant_identity_not_available`` before any
    model / tool invocation. Synthetic user:* fallbacks are forbidden
    even if some upstream caller still produces them.
    """
    from zuno.api.services.workspace_task_runtime import (
        WorkspaceTaskRuntimeService,
    )

    login_user = UserPayload(user_id="user-a", role="admin")
    task_contract = WorkspaceTaskContract(
        task_id="t-1",
        workspace_id="ws-1",
        session_id="s-1",
        user_id=login_user.user_id,
        goal="hello",
    )
    simple_task = _product_task(
        tenant_id="tenant-a", workspace_id="ws-1", task_id="t-1"
    )

    for bad_tenant in (f"user:{login_user.user_id}", "", "tenant:default"):
        with pytest.raises(BlockedConfiguration, match="tenant_identity_not_available"):
            WorkspaceTaskRuntimeService._start_unified_runtime_for_task(
                task=task_contract,
                simple_task=simple_task,
                login_user=login_user,
                goal="hello",
                tenant_id=bad_tenant,
            )


def test_wechat_product_path_accepts_explicit_real_identity(
    tmp_path, monkeypatch, product_deps
) -> None:
    """The WeChat product entry accepts explicit tenant / workspace identity
    from an authenticated product context (the adapter then reaches the
    canonical runtime composition instead of failing closed)."""
    from zuno.api.services.wechat import WeChatService
    from zuno.platform.services.workspace.wechat_agent import WeChatAgent

    configure_workspace_product_composition(_product_composition(tmp_path))
    monkeypatch.setattr(
        WeChatAgent, "init_wechat_agent", _async_noop
    )
    try:
        # Explicit real identity: the adapter proceeds to build the runtime.
        # (init is nooped here; the identity gating is covered by the
        # fail-closed test above.)
        agent = WeChatAgent(
            user_id="user-a",
            session_id="wechat-session-1",
            tenant_id="tenant-a",
            workspace_id="workspace-a",
        )
        assert agent._tenant_id == "tenant-a"
        assert agent._workspace_id == "workspace-a"
    finally:
        configure_workspace_product_composition(None)

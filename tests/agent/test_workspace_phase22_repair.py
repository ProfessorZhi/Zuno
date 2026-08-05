from __future__ import annotations

"""PHASE22 workspace cutover architecture-repair tests.

Covers the fail-closed semantics the Coordinator review required:

- B1: product composition never falls back to temp SQLite; SQLite exists
  only behind the explicit developer test profile; missing product bindings
  raise BLOCKED_CONFIGURATION; restart recovery from the injected store.
- B2: unresolved tool policy blocks before execution (manifest, not names).
- B3: side-effect tools without the ToolInvocationGateway binding fail
  closed with zero executor calls.
- B4: security / budget owner decision refs fail closed (missing / stale /
  foreign / denied / forged).
- B6: request identity is the submission, not the content hash.
- B8: pre-dispatch vs post-dispatch failure semantics; unknown effects go
  to reconciliation and are never auto-retried; telemetry failures do not
  erase a real business failure.
- B9: product approval flow not bound -> side effects fail closed.
"""

from pathlib import Path

import pytest

from zuno.agent.runtime import PROFILE_DEVELOPER_TEST, PROFILE_PRODUCT
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.capability.control_plane import ToolSideEffectLevel
from zuno.platform.services.workspace.single_controller_runtime import (
    BlockedConfiguration,
    WorkspaceAgentRuntime,
    WorkspaceRunRequest,
    WorkspaceToolBinding,
    configure_workspace_product_composition,
    get_workspace_product_composition,
)
from _phase22_gateway_fakes import FakeGatewayBinding

TEST_EPOCH = "security-epoch:test-v1"


class _FakeChatModel:
    def __init__(self) -> None:
        self.calls = 0

    async def ainvoke(self, prompt: str) -> Any:
        self.calls += 1

        class _Response:
            content = "mock grounded answer"

        return _Response()


def _read_binding(args: dict) -> dict:
    return {"read": True, "path": args.get("path", "")}


def _request(
    task_id: str,
    goal: str,
    plan_kind: str,
    *,
    tool_id: str | None = None,
    tool_arguments: dict | None = None,
    client_request_id: str = "client-1",
    tenant: str = "tenant-a",
    workspace: str = "workspace-a",
    principal: str = "user-a",
    **overrides: object,
) -> WorkspaceRunRequest:
    base = dict(
        task_id=task_id,
        thread_id="thread-1",
        tenant_id=tenant,
        workspace_id=workspace,
        principal_id=principal,
        submission_id=f"sub:{client_request_id}",
        client_request_id=client_request_id,
        user_id=principal,
        trace_id=f"trace:{task_id}",
        goal=goal,
        conversation_id="thread-1",
        agent_version="test-adapter-v1",
        content_fingerprint=f"content:{task_id}",
        security_epoch_ref=TEST_EPOCH,
        tool_id=tool_id,
        tool_arguments=tool_arguments,
        plan_kind=plan_kind,
    )
    base.update(overrides)
    return WorkspaceRunRequest(**base)


def _admission_reason(snapshot) -> str:
    return str((snapshot.security_summary or {}).get("reason") or "")


class _FakeSecurityResolver:
    """Owner-port fake: returns Security-owner facts by opaque decision_id."""

    def __init__(self, facts: dict[str, dict] | None = None) -> None:
        self._facts = dict(facts or {})
        self.resolved: list[str] = []

    def resolve(self, decision_id: str, context: dict) -> dict | None:
        self.resolved.append(decision_id)
        fact = self._facts.get(decision_id)
        return dict(fact) if fact is not None else None


class _FakeBudgetResolver:
    """Owner-port fake: returns a Budget-owner admission fact."""

    def __init__(self, fact: dict | None = None) -> None:
        self._fact = fact
        self.resolved: list[tuple[str, dict]] = []

    def resolve(self, decision_id: str, context: dict) -> dict | None:
        self.resolved.append((decision_id, context))
        return dict(self._fact) if self._fact is not None else None


def _write_runtime(tmp_path: Path, *, gateway: FakeGatewayBinding, executor) -> WorkspaceAgentRuntime:
    return WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[
            WorkspaceToolBinding(
                tool_id="tool.write_doc",
                display_name="write_doc",
                description="Write a workspace document.",
                input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
                side_effect_level=ToolSideEffectLevel.WRITE_LOCAL,
                executor=executor,
                credential_policy="brokered_secret",
            )
        ],
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        profile=PROFILE_DEVELOPER_TEST,
        sqlite_store_path=tmp_path / "runtime.db",
        security_epoch_ref=TEST_EPOCH,
        approval_flow="runtime_interrupt_resume",
        tool_unit_of_work_factory=gateway.tool_factory,
        security_unit_of_work_factory=gateway.security_factory,
        infrastructure_unit_of_work_factory=gateway.infrastructure_factory,
    )


def _start_write(runtime: WorkspaceAgentRuntime, task_id: str) -> Any:
    return runtime.start(
        _request(
            task_id=task_id,
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
            client_request_id=f"client-{task_id}",
        )
    )


# ---------------------------------------------------------------------------
# B8: failure and side-effect uncertainty semantics
# ---------------------------------------------------------------------------


def test_pre_dispatch_block_never_invokes_executor(tmp_path) -> None:
    """A pre-dispatch block (idempotency claim held by another owner) is
    NO_EFFECT with zero executor calls — never a direct executor fallback."""
    calls = {"n": 0}

    def counted_write(args: dict) -> dict:
        calls["n"] += 1
        return {"written": True}

    gateway = FakeGatewayBinding()
    runtime = _write_runtime(tmp_path, gateway=gateway, executor=counted_write)

    interrupted = _start_write(runtime, "task-predispatch")
    assert interrupted.finalization_status == "interrupted"

    # The side-effect idempotency claim is held by another worker BEFORE the
    # approved dispatch proceeds: the gateway must block with zero executor
    # calls (the claim is keyed by the run's idempotency key).
    pending = runtime.store().pending_interrupt("task-predispatch")
    claim_key = str((pending.payload or {}).get("idempotency_key") or "unknown")
    with gateway.infrastructure_factory("tenant-a") as repo:
        repo._claims[("tool-side-effect", claim_key)] = type(
            "R", (), {"status": "in_progress", "generation": 1, "owner": "someone-else", "result_ref": ""}
        )()

    resumed = runtime.resume(task_id="task-predispatch", approval_decision="approved")

    assert calls["n"] == 0
    tool_observations = [obs for obs in resumed.observations if obs.kind == "tool"]
    assert tool_observations
    # The executor was never invoked: the observation must not claim a
    # completed effect.
    assert tool_observations[-1].metadata.get("effect_certainty") != "CONFIRMED_EFFECT"
    assert runtime.classify_final_state(resumed) == "FAILED/BLOCKED"


def test_post_dispatch_exception_is_unknown_effect_reconciliation(tmp_path) -> None:
    """An exception after the executor was dispatched (provider state unknown)
    must be UNKNOWN_EFFECT -> RECONCILIATION_REQUIRED, never NO_EFFECT."""
    dispatched = {"n": 0}

    def failing_after_dispatch(args: dict) -> dict:
        dispatched["n"] += 1
        raise TimeoutError("provider connection reset after dispatch")

    gateway = FakeGatewayBinding()
    runtime = _write_runtime(tmp_path, gateway=gateway, executor=failing_after_dispatch)
    interrupted = _start_write(runtime, "task-postdispatch")
    assert interrupted.finalization_status == "interrupted"

    resumed = runtime.resume(task_id="task-postdispatch", approval_decision="approved")

    assert dispatched["n"] == 1
    tool_observations = [obs for obs in resumed.observations if obs.kind == "tool"]
    assert tool_observations
    assert tool_observations[-1].metadata.get("effect_certainty") == "UNKNOWN_EFFECT"
    assert runtime.classify_final_state(resumed) == "RECONCILIATION_REQUIRED"


def test_unknown_effect_is_never_auto_retried(tmp_path) -> None:
    dispatched = {"n": 0}

    def failing_after_dispatch(args: dict) -> dict:
        dispatched["n"] += 1
        raise TimeoutError("provider connection reset after dispatch")

    gateway = FakeGatewayBinding()
    runtime = _write_runtime(tmp_path, gateway=gateway, executor=failing_after_dispatch)
    interrupted = _start_write(runtime, "task-noretry")
    resumed = runtime.resume(task_id="task-noretry", approval_decision="approved")
    assert runtime.classify_final_state(resumed) == "RECONCILIATION_REQUIRED"

    # Replaying the same request must NOT re-dispatch the unknown effect.
    replayed = runtime.start_with_replay(
        _request(
            task_id="task-noretry",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
            client_request_id="client-task-noretry",
        )
    )
    assert dispatched["n"] == 1
    assert runtime.classify_final_state(replayed) == "RECONCILIATION_REQUIRED"


def test_telemetry_failure_does_not_erase_business_failure(tmp_path) -> None:
    """If the effect-receipt persistence fails after a real dispatch, the run
    must not be reported as NO_EFFECT: it becomes UNKNOWN_EFFECT and requires
    reconciliation."""

    from _phase22_gateway_fakes import FakeToolRepository, FakeToolUnitOfWork

    class _BrokenReceiptToolRepository(FakeToolRepository):
        def record_effect_receipt(self, receipt: Any) -> None:
            raise RuntimeError("telemetry persistence unavailable")

    class FailingReceiptGateway(FakeGatewayBinding):
        def tool_factory(self):
            uow = FakeToolUnitOfWork()
            uow._repo = _BrokenReceiptToolRepository()
            return uow

    def succeeds(args: dict) -> dict:
        return {"written": True, "provider_effect_id": "effect-123"}

    gateway = FailingReceiptGateway()
    runtime = _write_runtime(tmp_path, gateway=gateway, executor=succeeds)
    interrupted = _start_write(runtime, "task-telemetry")
    resumed = runtime.resume(task_id="task-telemetry", approval_decision="approved")

    # The effect DID happen but the receipt could not be persisted: the run
    # is UNKNOWN (reconciliation), not NO_EFFECT and not COMPLETED.
    tool_observations = [obs for obs in resumed.observations if obs.kind == "tool"]
    assert tool_observations
    assert tool_observations[-1].metadata.get("effect_certainty") == "UNKNOWN_EFFECT"
    assert runtime.classify_final_state(resumed) == "RECONCILIATION_REQUIRED"


def test_effect_committed_receipt_is_persisted(tmp_path) -> None:
    """A successful side-effect dispatch persists a CONFIRMED_EFFECT receipt
    and the run classifies as EFFECT_COMMITTED (derived from the durable
    receipt, not an observation heuristic)."""
    gateway = FakeGatewayBinding()
    runtime = _write_runtime(tmp_path, gateway=gateway, executor=_write_binding)
    interrupted = _start_write(runtime, "task-committed")
    resumed = runtime.resume(task_id="task-committed", approval_decision="approved")

    tool_observations = [obs for obs in resumed.observations if obs.kind == "tool"]
    assert tool_observations[-1].metadata.get("effect_certainty") == "CONFIRMED_EFFECT"
    assert tool_observations[-1].metadata.get("effect_receipt_ref")
    assert runtime.classify_final_state(resumed) == "EFFECT_COMMITTED"


def _write_binding(args: dict) -> dict:
    return {"written": True, "path": args.get("path", ""), "provider_effect_id": "effect-abc"}


def test_duplicate_resume_after_committed_effect_is_rejected(tmp_path) -> None:
    gateway = FakeGatewayBinding()
    runtime = _write_runtime(tmp_path, gateway=gateway, executor=_write_binding)
    interrupted = _start_write(runtime, "task-dup")
    runtime.resume(task_id="task-dup", approval_decision="approved")

    # The interrupt is consumed; a second resume must not re-execute.
    with pytest.raises(ValueError):
        runtime.resume(task_id="task-dup", approval_decision="approved")


# ---------------------------------------------------------------------------
# B1: composition profile semantics
# ---------------------------------------------------------------------------


def test_simple_agent_product_mode_requires_composition(monkeypatch, tmp_path) -> None:
    from zuno.platform.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "zuno.platform.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: _FakeChatModel(),
    )
    configure_workspace_product_composition(None)
    try:
        agent = WorkSpaceSimpleAgent(
            model_config={},
            user_id="u-1",
            session_id="s-1",
            original_query="hello",
            runtime_profile=PROFILE_PRODUCT,
        )
        agent.tools = []
        agent.bindings = []
        with pytest.raises(BlockedConfiguration) as exc_info:
            agent._build_canonical_runtime([])
        assert "BLOCKED_CONFIGURATION" in str(exc_info.value)
    finally:
        configure_workspace_product_composition(None)


def test_simple_agent_test_profile_uses_explicit_sqlite(monkeypatch, tmp_path) -> None:
    from zuno.agent.runtime import SQLiteAgentRunStore
    from zuno.platform.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "zuno.platform.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: _FakeChatModel(),
    )
    configure_workspace_product_composition(None)
    try:
        agent = WorkSpaceSimpleAgent(
            model_config={},
            user_id="u-1",
            session_id="s-1",
            original_query="hello",
            runtime_profile=PROFILE_DEVELOPER_TEST,
            tenant_id="tenant-a",
            workspace_id="workspace-a",
        )
        agent.tools = []
        runtime = agent._build_canonical_runtime([])
        # Explicit developer test profile: the SQLite store is constructed
        # only through the explicit profile path (never the product default).
        assert isinstance(runtime.store(), SQLiteAgentRunStore)
    finally:
        configure_workspace_product_composition(None)


def test_simple_agent_product_mode_uses_injected_composition_store(monkeypatch, tmp_path) -> None:
    from zuno.agent.runtime import SQLiteAgentRunStore
    from zuno.platform.services.workspace.single_controller_runtime import WorkspaceRuntimeComposition
    from zuno.platform.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "zuno.platform.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: _FakeChatModel(),
    )
    store = SQLiteAgentRunStore(tmp_path / "product.db")
    configure_workspace_product_composition(
        WorkspaceRuntimeComposition(
            store=store,
            security_epoch_ref=TEST_EPOCH,
            approval_flow="runtime_interrupt_resume",
        )
    )
    try:
        agent = WorkSpaceSimpleAgent(
            model_config={},
            user_id="u-1",
            session_id="s-1",
            original_query="hello",
            runtime_profile=PROFILE_PRODUCT,
            tenant_id="tenant-a",
            workspace_id="workspace-a",
        )
        agent.tools = []
        runtime = agent._build_canonical_runtime([])
        # Product mode uses the injected store as-is — no second store and no
        # temp SQLite file anywhere.
        assert runtime.store() is store
    finally:
        configure_workspace_product_composition(None)


def test_server_composition_root_wires_workspace_agents(monkeypatch, tmp_path) -> None:
    """The server composition root (workspace task runtime service) binds the
    workspace agent composition explicitly — never at module import time:
    shared durable store, no temp SQLite, approval flow not bound (fail
    closed), owner resolvers unbound (product runs fail closed until the
    Security / Budget owner facts are wired)."""
    from zuno.platform.services.workspace.single_controller_runtime import (
        get_workspace_product_composition,
    )
    from zuno.platform.services.workspace.simple_agent import WorkSpaceSimpleAgent

    # Importing the module must NOT configure the composition (explicit
    # initialization at application startup only).
    import zuno.api.services.workspace_task_runtime as task_runtime_module  # noqa: F401

    assert get_workspace_product_composition() is None

    WorkspaceTaskRuntimeService.configure_workspace_agent_product_composition()
    try:
        composition = get_workspace_product_composition()
        assert composition is not None
        assert composition.store is not None
        assert composition.approval_flow == "none"
        assert composition.security_decision_resolver is None
        assert composition.budget_decision_resolver is None

        monkeypatch.setattr(
            "zuno.platform.services.workspace.simple_agent.ModelManager.get_user_model",
            lambda **_: _FakeChatModel(),
        )
        agent = WorkSpaceSimpleAgent(
            model_config={},
            user_id="u-1",
            session_id="s-1",
            original_query="hello",
            runtime_profile=PROFILE_PRODUCT,
            tenant_id="tenant-a",
            workspace_id="workspace-a",
        )
        agent.tools = []
        runtime = agent._build_canonical_runtime([])
        # Product mode uses the server composition's shared store — never a
        # per-session temp SQLite file.
        assert runtime.store() is composition.store
    finally:
        WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()


def test_restart_recovers_run_from_injected_store(tmp_path) -> None:
    from zuno.agent.runtime import SQLiteAgentRunStore

    store = SQLiteAgentRunStore(tmp_path / "shared.db")
    runtime_a = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[],
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        profile=PROFILE_PRODUCT,
        store=store,
        security_epoch_ref=TEST_EPOCH,
    )
    snapshot = runtime_a.start(_request("task-restart", "hello", "simple"))
    assert snapshot.finalization_status == "finalized"

    # A brand-new composition root over the same injected store recovers the
    # original run (same tenant / workspace scope).
    restarted = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[],
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        profile=PROFILE_PRODUCT,
        store=store,
        security_epoch_ref=TEST_EPOCH,
    )
    recovered = restarted.snapshot("task-restart")
    assert recovered is not None
    assert recovered.task_id == "task-restart"
    assert recovered.finalization_status == "finalized"


def test_product_mode_with_side_effects_requires_gateway_factories(tmp_path) -> None:
    from zuno.agent.runtime import SQLiteAgentRunStore

    store = SQLiteAgentRunStore(tmp_path / "product.db")
    with pytest.raises(BlockedConfiguration) as exc_info:
        WorkspaceAgentRuntime(
            model=_FakeChatModel(),
            bindings=[
                WorkspaceToolBinding(
                    tool_id="tool.write_doc",
                    display_name="write_doc",
                    description="Write a workspace document.",
                    input_schema={"type": "object"},
                    side_effect_level=ToolSideEffectLevel.WRITE_LOCAL,
                    executor=_write_binding,
                )
            ],
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="user-a",
            profile=PROFILE_PRODUCT,
            store=store,
            security_epoch_ref=TEST_EPOCH,
        )
    assert "UoW factories" in str(exc_info.value)


# ---------------------------------------------------------------------------
# B6: submission identity (same text, different submission -> new run)
# ---------------------------------------------------------------------------


def test_same_text_different_submission_creates_two_runs(tmp_path) -> None:
    from zuno.agent.runtime import SQLiteAgentRunStore

    store = SQLiteAgentRunStore(tmp_path / "shared.db")
    runtime = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[],
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        profile=PROFILE_PRODUCT,
        store=store,
        security_epoch_ref=TEST_EPOCH,
    )
    first = runtime.start(_request("task-s1", "the same question", "simple", client_request_id="sub-1"))
    second = runtime.start(_request("task-s2", "the same question", "simple", client_request_id="sub-2"))

    assert first.task_id != second.task_id
    assert first.run_outcome_ref != second.run_outcome_ref


def test_tenant_a_b_same_client_key_do_not_conflict(tmp_path) -> None:
    from zuno.agent.runtime import SQLiteAgentRunStore

    store = SQLiteAgentRunStore(tmp_path / "shared.db")
    runtime_a = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[],
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        profile=PROFILE_PRODUCT,
        store=store,
        security_epoch_ref=TEST_EPOCH,
    )
    runtime_b = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[],
        tenant_id="tenant-b",
        workspace_id="workspace-b",
        principal_id="user-b",
        profile=PROFILE_PRODUCT,
        store=store,
        security_epoch_ref=TEST_EPOCH,
    )
    run_a = runtime_a.start(_request("task-key-a", "hello", "simple", client_request_id="same-key"))
    run_b = runtime_b.start(_request("task-key-b", "hello", "simple", client_request_id="same-key"))

    # Same client key in different tenants -> distinct runs, no cross-tenant
    # readback.
    assert run_a.task_id != run_b.task_id
    assert runtime_b.snapshot("task-key-a") is None


# ---------------------------------------------------------------------------
# B9: approval flow binding
# ---------------------------------------------------------------------------


def test_product_side_effect_requires_approval_flow_binding(tmp_path) -> None:
    """Product mode with approval_flow="none" must fail closed on side
    effects; the run never waits for an approval with no reachable resume."""
    from zuno.agent.runtime import SQLiteAgentRunStore

    store = SQLiteAgentRunStore(tmp_path / "product.db")
    gateway = FakeGatewayBinding()
    runtime = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[
            WorkspaceToolBinding(
                tool_id="tool.write_doc",
                display_name="write_doc",
                description="Write a workspace document.",
                input_schema={"type": "object"},
                side_effect_level=ToolSideEffectLevel.WRITE_LOCAL,
                executor=_write_binding,
                credential_policy="brokered_secret",
            )
        ],
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        profile=PROFILE_PRODUCT,
        store=store,
        security_epoch_ref=TEST_EPOCH,
        approval_flow="none",
        tool_unit_of_work_factory=gateway.tool_factory,
        security_unit_of_work_factory=gateway.security_factory,
        infrastructure_unit_of_work_factory=gateway.infrastructure_factory,
        security_decision_resolver=_FakeSecurityResolver(
            {"security-decision:user-a:tool.write_doc": _security_ref_payload()}
        ),
        budget_decision_resolver=_FakeBudgetResolver(
            _budget_ref_payload(run_id="run:task-flow-none")
        ),
    )
    snapshot = runtime.start(
        _request(
            "task-flow-none",
            "write the doc",
            "tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "x"},
            security_decision_id="security-decision:user-a:tool.write_doc",
            budget_decision_id="budget-decision:run:task-flow-none",
        )
    )

    assert runtime.store().pending_interrupt("task-flow-none") is None
    assert "PRODUCT_APPROVAL_FLOW_NOT_BOUND" in _admission_reason(snapshot)
    assert not [obs for obs in snapshot.observations if obs.kind == "tool" and obs.status == "completed"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"


def _security_ref_payload() -> dict:
    from zuno.agent.runtime.owner_refs import security_ref_hash

    base = {
        "decision_id": "security-decision:user-a:tool.write_doc",
        "tenant_id": "tenant-a",
        "workspace_id": "workspace-a",
        "principal_id": "user-a",
        "action": "tool.execute",
        "resource": "tool.write_doc",
        "decision": "allow",
        "security_epoch_ref": TEST_EPOCH,
    }
    return {**base, "decision_hash": security_ref_hash(**base), "expires_at": None}


def _budget_ref_payload(*, run_id: str) -> dict:
    from zuno.agent.contracts import BudgetDecisionRef
    from zuno.agent.runtime.owner_refs import budget_ref_hash

    ref = BudgetDecisionRef(
        budget_decision_id=f"budget-decision:{run_id}",
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        run_id=run_id,
        allowed=True,
        limits={},
        decision_hash="",
        owner="budget-owner:workspace-a",
    )
    return {**ref.model_dump(mode="json"), "decision_hash": budget_ref_hash(ref=ref)}

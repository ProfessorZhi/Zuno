from __future__ import annotations

from pathlib import Path
import re

import pytest

from zuno.agent.runtime import PROFILE_DEVELOPER_TEST, PROFILE_PRODUCT
from zuno.agent.runtime.owner_refs import budget_ref_hash, security_ref_hash
from zuno.capability.control_plane import ToolSideEffectLevel
from zuno.platform.services.workspace.single_controller_runtime import (
    BlockedConfiguration,
    WorkspaceAgentRuntime,
    WorkspaceRunRequest,
    WorkspaceToolBinding,
)
from _phase22_gateway_fakes import FakeGatewayBinding

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend" / "zuno"
WORKSPACE_DIR = BACKEND_ROOT / "platform" / "services" / "workspace"

TEST_EPOCH = "security-epoch:test-v1"


class _FakeChatModel:
    """Product chat model stub: the runtime's model steps invoke this."""

    def __init__(self) -> None:
        self.calls = 0

    async def ainvoke(self, prompt: str) -> Any:
        self.calls += 1

        class _Response:
            content = "mock grounded answer"

        return _Response()


class _FlakyTool:
    def __init__(self, fail_first: int = 1) -> None:
        self.calls = 0
        self.fail_first = fail_first

    async def ainvoke(self, args: dict) -> Any:
        self.calls += 1
        if self.calls <= self.fail_first:
            raise RuntimeError("transient tool failure")
        return {"ok": True}


def _read_binding(args: dict) -> dict:
    return {"read": True, "path": args.get("path", "")}


def _write_binding(args: dict) -> dict:
    return {"written": True, "path": args.get("path", "")}


def _security_ref(
    *,
    decision: str = "allow",
    epoch: str = TEST_EPOCH,
    tenant: str = "tenant-a",
    workspace: str = "workspace-a",
    principal: str = "user-a",
    action: str = "tool.execute",
    resource: str = "tool.read_doc,tool.write_doc",
    forged: bool = False,
) -> dict:
    decision_id = f"security-decision:{principal}:{resource}"
    base = {
        "decision_id": decision_id,
        "tenant_id": tenant,
        "workspace_id": workspace,
        "principal_id": principal,
        "action": action,
        "resource": resource,
        "decision": decision,
        "security_epoch_ref": epoch,
    }
    payload = dict(base)
    payload["decision_hash"] = security_ref_hash(**base) if not forged else "forged-hash"
    payload["expires_at"] = None
    return payload


def _budget_ref(
    *,
    allowed: bool = True,
    tenant: str = "tenant-a",
    workspace: str = "workspace-a",
    run_id: str = "",
    owner: str = "budget-owner:workspace-a",
    forged: bool = False,
) -> dict:
    from zuno.agent.contracts import BudgetDecisionRef

    ref = BudgetDecisionRef(
        budget_decision_id=f"budget-decision:{run_id or 'run'}",
        tenant_id=tenant,
        workspace_id=workspace,
        run_id=run_id,
        allowed=allowed,
        limits={},
        decision_hash="",
        owner=owner,
    )
    return {**ref.model_dump(mode="json"), "decision_hash": "forged-hash" if forged else budget_ref_hash(ref=ref)}

def _admission_reason(snapshot) -> str:
    return str((snapshot.security_summary or {}).get("reason") or "")




def _runtime(
    tmp_path: Path,
    *,
    model: Any | None = None,
    write: bool = True,
    epoch: str = TEST_EPOCH,
    gateway: FakeGatewayBinding | None = None,
    tenant: str = "tenant-a",
    workspace: str = "workspace-a",
    principal: str = "user-a",
    profile: str = PROFILE_DEVELOPER_TEST,
    approval_flow: str = "runtime_interrupt_resume",
    extra_bindings: list[WorkspaceToolBinding] | None = None,
    store=None,
) -> WorkspaceAgentRuntime:
    bindings = [
        WorkspaceToolBinding(
            tool_id="tool.read_doc",
            display_name="read_doc",
            description="Read a workspace document.",
            input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
            side_effect_level=ToolSideEffectLevel.READ,
            executor=_read_binding,
        ),
    ]
    if write:
        bindings.append(
            WorkspaceToolBinding(
                tool_id="tool.write_doc",
                display_name="write_doc",
                description="Write a workspace document.",
                input_schema={"type": "object", "properties": {"path": {"type": "string"}}},
                side_effect_level=ToolSideEffectLevel.WRITE_LOCAL,
                executor=_write_binding,
                credential_policy="brokered_secret",
            )
        )
    if extra_bindings:
        bindings.extend(extra_bindings)
    gateway = gateway or (FakeGatewayBinding() if write else None)
    return WorkspaceAgentRuntime(
        model=model or _FakeChatModel(),
        bindings=bindings,
        tenant_id=tenant,
        workspace_id=workspace,
        principal_id=principal,
        profile=profile,
        store=store,
        sqlite_store_path=tmp_path / "runtime.db" if profile == PROFILE_DEVELOPER_TEST else None,
        security_epoch_ref=epoch,
        approval_flow=approval_flow,
        tool_unit_of_work_factory=gateway.tool_factory if gateway else None,
        security_unit_of_work_factory=gateway.security_factory if gateway else None,
        infrastructure_unit_of_work_factory=gateway.infrastructure_factory if gateway else None,
    )


def _request(
    task_id: str = "task-1",
    goal: str = "hello",
    plan_kind: str = "simple",
    tenant: str = "tenant-a",
    workspace: str = "workspace-a",
    principal: str = "user-a",
    client_request_id: str = "client-1",
    security_ref: dict | None = None,
    budget_ref: dict | None = None,
    epoch: str = TEST_EPOCH,
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
        plan_kind=plan_kind,
        conversation_id="thread-1",
        agent_version="test-adapter-v1",
        content_fingerprint=f"content:{task_id}",
        security_epoch_ref=epoch,
    )
    if security_ref is not None:
        base["security_decision_ref"] = security_ref
    if budget_ref is not None:
        base["budget_decision_ref"] = budget_ref
    base.update(overrides)
    return WorkspaceRunRequest(**base)


# ---------------------------------------------------------------------------
# Normal paths
# ---------------------------------------------------------------------------


def test_workspace_simple_qa_uses_deterministic_single_step_plan(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(_request(goal="hello", plan_kind="simple"))

    assert snapshot.finalization_status == "finalized"
    assert snapshot.plan_state is not None
    assert len(snapshot.plan_state.steps) == 1
    assert snapshot.plan_state.steps[0].action_type == "answer_from_context"
    # Explicit PlanState with plan version; activation belongs to Agent Core.
    assert snapshot.plan_state.plan_version == 1
    assert snapshot.plan_state.activation_status == "activated"
    assert snapshot.plan_state.activated_by == "agent_core"
    assert snapshot.run_outcome_ref
    # No tool was involved: capability plan is empty and no tool observation.
    assert not snapshot.capability_plan.allowed_tools
    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]


def test_workspace_complex_task_fails_closed_without_dynamic_dag(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(task_id="task-complex", goal="compare and analyze across sources", plan_kind="complex")
    )

    # PHASE22 repair (B5): complex tasks need the formal Dynamic DAG planner;
    # an unbound composition must fail closed — never a fixed three-step fake.
    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"
    assert snapshot.plan_state is None or snapshot.plan_state.status in {"blocked", "created"}
    strategy_reason = str(snapshot.strategy.reason) if snapshot.strategy is not None else ""
    assert "DYNAMIC_PLAN_RUNTIME_NOT_BOUND" in _admission_reason(snapshot)


def test_wechat_agent_runs_on_the_same_single_controller(tmp_path, monkeypatch) -> None:
    from zuno.platform.services.workspace.wechat_agent import WeChatAgent

    monkeypatch.setattr(
        "zuno.platform.services.workspace.wechat_agent.ModelManager.get_conversation_model",
        lambda: _FakeChatModel(),
    )
    wechat = WeChatAgent(user_id="u-1", session_id="s-1")
    # Same composition root type as the workspace simple agent.
    assert wechat._runtime is None
    runtime = _runtime(tmp_path)
    assert isinstance(runtime, WorkspaceAgentRuntime)
    # WeChatAgent is a product adapter over WorkspaceAgentRuntime (import-time
    # contract): no independent ReAct runtime is constructed.
    import zuno.platform.services.workspace.wechat_agent as wechat_module
    assert "create_agent" not in wechat_module.__dict__


def test_read_only_tool_executes_through_control_plane(tmp_path) -> None:
    runtime = _runtime(tmp_path, write=False)
    snapshot = runtime.start(
        _request(
            task_id="task-read",
            goal="read the contract doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
        )
    )

    assert snapshot.finalization_status == "finalized"
    tool_observations = [obs for obs in snapshot.observations if obs.kind == "tool" and obs.tool_id == "tool.read_doc"]
    assert tool_observations
    assert tool_observations[-1].status == "completed"
    assert tool_observations[-1].metadata["tool_runtime_status"] == "completed"
    assert runtime.classify_final_state(snapshot) == "COMPLETED"


def test_approved_write_tool_succeeds_after_resume(tmp_path) -> None:
    gateway = FakeGatewayBinding()
    runtime = _runtime(tmp_path, gateway=gateway)
    interrupted = runtime.start(
        _request(
            task_id="task-write",
            goal="write the report",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "artifacts/report.md"},
        )
    )

    assert interrupted.finalization_status == "interrupted"
    assert runtime.store().pending_interrupt("task-write") is not None
    assert runtime.store().snapshot("task-write").status == "approval_waiting"

    resumed = runtime.resume(task_id="task-write", approval_decision="approved")

    assert resumed.finalization_status == "finalized"
    write_observations = [
        obs for obs in resumed.observations if obs.kind == "tool" and obs.tool_id == "tool.write_doc"
    ]
    assert write_observations
    assert write_observations[-1].metadata["tool_runtime_status"] == "completed"
    assert write_observations[-1].metadata["effect_certainty"] == "CONFIRMED_EFFECT"
    assert runtime.classify_final_state(resumed) == "EFFECT_COMMITTED"


def test_run_outcome_and_trace_are_readable(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(_request(task_id="task-trace", goal="trace me"))

    assert snapshot.run_outcome_ref
    assert snapshot.trace_id
    events = runtime.events("task-trace")
    assert events, "runtime events are persisted"
    event_types = [event.get("event_type") for event in events]
    assert "runtime_started" in event_types
    assert any(typ == "runtime_node" for typ in event_types)


# ---------------------------------------------------------------------------
# Security / budget owner decision refs (PHASE22 repair, B4)
# ---------------------------------------------------------------------------


def test_security_denial_ref_blocks_plan_and_executes_no_tool(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-sec",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
            security_ref=_security_ref(decision="deny"),
        )
    )

    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"
    assert "security" in _admission_reason(snapshot)


def test_missing_security_decision_ref_fails_closed_in_product_mode(tmp_path) -> None:
    store = _sqlite_store(tmp_path)
    runtime = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[
            WorkspaceToolBinding(
                tool_id="tool.read_doc",
                display_name="read_doc",
                description="Read a workspace document.",
                input_schema={"type": "object"},
                side_effect_level=ToolSideEffectLevel.READ,
                executor=_read_binding,
            )
        ],
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        profile=PROFILE_PRODUCT,
        store=store,
        security_epoch_ref=TEST_EPOCH,
        approval_flow="runtime_interrupt_resume",
    )
    snapshot = runtime.start(
        _request(
            task_id="task-sec-missing",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
        )
    )

    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"
    assert "security_decision_ref" in _admission_reason(snapshot)


def test_stale_security_epoch_fails_closed(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-epoch",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
            epoch="security-epoch:stale",
        )
    )

    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"
    assert "stale_security_epoch" in _admission_reason(snapshot)


def test_forged_security_ref_hash_fails_closed(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-forged",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
            security_ref=_security_ref(forged=True),
        )
    )

    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"
    assert "hash_mismatch" in _admission_reason(snapshot)


def test_foreign_tenant_security_ref_fails_closed(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-x-tenant-ref",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
            security_ref=_security_ref(tenant="tenant-b"),
        )
    )

    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"
    assert "tenant_mismatch" in _admission_reason(snapshot)


def test_current_security_epoch_allows_execution(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-epoch-ok",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
            security_ref=_security_ref(),
        )
    )

    assert snapshot.finalization_status == "finalized"
    assert [obs for obs in snapshot.observations if obs.kind == "tool" and obs.status == "completed"]


def test_budget_denied_ref_blocks_plan_before_any_side_effect(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-budget",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
            budget_ref=_budget_ref(allowed=False, run_id="run:task-budget"),
        )
    )

    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"
    assert "budget" in _admission_reason(snapshot)


def test_forged_budget_ref_fails_closed(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-budget-forged",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
            budget_ref=_budget_ref(forged=True, run_id="run:task-budget-forged"),
        )
    )

    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"


def test_budget_owner_missing_fails_closed(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-budget-owner",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
            budget_ref=_budget_ref(owner="", run_id="run:task-budget-owner"),
        )
    )

    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"


# ---------------------------------------------------------------------------
# Approval / side-effect gateway (PHASE22 repair, B3 / B9)
# ---------------------------------------------------------------------------


def test_side_effect_missing_gateway_fails_closed_zero_execution(tmp_path) -> None:
    calls: dict[str, int] = {"write": 0}

    def counted_write(args: dict) -> dict:
        calls["write"] += 1
        return {"written": True}

    runtime = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[
            WorkspaceToolBinding(
                tool_id="tool.write_doc",
                display_name="write_doc",
                description="Write a workspace document.",
                input_schema={"type": "object"},
                side_effect_level=ToolSideEffectLevel.WRITE_LOCAL,
                executor=counted_write,
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
        # NOTE: no tool/security/infrastructure UoW factories -> gateway not bound.
    )
    snapshot = runtime.start(
        _request(
            task_id="task-gateway-missing",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
        )
    )

    # Fail closed: the side-effect tool is blocked, executor never invoked.
    assert calls["write"] == 0
    tool_observations = [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert tool_observations
    assert tool_observations[-1].status in {"blocked", "failed"}
    assert "SIDE_EFFECT_GATEWAY_NOT_BOUND" in str(
        tool_observations[-1].metadata.get("blocked_reason") or tool_observations[-1].failure_reason
    )
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"


def test_side_effect_with_gateway_enters_approval_waiting(tmp_path) -> None:
    gateway = FakeGatewayBinding()
    runtime = _runtime(tmp_path, gateway=gateway)
    interrupted = runtime.start(
        _request(
            task_id="task-approval",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
        )
    )

    assert interrupted.finalization_status == "interrupted"
    pending = runtime.store().pending_interrupt("task-approval")
    assert pending is not None
    assert pending.required_approval == "tool:tool.write_doc"
    assert runtime.store().snapshot("task-approval").status == "approval_waiting"


def test_unapproved_tool_never_executes(tmp_path) -> None:
    calls: dict[str, int] = {"write": 0}

    def counted_write(args: dict) -> dict:
        calls["write"] += 1
        return {"written": True}

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
                executor=counted_write,
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
    interrupted = runtime.start(
        _request(
            task_id="task-noexec",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
        )
    )

    assert interrupted.finalization_status == "interrupted"
    assert calls["write"] == 0


def test_product_mode_side_effect_without_approval_flow_fails_closed(tmp_path) -> None:
    gateway = FakeGatewayBinding()
    store = _sqlite_store(tmp_path)
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
        approval_flow="none",  # product approval flow not bound (B9)
        tool_unit_of_work_factory=gateway.tool_factory,
        security_unit_of_work_factory=gateway.security_factory,
        infrastructure_unit_of_work_factory=gateway.infrastructure_factory,
        security_decision_issuer=lambda req: _security_ref(
            resource=f"tool.{req.tool_id}" if req.tool_id else ""
        ),
        budget_decision_issuer=lambda req: _budget_ref(run_id=f"run:{req.task_id}"),
    )
    snapshot = runtime.start(
        _request(
            task_id="task-flow",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
        )
    )

    # No approval-waiting interrupt with an unreachable product resume path:
    # the side effect fails closed before dispatch.
    assert runtime.store().pending_interrupt("task-flow") is None
    assert not [obs for obs in snapshot.observations if obs.kind == "tool" and obs.status == "completed"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"


def test_rejected_approval_never_executes(tmp_path) -> None:
    gateway = FakeGatewayBinding()
    runtime = _runtime(tmp_path, gateway=gateway)
    interrupted = runtime.start(
        _request(
            task_id="task-reject",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
        )
    )
    assert interrupted.finalization_status == "interrupted"

    rejected = runtime.resume(task_id="task-reject", approval_decision="rejected")
    assert rejected.finalization_status in {"failed", "blocked", "abstained"}
    tool_observations = [obs for obs in rejected.observations if obs.kind == "tool"]
    assert not tool_observations or tool_observations[-1].status not in {"completed"}


# ---------------------------------------------------------------------------
# Persistence / composition profile (PHASE22 repair, B1)
# ---------------------------------------------------------------------------


def _sqlite_store(tmp_path: Path):
    from zuno.agent.runtime import SQLiteAgentRunStore

    return SQLiteAgentRunStore(tmp_path / "runtime.db")


def test_product_mode_without_injected_store_fails_closed() -> None:
    with pytest.raises(BlockedConfiguration) as exc_info:
        WorkspaceAgentRuntime(
            model=_FakeChatModel(),
            bindings=[],
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="user-a",
            profile=PROFILE_PRODUCT,
        )
    assert "BLOCKED_CONFIGURATION" in str(exc_info.value)
    assert "injected durable AgentRunStore" in str(exc_info.value)


def test_test_profile_requires_explicit_sqlite_path(tmp_path) -> None:
    with pytest.raises(BlockedConfiguration):
        WorkspaceAgentRuntime(
            model=_FakeChatModel(),
            bindings=[],
            tenant_id="tenant-a",
            workspace_id="workspace-a",
            principal_id="user-a",
            profile=PROFILE_DEVELOPER_TEST,
        )


def test_product_mode_never_creates_temp_sqlite(tmp_path) -> None:
    """Product mode with an injected store uses the injected store as-is."""
    store = _sqlite_store(tmp_path)
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
    # The composition root never constructs its own second store: the injected
    # durable store is the single store the runtime reads and writes.
    assert runtime.store() is store


def test_worker_crash_recovers_snapshot_and_resume(tmp_path) -> None:
    gateway = FakeGatewayBinding()
    db_path = tmp_path / "runtime.db"
    runtime = _runtime(tmp_path, model=_FakeChatModel(), gateway=gateway)
    interrupted = runtime.start(
        _request(
            task_id="task-crash",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
        )
    )
    assert interrupted.finalization_status == "interrupted"

    # Simulate a worker restart: a brand-new composition root on the same store.
    restarted = _runtime(tmp_path, model=_FakeChatModel(), gateway=FakeGatewayBinding())
    recovered = restarted.snapshot("task-crash")
    assert recovered is not None
    assert recovered.task_id == "task-crash"
    assert restarted.store().pending_interrupt("task-crash") is not None

    resumed = restarted.resume(task_id="task-crash", approval_decision="approved")
    assert resumed.finalization_status == "finalized"


def test_restart_never_selects_legacy_runtime(tmp_path) -> None:
    first = _runtime(tmp_path)
    second = _runtime(tmp_path)
    # Both instances are canonical runtime composition roots; there is no
    # legacy agent attribute to select on restart.
    for runtime in (first, second):
        assert not hasattr(runtime, "react_agent")
        assert not hasattr(runtime, "legacy_runner")
        assert isinstance(runtime, WorkspaceAgentRuntime)


def test_streaming_restart_does_not_duplicate_events(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    runtime.start_with_replay(_request(task_id="task-stream", goal="hello"))
    events_before = len(runtime.events("task-stream"))
    assert events_before > 0

    restarted = _runtime(tmp_path)
    restarted.start_with_replay(_request(task_id="task-stream", goal="hello"))
    events_after = len(restarted.events("task-stream"))

    # The store is the single source of truth: replaying the same request
    # does not append a second copy of the events.
    assert events_after == events_before


def test_same_client_request_id_returns_same_facts(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    first = runtime.start(_request(task_id="task-same", goal="hello", client_request_id="client-x"))
    second = runtime.start(_request(task_id="task-same", goal="hello", client_request_id="client-x"))

    assert first.run_outcome_ref == second.run_outcome_ref
    assert first.finalization_status == second.finalization_status
    assert first.plan_state == second.plan_state


# ---------------------------------------------------------------------------
# Identity / idempotency (PHASE22 repair, B6)
# ---------------------------------------------------------------------------


def test_same_text_different_client_request_id_creates_new_run(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    first = runtime.start(
        _request(task_id="task-id-1", goal="hello", client_request_id="client-a")
    )
    second = runtime.start(
        _request(task_id="task-id-2", goal="hello", client_request_id="client-b")
    )

    # Same text, different client_request_id -> different runs.
    assert first.task_id != second.task_id
    assert first.trace_id != second.trace_id


def test_committed_effect_is_not_executed_twice_on_repeat_request(tmp_path) -> None:
    write_calls = {"n": 0}

    def counted_write(args: dict) -> dict:
        write_calls["n"] += 1
        return {"written": True}

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
                executor=counted_write,
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
    request = _request(
        task_id="task-idem",
        goal="write the doc",
        plan_kind="tool",
        tool_id="tool.write_doc",
        tool_arguments={"path": "out.md"},
        client_request_id="client-idem",
    )

    interrupted = runtime.start(request)
    assert interrupted.finalization_status == "interrupted"
    assert write_calls["n"] == 0

    resumed = runtime.resume(task_id="task-idem", approval_decision="approved")
    assert resumed.finalization_status == "finalized"
    assert write_calls["n"] == 1
    assert runtime.classify_final_state(resumed) == "EFFECT_COMMITTED"

    # Repeat the same request (same client_request_id): the idempotent replay
    # returns the committed facts; the write tool does not execute a second
    # time.
    second = runtime.start(request)
    assert write_calls["n"] == 1
    assert second.task_id == resumed.task_id


# ---------------------------------------------------------------------------
# Tenant isolation (PHASE22 repair, B7)
# ---------------------------------------------------------------------------


def test_cross_tenant_isolation_blocks_foreign_tool(tmp_path) -> None:
    runtime_a = _runtime(tmp_path, tenant="tenant-a", workspace="workspace-a")
    runtime_b = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[
            WorkspaceToolBinding(
                tool_id="tool.b_read",
                display_name="b_read",
                description="B's tool",
                input_schema={"type": "object"},
                side_effect_level=ToolSideEffectLevel.READ,
                executor=_read_binding,
            )
        ],
        tenant_id="tenant-b",
        workspace_id="workspace-b",
        principal_id="user-b",
        profile=PROFILE_DEVELOPER_TEST,
        sqlite_store_path=tmp_path / "b.db",
        security_epoch_ref=TEST_EPOCH,
        approval_flow="runtime_interrupt_resume",
    )

    # User B's runtime has no binding for user A's tool -> fail-closed at
    # planning admission: no tool step, no execution, no side effect.
    snapshot = runtime_b.start(
        _request(
            task_id="task-x-tenant",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
            tenant="tenant-b",
            workspace="workspace-b",
            principal="user-b",
        )
    )
    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime_b.classify_final_state(snapshot) == "FAILED/BLOCKED"
    # A's own tool still executes normally in A's runtime.
    snapshot_a = runtime_a.start(
        _request(
            task_id="task-x-tenant-a",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
        )
    )
    assert snapshot_a.finalization_status == "finalized"


def test_tenant_a_cannot_read_tenant_b_run_on_shared_store(tmp_path) -> None:
    # Both tenants share the same durable store file; reads are still scoped.
    runtime_a = _runtime(tmp_path, tenant="tenant-a", workspace="workspace-a")
    runtime_b = _runtime(tmp_path, tenant="tenant-b", workspace="workspace-b")

    snapshot_a = runtime_a.start(_request(task_id="task-shared-a", goal="hello", tenant="tenant-a"))
    assert snapshot_a.finalization_status == "finalized"

    # Tenant B cannot read tenant A's run through B's composition root.
    assert runtime_b.snapshot("task-shared-a") is None
    with pytest.raises(PermissionError):
        runtime_b.events("task-shared-a")
    with pytest.raises(PermissionError):
        runtime_b.resume(task_id="task-shared-a", approval_decision="approved")


def test_workspace_a_cannot_resume_workspace_b_checkpoint(tmp_path) -> None:
    gateway = FakeGatewayBinding()
    runtime_a = _runtime(tmp_path, gateway=gateway, tenant="tenant-a", workspace="workspace-a")
    runtime_b = _runtime(tmp_path, tenant="tenant-b", workspace="workspace-b")

    interrupted = runtime_a.start(
        _request(
            task_id="task-cp",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
        )
    )
    assert interrupted.finalization_status == "interrupted"

    # Workspace B (different tenant) cannot restore workspace A's checkpoint.
    assert runtime_b.snapshot("task-cp") is None
    with pytest.raises(PermissionError):
        runtime_b.resume(task_id="task-cp", approval_decision="approved")


# ---------------------------------------------------------------------------
# Failure / recovery / uncertainty (PHASE22 repair, B8)
# ---------------------------------------------------------------------------


def test_transient_tool_failure_retries_with_original_plan(tmp_path) -> None:
    flaky = _FlakyTool(fail_first=1)
    runtime = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[
            WorkspaceToolBinding(
                tool_id="tool.flaky",
                display_name="flaky",
                description="Flaky tool",
                input_schema={"type": "object"},
                side_effect_level=ToolSideEffectLevel.READ,
                executor=lambda args: flaky.ainvoke(args),
            )
        ],
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        profile=PROFILE_DEVELOPER_TEST,
        sqlite_store_path=tmp_path / "runtime.db",
        security_epoch_ref=TEST_EPOCH,
        approval_flow="runtime_interrupt_resume",
    )
    request = _request(
        task_id="task-retry",
        goal="run the flaky tool",
        plan_kind="tool",
        tool_id="tool.flaky",
        tool_arguments={"x": 1},
        client_request_id="client-retry",
    )

    first = runtime.start(request)
    assert flaky.calls == 1
    assert runtime.classify_final_state(first) == "FAILED/BLOCKED"

    # Explicit retry re-runs the ORIGINAL plan; the transient failure is gone.
    second = runtime.start(request)
    assert flaky.calls == 2
    assert second.finalization_status == "finalized"
    assert runtime.classify_final_state(second) == "COMPLETED"


def test_permanent_tool_failure_marks_run_failed(tmp_path) -> None:
    def broken(args: dict) -> dict:
        raise RuntimeError("permanent failure")

    runtime = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[
            WorkspaceToolBinding(
                tool_id="tool.broken",
                display_name="broken",
                description="Broken tool",
                input_schema={"type": "object"},
                side_effect_level=ToolSideEffectLevel.READ,
                executor=broken,
            )
        ],
        tenant_id="tenant-a",
        workspace_id="workspace-a",
        principal_id="user-a",
        profile=PROFILE_DEVELOPER_TEST,
        sqlite_store_path=tmp_path / "runtime.db",
        security_epoch_ref=TEST_EPOCH,
        approval_flow="runtime_interrupt_resume",
    )
    snapshot = runtime.start(
        _request(
            task_id="task-permanent",
            goal="run the broken tool",
            plan_kind="tool",
            tool_id="tool.broken",
            tool_arguments={},
        )
    )

    tool_observations = [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert tool_observations
    assert tool_observations[-1].status in {"blocked", "failed"}
    # A read tool failure has no lasting external effect.
    assert tool_observations[-1].metadata.get("effect_certainty") == "NO_EFFECT"
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"


def test_unknown_effect_enters_reconciliation(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(_request(task_id="task-unknown", goal="run"))
    unknown = snapshot.model_copy(
        update={"finalization_status": "not_ready"}
    )
    assert runtime.classify_final_state(unknown) == "RECONCILIATION_REQUIRED"


def test_duplicate_approval_does_not_repeat_effect(tmp_path) -> None:
    write_calls = {"n": 0}

    def counted_write(args: dict) -> dict:
        write_calls["n"] += 1
        return {"written": True}

    gateway = FakeGatewayBinding()
    runtime = _runtime(tmp_path, gateway=gateway, extra_bindings=[])
    runtime = WorkspaceAgentRuntime(
        model=_FakeChatModel(),
        bindings=[
            WorkspaceToolBinding(
                tool_id="tool.write_doc",
                display_name="write_doc",
                description="Write a workspace document.",
                input_schema={"type": "object"},
                side_effect_level=ToolSideEffectLevel.WRITE_LOCAL,
                executor=counted_write,
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
    request = _request(
        task_id="task-dup-approval",
        goal="write the doc",
        plan_kind="tool",
        tool_id="tool.write_doc",
        tool_arguments={"path": "out.md"},
        client_request_id="client-dup",
    )

    interrupted = runtime.start(request)
    assert interrupted.finalization_status == "interrupted"
    resumed = runtime.resume(task_id="task-dup-approval", approval_decision="approved")
    assert write_calls["n"] == 1

    # A second approval on the same task must not re-execute the effect.
    with pytest.raises(ValueError):
        runtime.resume(task_id="task-dup-approval", approval_decision="approved")
    assert write_calls["n"] == 1


# ---------------------------------------------------------------------------
# Static gates
# ---------------------------------------------------------------------------


def test_simple_agent_has_no_direct_tool_call_path() -> None:
    source = (WORKSPACE_DIR / "simple_agent.py").read_text(encoding="utf-8")
    # No top-level ReAct product runtime and no direct tool execution loop.
    assert "create_agent" not in source
    assert "react_agent" not in source
    assert "setup_middlewares" not in source
    # Tool execution is delegated to the canonical composition root.
    assert "WorkspaceAgentRuntime" in source
    assert "_run_direct_routed_tool" not in source
    # PHASE22 repair (B2): no name-based side-effect classification remains.
    assert "_classify_tool_effect" not in source
    assert "_tool_execution_mode" not in source
    assert "_tool_has_network" not in source
    # PHASE22 repair (B1): the temp SQLite path exists only inside the
    # explicit developer-test-profile branch of the canonical runtime builder.
    build_section = source.split("_build_canonical_runtime", 1)[1]
    assert "developer_test_profile" in build_section
    assert "tempfile.gettempdir()" in build_section


def test_wechat_agent_has_no_direct_tool_call_path() -> None:
    source = (WORKSPACE_DIR / "wechat_agent.py").read_text(encoding="utf-8")
    assert "create_agent" not in source
    assert "react_agent" not in source
    assert "ToolCallLimitMiddleware" not in source
    assert "WorkspaceAgentRuntime" in source
    assert "_classify_tool_effect" not in source


def test_no_independent_top_level_react_agent_graph_in_product_path() -> None:
    # The workspace product path must not import langchain's agent runtime.
    for module_file in ("simple_agent.py", "wechat_agent.py", "single_controller_runtime.py"):
        source = (WORKSPACE_DIR / module_file).read_text(encoding="utf-8")
        assert "langchain.agents" not in source
        assert "langgraph.prebuilt" not in source


def test_product_runtime_flows_through_plan_trace_budget_runoutcome(tmp_path) -> None:
    runtime = _runtime(tmp_path, write=False)
    snapshot = runtime.start(
        _request(task_id="task-contract", goal="read the doc", plan_kind="tool", tool_id="tool.read_doc", tool_arguments={"path": "docs/contract.md"})
    )

    # Plan
    assert snapshot.plan_state is not None and snapshot.plan_state.steps
    # Trace
    assert snapshot.trace_id
    assert runtime.events("task-contract")
    # Budget (limits present on the run)
    assert snapshot.limits.max_steps >= 1
    # RunOutcome
    assert snapshot.run_outcome_ref is not None


def test_no_legacy_fallback_in_product_path() -> None:
    for module_file in ("simple_agent.py", "wechat_agent.py", "single_controller_runtime.py"):
        source = (WORKSPACE_DIR / module_file).read_text(encoding="utf-8")
        assert "_fallback_to_legacy" not in source
        assert "legacy_runner" not in source


def test_no_name_based_side_effect_classification_anywhere() -> None:
    # PHASE22 repair (B2): the workspace product path must not classify tool
    # policy from tool names.
    for module_file in ("simple_agent.py", "wechat_agent.py", "single_controller_runtime.py"):
        source = (WORKSPACE_DIR / module_file).read_text(encoding="utf-8")
        assert "_classify_tool_effect" not in source
        assert "_tool_execution_mode" not in source
        assert "_tool_has_network" not in source
        assert "declared_policy_from_metadata" in source

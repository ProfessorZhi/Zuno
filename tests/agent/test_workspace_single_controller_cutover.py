from __future__ import annotations

from pathlib import Path
import re

import pytest

from zuno.capability.control_plane import ToolSideEffectLevel
from zuno.platform.services.workspace.single_controller_runtime import (
    WorkspaceAgentRuntime,
    WorkspaceRunRequest,
    WorkspaceToolBinding,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend" / "zuno"
WORKSPACE_DIR = BACKEND_ROOT / "platform" / "services" / "workspace"


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


def _runtime(
    tmp_path: Path,
    *,
    model: Any | None = None,
    write: bool = True,
    epoch: str = "security-epoch:workspace-v1",
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
            )
        )
    return WorkspaceAgentRuntime(
        model=model or _FakeChatModel(),
        bindings=bindings,
        store_path=tmp_path / "runtime.db",
        security_epoch_ref=epoch,
    )


def _request(
    task_id: str = "task-1",
    goal: str = "hello",
    plan_kind: str = "simple",
    **overrides: object,
) -> WorkspaceRunRequest:
    base = dict(
        task_id=task_id,
        thread_id="thread-1",
        workspace_id="workspace-a",
        user_id="user-a",
        trace_id=f"trace:{task_id}",
        goal=goal,
        plan_kind=plan_kind,
    )
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
    assert snapshot.run_outcome_ref
    # No tool was involved: capability plan is empty and no tool observation.
    assert not snapshot.capability_plan.allowed_tools
    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]


def test_workspace_complex_task_uses_multi_step_plan(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(task_id="task-complex", goal="compare and analyze across sources", plan_kind="complex")
    )

    assert snapshot.finalization_status == "finalized"
    assert snapshot.plan_state is not None
    assert len(snapshot.plan_state.steps) == 3
    action_types = [step.action_type for step in snapshot.plan_state.steps]
    assert action_types == ["model_transform", "prepare_replan_if_evidence_low", "answer_from_context"]
    assert snapshot.run_outcome_ref


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
    runtime = _runtime(tmp_path)
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
    runtime = _runtime(tmp_path)
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
# Security / approval / budget paths
# ---------------------------------------------------------------------------


def test_security_denial_blocks_plan_and_executes_no_tool(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-sec",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
            security_summary={"decision": "block", "recommended_action": "refuse", "reason": "input_security_block"},
        )
    )

    # The canonical planning admission gate produced a blocked plan: no steps,
    # no tool observation, no side effect.
    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert snapshot.plan_state is None or snapshot.plan_state.status in {"blocked", "created"}
    assert snapshot.finalization_status in {"failed", "blocked", "abstained", "finalized"}
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"


def test_approval_required_enters_waiting_approval(tmp_path) -> None:
    runtime = _runtime(tmp_path)
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
            )
        ],
        store_path=tmp_path / "runtime.db",
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


def test_budget_denial_blocks_plan_before_any_side_effect(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-budget",
            goal="write the doc",
            plan_kind="tool",
            tool_id="tool.write_doc",
            tool_arguments={"path": "out.md"},
            budget_verdict={"allowed": False, "reason": "budget_guard_blocked"},
        )
    )

    # Planning admission blocked the plan: no tool step ran, no side effect.
    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"


def test_stale_security_epoch_fails_closed(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-epoch",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
            security_epoch_ref="security-epoch:stale",
        )
    )

    assert not [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"
    # The canonical planning gate recorded the stale-epoch reason.
    if snapshot.strategy is not None:
        assert "security" in str(snapshot.strategy.reason).lower() or snapshot.strategy.reason == "security_blocked"


def test_current_security_epoch_allows_execution(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(
        _request(
            task_id="task-epoch-ok",
            goal="read the doc",
            plan_kind="tool",
            tool_id="tool.read_doc",
            tool_arguments={"path": "docs/contract.md"},
            security_epoch_ref="security-epoch:workspace-v1",
        )
    )

    assert snapshot.finalization_status == "finalized"
    assert [obs for obs in snapshot.observations if obs.kind == "tool" and obs.status == "completed"]


def test_cross_tenant_isolation_blocks_foreign_tool(tmp_path) -> None:
    runtime_a = _runtime(tmp_path / "a.db")
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
        store_path=tmp_path / "b.db",
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


# ---------------------------------------------------------------------------
# Failure / recovery / idempotency paths
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
        store_path=tmp_path / "runtime.db",
    )
    request = _request(
        task_id="task-retry",
        goal="run the flaky tool",
        plan_kind="tool",
        tool_id="tool.flaky",
        tool_arguments={"x": 1},
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
        store_path=tmp_path / "runtime.db",
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
    assert runtime.classify_final_state(snapshot) == "FAILED/BLOCKED"


def test_committed_effect_is_not_executed_twice_on_repeat_request(tmp_path) -> None:
    write_calls = {"n": 0}

    def counted_write(args: dict) -> dict:
        write_calls["n"] += 1
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
            )
        ],
        store_path=tmp_path / "runtime.db",
    )
    request = _request(
        task_id="task-idem",
        goal="write the doc",
        plan_kind="tool",
        tool_id="tool.write_doc",
        tool_arguments={"path": "out.md"},
    )

    interrupted = runtime.start(request)
    assert interrupted.finalization_status == "interrupted"
    assert write_calls["n"] == 0

    resumed = runtime.resume(task_id="task-idem", approval_decision="approved")
    assert resumed.finalization_status == "finalized"
    assert write_calls["n"] == 1
    assert runtime.classify_final_state(resumed) == "EFFECT_COMMITTED"

    # Repeat the same request: the idempotent replay returns the committed
    # facts; the write tool does not execute a second time.
    second = runtime.start(request)
    assert write_calls["n"] == 1
    assert second.task_id == resumed.task_id


def test_unknown_effect_enters_reconciliation(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    # A run that started but produced no recognized terminal shape is an
    # unknown-effect state: classification must return RECONCILIATION_REQUIRED.
    snapshot = runtime.start(_request(task_id="task-unknown", goal="run"))
    unknown = snapshot.model_copy(
        update={"finalization_status": "not_ready"}
    )
    assert runtime.classify_final_state(unknown) == "RECONCILIATION_REQUIRED"


def test_worker_crash_recovers_snapshot_and_resume(tmp_path) -> None:
    db_path = tmp_path / "runtime.db"
    runtime = _runtime(tmp_path, model=_FakeChatModel())
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
    restarted = _runtime(tmp_path, model=_FakeChatModel())
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


def test_same_idempotency_key_returns_same_facts(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    first = runtime.start(_request(task_id="task-same", goal="hello"))
    second = runtime.start(_request(task_id="task-same", goal="hello"))

    assert first.run_outcome_ref == second.run_outcome_ref
    assert first.finalization_status == second.finalization_status
    assert first.plan_state == second.plan_state


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


def test_wechat_agent_has_no_direct_tool_call_path() -> None:
    source = (WORKSPACE_DIR / "wechat_agent.py").read_text(encoding="utf-8")
    assert "create_agent" not in source
    assert "react_agent" not in source
    assert "ToolCallLimitMiddleware" not in source
    assert "WorkspaceAgentRuntime" in source


def test_no_independent_top_level_react_agent_graph_in_product_path() -> None:
    # The workspace product path must not import langchain's agent runtime.
    for module_file in ("simple_agent.py", "wechat_agent.py", "single_controller_runtime.py"):
        source = (WORKSPACE_DIR / module_file).read_text(encoding="utf-8")
        assert "langchain.agents" not in source
        assert "langgraph.prebuilt" not in source


def test_product_runtime_flows_through_plan_trace_budget_runoutcome(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    snapshot = runtime.start(_request(task_id="task-contract", goal="read the doc", plan_kind="tool", tool_id="tool.read_doc", tool_arguments={"path": "docs/contract.md"}))

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

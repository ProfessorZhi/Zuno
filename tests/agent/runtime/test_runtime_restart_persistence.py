from __future__ import annotations

from zuno.agent.durable_runtime import SingleControllerDurableRuntime
from zuno.agent.harness import ControllerRuntimeState
from zuno.agent.runtime.sqlite_store import SQLiteAgentRunStore


def _state(task_id: str = "task_restart") -> ControllerRuntimeState:
    return ControllerRuntimeState(
        thread_id="thread_restart",
        workspace_id="workspace_restart",
        user_id="user_restart",
        task_id=task_id,
        trace_id=f"trace_{task_id}",
        goal="Resume after process restart",
        context_pack={"uploaded_file_ids": ["file_contract"]},
    )


def test_sqlite_store_recovers_pending_interrupt_after_new_store_instance(tmp_path) -> None:
    db_path = tmp_path / "runtime.db"
    first_runtime = SingleControllerDurableRuntime(store=SQLiteAgentRunStore(db_path))
    waiting = first_runtime.start_task(
        _state(),
        interrupt_at_node="act_react_loop",
        required_approval="tool:send_email",
        interrupt_payload={"tool": "send_email", "side_effect": "external_write"},
    )

    assert waiting.status == "approval_waiting"
    assert waiting.pending_interrupt is not None
    assert waiting.latest_checkpoint is not None
    assert waiting.latest_checkpoint.node == "act_react_loop"

    second_runtime = SingleControllerDurableRuntime(store=SQLiteAgentRunStore(db_path))
    rehydrated = second_runtime.get_task_snapshot("task_restart")
    assert rehydrated is not None
    assert rehydrated.status == "approval_waiting"
    assert rehydrated.pending_interrupt is not None
    assert rehydrated.pending_interrupt.required_approval == "tool:send_email"

    resumed = second_runtime.resume_task(
        task_id="task_restart",
        approval_decision="approved",
        comment="approved after new store instance",
    )

    assert resumed.status == "completed"
    assert resumed.pending_interrupt is None
    assert resumed.latest_checkpoint is not None
    assert resumed.latest_checkpoint.node == "post_turn_commit"
    assert "runtime_resumed" in [event.type for event in resumed.events]
    assert "artifact:task_restart:answer" in resumed.state.artifact_refs


def test_sqlite_store_rejects_duplicate_task_on_restart(tmp_path) -> None:
    db_path = tmp_path / "runtime.db"
    runtime = SingleControllerDurableRuntime(store=SQLiteAgentRunStore(db_path))
    runtime.start_task(_state("task_duplicate"), stop_after_node="plan")

    restarted_runtime = SingleControllerDurableRuntime(store=SQLiteAgentRunStore(db_path))

    try:
        restarted_runtime.start_task(_state("task_duplicate"))
    except ValueError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("duplicate durable runtime task should fail")

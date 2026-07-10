from __future__ import annotations

import pytest

from zuno.agent.runtime import (
    ReflectionDecision,
    RuntimeNode,
    RuntimeStartRequest,
    SQLiteAgentRunStore,
    UnifiedAgentRuntimeService,
)


def _request(task_id: str, decision: ReflectionDecision) -> RuntimeStartRequest:
    return RuntimeStartRequest(
        run_id=f"run:{task_id}",
        thread_id="thread_interrupt",
        workspace_id="workspace_interrupt",
        user_id="user_interrupt",
        task_id=task_id,
        trace_id=f"trace:{task_id}",
        goal="exercise interrupt resume path",
        reflection_decision=decision,
    )


def test_approval_interrupt_persists_and_resumes_after_new_service_instance(tmp_path) -> None:
    db_path = tmp_path / "runtime.db"
    first = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(db_path))

    interrupted = first.start(_request("task_approval", ReflectionDecision.USE_TOOL))

    assert interrupted.finalization_status == "interrupted"
    assert interrupted.current_node == RuntimeNode.APPROVAL.value
    assert first.store.snapshot("task_approval").status == "approval_waiting"
    assert first.store.pending_interrupt("task_approval").node == RuntimeNode.APPROVAL.value

    second = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(db_path))
    rehydrated = second.get_snapshot("task_approval")
    assert rehydrated is not None
    assert rehydrated.current_node == RuntimeNode.APPROVAL.value

    resumed = second.resume(task_id="task_approval", approval_decision="approved")

    assert resumed.finalization_status == "finalized"
    assert resumed.current_node == RuntimeNode.POST_TURN_COMMIT.value
    assert second.store.pending_interrupt("task_approval") is None
    assert second.store.snapshot("task_approval").status == "completed"
    assert "runtime_resumed" in [event.type for event in second.store.events("task_approval")]


def test_ask_user_interrupt_is_not_marked_measured_or_completed(tmp_path) -> None:
    service = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))

    interrupted = service.start(_request("task_ask_user", ReflectionDecision.ASK_USER))

    assert interrupted.finalization_status == "interrupted"
    assert interrupted.current_node == RuntimeNode.INTERRUPT.value
    assert service.store.snapshot("task_ask_user").status == "approval_waiting"
    event_types = [event.type for event in service.store.events("task_ask_user")]
    assert "runtime_completed" not in event_types


def test_resume_without_pending_interrupt_fails(tmp_path) -> None:
    service = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))
    service.start(_request("task_done", ReflectionDecision.PASS))

    with pytest.raises(ValueError, match="not waiting"):
        service.resume(task_id="task_done")

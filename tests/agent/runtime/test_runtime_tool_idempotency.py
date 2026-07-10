from __future__ import annotations

from zuno.agent.runtime import RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService


def _request() -> RuntimeStartRequest:
    return RuntimeStartRequest(
        run_id="run:task_tool_idempotency",
        thread_id="thread_tool",
        workspace_id="workspace_tool",
        user_id="user_tool",
        task_id="task_tool_idempotency",
        trace_id="trace:task_tool_idempotency",
        goal="Send an email update to the reviewer.",
    )


def test_tool_resume_claims_idempotency_key_once(tmp_path) -> None:
    db_path = tmp_path / "runtime.db"
    first = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(db_path))
    interrupted = first.start(_request())

    idempotency_key = interrupted.observations[-1].metadata["idempotency_key"]
    assert idempotency_key.startswith("toolclaim:")

    second = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(db_path))
    resumed = second.resume(task_id="task_tool_idempotency", approval_decision="approved")

    assert resumed.finalization_status == "finalized"
    duplicate = second.store.claim_tool_execution(
        task_id="task_tool_idempotency",
        workspace_id="workspace_tool",
        user_id="user_tool",
        idempotency_key=idempotency_key,
        tool_name="mail.send",
        payload={"step_id": resumed.plan_state.steps[0].step_id, "status": "claimed"},
    )
    assert duplicate is False

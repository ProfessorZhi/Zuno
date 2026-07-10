from __future__ import annotations

from zuno.agent.runtime import RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.routing import RuntimeNode
from zuno.capability.runtime import build_default_tool_control_plane_runtime


def _request(task_id: str, goal: str) -> RuntimeStartRequest:
    return RuntimeStartRequest(
        run_id=f"run:{task_id}",
        thread_id="thread_tool",
        workspace_id="workspace_tool",
        user_id="user_tool",
        task_id=task_id,
        trace_id=f"trace:{task_id}",
        goal=goal,
    )


def test_unified_runtime_read_only_tool_executes_through_control_plane(tmp_path) -> None:
    service = UnifiedAgentRuntimeService(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
    )

    snapshot = service.start(_request("task_read_tool", "Search the web for a source and summarize it."))

    tool_observations = [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert tool_observations
    assert tool_observations[0].metadata["tool_runtime_status"] == "completed"
    assert tool_observations[0].metadata["task_events"] == ["tool_call", "sandbox_audit", "tool_result"]
    assert tool_observations[0].metadata["result"]["audit_ref"]
    assert snapshot.finalization_status == "finalized"


def test_unified_runtime_side_effect_tool_waits_for_approval_and_resumes(tmp_path) -> None:
    db_path = tmp_path / "runtime.db"
    service = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(db_path))

    interrupted = service.start(_request("task_mail_tool", "Send an email update to the reviewer."))

    assert interrupted.finalization_status == "interrupted"
    assert interrupted.current_node == RuntimeNode.EXECUTE_STEP.value
    assert service.store.snapshot("task_mail_tool").status == "approval_waiting"
    pending = service.store.pending_interrupt("task_mail_tool")
    assert pending is not None
    assert pending.required_approval == "tool:mail.send"
    assert pending.payload["idempotency_key"].startswith("toolclaim:")

    resumed = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(db_path)).resume(
        task_id="task_mail_tool",
        approval_decision="approved",
    )

    assert resumed.finalization_status == "finalized"
    assert resumed.current_node == RuntimeNode.POST_TURN_COMMIT.value
    tool_observations = [obs for obs in resumed.observations if obs.kind == "tool"]
    mail_observations = [obs for obs in tool_observations if obs.tool_id == "mail.send"]
    assert mail_observations[-1].metadata["tool_runtime_status"] == "completed"
    assert mail_observations[-1].metadata["credential_refs"] == ["credref://workspace_tool/mail.send"]


def test_unified_runtime_tool_network_block_becomes_observation(tmp_path) -> None:
    runtime = build_default_tool_control_plane_runtime()
    service = UnifiedAgentRuntimeService(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
        dependencies=RuntimeDependencies(tool_control_plane=runtime),
    )

    snapshot = service.start(_request("task_blocked_tool", "Send an email update to https://example.com."))

    assert snapshot.finalization_status == "finalized"
    blocked = [obs for obs in snapshot.observations if obs.kind == "tool" and obs.status == "blocked"]
    assert blocked
    assert blocked[-1].failure_reason == "blocked"
    assert blocked[-1].metadata["tool_runtime_status"] == "blocked"
    assert blocked[-1].metadata["task_events"] == ["tool_call", "sandbox_audit", "tool_result"]

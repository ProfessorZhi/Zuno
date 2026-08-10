from __future__ import annotations

from zuno.agent.runtime import AgentRuntimeService, RuntimeStartRequest, SQLiteAgentRunStore
from zuno.agent.runtime.dependencies import RuntimeDependencies
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


def test_agent_run_read_only_tool_executes_through_control_plane(tmp_path) -> None:
    from zuno.agent.runtime.dependencies import RuntimeDependencies

    service = AgentRuntimeService(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
        dependencies=RuntimeDependencies(
            tool_control_plane=build_default_tool_control_plane_runtime(persist_facts=False),
        ),
    )

    snapshot = service.start(_request("task_read_tool", "Search the web for a source and summarize it."))

    tool_observations = [obs for obs in snapshot.observations if obs.kind == "tool"]
    assert tool_observations
    assert tool_observations[0].metadata["tool_runtime_status"] == "completed"
    assert tool_observations[0].metadata["task_events"] == ["tool_call", "sandbox_audit", "tool_result"]
    assert tool_observations[0].metadata["result"]["audit_ref"]
    assert snapshot.finalization_status == "finalized"


def test_agent_run_side_effect_tool_stops_when_effect_gateway_is_unavailable(tmp_path) -> None:
    db_path = tmp_path / "runtime.db"
    service = AgentRuntimeService(
        store=SQLiteAgentRunStore(db_path),
        dependencies=RuntimeDependencies(
            tool_control_plane=build_default_tool_control_plane_runtime(persist_facts=False),
        ),
    )

    interrupted = service.start(_request("task_mail_tool", "Send an email update to the reviewer."))

    assert interrupted.finalization_status == "finalized"
    tool_observations = [obs for obs in interrupted.observations if obs.kind == "tool"]
    assert tool_observations
    assert tool_observations[-1].metadata["tool_runtime_status"] == "blocked"
    assert tool_observations[-1].metadata["blocked_reason"]


def test_agent_run_tool_network_block_becomes_observation(tmp_path) -> None:
    runtime = build_default_tool_control_plane_runtime(persist_facts=False)
    service = AgentRuntimeService(
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

from __future__ import annotations

import json

from zuno.agent.runtime import SQLiteAgentRunStore, UnifiedAgentRuntimeService
from zuno.api.services.user import UserPayload
from zuno.api.services.workspace_task_runtime import WorkspaceTaskRuntimeService
from zuno.schema.workspace import WorkSpaceSimpleTask


def _user() -> UserPayload:
    return UserPayload(
        user_id="user_phase11_workspace",
        user_name="Phase11 Workspace User",
        role="admin",
    )


def _task() -> WorkSpaceSimpleTask:
    return WorkSpaceSimpleTask(
        query="Create a cited workspace answer from local evidence.",
        model_id="model-local",
        session_id="session_phase11_workspace",
        workspace_id="workspace_phase11",
        task_id="task_phase11_workspace",
        trace_id="trace_phase11_workspace",
        goal="workspace unified runtime cutover",
        product_mode="general_agent",
        plugins=[],
        mcp_servers=[],
    )


def test_workspace_task_snapshot_and_stream_include_unified_runtime(tmp_path) -> None:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    store = SQLiteAgentRunStore(tmp_path / "workspace_unified_runtime.db")
    WorkspaceTaskRuntimeService.configure_unified_runtime_store_for_tests(store)

    snapshot = WorkspaceTaskRuntimeService.create_task(simple_task=_task(), login_user=_user())

    assert snapshot["task"]["task_id"] == "task_phase11_workspace"
    assert snapshot["unified_runtime"]["task_id"] == "task_phase11_workspace"
    assert snapshot["unified_runtime"]["run_id"] == "run:task_phase11_workspace"
    assert snapshot["unified_runtime"]["finalization_status"] in {"finalized", "abstained"}

    events = WorkspaceTaskRuntimeService.list_task_events("task_phase11_workspace")
    runtime_events = [event for event in events if event["payload"].get("runtime_topology") == "unified_agent_runtime"]
    runtime_event_types = [event["type"] for event in runtime_events]
    assert "runtime_started" in runtime_event_types
    assert "runtime_node" in runtime_event_types
    assert "runtime_completed" in runtime_event_types

    async def _collect_stream() -> list[dict]:
        payloads = []
        async for raw in WorkspaceTaskRuntimeService.stream_task_events("task_phase11_workspace"):
            payloads.append(json.loads(raw.removeprefix("data: ").strip()))
        return payloads

    import anyio

    streamed = anyio.run(_collect_stream)
    runtime_streamed = [
        payload for payload in streamed if payload["data"].get("runtime_topology") == "unified_agent_runtime"
    ]
    assert runtime_streamed
    assert {payload["data"]["task_id"] for payload in runtime_streamed} == {"task_phase11_workspace"}
    assert {payload["data"]["trace_id"] for payload in runtime_streamed} == {"trace_phase11_workspace"}


def test_workspace_unified_runtime_snapshot_recovers_from_sqlite_store(tmp_path) -> None:
    WorkspaceTaskRuntimeService.reset_runtime_state_for_tests()
    store = SQLiteAgentRunStore(tmp_path / "workspace_unified_runtime_recovery.db")
    WorkspaceTaskRuntimeService.configure_unified_runtime_store_for_tests(store)
    WorkspaceTaskRuntimeService.create_task(simple_task=_task(), login_user=_user())

    recovered = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(store.db_path)).get_snapshot(
        "task_phase11_workspace"
    )

    assert recovered is not None
    assert recovered.task_id == "task_phase11_workspace"
    assert recovered.trace_id == "trace_phase11_workspace"
    assert str(recovered.finalization_status) in {"finalized", "abstained"}

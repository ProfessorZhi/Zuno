from __future__ import annotations

import sqlite3

import pytest

from zuno.agent.durable_runtime import DurableRuntimeEvent
from zuno.agent.harness import ControllerRuntimeState
from zuno.agent.runtime.sqlite_store import RuntimeStateCorruptError, SQLiteAgentRunStore
from zuno.platform.observability.local_trace_store import SQLiteLocalTraceStore


def _state(task_id: str = "task_store", workspace_id: str = "workspace_1", user_id: str = "user_1") -> ControllerRuntimeState:
    return ControllerRuntimeState(
        thread_id=f"thread_{task_id}",
        workspace_id=workspace_id,
        user_id=user_id,
        task_id=task_id,
        trace_id=f"trace_{task_id}",
        goal="Persist runtime facts",
        context_pack={"context_pack_id": f"ctx_{task_id}"},
    )


def test_sqlite_runtime_store_persists_run_scope_and_events(tmp_path) -> None:
    store = SQLiteAgentRunStore(tmp_path / "runtime.db")
    state = _state()
    store.create_task(state, status="running")
    store.append_event(
        DurableRuntimeEvent(
            event_id="task_store:runtime_event:1",
            task_id=state.task_id,
            trace_id=state.trace_id,
            thread_id=state.thread_id,
            type="runtime_started",
            status="running",
        )
    )

    snapshot = store.load_latest(run_id=state.task_id, workspace_id=state.workspace_id, user_id=state.user_id)

    assert snapshot.task_id == state.task_id
    assert snapshot.workspace_id == state.workspace_id
    assert snapshot.events[0].event_id == "task_store:runtime_event:1"
    with pytest.raises(KeyError):
        store.load_latest(run_id=state.task_id, workspace_id="other_workspace", user_id=state.user_id)


def test_sqlite_runtime_store_rejects_duplicate_event_sequence(tmp_path) -> None:
    store = SQLiteAgentRunStore(tmp_path / "runtime.db")
    state = _state()
    store.create_task(state)
    event = DurableRuntimeEvent(
        event_id="task_store:runtime_event:1",
        task_id=state.task_id,
        trace_id=state.trace_id,
        thread_id=state.thread_id,
        type="runtime_started",
        status="running",
    )
    store.append_event(event)

    with pytest.raises(sqlite3.IntegrityError):
        store.append_event(event)


def test_sqlite_runtime_store_claims_tool_execution_once(tmp_path) -> None:
    store = SQLiteAgentRunStore(tmp_path / "runtime.db")
    state = _state()
    store.create_task(state)

    first = store.claim_tool_execution(
        task_id=state.task_id,
        workspace_id=state.workspace_id,
        user_id=state.user_id,
        idempotency_key="tool:send_email:task_store:1",
        tool_name="send_email",
        payload={"credential_ref": "cred:mail"},
    )
    second = store.claim_tool_execution(
        task_id=state.task_id,
        workspace_id=state.workspace_id,
        user_id=state.user_id,
        idempotency_key="tool:send_email:task_store:1",
        tool_name="send_email",
        payload={"credential_ref": "cred:mail"},
    )

    assert first is True
    assert second is False


def test_sqlite_runtime_store_reports_corrupt_snapshot(tmp_path) -> None:
    db_path = tmp_path / "runtime.db"
    store = SQLiteAgentRunStore(db_path)
    state = _state()
    store.create_task(state)

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE agent_runtime_runs SET state_json = ? WHERE task_id = ?",
            ("not-json", state.task_id),
        )

    with pytest.raises(RuntimeStateCorruptError):
        store.snapshot(state.task_id)


def test_local_trace_store_persists_events_by_trace(tmp_path) -> None:
    store = SQLiteLocalTraceStore(tmp_path / "trace.db")
    store.append(
        event_id="evt-1",
        task_id="task-trace",
        trace_id="trace-1",
        sequence=1,
        event_type="runtime_started",
        payload={"node": "start"},
    )
    store.append(
        event_id="evt-2",
        task_id="task-trace",
        trace_id="trace-1",
        sequence=2,
        event_type="checkpoint_saved",
        payload={"node": "plan"},
    )

    assert [event["event_type"] for event in store.list_by_trace("trace-1")] == [
        "runtime_started",
        "checkpoint_saved",
    ]

from __future__ import annotations

from zuno.agent.runtime import AgentRuntimeService, RuntimeStartRequest, SQLiteAgentRunStore
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.capability.runtime import build_default_tool_control_plane_runtime


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
    store = SQLiteAgentRunStore(db_path)
    first = AgentRuntimeService(
        store=store,
        dependencies=RuntimeDependencies(
            tool_control_plane=build_default_tool_control_plane_runtime(persist_facts=False),
        ),
    )
    interrupted = first.start(_request())

    tool_observation = next(observation for observation in interrupted.observations if observation.kind == "tool")
    idempotency_key = tool_observation.metadata["idempotency_key"]
    assert idempotency_key.startswith("toolclaim:")

    first_claim = store.claim_tool_execution(
        task_id="task_tool_idempotency",
        workspace_id="workspace_tool",
        user_id="user_tool",
        idempotency_key=idempotency_key,
        tool_name="mail.send",
        payload={"step_id": tool_observation.step_id or "", "status": "claimed"},
    )
    assert first_claim is True
    duplicate = store.claim_tool_execution(
        task_id="task_tool_idempotency",
        workspace_id="workspace_tool",
        user_id="user_tool",
        idempotency_key=idempotency_key,
        tool_name="mail.send",
        payload={"step_id": tool_observation.step_id or "", "status": "claimed"},
    )
    assert duplicate is False

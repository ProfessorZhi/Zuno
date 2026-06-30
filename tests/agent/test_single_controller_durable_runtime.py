from __future__ import annotations


def _state(task_id: str = "task_durable"):
    from zuno.agent.harness import ControllerRuntimeState

    return ControllerRuntimeState(
        thread_id="thread_durable",
        workspace_id="workspace_durable",
        user_id="user_durable",
        task_id=task_id,
        trace_id=f"trace_{task_id}",
        goal="Review supplier contract with durable runtime",
        context_pack={"uploaded_file_ids": ["file_contract"]},
    )


def test_durable_runtime_interrupt_checkpoint_and_resume_keep_trace_identity() -> None:
    from zuno.agent.durable_runtime import InMemoryDurableRuntimeStore
    from zuno.agent.durable_runtime import SingleControllerDurableRuntime

    runtime = SingleControllerDurableRuntime(store=InMemoryDurableRuntimeStore())

    waiting = runtime.start_task(
        _state(),
        interrupt_at_node="act_react_loop",
        required_approval="tool:send_email",
        interrupt_payload={"tool": "send_email", "side_effect": "external_write"},
    )

    waiting_payload = waiting.to_dict()
    assert waiting_payload["status"] == "approval_waiting"
    assert waiting_payload["task_id"] == "task_durable"
    assert waiting_payload["trace_id"] == "trace_task_durable"
    assert waiting_payload["thread_id"] == "thread_durable"
    assert waiting_payload["pending_interrupt"]["node"] == "act_react_loop"
    assert waiting_payload["pending_interrupt"]["required_approval"] == "tool:send_email"
    assert waiting_payload["latest_checkpoint"]["node"] == "act_react_loop"
    assert waiting_payload["latest_checkpoint"]["state"]["trace_id"] == "trace_task_durable"
    assert waiting_payload["checkpoint_ids"][-1].endswith(":act_react_loop:checkpoint")

    event_types = [event["type"] for event in waiting_payload["events"]]
    assert event_types[:3] == ["runtime_started", "runtime_node", "runtime_node"]
    assert event_types[-1] == "runtime_interrupt"
    assert {event["trace_id"] for event in waiting_payload["events"]} == {"trace_task_durable"}

    resumed = runtime.resume_task(
        task_id="task_durable",
        approval_decision="approved",
        comment="Approved after durable checkpoint.",
    )
    resumed_payload = resumed.to_dict()

    assert resumed_payload["status"] == "completed"
    assert resumed_payload["pending_interrupt"] is None
    assert resumed_payload["latest_checkpoint"]["node"] == "post_turn_commit"
    assert resumed_payload["trace_id"] == waiting_payload["trace_id"]
    assert resumed_payload["thread_id"] == waiting_payload["thread_id"]
    assert "artifact:task_durable:answer" in resumed_payload["state"]["artifact_refs"]

    resumed_event_types = [event["type"] for event in resumed_payload["events"]]
    assert "runtime_resumed" in resumed_event_types
    assert resumed_event_types[-1] == "runtime_completed"


def test_durable_runtime_cancel_and_failure_recovery_are_distinguishable() -> None:
    from zuno.agent.durable_runtime import InMemoryDurableRuntimeStore
    from zuno.agent.durable_runtime import SingleControllerDurableRuntime

    runtime = SingleControllerDurableRuntime(store=InMemoryDurableRuntimeStore())

    running = runtime.start_task(_state("task_cancel"), stop_after_node="plan")
    assert running.status == "running"
    assert running.latest_checkpoint is not None
    assert running.latest_checkpoint.node == "plan"

    cancelled = runtime.cancel_task("task_cancel", reason="user_cancelled")
    assert cancelled.status == "cancelled"
    assert cancelled.to_dict()["events"][-1]["type"] == "runtime_cancelled"
    assert cancelled.to_dict()["events"][-1]["payload"]["reason"] == "user_cancelled"

    runtime.start_task(_state("task_recoverable"), stop_after_node="plan")
    recoverable = runtime.mark_failure(
        "task_recoverable",
        node="act_react_loop",
        error="tool timeout",
        recoverable=True,
    )
    recoverable_payload = recoverable.to_dict()
    assert recoverable_payload["status"] == "failed"
    assert recoverable_payload["failure"]["recoverable"] is True
    assert recoverable_payload["failure"]["node"] == "act_react_loop"
    assert recoverable_payload["latest_checkpoint"]["node"] == "plan"

    runtime.start_task(_state("task_fatal"), stop_after_node="plan")
    fatal = runtime.mark_failure(
        "task_fatal",
        node="post_turn_commit",
        error="state version mismatch",
        recoverable=False,
    )
    fatal_payload = fatal.to_dict()
    assert fatal_payload["status"] == "failed"
    assert fatal_payload["failure"]["recoverable"] is False
    assert fatal_payload["events"][-1]["payload"]["recoverable"] is False


def test_durable_runtime_store_round_trips_after_new_runtime_instance() -> None:
    from zuno.agent.durable_runtime import InMemoryDurableRuntimeStore
    from zuno.agent.durable_runtime import SingleControllerDurableRuntime

    store = InMemoryDurableRuntimeStore()
    first_runtime = SingleControllerDurableRuntime(store=store)
    first_runtime.start_task(
        _state("task_store_round_trip"),
        interrupt_at_node="act_react_loop",
        required_approval="tool:filesystem.write",
        interrupt_payload={"tool": "filesystem.write"},
    )

    resumed_by_new_instance = SingleControllerDurableRuntime(store=store).resume_task(
        task_id="task_store_round_trip",
        approval_decision="approved",
        comment="Resume through a new runtime facade.",
    )
    payload = resumed_by_new_instance.to_dict()

    assert payload["status"] == "completed"
    assert payload["trace_id"] == "trace_task_store_round_trip"
    assert payload["pending_interrupt"] is None
    assert payload["latest_checkpoint"]["node"] == "post_turn_commit"
    assert "runtime_resumed" in [event["type"] for event in payload["events"]]

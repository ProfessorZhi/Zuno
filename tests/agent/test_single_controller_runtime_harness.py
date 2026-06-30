from __future__ import annotations


EXPECTED_NODE_ORDER = [
    "prepare_context",
    "intent_and_policy_route",
    "plan",
    "act_react_loop",
    "observe",
    "evidence_check",
    "reflect",
    "replan_if_needed",
    "answer_or_artifact",
    "post_turn_commit",
]


def test_single_controller_runtime_harness_declares_fixed_node_contracts() -> None:
    from zuno.agent.harness import build_single_controller_runtime_harness

    harness = build_single_controller_runtime_harness()

    assert harness.runtime_topology == "single_controller"
    assert harness.node_names() == EXPECTED_NODE_ORDER
    assert harness.edge_pairs()[0] == ("prepare_context", "intent_and_policy_route")
    assert harness.edge_pairs()[-1] == ("answer_or_artifact", "post_turn_commit")

    plan_contract = harness.node_contract("plan")
    assert "goal" in plan_contract.input_keys
    assert "context_pack" in plan_contract.input_keys
    assert "plan" in plan_contract.output_keys
    assert plan_contract.trace_span == "runtime.plan"
    assert plan_contract.checkpoint_policy == "before_and_after"

    assert harness.node_contract("act_react_loop").failure_policy == "checkpoint_and_resume"
    assert harness.node_contract("post_turn_commit").output_keys == ("runtime_ledger",)


def test_runtime_state_checkpoint_interrupt_and_stream_event_are_traceable() -> None:
    from zuno.agent.harness import ControllerRuntimeState
    from zuno.agent.harness import build_single_controller_runtime_harness

    harness = build_single_controller_runtime_harness()
    state = ControllerRuntimeState(
        thread_id="thread_1",
        workspace_id="workspace_1",
        user_id="u_1",
        task_id="task_1",
        trace_id="trace_1",
        goal="Review the supplier contract",
        context_pack={"items": [{"item_id": "doc_1"}]},
        plan=("Find payment clauses",),
        current_step="Find payment clauses",
        retrieval_events=({"chunk_id": "chunk_1"},),
        memory_candidates=("candidate_1",),
        artifact_refs=("artifact_1",),
    )

    checkpoint = harness.checkpoint_state(
        state,
        node="plan",
        payload={"reason": "plan_ready"},
    )
    interrupt = harness.request_interrupt(
        state,
        node="act_react_loop",
        reason="approval_required",
        required_approval="external_write",
        payload={"tool": "send_email"},
    )
    event = harness.stream_event(
        state,
        node="plan",
        status="completed",
        payload={"plan_size": 1},
    )
    resumed = harness.resume_from_checkpoint(checkpoint)

    assert checkpoint.checkpoint_id == "trace_1:plan:checkpoint"
    assert checkpoint.state["trace_id"] == "trace_1"
    assert checkpoint.state["task_id"] == "task_1"
    assert checkpoint.payload == {"reason": "plan_ready"}

    assert interrupt.interrupt_id == "trace_1:act_react_loop:interrupt"
    assert interrupt.resumable is True
    assert interrupt.required_approval == "external_write"
    assert interrupt.payload["tool"] == "send_email"

    assert event["event_type"] == "runtime_node"
    assert event["trace_id"] == "trace_1"
    assert event["task_id"] == "task_1"
    assert event["node"] == "plan"
    assert event["status"] == "completed"
    assert event["payload"] == {"plan_size": 1}

    assert resumed.trace_id == state.trace_id
    assert resumed.stage_order == state.stage_order
    assert resumed.context_pack == state.context_pack

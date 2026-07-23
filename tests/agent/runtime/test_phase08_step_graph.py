from __future__ import annotations

import pytest

from zuno.agent.runtime import (
    Phase08RuntimeError,
    Phase08StepService,
    build_phase08_step_graph,
    build_phase08_test_checkpointer,
)


def _step_state(**overrides):
    state = {
        "run_id": "run:p08:t05:1",
        "thread_id": "thread:p08:t05:1",
        "step_run_id": "step-run:p08:t05:1",
        "step_definition_id": "step-def:p08:t05:1",
        "plan_version_id": "plan:p08:t05:1",
        "controller_epoch": 1,
        "execution_epoch": 1,
    }
    state.update(overrides)
    return state


def test_step_graph_success_blocked_denied_invalid_retry_and_abstain() -> None:
    service = Phase08StepService(graph=build_phase08_step_graph(checkpointer=build_phase08_test_checkpointer()))

    success = service.run(_step_state())
    blocked = service.run(_step_state(blocked_reason="missing_input"))
    denied = service.run(_step_state(security_denied=True))
    invalid = service.run(_step_state(invalid_proposal=True))
    retryable = service.run(_step_state(retryable_failure=True))
    abstained = service.run(_step_state(abstain_requested=True))

    assert success["step_phase"] == "commit_step_result"
    assert success["validation_ref"].startswith("agent-domain:deterministic-validation:")
    assert success["output_ref"].startswith("agent-domain:output:")
    assert success["step_result_commit_ref"].startswith("agent-domain:step-result-completed:")
    assert blocked["outcome_status"] == "blocked"
    assert blocked["step_result_commit_ref"].startswith("agent-domain:step-result-blocked:")
    assert denied["outcome_status"] == "denied"
    assert invalid["failure_ref"] == "invalid_proposal"
    assert retryable["retry_count"] == 1
    assert retryable["outcome_status"] == "retryable"
    assert "step_result_commit_ref" not in retryable
    assert abstained["outcome_status"] == "abstained"


def test_step_graph_requires_explicit_checkpointer_boundary() -> None:
    with pytest.raises(Phase08RuntimeError, match="explicit durable checkpointer"):
        build_phase08_step_graph()

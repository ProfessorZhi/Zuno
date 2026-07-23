from __future__ import annotations

from zuno.agent.runtime import Phase08StepService, build_phase08_step_graph


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
    service = Phase08StepService(graph=build_phase08_step_graph())

    success = service.run(_step_state())
    blocked = service.run(_step_state(blocked_reason="missing_input"))
    denied = service.run(_step_state(security_denied=True))
    invalid = service.run(_step_state(invalid_proposal=True))
    retryable = service.run(_step_state(retryable_failure=True))
    abstained = service.run(_step_state(abstain_requested=True))

    assert success["output_ref"] == "output:step-run:p08:t05:1"
    assert blocked["outcome_status"] == "blocked"
    assert denied["outcome_status"] == "denied"
    assert invalid["failure_ref"] == "invalid_proposal"
    assert retryable["retry_count"] == 1
    assert retryable["outcome_status"] == "retryable"
    assert abstained["outcome_status"] == "abstained"

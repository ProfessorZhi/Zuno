from __future__ import annotations

from zuno.agent.runtime import RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService


def test_phase19_unified_runtime_commits_final_candidate_publication_outcome_and_delivery(tmp_path) -> None:
    service = UnifiedAgentRuntimeService(store=SQLiteAgentRunStore(tmp_path / "runtime.db"))

    snapshot = service.start(
        RuntimeStartRequest(
            run_id="run:phase19:integration",
            thread_id="thread_phase19_integration",
            workspace_id="workspace_phase19_integration",
            user_id="user_phase19_integration",
            task_id="task_phase19_integration",
            trace_id="trace_phase19_integration",
            goal="plan and execute a grounded answer",
        )
    )

    assert snapshot.finalization_status == "finalized"
    assert snapshot.final_candidate_ref is not None
    assert snapshot.publication_ref is not None
    assert snapshot.run_outcome_ref is not None
    assert snapshot.delivery_ref is not None
    finalization = [obs for obs in snapshot.observations if obs.metadata.get("phase19_finalization")][-1]
    commit = finalization.metadata["finalization_commit"]
    assert commit["final_gate"]["outcome"] == "PASS"
    assert commit["publication"]["publication_id"] == snapshot.publication_ref
    assert commit["run_outcome"]["publication_ref"] == snapshot.publication_ref
    assert commit["delivery"]["publication_ref"] == snapshot.publication_ref
    assert commit["delivery"]["retry_reexecutes_agent_run"] is False

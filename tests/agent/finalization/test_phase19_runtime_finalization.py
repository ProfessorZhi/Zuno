from __future__ import annotations

from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.nodes.core import draft_and_bind_claims, finalize
from zuno.agent.runtime.state import AgentRuntimeState


def test_phase19_runtime_finalize_records_publication_outcome_and_delivery_refs() -> None:
    state = AgentRuntimeState(
        run_id="run_runtime_phase19",
        thread_id="thread_runtime_phase19",
        workspace_id="workspace_runtime_phase19",
        user_id="user_runtime_phase19",
        task_id="task_runtime_phase19",
        trace_id="trace_runtime_phase19",
        goal="Produce a cited answer.",
        observations=[
            NormalizedObservation(
                observation_id="retrieval:runtime-phase19:1",
                kind=ObservationKind.RETRIEVAL,
                status=ObservationStatus.COMPLETED,
                source="unit",
                evidence_ids=["evidence:runtime-phase19:1"],
                citation_ids=["citation:runtime-phase19:1"],
            )
        ],
    )

    state = draft_and_bind_claims(state, RuntimeDependencies())
    state = finalize(state, RuntimeDependencies())

    assert state.finalization_status == "finalized"
    assert state.final_candidate_ref is not None
    assert state.publication_ref is not None
    assert state.run_outcome_ref is not None
    assert state.delivery_ref is not None
    finalization_observation = state.observations[-1]
    assert finalization_observation.metadata["phase19_finalization"] is True
    assert finalization_observation.metadata["finalization_commit"]["publication"]["publication_id"] == state.publication_ref

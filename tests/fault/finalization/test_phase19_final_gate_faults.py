from __future__ import annotations

from zuno.agent.application.finalization import FinalizationService
from zuno.agent.domain.finalization import FinalGateOutcome
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.agent.runtime.synthesis import GroundedSynthesisEngine


def test_phase19_final_gate_blocks_unknown_tool_effect_without_publication() -> None:
    retrieval = NormalizedObservation(
        observation_id="retrieval:fault-phase19:1",
        kind=ObservationKind.RETRIEVAL,
        status=ObservationStatus.COMPLETED,
        source="fault",
        evidence_ids=["evidence:fault-phase19:1"],
        citation_ids=["citation:fault-phase19:1"],
    )
    tool_unknown = NormalizedObservation(
        observation_id="tool:fault-phase19:unknown",
        kind=ObservationKind.TOOL,
        status=ObservationStatus.WAITING,
        source="fault",
        metadata={"effect_status": "UNKNOWN"},
    )
    draft_state = AgentRuntimeState(
        run_id="run_fault_phase19",
        thread_id="thread_fault_phase19",
        workspace_id="workspace_fault_phase19",
        user_id="user_fault_phase19",
        task_id="task_fault_phase19",
        trace_id="trace_fault_phase19",
        goal="Answer only after unknown effects reconcile.",
        observations=[retrieval, tool_unknown],
    )
    synthesis = GroundedSynthesisEngine().synthesize(draft_state)

    commit = FinalizationService().commit(
        AgentRuntimeState(
            run_id=draft_state.run_id,
            thread_id=draft_state.thread_id,
            workspace_id=draft_state.workspace_id,
            user_id=draft_state.user_id,
            task_id=draft_state.task_id,
            trace_id=draft_state.trace_id,
            goal=draft_state.goal,
            observations=[retrieval, tool_unknown, synthesis],
        )
    )

    assert commit.final_gate.outcome is FinalGateOutcome.BLOCKED
    assert commit.final_gate.tool_unknown_refs == ("tool:fault-phase19:unknown",)
    assert commit.publication is None
    assert commit.delivery is None
    assert commit.run_outcome.status == "BLOCKED"
    assert commit.reflexion_candidate is not None

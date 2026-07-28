from __future__ import annotations

from zuno.agent.application.finalization import FinalizationService
from zuno.agent.domain.finalization import FinalGateOutcome
from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.agent.runtime.synthesis import GroundedSynthesisEngine


def _state(observations: list[NormalizedObservation]) -> AgentRuntimeState:
    synthesis = GroundedSynthesisEngine().synthesize(
        AgentRuntimeState(
            run_id="run_phase19",
            thread_id="thread_phase19",
            workspace_id="workspace_phase19",
            user_id="user_phase19",
            task_id="task_phase19",
            trace_id="trace_phase19",
            goal="Answer with formal citations.",
            observations=observations,
        )
    )
    return AgentRuntimeState(
        run_id="run_phase19",
        thread_id="thread_phase19",
        workspace_id="workspace_phase19",
        user_id="user_phase19",
        task_id="task_phase19",
        trace_id="trace_phase19",
        goal="Answer with formal citations.",
        observations=[*observations, synthesis],
        evidence_refs=["evidence:ledger:1"],
        trace_event_ids=["trace:event:finalization"],
    )


def test_phase19_supported_claim_publishes_without_delivery_mutating_publication() -> None:
    retrieval = NormalizedObservation(
        observation_id="retrieval:phase19:1",
        kind=ObservationKind.RETRIEVAL,
        status=ObservationStatus.COMPLETED,
        source="unit",
        evidence_ids=["evidence:strict:1"],
        citation_ids=["citation:strict:1"],
    )

    commit = FinalizationService().commit(_state([retrieval]))

    assert commit.final_gate.outcome is FinalGateOutcome.PASS
    assert commit.publication is not None
    assert commit.delivery is not None
    assert commit.publication.delivery_ref == commit.delivery.delivery_id
    assert commit.delivery.retry_reexecutes_agent_run is False
    assert commit.run_outcome.status == "COMPLETED"
    assert commit.reflexion_candidate is None


def test_phase19_unsupported_claim_abstains_and_creates_governed_reflexion_candidate() -> None:
    retrieval = NormalizedObservation(
        observation_id="retrieval:phase19:doc-only",
        kind=ObservationKind.RETRIEVAL,
        status=ObservationStatus.COMPLETED,
        source="unit",
        evidence_ids=["evidence:doc-only"],
        citation_ids=[],
    )

    commit = FinalizationService().commit(_state([retrieval]))

    assert commit.final_gate.outcome is FinalGateOutcome.ABSTAIN
    assert commit.final_candidate.unsupported_claim_refs
    assert commit.publication is not None
    assert commit.run_outcome.status == "ABSTAINED"
    assert commit.reflexion_candidate is not None
    assert commit.reflexion_candidate.memory_governance_required is True
    assert commit.reflexion_candidate.hidden_reasoning_persisted is False


def test_phase19_unknown_tool_effect_blocks_publication() -> None:
    retrieval = NormalizedObservation(
        observation_id="retrieval:phase19:1",
        kind=ObservationKind.RETRIEVAL,
        status=ObservationStatus.COMPLETED,
        source="unit",
        evidence_ids=["evidence:strict:1"],
        citation_ids=["citation:strict:1"],
    )
    tool_unknown = NormalizedObservation(
        observation_id="tool:phase19:unknown",
        kind=ObservationKind.TOOL,
        status=ObservationStatus.WAITING,
        source="unit",
        metadata={"effect_status": "UNKNOWN"},
    )

    commit = FinalizationService().commit(_state([retrieval, tool_unknown]))

    assert commit.final_gate.outcome is FinalGateOutcome.BLOCKED
    assert commit.publication is None
    assert commit.delivery is None
    assert commit.run_outcome.status == "BLOCKED"
    assert commit.reflexion_candidate is not None

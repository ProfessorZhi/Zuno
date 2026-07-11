from __future__ import annotations

from zuno.agent.runtime.contracts import NormalizedObservation, ObservationKind, ObservationStatus
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.agent.runtime.synthesis import GroundedSynthesisEngine


def _state(observations: list[NormalizedObservation]) -> AgentRuntimeState:
    return AgentRuntimeState(
        run_id="run_synthesis",
        thread_id="thread_synthesis",
        workspace_id="workspace_synthesis",
        user_id="user_synthesis",
        task_id="task_synthesis",
        trace_id="trace_synthesis",
        goal="Answer with grounded citations.",
        observations=observations,
    )


def test_grounded_synthesis_binds_only_strict_retrieval_citations() -> None:
    observation = NormalizedObservation(
        observation_id="obs_retrieval",
        kind=ObservationKind.RETRIEVAL,
        status=ObservationStatus.COMPLETED,
        source="unit",
        evidence_ids=["ev_1"],
        citation_ids=["citation:ev_1"],
    )

    synthesis = GroundedSynthesisEngine().synthesize(_state([observation]))

    assert synthesis.citation_ids == ["citation:ev_1"]
    assert synthesis.metadata["citation_bindings"][0]["support_verdict"] == "supported"
    assert synthesis.metadata["unsupported_claims"] == []


def test_grounded_synthesis_does_not_upgrade_doc_only_evidence_to_strict_citation() -> None:
    observation = NormalizedObservation(
        observation_id="obs_doc_only",
        kind=ObservationKind.RETRIEVAL,
        status=ObservationStatus.COMPLETED,
        source="unit",
        evidence_ids=["ev_doc_only"],
        citation_ids=[],
    )

    synthesis = GroundedSynthesisEngine().synthesize(_state([observation]))

    assert synthesis.evidence_ids == ["ev_doc_only"]
    assert synthesis.citation_ids == []
    assert synthesis.metadata["citation_bindings"][0]["support_verdict"] == "insufficient"
    assert synthesis.metadata["final_answer"] == "Insufficient cited evidence to answer: Answer with grounded citations."
    assert synthesis.metadata["unsupported_claims"] == [
        "Insufficient cited evidence to answer: Answer with grounded citations."
    ]

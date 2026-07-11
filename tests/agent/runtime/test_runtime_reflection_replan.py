from __future__ import annotations

from dataclasses import dataclass

from zuno.agent.runtime import RuntimeDependencyFactory, RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService
from zuno.knowledge.agentic import (
    CorrectiveAction,
    CorrectiveRetrievalResult,
    EvidenceLedger,
    EvidenceLedgerRecord,
    QueryStrategy,
    RetrievalQualityVerdict,
)


def _request(task_id: str, goal: str = "Compare evidence across documents and synthesize conflicts with citations.") -> RuntimeStartRequest:
    return RuntimeStartRequest(
        run_id=f"run:{task_id}",
        thread_id="thread_phase09",
        workspace_id="workspace_phase09",
        user_id="user_phase09",
        task_id=task_id,
        trace_id=f"trace:{task_id}",
        goal=goal,
    )


@dataclass
class _StatefulKnowledgeRuntime:
    second_has_source_span: bool = True
    calls: int = 0

    def retrieve(self, request):
        self.calls += 1
        ledger = EvidenceLedger()
        if self.calls > 1 or not self.second_has_source_span:
            ledger.add(
                EvidenceLedgerRecord(
                    evidence_id=f"ev:{self.calls}",
                    document_id="doc_phase09",
                    document_version="v1",
                    source_span={"page": 2, "line_range": [10, 11]} if self.second_has_source_span else {},
                    retrieval_round=1,
                    query_id=f"{request.trace_id}:q:{self.calls}",
                    query_strategy=QueryStrategy.DIRECT,
                    retriever="unit",
                    raw_score=0.9,
                    rerank_score=0.9,
                    text="Renewal notice must be sent 30 days before anniversary.",
                )
            )
        verdict = RetrievalQualityVerdict.RELEVANT if ledger.records() else RetrievalQualityVerdict.IRRELEVANT
        return CorrectiveRetrievalResult(
            answer="unit answer",
            ledger=ledger,
            rounds=({"round": self.calls, "verdict": verdict.value},),
            final_verdict=verdict,
            final_action=CorrectiveAction.CONTINUE if ledger.records() else CorrectiveAction.ABSTAIN,
            trace={"ledger": ledger.to_trace(), "rounds": []},
        )


def _dependencies_with_knowledge(knowledge_runtime):
    dependencies = RuntimeDependencyFactory().dependencies()
    return dependencies.__class__(
        model_gateway=dependencies.model_gateway,
        memory_engine=dependencies.memory_engine,
        knowledge_runtime=knowledge_runtime,
        capability_runtime=dependencies.capability_runtime,
        tool_control_plane=dependencies.tool_control_plane,
        trace_sink=dependencies.trace_sink,
    )


def test_reflection_replan_executes_second_retrieval_and_finalizes(tmp_path) -> None:
    knowledge_runtime = _StatefulKnowledgeRuntime()
    service = UnifiedAgentRuntimeService(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
        dependencies=_dependencies_with_knowledge(knowledge_runtime),
    )

    snapshot = service.start(_request("task_phase09_replan"))

    assert snapshot.finalization_status == "finalized"
    assert knowledge_runtime.calls == 2
    assert snapshot.counters.replans == 1
    assert snapshot.reflection_decision == "pass"
    assert any(
        observation.metadata.get("replan_diff", {}).get("trajectory_changed") is True
        for observation in snapshot.observations
    )
    retrieval_observations = [item for item in snapshot.observations if item.kind == "retrieval"]
    assert len(retrieval_observations) == 2
    assert retrieval_observations[0].evidence_ids == []
    assert retrieval_observations[1].evidence_ids == ["ev:2"]
    assert retrieval_observations[1].citation_ids == ["citation:ev:2"]


def test_rewrite_answer_routes_back_to_claim_binding_before_abstain(tmp_path) -> None:
    knowledge_runtime = _StatefulKnowledgeRuntime(second_has_source_span=False)
    service = UnifiedAgentRuntimeService(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
        dependencies=_dependencies_with_knowledge(knowledge_runtime),
    )

    snapshot = service.start(_request("task_phase09_rewrite"))

    assert snapshot.finalization_status == "abstained"
    assert snapshot.reflection_decision == "abstain"
    node_names = [outcome["node"] for outcome in snapshot.node_outcomes]
    assert node_names.index("revise_draft") < node_names.index("finalize")
    assert node_names.count("draft_and_bind_claims") >= 2
    assert any(item.metadata.get("answer_rewritten") is True for item in snapshot.observations)
    assert not any(item.citation_ids for item in snapshot.observations if item.kind == "retrieval")

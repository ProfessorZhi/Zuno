from __future__ import annotations

from zuno.agent.contracts import ContextPack, PlanStep
from zuno.agent.runtime.dependencies import RuntimeDependencies
from zuno.agent.runtime.execution import KnowledgeStepExecutor
from zuno.agent.runtime.state import AgentRuntimeState
from zuno.knowledge.agentic import CorrectiveAction, CorrectiveAgenticRetrievalRuntime, CorrectiveRetrievalRequest, QueryStrategy
from zuno.knowledge.indexing import KnowledgeIndexRuntime
from zuno.knowledge.ingestion import CanonicalDocumentIR, DocumentBlock, DocumentMetadata, DocumentProvenance, SourceSpan


def _runtime() -> CorrectiveAgenticRetrievalRuntime:
    index = KnowledgeIndexRuntime()
    index.create_knowledge_space("ks_corrective", "workspace_corrective")
    index.index_document(
        "ks_corrective",
        CanonicalDocumentIR(
            metadata=DocumentMetadata(
                document_id="doc_corrective",
                workspace_id="workspace_corrective",
                source_uri="memory://corrective.md",
                mime_type="text/markdown",
                hash="sha256-corrective",
                parser_id="native",
                parser_version="phase08-test",
            ),
            blocks=[
                DocumentBlock(
                    block_id="block_notice",
                    type="paragraph",
                    text="Renewal notice must be sent 30 days before anniversary.",
                    source_span=SourceSpan(page=3, line_range=[8, 9]),
                )
            ],
            provenance=DocumentProvenance(
                parser_id="native",
                parser_version="phase08-test",
                source_uri="memory://corrective.md",
                confidence=1.0,
            ),
        ),
        targets=["bm25", "vector", "graph"],
    )
    return CorrectiveAgenticRetrievalRuntime(index_runtime=index)


def test_corrective_runtime_runs_second_round_after_doc_miss() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="indemnity waiver",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_corrective",
            task_id="task_corrective",
            failure_bucket="doc_miss",
            max_rounds=2,
        )
    )

    assert len(result.rounds) == 2
    assert result.rounds[0]["corrective_action"] == CorrectiveAction.QUERY_REWRITE.value
    assert result.rounds[1]["query_strategy"] == QueryStrategy.REWRITE.value
    assert result.rounds[1]["query"] != result.rounds[0]["query"]
    assert result.final_action == CorrectiveAction.ABSTAIN
    assert result.trace["ledger"]["rounds"] == []


def test_corrective_runtime_continues_when_first_round_has_strict_source_span() -> None:
    result = _runtime().retrieve(
        CorrectiveRetrievalRequest(
            query="renewal notice 30 days anniversary",
            workspace_id="workspace_corrective",
            knowledge_space_ids=["ks_corrective"],
            trace_id="trace_corrective_pass",
            task_id="task_corrective_pass",
            max_rounds=2,
        )
    )

    assert len(result.rounds) == 1
    assert result.rounds[0]["corrective_action"] == CorrectiveAction.CONTINUE.value
    assert result.ledger.records()[0].source_span["page"] == 3
    assert result.ledger.records()[0].strict_citation_allowed is True


def test_knowledge_step_executor_consumes_corrective_retrieval_runtime() -> None:
    state = AgentRuntimeState(
        run_id="run_corrective",
        thread_id="thread_corrective",
        workspace_id="workspace_corrective",
        user_id="user_corrective",
        task_id="task_corrective_step",
        trace_id="trace_corrective_step",
        goal="renewal notice 30 days anniversary",
        context_pack=ContextPack(
            context_pack_id="context_corrective",
            user_goal="renewal notice 30 days anniversary",
            task_state={"knowledge_space_ids": ["ks_corrective"]},
        ),
    )
    step = PlanStep(
        step_id="step_retrieve",
        goal="retrieve grounded renewal evidence",
        action_type="retrieve_evidence",
    )

    result = KnowledgeStepExecutor().execute(
        state=state,
        step=step,
        deps=RuntimeDependencies(knowledge_runtime=_runtime()),
    )

    assert result.observation.metadata["agentic_corrective_retrieval"] is True
    assert result.observation.metadata["final_action"] == CorrectiveAction.CONTINUE.value
    assert result.observation.metadata["ledger"]["record_count"] == 1
    assert result.observation.evidence_ids
    assert result.observation.citation_ids

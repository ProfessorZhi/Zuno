from __future__ import annotations

from pathlib import Path


PDF_FIXTURE = Path("tests/fixtures/documents/phase12_source_span.pdf")


def test_pdf_agent_answer_binds_page_level_citation_and_evidence_ledger() -> None:
    from zuno.knowledge.agentic import CorrectiveAgenticRetrievalRuntime, CorrectiveRetrievalRequest
    from zuno.knowledge.agentic.contracts import CorrectiveAction, RetrievalQualityVerdict
    from zuno.knowledge.agentic_graphrag import AgenticRetrievalRuntime, AgenticRetrievalRuntimeRequest, ProductMode
    from zuno.knowledge.indexing import KnowledgeIndexRuntime
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    parsed = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_phase12_pdf_agent",
            source_id="source_phase12_pdf_agent",
            workspace_id="workspace_phase12_pdf_agent",
            source_uri=f"file:///{PDF_FIXTURE.resolve().as_posix()}",
            mime_type="application/pdf",
            source_bytes=PDF_FIXTURE.read_bytes(),
            parser_version="phase12-pymupdf-test",
        )
    )
    assert parsed.status == "succeeded"
    assert parsed.document is not None

    index_runtime = KnowledgeIndexRuntime()
    index_runtime.create_knowledge_space("ks_phase12_pdf_agent", "workspace_phase12_pdf_agent")
    index_runtime.index_document(
        "ks_phase12_pdf_agent",
        parsed.document,
        targets=["bm25", "vector", "graph"],
    )

    claim = "Release gate status is implementation complete but quality not yet proven."
    result = AgenticRetrievalRuntime(index_runtime=index_runtime).answer(
        AgenticRetrievalRuntimeRequest(
            query="What is the release gate status?",
            workspace_id="workspace_phase12_pdf_agent",
            knowledge_space_ids=["ks_phase12_pdf_agent"],
            product_mode=ProductMode.ENHANCED,
            claims=[claim],
            trace_id="trace_phase12_pdf_agent",
            task_id="task_phase12_pdf_agent",
        )
    )

    assert "[1]" in result.answer
    assert result.citations
    assert result.citations[0].source_span["page_number"] == 1
    assert result.citations[0].source_span["bbox"]
    assert result.claim_bindings[0].support_verdict == "supported"
    assert result.claim_bindings[0].citation_label == "[1]"
    assert result.claim_bindings[0].source_span["page_number"] == 1
    assert result.trace_metadata["claim_citation_binding_metrics"]["supported_claim_count"] == 1

    corrective = CorrectiveAgenticRetrievalRuntime(index_runtime=index_runtime).retrieve(
        CorrectiveRetrievalRequest(
            query="release gate status quality not yet proven",
            workspace_id="workspace_phase12_pdf_agent",
            knowledge_space_ids=["ks_phase12_pdf_agent"],
            trace_id="trace_phase12_pdf_ledger",
            task_id="task_phase12_pdf_ledger",
            claims=[claim],
            max_rounds=1,
        )
    )

    records = corrective.ledger.records()
    assert corrective.final_verdict == RetrievalQualityVerdict.RELEVANT
    assert corrective.final_action == CorrectiveAction.CONTINUE
    assert records
    assert records[0].document_version == parsed.document.metadata.document_version_id
    assert records[0].source_span["page_number"] == 1
    assert records[0].source_span["bbox"]
    assert records[0].trace_span == "trace_phase12_pdf_ledger:retrieval:1"


def test_unified_runtime_pdf_retrieval_synthesis_binds_page_citation(tmp_path) -> None:
    from zuno.agent.runtime import RuntimeDependencyFactory, RuntimeStartRequest, SQLiteAgentRunStore, UnifiedAgentRuntimeService
    from zuno.knowledge.indexing import KnowledgeIndexRuntime
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    parsed = ParseGateway.parse_document(
        ParseDocumentRequest(
            document_id="doc_phase05_pdf_runtime",
            source_id="source_phase05_pdf_runtime",
            workspace_id="workspace_phase05_pdf_runtime",
            source_uri=f"file:///{PDF_FIXTURE.resolve().as_posix()}",
            mime_type="application/pdf",
            source_bytes=PDF_FIXTURE.read_bytes(),
            parser_version="phase05-runtime-test",
        )
    )
    assert parsed.status == "succeeded"
    assert parsed.document is not None

    index_runtime = KnowledgeIndexRuntime()
    index_runtime.create_knowledge_space("ks_phase05_pdf_runtime", "workspace_phase05_pdf_runtime")
    index_runtime.index_document(
        "ks_phase05_pdf_runtime",
        parsed.document,
        targets=["bm25", "vector", "graph"],
    )
    assembly = RuntimeDependencyFactory.for_workspace_task(
        store=SQLiteAgentRunStore(tmp_path / "runtime.db"),
        knowledge_index_runtime=index_runtime,
    )
    service = UnifiedAgentRuntimeService(store=assembly.store, dependencies=assembly.dependencies)

    snapshot = service.start(
        RuntimeStartRequest(
            run_id="run:phase05_pdf_runtime",
            thread_id="thread_phase05_pdf_runtime",
            workspace_id="workspace_phase05_pdf_runtime",
            user_id="user_phase05_pdf_runtime",
            task_id="task_phase05_pdf_runtime",
            trace_id="trace_phase05_pdf_runtime",
            goal="Compare evidence across documents and synthesize the release gate status with citations.",
            knowledge_space_ids=("ks_phase05_pdf_runtime",),
        )
    )

    retrievals = [observation for observation in snapshot.observations if observation.kind == "retrieval"]
    synthesis = [observation for observation in snapshot.observations if observation.metadata.get("grounded_synthesis")]

    assert snapshot.finalization_status == "finalized"
    assert retrievals
    assert retrievals[-1].citation_ids
    assert retrievals[-1].metadata["ledger"]["records"][0]["source_span"]["page_number"] == 1
    assert retrievals[-1].metadata["ledger"]["records"][0]["source_span"]["bbox"]
    assert synthesis
    assert synthesis[-1].metadata["final_answer"]
    assert synthesis[-1].metadata["citation_bindings"][0]["support_verdict"] == "supported"

from __future__ import annotations


def _contract_document():
    from zuno.knowledge.ingestion import (
        CanonicalDocumentIR,
        DocumentBlock,
        DocumentMetadata,
        DocumentProvenance,
        SourceSpan,
    )

    return CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc_contract_runtime",
            workspace_id="workspace_retrieval",
            source_uri="memory://contracts/runtime.md",
            mime_type="text/markdown",
            hash="sha256-runtime",
            parser_id="native",
            parser_version="phase09-test",
        ),
        blocks=[
            DocumentBlock(
                block_id="block_renewal",
                type="paragraph",
                text="Renewal notice must be sent 30 days before the contract anniversary.",
                source_span=SourceSpan(page=2, line_range=[10, 12], section_path=["Renewal"]),
            ),
            DocumentBlock(
                block_id="block_security",
                type="paragraph",
                text="Security incidents require notification within 24 hours.",
                source_span=SourceSpan(page=4, line_range=[30, 32], section_path=["Security"]),
            ),
        ],
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="phase09-test",
            source_uri="memory://contracts/runtime.md",
            confidence=0.99,
        ),
    )


def _restricted_document():
    from zuno.knowledge.ingestion import (
        CanonicalDocumentIR,
        DocumentBlock,
        DocumentMetadata,
        DocumentProvenance,
        SourceSpan,
    )

    return CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc_restricted_runtime",
            workspace_id="workspace_retrieval",
            source_uri="memory://contracts/restricted.md",
            mime_type="text/markdown",
            hash="sha256-restricted",
            parser_id="native",
            parser_version="phase09-test",
        ),
        blocks=[
            DocumentBlock(
                block_id="block_private",
                type="paragraph",
                text="Private executive renewal terms require 90 days notice.",
                source_span=SourceSpan(page=7, line_range=[4, 5], section_path=["Private"]),
                acl_scope="executive",
            )
        ],
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="phase09-test",
            source_uri="memory://contracts/restricted.md",
            confidence=0.99,
        ),
    )


def _indexed_runtime():
    from zuno.knowledge.agentic_graphrag import AgenticRetrievalRuntime
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    index_runtime = KnowledgeIndexRuntime()
    index_runtime.create_knowledge_space("ks_contracts", "workspace_retrieval")
    index_runtime.index_document(
        "ks_contracts",
        _contract_document(),
        targets=["bm25", "vector", "graph"],
    )
    return AgenticRetrievalRuntime(index_runtime=index_runtime)


def test_agentic_retrieval_runtime_consumes_index_runtime_and_returns_cited_answer() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticRetrievalRuntimeRequest,
        ProductMode,
        QueryMethod,
    )

    result = _indexed_runtime().answer(
        AgenticRetrievalRuntimeRequest(
            query="What is the renewal notice requirement?",
            workspace_id="workspace_retrieval",
            knowledge_space_ids=["ks_contracts"],
            product_mode=ProductMode.ENHANCED,
            allowed_acl_scopes={"workspace"},
            trace_id="trace_phase09_runtime",
            task_id="task_phase09_runtime",
            claims=[
                "Renewal notice must be sent 30 days before the contract anniversary.",
                "The contract waives indemnity.",
            ],
        )
    )

    assert result.decision.retrieval_required is True
    assert result.decision.resolved_methods == [QueryMethod.LOCAL, QueryMethod.BASIC]
    assert result.index_payloads[0]["retrievers_used"] == ["bm25", "vector", "graph"]
    assert result.evidence_bundle.coverage == 1.0
    assert result.citations[0].label == "[1]"
    assert result.citations[0].source_span["page"] == 2
    assert "[1]" in result.answer
    assert "Renewal notice must be sent 30 days" in result.answer
    assert result.unsupported_claim_check.unsupported_claims == ["The contract waives indemnity."]
    assert result.trace.to_dict()["citation_coverage"] == 1.0
    trace_item = result.trace_metadata["evidence_bundle"]["items"][0]
    assert trace_item["retriever_source"] in {"normalized_phrase", "bm25", "vector", "graph"}
    assert "raw_score" in trace_item
    assert "normalized_score" in trace_item
    assert "candidate_reason" in trace_item
    assert result.to_task_event()["type"] == "retrieval"
    assert result.to_task_event()["payload"]["citation_ids"] == ["[1]"]
    assert result.to_task_event()["payload"]["evidence_verdict"]["status"] == "pass"
    assert result.to_task_event()["payload"]["artifact_manifest"]["retrieval_refs"] == [
        "doc_contract_runtime::block_renewal"
    ]
    assert result.to_task_event()["payload"]["runtime_trace_event_ids"] == [
        "trace_phase09_runtime:0001:pre_retrieval",
        "trace_phase09_runtime:0002:post_retrieval",
        "trace_phase09_runtime:0003:post_answer",
    ]
    graph_trace = result.trace_metadata["production_graphrag"]["graph_extraction"]
    renewal_chunk_id = result.evidence_bundle.items[0].chunk_id
    assert graph_trace["entity_index"]["Renewal"]["supporting_chunk_ids"] == [renewal_chunk_id]
    assert graph_trace["entity_index"]["Renewal"]["supporting_span_ids"] == [renewal_chunk_id]
    relation = next(
        item for item in graph_trace["relation_index"] if item["target"] == "Renewal"
    )
    assert relation["supporting_chunk_ids"] == [renewal_chunk_id]
    assert relation["evidence_span_ids"] == [renewal_chunk_id]
    report = result.trace_metadata["production_graphrag"]["community_report"]["reports"][0]
    assert renewal_chunk_id in report["source_chunk_ids"]
    assert renewal_chunk_id in report["source_span_ids"]


def test_agentic_retrieval_runtime_covers_normal_global_and_drift_modes() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticRetrievalRuntimeRequest,
        ProductMode,
        QueryMethod,
    )

    runtime = _indexed_runtime()

    normal = runtime.answer(
        AgenticRetrievalRuntimeRequest(
            query="renewal anniversary",
            workspace_id="workspace_retrieval",
            knowledge_space_ids=["ks_contracts"],
            product_mode=ProductMode.NORMAL,
            trace_id="trace_phase09_normal",
            task_id="task_phase09_normal",
        )
    )
    assert normal.decision.resolved_methods == [QueryMethod.BASIC]
    assert [item.retrieval_method for item in normal.evidence_bundle.items] == [QueryMethod.BASIC]

    global_result = runtime.answer(
        AgenticRetrievalRuntimeRequest(
            query="Compare global renewal and security themes across all policies",
            workspace_id="workspace_retrieval",
            knowledge_space_ids=["ks_contracts"],
            product_mode=ProductMode.ENHANCED,
            trace_id="trace_phase09_global",
            task_id="task_phase09_global",
        )
    )
    assert global_result.decision.resolved_methods == [
        QueryMethod.GLOBAL,
        QueryMethod.LOCAL,
        QueryMethod.BASIC,
    ]
    assert [stage.name for stage in global_result.fusion_plan.stages] == [
        "community_prior",
        "chunk_evidence_backfill",
    ]
    assert global_result.trace_metadata["artifact_manifest"]["retrieval_refs"] == [
        "doc_contract_runtime::block_renewal",
        "doc_contract_runtime::block_security",
    ]

    drift = runtime.answer(
        AgenticRetrievalRuntimeRequest(
            query="What changed between old and new renewal policy versions?",
            workspace_id="workspace_retrieval",
            knowledge_space_ids=["ks_contracts"],
            product_mode=ProductMode.AUTO,
            fallback_history=["low_coverage"],
            trace_id="trace_phase09_drift",
            task_id="task_phase09_drift",
        )
    )
    assert drift.decision.resolved_methods == [
        QueryMethod.DRIFT,
        QueryMethod.LOCAL,
        QueryMethod.BASIC,
    ]
    assert drift.decision.fallback_reason == "low_coverage"
    assert [stage.name for stage in drift.fusion_plan.stages] == [
        "drift_scan",
        "drift_evidence_backfill",
    ]


def test_agentic_retrieval_runtime_records_production_graphrag_traceability_metrics() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticRetrievalRuntimeRequest,
        ProductMode,
    )

    result = _indexed_runtime().answer(
        AgenticRetrievalRuntimeRequest(
            query="Compare global renewal and security themes across all policies",
            workspace_id="workspace_retrieval",
            knowledge_space_ids=["ks_contracts"],
            product_mode=ProductMode.ENHANCED,
            trace_id="trace_phase11_production",
            task_id="task_phase11_production",
            claims=[
                "Renewal notice must be sent 30 days before the contract anniversary.",
                "The contract includes an uncited indemnity waiver.",
            ],
        )
    )

    trace = result.trace_metadata
    first_citation = result.citations[0]
    first_item = trace["evidence_bundle"]["items"][0]
    production = trace["production_graphrag"]

    assert first_citation.source_uri == "memory://contracts/runtime.md"
    assert first_citation.provenance["hash"] == "sha256-runtime"
    assert first_item["source_uri"] == "memory://contracts/runtime.md"
    assert first_item["provenance"]["hash"] == "sha256-runtime"
    assert first_item["source_span"]["page"] == 2
    assert first_item["source_methods"]

    assert production["current_runtime"] == "local_deterministic"
    assert production["external_graph_index"] == {
        "status": "target_blocked",
        "target": "external_graph_index_service",
        "blocked_reason": "external graph index service is not connected in local runtime",
    }
    assert production["graph_extraction"]["status"] == "local_deterministic"
    assert production["graph_extraction"]["text_unit_count"] == len(result.evidence_bundle.items)
    assert production["graph_extraction"]["records"][0]["source_uri"] == "memory://contracts/runtime.md"
    assert production["community_report"]["status"] == "local_deterministic"
    assert production["community_report"]["reports"][0]["source_evidence_ids"]
    assert production["fusion"]["strategy"] == "local_rrf_then_score_rerank"
    assert production["fusion"]["ranked_evidence_ids"] == [
        item.evidence_id for item in result.evidence_bundle.items
    ]
    assert production["fusion"]["rrf_scores"][result.evidence_bundle.items[0].evidence_id] > 0

    assert trace["unsupported_claim_metrics"] == {
        "checked_claim_count": 2,
        "unsupported_claim_count": 1,
        "unsupported_claims": ["The contract includes an uncited indemnity waiver."],
        "guard_status": "blocked_confident_wording",
    }
    assert result.to_task_event()["payload"]["unsupported_claim_metrics"] == trace["unsupported_claim_metrics"]


def test_agentic_retrieval_runtime_preserves_parse_lineage_in_evidence_provenance() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticRetrievalRuntime,
        AgenticRetrievalRuntimeRequest,
        ProductMode,
    )
    from zuno.knowledge.indexing import KnowledgeIndexRuntime
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway

    submitted = ParseGateway.submit_parse_job(
        ParseDocumentRequest(
            document_id="doc_agent_lineage",
            workspace_id="workspace_retrieval",
            source_uri="file://contracts/agent-lineage.md",
            mime_type="text/markdown",
            source_text="# Renewal\nRenewal lineage evidence must cite the parse job.",
            parser_config={"chunking": "line"},
        )
    )
    assert submitted.document is not None
    parse_snapshot = ParseGateway.get_job_snapshot(submitted.job_id)
    index_runtime = KnowledgeIndexRuntime()
    index_runtime.create_knowledge_space("ks_agent_lineage", "workspace_retrieval")
    index_runtime.index_document(
        "ks_agent_lineage",
        submitted.document,
        targets=["bm25", "vector", "graph"],
        parse_job_snapshot=parse_snapshot,
    )

    result = AgenticRetrievalRuntime(index_runtime=index_runtime).answer(
        AgenticRetrievalRuntimeRequest(
            query="renewal lineage evidence",
            workspace_id="workspace_retrieval",
            knowledge_space_ids=["ks_agent_lineage"],
            product_mode=ProductMode.ENHANCED,
            trace_id="trace_phase06_lineage",
            task_id="task_phase06_lineage",
        )
    )
    item = result.evidence_bundle.items[0]
    citation = result.citations[0]

    assert item.provenance["parse_job_id"] == parse_snapshot.job_id
    assert item.provenance["parse_attempt_id"] == parse_snapshot.parse_attempt_id
    assert item.provenance["document_version_id"] == submitted.document.metadata.document_version_id
    assert item.provenance["source_sha256"] == submitted.document.metadata.source_sha256
    assert citation.provenance["parse_job_id"] == parse_snapshot.job_id


def test_agentic_retrieval_runtime_drops_disallowed_acl_evidence() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticRetrievalRuntime,
        AgenticRetrievalRuntimeRequest,
        ProductMode,
    )
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    index_runtime = KnowledgeIndexRuntime()
    index_runtime.create_knowledge_space("ks_restricted", "workspace_retrieval")
    index_runtime.index_document(
        "ks_restricted",
        _restricted_document(),
        targets=["bm25", "vector", "graph"],
    )

    result = AgenticRetrievalRuntime(index_runtime=index_runtime).answer(
        AgenticRetrievalRuntimeRequest(
            query="Private executive renewal terms notice",
            workspace_id="workspace_retrieval",
            knowledge_space_ids=["ks_restricted"],
            product_mode=ProductMode.ENHANCED,
            allowed_acl_scopes={"workspace"},
            trace_id="trace_phase09_acl",
            task_id="task_phase09_acl",
        )
    )

    assert result.evidence_bundle.items == []
    assert result.evidence_bundle.dropped_evidence_ids == [
        "ev:local:doc_restricted_runtime::block_private::cite1"
    ]
    assert result.to_task_event()["payload"]["dropped_evidence_ids"] == [
        "ev:local:doc_restricted_runtime::block_private::cite1"
    ]
    assert result.trace_metadata["evidence_verdict"]["fallback_reason"] == "evidence_missing"


def test_agentic_retrieval_runtime_records_low_confidence_for_zero_score_fallback() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticRetrievalRuntimeRequest,
        ProductMode,
    )

    result = _indexed_runtime().answer(
        AgenticRetrievalRuntimeRequest(
            query="Which indemnity waiver exists?",
            workspace_id="workspace_retrieval",
            knowledge_space_ids=["ks_contracts"],
            product_mode=ProductMode.ENHANCED,
            trace_id="trace_phase09_zero",
            task_id="task_phase09_zero",
        )
    )

    assert result.evidence_bundle.items == []
    assert result.answer == "No indexed evidence matched this request."
    assert result.trace_metadata["evidence_verdict"]["status"] == "low_confidence"
    assert result.trace_metadata["evidence_verdict"]["fallback_reason"] == "evidence_missing"
    assert result.trace_metadata["pipeline_trace"]["steps"][-1]["name"] == "artifact_manifest"


def test_agentic_retrieval_runtime_honors_auto_no_retrieval_without_index_query() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticRetrievalRuntime,
        AgenticRetrievalRuntimeRequest,
        ProductMode,
    )
    from zuno.knowledge.indexing import KnowledgeIndexRuntime

    runtime = AgenticRetrievalRuntime(index_runtime=KnowledgeIndexRuntime())
    result = runtime.answer(
        AgenticRetrievalRuntimeRequest(
            query="Tighten this sentence.",
            workspace_id="workspace_retrieval",
            knowledge_space_ids=["ks_missing"],
            product_mode=ProductMode.AUTO,
            context_pack={"draft_only": True},
            evidence_state={"coverage": 1.0},
            allowed_acl_scopes={"workspace"},
            trace_id="trace_phase09_auto",
            task_id="task_phase09_auto",
        )
    )

    assert result.decision.retrieval_required is False
    assert result.index_payloads == []
    assert result.evidence_bundle.items == []
    assert result.answer == "No retrieval was required for this request."
    assert result.trace.to_dict()["router_decision"] == "auto_no_retrieval"

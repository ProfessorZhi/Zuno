from __future__ import annotations


def test_router_keeps_product_mode_separate_from_resolved_methods() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticRetrievalRouter,
        ProductMode,
        QueryMethod,
        RetrievalRouterInput,
    )

    router = AgenticRetrievalRouter()

    normal = router.decide(
        RetrievalRouterInput(
            query="What is the renewal notice?",
            workspace_id="ws_contracts",
            context_pack={"task_id": "task-1"},
            product_mode=ProductMode.NORMAL,
            budget={"latency_ms": 1000},
            acl_scope={"workspace_id": "ws_contracts"},
            evidence_state={"coverage": 0.0},
            fallback_history=[],
            trace_id="trace-normal",
            task_id="task-1",
        )
    )
    assert normal.retrieval_required is True
    assert normal.resolved_methods == [QueryMethod.BASIC]
    assert normal.requested_product_mode == ProductMode.NORMAL
    assert "auto" not in [method.value for method in normal.resolved_methods]

    automatic = router.decide(
        RetrievalRouterInput(
            query="Tighten this sentence for the final report.",
            workspace_id="ws_contracts",
            context_pack={"draft_only": True},
            product_mode=ProductMode.AUTO,
            budget={"latency_ms": 1000},
            acl_scope={"workspace_id": "ws_contracts"},
            evidence_state={"coverage": 1.0},
            fallback_history=[],
            trace_id="trace-auto",
            task_id="task-2",
        )
    )
    assert automatic.retrieval_required is False
    assert automatic.resolved_methods == []
    assert automatic.no_retrieval_reason == "query_can_be_answered_from_context"
    assert "auto" not in [method.value for method in automatic.candidate_methods]


def test_enhanced_global_query_uses_staged_fusion_with_chunk_backfill() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticRetrievalRouter,
        ProductMode,
        QueryMethod,
        RetrievalRouterInput,
        StagedFusionPlan,
    )

    decision = AgenticRetrievalRouter().decide(
        RetrievalRouterInput(
            query="Compare the global themes and obligations across all departments.",
            workspace_id="ws_contracts",
            context_pack={"task_id": "task-3"},
            product_mode=ProductMode.ENHANCED,
            budget={"latency_ms": 5000, "max_methods": 3},
            acl_scope={"workspace_id": "ws_contracts"},
            evidence_state={"coverage": 0.2},
            fallback_history=[],
            trace_id="trace-global",
            task_id="task-3",
        )
    )
    plan = StagedFusionPlan.from_decision(decision)

    assert decision.retrieval_required is True
    assert QueryMethod.GLOBAL in decision.resolved_methods
    assert plan.stages[0].name == "community_prior"
    assert plan.stages[0].methods == [QueryMethod.GLOBAL]
    assert plan.stages[1].name == "chunk_evidence_backfill"
    assert plan.stages[1].methods == [QueryMethod.LOCAL, QueryMethod.BASIC]
    assert plan.to_trace()["global_is_prior_not_chunk_ranker"] is True


def test_evidence_bundle_citations_and_unsupported_claims_are_traceable() -> None:
    from zuno.knowledge.agentic_graphrag import (
        CitationBuilder,
        EvidenceBundle,
        EvidenceItem,
        QueryMethod,
        UnsupportedClaimChecker,
    )

    bundle = EvidenceBundle.from_candidates(
        [
            EvidenceItem(
                evidence_id="ev-1",
                document_id="doc-a",
                block_id="block-1",
                retrieval_method=QueryMethod.LOCAL,
                score=0.93,
                source_span={"page": 2, "section_path": ["Termination"]},
                citation_label="[1]",
                trust_label="verified",
                acl_scope="workspace",
                text="Termination notice must be sent 30 days before renewal.",
            ),
            EvidenceItem(
                evidence_id="ev-secret",
                document_id="doc-secret",
                block_id="block-9",
                retrieval_method=QueryMethod.BASIC,
                score=0.99,
                source_span={"page": 1},
                citation_label="[2]",
                trust_label="filtered",
                acl_scope="restricted",
                text="Private cross-workspace material.",
            ),
        ],
        allowed_acl_scopes={"workspace"},
    )
    citations = CitationBuilder().build(bundle)
    check = UnsupportedClaimChecker().check(
        claims=[
            "Termination notice must be sent 30 days before renewal.",
            "The contract includes an uncited indemnity waiver.",
        ],
        evidence_bundle=bundle,
    )

    assert [item.evidence_id for item in bundle.items] == ["ev-1"]
    assert bundle.coverage == 1.0
    assert citations[0].label == "[1]"
    assert citations[0].source_span["page"] == 2
    assert check.unsupported_claims == ["The contract includes an uncited indemnity waiver."]
    assert check.recommended_actions == [
        "rewrite",
        "retrieve_more",
        "evidence_limited_answer",
        "block_high_risk_confident_wording",
    ]


def test_graph_index_pipeline_consumes_document_ir_source_spans() -> None:
    from zuno.knowledge.agentic_graphrag import GraphRAGIndexPipelineContract
    from zuno.knowledge.ingestion import (
        CanonicalDocumentIR,
        DocumentBlock,
        DocumentMetadata,
        DocumentProvenance,
        SourceSpan,
    )

    document = CanonicalDocumentIR(
        metadata=DocumentMetadata(
            document_id="doc-a",
            workspace_id="ws_contracts",
            source_uri="contracts/a.md",
            mime_type="text/markdown",
            hash="sha256:a",
            parser_id="native",
            parser_version="v1",
        ),
        blocks=[
            DocumentBlock(
                block_id="block-1",
                type="paragraph",
                text="Acme renews the support contract annually.",
                source_span=SourceSpan(page=1, line_range=[10, 12]),
            )
        ],
        provenance=DocumentProvenance(
            parser_id="native",
            parser_version="v1",
            source_uri="contracts/a.md",
            confidence=0.99,
        ),
    )

    contract = GraphRAGIndexPipelineContract.from_document_ir(document)

    assert contract.input_document_id == "doc-a"
    assert contract.pipeline_steps == [
        "document_ir",
        "text_unit",
        "entity_relation_extraction",
        "entity_resolution",
        "graph_upsert",
        "community_detection",
        "community_report",
        "embeddings_search_index",
        "index_manifest",
    ]
    assert contract.text_units[0]["source_span"]["line_range"] == [10, 12]
    assert contract.index_manifest["workspace_id"] == "ws_contracts"


def test_trace_payload_records_router_evidence_and_citation_coverage() -> None:
    from zuno.knowledge.agentic_graphrag import (
        AgenticGraphRAGTrace,
        AgenticRetrievalRouter,
        CitationBuilder,
        EvidenceBundle,
        EvidenceItem,
        ProductMode,
        QueryMethod,
        RetrievalRouterInput,
    )

    decision = AgenticRetrievalRouter().decide(
        RetrievalRouterInput(
            query="Research the policy drift between old and new renewal language.",
            workspace_id="ws_contracts",
            context_pack={"task_id": "task-4"},
            product_mode=ProductMode.AUTO,
            budget={"latency_ms": 8000},
            acl_scope={"workspace_id": "ws_contracts"},
            evidence_state={"coverage": 0.1},
            fallback_history=["local_low_coverage"],
            trace_id="trace-drift",
            task_id="task-4",
        )
    )
    bundle = EvidenceBundle.from_candidates(
        [
            EvidenceItem(
                evidence_id="ev-1",
                document_id="doc-a",
                block_id="block-1",
                retrieval_method=QueryMethod.DRIFT,
                score=0.88,
                source_span={"page": 4},
                citation_label="[1]",
                trust_label="verified",
                acl_scope="workspace",
                text="Renewal language changed between v1 and v2.",
            )
        ],
        allowed_acl_scopes={"workspace"},
    )
    payload = AgenticGraphRAGTrace.from_decision(
        decision=decision,
        evidence_bundle=bundle,
        citations=CitationBuilder().build(bundle),
    ).to_dict()

    assert decision.resolved_methods == [QueryMethod.DRIFT, QueryMethod.LOCAL, QueryMethod.BASIC]
    assert payload["requested_product_mode"] == "auto"
    assert payload["router_decision"] == "auto_drift_research"
    assert payload["candidate_methods"] == ["drift", "local", "basic"]
    assert payload["resolved_methods"] == ["drift", "local", "basic"]
    assert payload["evidence_coverage"] == 1.0
    assert payload["citation_coverage"] == 1.0

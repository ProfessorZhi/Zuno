from __future__ import annotations

import asyncio


def test_knowledge_project_snapshot_carries_extractor_config() -> None:
    from zuno.services.application.knowledge import KnowledgeQueryService

    async def fake_config_loader(_knowledge_id: str) -> dict:
        return {
            "index_capability": "rag_graph",
            "graphrag_project_id": "contract_review",
            "graphrag_project": {
                "graphrag_project_id": "contract_review",
                "query_method": "local",
                "prompt_version": "extract-v2",
                "query_prompt_version": "query-v3",
                "index_version": "graph-v4",
                "community_version": "community-v1",
                "status": "ready",
            },
            "model_refs": {"entity_extraction_llm_id": "llm_extract_contract"},
            "graph_index_settings": {
                "entity_extraction_mode": "llm",
                "entity_extraction_schema_version": "contract-schema-v2",
                "entity_extraction_prompt_id": "extract-contract-v2",
                "health_status": "ready",
                "community_report_status": "ready",
            },
            "policy_refs": {"entity_extraction_cost_latency_profile": "low_cost"},
            "eval_refs": {"entity_extraction_eval_profile": "contract-local"},
        }

    class NoopProjectLoader:
        def load(self, _project_id):
            return None

    service = KnowledgeQueryService(
        config_loader=fake_config_loader,
        project_loader=NoopProjectLoader(),
    )
    snapshot = asyncio.run(
        service.build_project_snapshot(user_id="u_1", knowledge_id="kb_contract")
    )
    trace = snapshot.to_trace()

    assert snapshot.extractor_config["resolved_mode"] == "llm"
    assert snapshot.extractor_config["model_ref"] == "llm_extract_contract"
    assert snapshot.extractor_config["schema_version"] == "contract-schema-v2"
    assert trace["extractor_config"]["llm_first"] is True
    assert trace["contract"]["query_method"] == "local"


def test_query_result_trace_exposes_method_citation_and_fusion_contracts() -> None:
    from zuno.services.graphrag.query_service import (
        GraphRAGProjectSnapshot,
        GraphRAGQueryService,
    )

    class FakeOrchestrator:
        async def run(self, mode, query, knowledge_ids, retrieval_options=None):
            del mode, query, knowledge_ids
            return {
                "content": "local graph answer",
                "metadata": {
                    "trace_id": "trace-phase08",
                    "requested_product_mode": "enhanced",
                    "resolved_product_mode": "enhanced",
                    "requested_query_method": "auto",
                    "resolved_query_method": "local",
                    "router_decision": "enhanced_local",
                    "internal_route": "local_graphrag",
                    "route_trace": {
                        "local_graph_required": True,
                        "community_required": False,
                        "fallback_reason": None,
                    },
                    "retrievers_used": ["vector", "bm25", "graph"],
                    "fusion_strategy": "baseline_preserving",
                    "rerank_used": True,
                    "evidence_bundle": {
                        "document_count": 2,
                        "chunk_ids": ["chunk-1", "chunk-2"],
                        "citation_chunks": ["chunk-1", "chunk-2"],
                        "citation_coverage": 1.0,
                    },
                    "citation_chunks": ["chunk-1", "chunk-2"],
                },
                "final_pass_result": {
                    "documents": [
                        {"chunk_id": "chunk-1", "file_name": "contract-a.md"},
                        {"chunk_id": "chunk-2", "file_name": "contract-b.md"},
                    ]
                },
            }

    service = GraphRAGQueryService(orchestrator=FakeOrchestrator())
    result = asyncio.run(
        service.query(
            query="Explain termination notice relationships",
            knowledge_ids=["kb_contract"],
            snapshot=GraphRAGProjectSnapshot(
                graphrag_project_id="contract_review",
                contract={"query_method": "local"},
                index_health={"graph": "ready", "community": "ready"},
                knowledge_capability="rag_graph",
                extractor_config={
                    "resolved_mode": "llm",
                    "schema_version": "contract-schema-v2",
                    "llm_first": True,
                },
            ),
            product_mode="enhanced",
            query_method="local",
        )
    )
    trace = result.trace_metadata

    assert trace["extractor_config"]["resolved_mode"] == "llm"
    assert trace["query_method_contract"]["resolved_query_method"] == "local"
    assert trace["query_method_contract"]["internal_route"] == "local_graphrag"
    assert trace["query_method_contract"]["local_graph_required"] is True
    assert trace["citation_contract"]["status"] == "pass"
    assert trace["citation_contract"]["citation_coverage"] == 1.0
    assert trace["retrieval_fusion_contract"] == {
        "retrievers_used": ["vector", "bm25", "graph"],
        "fusion_strategy": "baseline_preserving",
        "rerank_used": True,
        "evidence_document_count": 2,
        "citation_coverage": 1.0,
    }

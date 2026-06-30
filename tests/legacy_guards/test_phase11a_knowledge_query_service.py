import asyncio
from pathlib import Path


class _RecordingOrchestrator:
    def __init__(self):
        self.calls = []

    async def run(self, mode, query, knowledge_ids, retrieval_options=None):
        self.calls.append(
            {
                "mode": mode,
                "query": query,
                "knowledge_ids": list(knowledge_ids),
                "retrieval_options": dict(retrieval_options or {}),
            }
        )
        return {
            "content": "answer from project runtime",
            "metadata": {
                "requested_product_mode": retrieval_options.get("product_mode", "auto"),
                "resolved_product_mode": retrieval_options.get("product_mode", "auto"),
                "requested_query_method": retrieval_options["query_method"],
                "resolved_query_method": "local",
                "router_decision": "enhanced_local",
                "query_method_fallback_reason": None,
                "budget_policy": retrieval_options.get("budget_policy") or {},
                "fallback_policy": retrieval_options.get("fallback_policy") or {},
                "retrievers_used": ["vector", "bm25", "graph"],
                "used_paths": [{"source": "A", "target": "B"}],
                "used_communities": [],
                "prompt_version": "extract-v2",
                "query_prompt_version": "query-v3",
                "index_version": retrieval_options["index_version"],
                "pipeline_trace": {
                    "requested_product_mode": retrieval_options.get("product_mode", "auto"),
                    "resolved_product_mode": retrieval_options.get("product_mode", "auto"),
                    "requested_query_method": retrieval_options["query_method"],
                    "resolved_query_method": "local",
                },
                "evidence_bundle": {
                    "document_count": 1,
                    "chunk_ids": ["chunk-1"],
                    "citation_chunks": ["chunk-1"],
                    "citation_coverage": 1.0,
                },
                "citation_chunks": ["chunk-1"],
            },
            "final_pass_result": {
                "documents": [
                    {
                        "chunk_id": "chunk-1",
                        "knowledge_id": "kb-1",
                        "content": "project evidence",
                    }
                ]
            },
        }


def _write_project(root: Path) -> None:
    project_dir = root / "contract_review"
    (project_dir / "prompts").mkdir(parents=True)
    (project_dir / "settings.yaml").write_text(
        """
graphrag_project_id: contract_review
prompt_version: extract-v2
query_prompt_version: query-v3
index_version: idx-v7
community_version: community-v2
query_method: local
status: ready
prompts:
  extract_graph: prompts/extract_graph.md
  local_query: prompts/local_query.md
""",
        encoding="utf-8",
    )
    (project_dir / "prompts" / "extract_graph.md").write_text("extract", encoding="utf-8")
    (project_dir / "prompts" / "local_query.md").write_text("local", encoding="utf-8")


def test_knowledge_query_service_uses_project_runtime_without_domain_pack_loader(tmp_path, monkeypatch):
    del monkeypatch
    repo_root = Path(__file__).resolve().parents[2]
    assert not (repo_root / "src/backend/zuno/services/domain_pack").exists()

    _write_project(tmp_path)
    orchestrator = _RecordingOrchestrator()

    async def load_config(knowledge_id):
        assert knowledge_id == "kb-1"
        return {
            "index_capability": "rag_graph",
            "graphrag_project_id": "contract_review",
            "retrieval_settings": {
                "default_mode": "rag_graph",
                "profile": "auto",
                "top_k": 3,
                "rerank_enabled": True,
                "rerank_top_k": 3,
                "graph_hop_limit": 2,
                "max_paths_per_entity": 5,
            },
            "index_settings": {
                "index_version": "vec-v4",
                "health_status": "ready",
                "status": "active",
            },
            "graph_index_settings": {
                "index_version": "graph-v5",
                "health_status": "ready",
                "community_report_status": "ready",
                "community_version": "community-v2",
            },
        }

    from zuno.services.application.knowledge import KnowledgeQueryService
    from zuno.services.graphrag.project.loader import GraphRAGProjectLoader
    from zuno.services.graphrag.query_service import GraphRAGQueryService

    service = KnowledgeQueryService(
        config_loader=load_config,
        project_loader=GraphRAGProjectLoader(projects_root=tmp_path),
        query_service=GraphRAGQueryService(orchestrator=orchestrator),
    )

    result = asyncio.run(
        service.query(
            user_id="user-1",
            knowledge_ids=["kb-1"],
            query="终止条款和通知期限是什么关系",
            product_mode="enhanced",
            query_method="local",
        )
    )

    call = orchestrator.calls[0]
    options = call["retrieval_options"]

    assert call["mode"] == "enhanced_retrieval"
    assert options["product_mode"] == "enhanced"
    assert options["query_method"] == "local"
    assert options["knowledge_capability"] == "rag_graph"
    assert options["graphrag_project"]["graphrag_project_id"] == "contract_review"
    assert options["index_version"] == {
        "vector": "vec-v4",
        "graph": "graph-v5",
        "community": "community-v2",
        "prompt": "extract-v2",
        "query_prompt": "query-v3",
    }
    assert "domain_pack_id" not in options
    assert result.graphrag_project_id == "contract_review"
    assert result.answer == "answer from project runtime"
    assert result.requested_query_method == "local"
    assert result.resolved_query_method == "local"
    assert result.trace_metadata["requested_product_mode"] == "enhanced"
    assert result.retrievers_used == ["vector", "bm25", "graph"]
    assert result.citations == ["chunk-1"]
    assert result.trace_metadata["pipeline_trace"]["resolved_query_method"] == "local"


def test_graphrag_query_service_maps_runtime_result_to_single_result_model():
    from zuno.services.graphrag.query_service import (
        GraphRAGProjectSnapshot,
        GraphRAGQueryService,
    )

    orchestrator = _RecordingOrchestrator()
    service = GraphRAGQueryService(orchestrator=orchestrator)
    snapshot = GraphRAGProjectSnapshot(
        graphrag_project_id="contract_review",
        contract={
            "graphrag_project_id": "contract_review",
            "prompt_version": "extract-v2",
            "query_prompt_version": "query-v3",
            "index_version": "idx-v7",
            "community_version": "community-v2",
            "query_method": "local",
            "status": "ready",
        },
        readiness={"ready": True, "status": "ready", "errors": []},
        prompt_categories=["extract_graph", "local_query"],
        retrieval_settings={"top_k": 3, "rerank_enabled": True},
        index_version={
            "vector": "vec-v4",
            "graph": "graph-v5",
            "community": "community-v2",
            "prompt": "extract-v2",
            "query_prompt": "query-v3",
        },
        index_health={"vector": "ready", "graph": "ready", "community": "ready"},
        knowledge_capability="rag_graph",
        query_policy={"max_context_chunks": 8},
    )

    result = asyncio.run(
        service.query(
            query="Where is the notice clause?",
            knowledge_ids=["kb-1"],
            snapshot=snapshot,
            product_mode="auto",
            query_method=None,
        )
    )

    options = orchestrator.calls[0]["retrieval_options"]
    assert options["product_mode"] == "auto"
    assert options["query_policy"] == {"max_context_chunks": 8}
    assert "domain_pack_id" not in options
    assert result.to_dict()["graphrag_project_id"] == "contract_review"
    assert result.to_dict()["evidence"]["document_count"] == 1
    assert result.to_dict()["documents"][0]["chunk_id"] == "chunk-1"
    assert result.requested_query_method == "local"
    assert result.resolved_query_method in {"basic", "local", "global", "drift"}
    assert result.resolved_query_method != "auto"


def test_graphrag_query_service_keeps_normal_mode_as_router_input():
    from zuno.services.graphrag.query_service import (
        GraphRAGProjectSnapshot,
        GraphRAGQueryService,
    )

    orchestrator = _RecordingOrchestrator()
    service = GraphRAGQueryService(orchestrator=orchestrator)
    snapshot = GraphRAGProjectSnapshot(
        graphrag_project_id="contract_review",
        contract={
            "graphrag_project_id": "contract_review",
            "query_method": "local",
            "status": "ready",
        },
        index_version={"vector": "vec-v4", "graph": "graph-v5"},
        index_health={"vector": "ready", "graph": "ready"},
        knowledge_capability="rag_graph",
    )

    asyncio.run(
        service.query(
            query="普通检索合同条款",
            knowledge_ids=["kb-1"],
            snapshot=snapshot,
            product_mode="normal",
            query_method=None,
        )
    )

    call = orchestrator.calls[0]
    options = call["retrieval_options"]
    assert call["mode"] == "standard_retrieval"
    assert options["product_mode"] == "normal"
    assert options["query_method"] == "auto"

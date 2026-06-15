from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))


def test_phase2_orchestrator_delegates_auto_mode_decision_to_planner() -> None:
    _ensure_runtime_paths()

    retrieval_models = importlib.import_module("zuno.services.retrieval.models")
    RetrievalOrchestrator = importlib.import_module(
        "zuno.services.retrieval.orchestrator"
    ).RetrievalOrchestrator

    RetrievalPlan = retrieval_models.RetrievalPlan
    ProcessedQuery = retrieval_models.ProcessedQuery
    RetrievedDocument = retrieval_models.RetrievedDocument
    FusionResult = retrieval_models.FusionResult

    captured: dict[str, object] = {}

    class FakePlanner:
        def build_plan(self, request, processed_query, *, knowledge_capability: str = "rag"):
            captured["requested_mode"] = request.mode
            captured["knowledge_capability"] = knowledge_capability
            captured["query"] = processed_query.normalized_query
            return RetrievalPlan(
                requested_mode="auto",
                resolved_mode="graphrag",
                requested_profile="auto",
                resolved_profile="graph_relation",
                enabled_retrievers=["graph"],
                retriever_configs={"graph": {"graph_hop_limit": 3, "max_paths_per_entity": 4}},
                fusion_policy={"name": "query_aware"},
                rerank_policy={"enabled": False, "top_k": None},
                budget_policy={"top_k": 5, "graph_hop_limit": 3, "max_paths_per_entity": 4},
                fallback_policy={"allow_retry": False},
                trace_policy={"enabled": True},
                scope_policy={"status": "active"},
                index_version={"graph": "graph_v2"},
                index_health={"graph": "ready"},
            )

    class FakeQueryProcessor:
        async def process(self, query: str):
            return ProcessedQuery(
                original_query=query,
                normalized_query=query,
                rewritten_queries=[query],
                intent_labels=[],
                query_features={"relation_question": True},
                route_hints=[],
            )

    class EmptyRetriever:
        async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
            return {"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}

    class FakeQueryExpander:
        async def expand(self, query: str) -> list[str]:
            return [query]

    class FakeGraphRetriever:
        async def retrieve(self, query: str, knowledge_ids: list[str], options: dict | None = None) -> dict:
            return {
                "content": "第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
                "documents": [
                    {
                        "chunk_id": "chunk_1",
                        "knowledge_id": "kb_1",
                        "file_id": "file_1",
                        "file_name": "loan_contract.md",
                        "content": "第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
                        "score": 0.91,
                    }
                ],
                "entities": ["违约责任"],
                "paths": ["第八条 违约责任 -> 违约责任"],
                "structured_paths": [{"source": "第八条 违约责任", "target": "违约责任", "chunk_ids": ["chunk_1"]}],
                "domain_pack_id": "contract_review",
            }

    class FakeFusion:
        def merge(self, *, query: str, documents_by_source: dict[str, list[RetrievedDocument]], top_k: int | None = None):
            docs = list(documents_by_source.get("graph") or [])
            return FusionResult(
                documents=docs[: top_k or len(docs)],
                dropped_documents=[],
                fusion_metadata={"query": query},
                rerank_metadata={},
            )

    orchestrator = RetrievalOrchestrator(
        rag_retriever=EmptyRetriever(),
        keyword_retriever=EmptyRetriever(),
        graph_retriever=FakeGraphRetriever(),
        query_expander=FakeQueryExpander(),
        planner=FakePlanner(),
        query_processor=FakeQueryProcessor(),
        fusion=FakeFusion(),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="auto",
            query="违约责任和还款义务是什么关系",
            knowledge_ids=["kb_1"],
            retrieval_options={"knowledge_capability": "rag_graph", "top_k": 5},
        )
    )

    assert captured["requested_mode"] == "auto"
    assert result["actual_mode"] == "graphrag"
    assert result["metadata"]["requested_mode"] == "auto"
    assert result["metadata"]["resolved_mode"] == "graphrag"


def test_phase2_graph_retriever_accepts_domain_policy_driven_graph_cues() -> None:
    _ensure_runtime_paths()

    GraphRetriever = importlib.import_module("zuno.services.graphrag.retriever").GraphRetriever

    class FakeClient:
        async def query_neighbors(
            self,
            entity_name,
            knowledge_id,
            hops=1,
            limit=10,
            domain_pack_id=None,
            index_version=None,
            status=None,
        ):
            if entity_name != "审批流":
                return []
            return [
                {
                    "source": "审批流",
                    "target": "复核节点",
                    "chunk_ids": ["chunk_1"],
                }
            ]

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, collection_name, chunk_ids):
            return [
                {
                    "chunk_id": "chunk_1",
                    "file_name": "workflow.md",
                    "content": "审批流经过复核节点后进入归档节点。",
                    "summary": "",
                }
            ]

    result = asyncio.run(
        GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore()).retrieve(
            "审批流怎么走",
            "kb_workflow",
            graph_hop_limit=2,
            max_paths_per_entity=5,
            query_policy={
                "graph_seed_terms": ["审批流"],
                "graph_relation_cues": ["怎么走"],
            },
        )
    )

    assert result["paths"] == ["审批流 -> 复核节点"]
    assert result["documents"][0]["chunk_id"] == "chunk_1"


def test_phase2_graph_retriever_runtime_no_longer_contains_contract_review_hardcoding() -> None:
    content = (BACKEND_ROOT / "zuno" / "services" / "graphrag" / "retriever.py").read_text(encoding="utf-8")

    assert "CONTRACT_REVIEW_SEED_CUES" not in content
    assert "CONTRACT_REVIEW_GRAPH_CUES" not in content
    assert "CONTRACT_REVIEW_STEP_CUES" not in content


def test_phase2_docs_position_local_graphrag_as_current_mainline() -> None:
    phase_doc = (
        REPO_ROOT / "docs" / "architecture" / "phases" / "phase-02-graphrag-mainline-deepening.md"
    ).read_text(encoding="utf-8")
    orchestrator_doc = (
        REPO_ROOT / "docs" / "architecture" / "specs" / "retrieval-orchestrator.md"
    ).read_text(encoding="utf-8")

    assert "RetrievalOrchestrator" in phase_doc
    assert "RetrievalPlanner" in phase_doc
    assert "rag / hybrid / graphrag" in phase_doc
    assert "Local GraphRAG" in phase_doc
    assert "Community GraphRAG" in phase_doc
    assert "planner 决定" in orchestrator_doc or "planner" in orchestrator_doc.lower()

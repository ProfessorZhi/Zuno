import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from zuno.core.graphs.domain_qa_graph import DomainQAGraph
from zuno.services.pipeline.manager import KnowledgePipelineManager
from zuno.services.retrieval.models import ProcessedQuery, RetrievalRequest
from zuno.services.retrieval.planner import RetrievalPlanner


def test_phase5_domain_graph_merges_runtime_retrieval_contract() -> None:
    mode, options = DomainQAGraph._merge_retrieval_options(
        {
            "knowledge_status": "active",
            "knowledge_config": {
                "index_capability": "rag_graph",
                "index_settings": {
                    "status": "active",
                    "index_version": "vector-v3",
                    "health_status": "ready",
                },
                "graph_index_settings": {
                    "index_version": "graph-v7",
                    "health_status": "ready",
                    "use_rag_entry_chunk": False,
                },
                "retrieval_settings": {
                    "default_mode": "rag_graph",
                    "profile": "enhanced",
                    "top_k": 7,
                    "rerank_enabled": True,
                    "rerank_top_k": 5,
                    "graph_hop_limit": 3,
                    "max_paths_per_entity": 4,
                },
            },
        },
        {
            "id": "contracts-pack",
            "retrieval_policy_data": {
                "fallback_policy": {"query_rewrite_retry": False},
                "budget_policy": {"max_latency_ms": 1500},
            },
        },
    )

    assert mode == "rag_graph"
    assert options["requested_profile"] == "enhanced"
    assert options["knowledge_capability"] == "rag_graph"
    assert options["domain_pack_id"] == "contracts-pack"
    assert options["index_version"] == {"vector": "vector-v3", "graph": "graph-v7"}
    assert options["index_health"] == {"vector": "ready", "graph": "ready"}
    assert options["budget_policy"]["graph_hop_limit"] == 3
    assert options["fallback_policy"]["query_rewrite_retry"] is False


def test_phase5_retrieval_planner_stabilizes_modes_and_profiles() -> None:
    planner = RetrievalPlanner(enable_keyword_recall=True)
    processed_query = ProcessedQuery(
        original_query="这两个实体是什么关系？",
        normalized_query="这两个实体是什么关系？",
        rewritten_queries=["这两个实体是什么关系？"],
        query_features={"relation_question": True},
    )

    auto_request = RetrievalRequest(
        query="这两个实体是什么关系？",
        knowledge_ids=["kb-1"],
        mode="auto",
        requested_profile="auto",
        top_k=6,
        graph_hop_limit=2,
        max_paths_per_entity=5,
        index_health={"graph": "ready"},
        scope_policy={"status": "active"},
    )
    auto_plan = planner.build_plan(auto_request, processed_query, knowledge_capability="rag_graph")

    assert auto_plan.resolved_mode == "hybrid"
    assert auto_plan.resolved_profile == "relation_hybrid"
    assert auto_plan.enabled_retrievers == ["vector", "bm25", "graph"]

    degraded_request = RetrievalRequest(
        query="实体关系",
        knowledge_ids=["kb-1"],
        mode="graphrag",
        requested_profile="auto",
        index_health={"graph": "stale"},
        scope_policy={"status": "active"},
    )
    degraded_plan = planner.build_plan(degraded_request, processed_query, knowledge_capability="rag_graph")

    assert degraded_plan.resolved_mode == "rag"
    assert degraded_plan.resolved_profile == "vector_rerank"
    assert degraded_plan.enabled_retrievers == ["vector"]
    assert degraded_plan.fallback_policy["graph_degraded"] is True


def test_phase5_langgraph_runtime_keeps_retrieval_trace_and_citations() -> None:
    async def retrieval_runner(*, query, knowledge_ids, runtime_settings, domain_pack):
        assert query == "终止条款"
        assert knowledge_ids == ["kb-1"]
        assert runtime_settings["knowledge_config"]["retrieval_settings"]["profile"] == "enhanced"
        assert domain_pack["id"] == "contracts-pack"
        return {
            "actual_mode": "hybrid",
            "domain_pack_id": "contracts-pack",
            "metadata": {
                "requested_mode": "rag_graph",
                "requested_profile": "enhanced",
                "resolved_profile": "relation_hybrid",
                "fallback_triggered": False,
                "scope_policy": {"status": "active"},
                "index_version": {"vector": "vector-v1", "graph": "graph-v2"},
                "index_health": {"vector": "ready", "graph": "ready"},
            },
            "graph_result": {"structured_paths": [{"source": "终止条款", "target": "违约责任"}]},
            "final_pass_result": {
                "documents": [
                    {
                        "chunk_id": "chunk-1",
                        "knowledge_id": "kb-1",
                        "file_name": "contract.md",
                        "content": "终止条款要求提前 30 天通知，并约定违约责任。",
                    }
                ],
                "paths": ["终止条款 -> 违约责任"],
                "structured_paths": [{"source": "终止条款", "target": "违约责任"}],
            },
        }

    graph = DomainQAGraph(retrieval_runner=retrieval_runner)
    state = graph.build_initial_state(
        user_id="u-1",
        agent_id="a-1",
        dialog_id="d-1",
        query="终止条款",
        knowledge_ids=["kb-1"],
        domain_pack_id="contracts-pack",
        runtime_settings={
            "knowledge_config": {
                "retrieval_settings": {
                    "default_mode": "rag_graph",
                    "profile": "enhanced",
                }
            }
        },
        domain_pack={"id": "contracts-pack"},
    )

    final_state = asyncio.run(graph.ainvoke(state))

    assert final_state["status"] == "completed"
    assert final_state["citations"] == [
        {"chunk_id": "chunk-1", "file_name": "contract.md", "knowledge_id": "kb-1"}
    ]
    assert final_state["support_verdict"]["status"] == "supported"
    assert final_state["cost_metadata"]["path_count"] == 1

    trace_nodes = [item["node"] for item in final_state["trace_metadata"]["nodes"]]
    assert trace_nodes == [
        "resolve_domain_pack",
        "route_intent",
        "rewrite_query",
        "retrieve_evidence",
        "draft_answer",
        "citation_check",
        "finalize",
    ]
    retrieval_trace = final_state["trace_metadata"]["nodes"][3]["payload"]
    assert retrieval_trace["actual_mode"] == "hybrid"
    assert retrieval_trace["requested_profile"] == "enhanced"
    assert retrieval_trace["resolved_profile"] == "relation_hybrid"


def test_phase5_graph_pipeline_applies_incremental_graph_updates(monkeypatch) -> None:
    manager = KnowledgePipelineManager(enable_graph_indexing=True)
    task = SimpleNamespace(
        id="task-1",
        knowledge_id="kb-1",
        knowledge_file_id="file-1",
        result_summary={"chunk_count": 2},
    )

    chunks = [
        SimpleNamespace(
            chunk_id="chunk-a",
            content="甲方应提前通知乙方。",
            summary="通知义务",
            file_id="file-1",
            file_name="contract-a.md",
            knowledge_id="kb-1",
            update_time="2026-06-11",
            source_url="local://contract-a.md",
            to_dict=lambda: {
                "chunk_id": "chunk-a",
                "source_chunk_id": "chunk-a",
                "document_hash": "doc-hash-a",
                "chunk_hash": "chunk-hash-a",
            },
        ),
        SimpleNamespace(
            chunk_id="chunk-b",
            content="乙方违约时承担赔偿责任。",
            summary="违约责任",
            file_id="file-1",
            file_name="contract-a.md",
            knowledge_id="kb-1",
            update_time="2026-06-11",
            source_url="local://contract-a.md",
            to_dict=lambda: {
                "chunk_id": "chunk-b",
                "source_chunk_id": "chunk-b",
                "document_hash": "doc-hash-b",
                "chunk_hash": "chunk-hash-b",
            },
        ),
    ]

    delete_calls = []
    entity_payloads = []
    relation_payloads = []
    finish_calls = []

    async def fake_load_task(task_id: str):
        assert task_id == "task-1"
        return task

    async def fake_parse_chunks(_task):
        return chunks

    async def fake_record_stage(*args, **kwargs):
        return None

    async def fake_mark_finished(*args, **kwargs):
        finish_calls.append({"args": args, "kwargs": kwargs})

    async def fake_create_task_event(*args, **kwargs):
        return None

    async def fake_update_pipeline_fields(*args, **kwargs):
        return None

    async def fake_get_knowledge_config(_knowledge_id: str):
        return {
            "index_capability": "rag_graph",
            "index_settings": {"status": "active"},
            "graph_index_settings": {"index_version": "graph-v9"},
        }

    async def fake_get_runtime_settings(_knowledge_id: str):
        return {
            "domain_pack": {"name": "contracts"},
            "domain_pack_id": "contracts-pack",
        }

    class FakeExtractor:
        async def extract_from_chunk(self, chunk, knowledge_id, domain_pack=None):
            payload = chunk.to_dict()
            return {
                "entities": [
                    {
                        "name": f"Entity-{payload['chunk_id']}",
                        "knowledge_id": knowledge_id,
                        "chunk_id": payload["chunk_id"],
                        "source_chunk_id": payload["source_chunk_id"],
                        "document_hash": payload["document_hash"],
                        "chunk_hash": payload["chunk_hash"],
                    }
                ],
                "relations": [
                    {
                        "source": f"Entity-{payload['chunk_id']}",
                        "target": "Clause",
                        "knowledge_id": knowledge_id,
                        "chunk_id": payload["chunk_id"],
                        "source_chunk_id": payload["source_chunk_id"],
                        "document_hash": payload["document_hash"],
                        "chunk_hash": payload["chunk_hash"],
                    }
                ],
            }

    class FakeNeo4jClient:
        @classmethod
        def is_enabled(cls) -> bool:
            return True

        async def delete_by_source_chunk(self, knowledge_file_id, knowledge_id, source_chunk_id):
            delete_calls.append((knowledge_file_id, knowledge_id, source_chunk_id))

        async def upsert_entity(self, payload):
            entity_payloads.append(payload)

        async def upsert_relation(self, payload):
            relation_payloads.append(payload)

    monkeypatch.setattr(manager, "_load_task", fake_load_task)
    monkeypatch.setattr(manager, "_parse_chunks", fake_parse_chunks)
    monkeypatch.setattr(manager, "_record_stage", fake_record_stage)
    monkeypatch.setattr(manager, "_update_task_progress", lambda *args, **kwargs: None)

    manager_module = sys.modules["zuno.services.pipeline.manager"]
    monkeypatch.setattr(manager_module.KnowledgeTaskDao, "mark_task_finished", fake_mark_finished)
    monkeypatch.setattr(manager_module.KnowledgeTaskDao, "create_task_event", fake_create_task_event)
    monkeypatch.setattr(manager_module.KnowledgeFileDao, "update_pipeline_fields", fake_update_pipeline_fields)
    monkeypatch.setattr(manager_module.KnowledgeService, "get_knowledge_config", fake_get_knowledge_config)
    monkeypatch.setattr(manager_module.KnowledgeService, "get_runtime_settings", fake_get_runtime_settings)
    monkeypatch.setattr(manager_module, "CachedGraphExtractor", FakeExtractor)
    monkeypatch.setattr(manager_module, "Neo4jClient", FakeNeo4jClient)

    asyncio.run(manager.run_graph_stage("task-1"))

    assert delete_calls == [
        ("file-1", "kb-1", "chunk-a"),
        ("file-1", "kb-1", "chunk-b"),
    ]
    assert len(entity_payloads) == 2
    assert len(relation_payloads) == 2
    assert all(payload["domain_pack_id"] == "contracts-pack" for payload in entity_payloads + relation_payloads)
    assert all(payload["index_version"] == "graph-v9" for payload in entity_payloads + relation_payloads)
    assert all(payload["status"] == "active" for payload in entity_payloads + relation_payloads)
    assert {payload["document_hash"] for payload in entity_payloads} == {"doc-hash-a", "doc-hash-b"}
    assert {payload["chunk_hash"] for payload in relation_payloads} == {"chunk-hash-a", "chunk-hash-b"}
    assert finish_calls and finish_calls[0]["kwargs"]["status"] == "success"

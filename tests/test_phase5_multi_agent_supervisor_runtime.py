import asyncio
import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SERVICE_API_ROOT = REPO_ROOT / "src" / "backend"
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    for runtime_root in (str(BACKEND_ROOT),):
        if runtime_root not in sys.path:
            sys.path.insert(0, runtime_root)


def test_multi_agent_supervisor_graph_builds_initial_state():
    _ensure_runtime_paths()

    MultiAgentSupervisorGraph = importlib.import_module(
        "zuno.core.graphs.multi_agent_supervisor_graph"
    ).MultiAgentSupervisorGraph

    graph = MultiAgentSupervisorGraph()
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="这份合同是否约定了违约责任？",
        knowledge_ids=["kb_contract"],
        domain_pack_id="contract_review",
    )

    assert state["domain_pack_id"] == "contract_review"
    assert state["planned_agents"] == []
    assert state["specialist_outputs"] == []
    assert state["status"] == "pending"


def test_multi_agent_supervisor_graph_runs_actual_domain_graph_path():
    _ensure_runtime_paths()

    DomainQAGraph = importlib.import_module("zuno.core.graphs.domain_qa_graph").DomainQAGraph
    MultiAgentSupervisorGraph = importlib.import_module(
        "zuno.core.graphs.multi_agent_supervisor_graph"
    ).MultiAgentSupervisorGraph

    async def fake_retrieval_runner(*, query, knowledge_ids, runtime_settings, domain_pack):
        assert "违约责任" in query
        assert knowledge_ids == ["kb_contract"]
        assert (domain_pack or {}).get("id") == "contract_review"
        return {
            "content": "合同明确约定了违约责任。",
            "actual_mode": "hybrid",
            "domain_pack_id": "contract_review",
            "metadata": {
                "requested_mode": "graphrag",
                "requested_profile": "relation_hybrid",
                "resolved_profile": "relation_hybrid",
                "fallback_triggered": False,
                "scope_policy": {"status": "active"},
                "index_version": {"vector": "vector_v2", "graph": "graph_v2"},
                "index_health": {"vector": "ready", "graph": "ready"},
            },
            "graph_result": {
                "paths": ["第八条 违约责任 -> 违约责任"],
                "structured_paths": [
                    {
                        "source": "第八条 违约责任",
                        "target": "违约责任",
                        "chunk_ids": ["contract_chunk_1"],
                    }
                ],
            },
            "final_pass_result": {
                "documents": [
                    {
                        "chunk_id": "contract_chunk_1",
                        "file_name": "loan_contract_001.md",
                        "knowledge_id": "kb_contract",
                        "content": "第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
                    },
                    {
                        "chunk_id": "contract_chunk_1",
                        "file_name": "loan_contract_001.md",
                        "knowledge_id": "kb_contract",
                        "content": "第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
                    },
                ],
                "paths": ["第八条 违约责任 -> 违约责任"],
                "structured_paths": [
                    {
                        "source": "第八条 违约责任",
                        "target": "违约责任",
                        "chunk_ids": ["contract_chunk_1"],
                    }
                ],
            },
        }

    async def actual_domain_qa_runner(state):
        subgraph = DomainQAGraph(retrieval_runner=fake_retrieval_runner)
        sub_state = subgraph.build_initial_state(
            user_id=state["user_id"],
            agent_id=state["agent_id"],
            dialog_id=state["dialog_id"],
            query=state["query"],
            knowledge_ids=state.get("knowledge_ids") or [],
            domain_pack_id=state.get("domain_pack_id"),
            runtime_settings=state.get("runtime_settings"),
            domain_pack=state.get("domain_pack"),
        )
        return await subgraph.ainvoke(sub_state)

    graph = MultiAgentSupervisorGraph(domain_qa_runner=actual_domain_qa_runner)
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="这份合同是否约定了违约责任？",
        knowledge_ids=["kb_contract"],
        domain_pack_id="contract_review",
        runtime_settings={
            "knowledge_config": {
                "retrieval_settings": {
                    "default_mode": "graphrag",
                    "graph_hop_limit": 2,
                },
                "index_capability": "rag_graph",
                "index_settings": {"index_version": "vector_v2", "health_status": "ready"},
                "graph_index_settings": {"index_version": "graph_v2", "health_status": "ready"},
            }
        },
        domain_pack={
            "id": "contract_review",
            "answer_template_text": "你是一名合同审查助手，请严格基于检索证据回答。",
        },
    )

    result = asyncio.run(graph.ainvoke(state))

    assert result["status"] == "completed"
    assert result["planned_agents"] == ["domain_qa_specialist", "citation_verifier_specialist"]
    assert len(result["specialist_outputs"]) == 2
    assert result["specialist_outputs"][0]["agent"] == "domain_qa_specialist"
    assert result["specialist_outputs"][1]["agent"] == "citation_verifier_specialist"
    assert result["graph_paths"][0]["source"] == "第八条 违约责任"
    assert result["citations"] == [
        {
            "chunk_id": "contract_chunk_1",
            "file_name": "loan_contract_001.md",
            "knowledge_id": "kb_contract",
        }
    ]
    assert result["support_verdict"]["status"] == "supported"
    assert result["evidence_bundle"]["document_count"] == 2
    assert result["final_answer"].startswith("你是一名合同审查助手")
    assert "第八条 违约责任" in result["final_answer"]
    assert [node["node"] for node in result["trace_metadata"]["nodes"]] == [
        "plan_specialists",
        "domain_qa_specialist",
        "citation_verifier_specialist",
        "finalize",
    ]
    assert result["cost_metadata"]["planned_agent_count"] == 2
    assert result["cost_metadata"]["specialist_count"] == 2
    assert result["cost_metadata"]["citation_count"] == 1
    assert result["cost_metadata"]["path_count"] == 1


def test_multi_agent_supervisor_graph_records_failure_and_finalizes():
    _ensure_runtime_paths()

    MultiAgentSupervisorGraph = importlib.import_module(
        "zuno.core.graphs.multi_agent_supervisor_graph"
    ).MultiAgentSupervisorGraph

    async def failing_domain_qa_runner(state):
        raise RuntimeError("domain specialist unavailable")

    graph = MultiAgentSupervisorGraph(domain_qa_runner=failing_domain_qa_runner)
    state = graph.build_initial_state(
        user_id="u1",
        agent_id="a1",
        dialog_id="d1",
        query="这份合同是否约定了违约责任？",
        domain_pack_id="contract_review",
    )

    result = asyncio.run(graph.ainvoke(state))

    assert result["status"] == "failed"
    assert result["failure_metadata"]["node"] == "domain_qa_specialist"
    assert "domain specialist unavailable" in result["failure_metadata"]["error"]
    assert "domain_qa_specialist" in result["final_answer"]
    assert result["trace_metadata"]["nodes"][-1]["node"] == "finalize"

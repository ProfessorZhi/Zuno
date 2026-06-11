import asyncio
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_backend_path() -> None:
    backend_path = str(BACKEND_ROOT)
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)


def _build_fake_retrieval_result(*, content: str) -> dict:
    return {
        "content": content,
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
                    "content": content,
                }
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


def _runtime_settings() -> dict:
    return {
        "domain_pack_id": "contract_review",
        "domain_pack": {
            "id": "contract_review",
            "answer_template_text": "你是一名合同审查助手，请严格基于检索证据回答。",
        },
        "knowledge_config": {
            "retrieval_settings": {
                "default_mode": "graphrag",
                "graph_hop_limit": 2,
            },
            "index_capability": "rag_graph",
            "index_settings": {"index_version": "vector_v2", "health_status": "ready"},
            "graph_index_settings": {"index_version": "graph_v2", "health_status": "ready"},
        },
    }


def test_workspace_prefetch_exposes_supported_contract_review_evidence(monkeypatch):
    _ensure_backend_path()

    workspace_module = importlib.import_module("agentchat.services.workspace.simple_agent")
    WorkSpaceSimpleAgent = importlib.import_module("zuno.services.workspace.simple_agent").WorkSpaceSimpleAgent
    DomainQAGraph = importlib.import_module("zuno.core.graphs.domain_qa_graph").DomainQAGraph

    monkeypatch.setattr(workspace_module.ModelManager, "get_user_model", lambda **_: SimpleNamespace())

    async def fake_runtime_settings(_knowledge_id):
        return _runtime_settings()

    async def fake_retrieval_runner(*, query, knowledge_ids, runtime_settings, domain_pack):
        assert "违约责任" in query
        assert knowledge_ids == ["kb_contract"]
        assert (domain_pack or {}).get("id") == "contract_review"
        return _build_fake_retrieval_result(
            content="第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。"
        )

    monkeypatch.setattr(workspace_module.KnowledgeService, "get_runtime_settings", fake_runtime_settings)

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_contract"],
        retrieval_mode="graphrag",
    )
    agent.domain_qa_runtime.graph = DomainQAGraph(retrieval_runner=fake_retrieval_runner)

    context = asyncio.run(agent._prefetch_knowledge_context("这份合同是否约定了违约责任？"))

    assert context is not None
    result = context["result"]
    assert result["support_verdict"]["status"] == "supported"
    assert result["evidence_bundle"]["citation_count"] == 1
    assert result["metadata"]["domain_pack_support_verdict"]["status"] == "supported"
    assert result["metadata"]["domain_pack_evidence_bundle"]["document_count"] == 1

    payload = agent._build_retrieval_event_payload(result, phase="retrieval")
    assert payload["status"] == "END"
    assert payload["domain_pack_support_verdict"]["status"] == "supported"
    assert payload["domain_pack_evidence_bundle"]["citation_count"] == 1


def test_workspace_prefetch_exposes_insufficient_contract_review_evidence(monkeypatch):
    _ensure_backend_path()

    workspace_module = importlib.import_module("agentchat.services.workspace.simple_agent")
    WorkSpaceSimpleAgent = importlib.import_module("zuno.services.workspace.simple_agent").WorkSpaceSimpleAgent
    DomainQAGraph = importlib.import_module("zuno.core.graphs.domain_qa_graph").DomainQAGraph

    monkeypatch.setattr(workspace_module.ModelManager, "get_user_model", lambda **_: SimpleNamespace())

    async def fake_runtime_settings(_knowledge_id):
        return _runtime_settings()

    async def fake_retrieval_runner(*, query, knowledge_ids, runtime_settings, domain_pack):
        assert "72" in query
        assert knowledge_ids == ["kb_contract"]
        return _build_fake_retrieval_result(
            content="第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。"
        )

    monkeypatch.setattr(workspace_module.KnowledgeService, "get_runtime_settings", fake_runtime_settings)

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_contract"],
        retrieval_mode="graphrag",
    )
    agent.domain_qa_runtime.graph = DomainQAGraph(retrieval_runner=fake_retrieval_runner)

    context = asyncio.run(agent._prefetch_knowledge_context("这份合同是否要求 72 小时内删除数据？"))

    assert context is not None
    result = context["result"]
    assert result["support_verdict"]["status"] == "insufficient_evidence"
    assert result["support_verdict"]["reason"] == "evidence_not_query_aligned"
    assert result["metadata"]["domain_pack_support_verdict"]["status"] == "insufficient_evidence"
    assert result["metadata"]["domain_pack_evidence_bundle"]["citation_count"] == 1

    payload = agent._build_retrieval_event_payload(result, phase="retrieval")
    assert payload["status"] == "END"
    assert payload["domain_pack_support_verdict"]["status"] == "insufficient_evidence"
    assert payload["domain_pack_evidence_bundle"]["document_count"] == 1

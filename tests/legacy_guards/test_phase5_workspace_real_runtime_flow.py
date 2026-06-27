import asyncio
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICE_API_ROOT = REPO_ROOT / "src" / "backend"
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _ensure_runtime_paths() -> None:
    for runtime_root in (str(BACKEND_ROOT),):
        if runtime_root not in sys.path:
            sys.path.insert(0, runtime_root)


def test_workspace_prefetch_exposes_supported_contract_review_evidence(monkeypatch):
    _ensure_runtime_paths()

    workspace_module = importlib.import_module("zuno.services.workspace.simple_agent")
    WorkSpaceSimpleAgent = importlib.import_module("zuno.services.workspace.simple_agent").WorkSpaceSimpleAgent
    KnowledgeQueryResult = importlib.import_module("zuno.services.graphrag.query_service").KnowledgeQueryResult

    monkeypatch.setattr(workspace_module.ModelManager, "get_user_model", lambda **_: SimpleNamespace())

    async def fake_project_query(self, *, user_id, knowledge_ids, query, query_method=None, top_k=None):
        assert "违约责任" in query
        assert knowledge_ids == ["kb_contract"]
        assert query_method is None
        return KnowledgeQueryResult(
            graphrag_project_id="contract_review",
            answer="第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
            requested_query_method="auto",
            resolved_query_method="local",
            fallback_reason=None,
            documents=[
                {
                    "chunk_id": "contract_chunk_1",
                    "file_name": "loan_contract_001.md",
                    "knowledge_id": "kb_contract",
                    "content": "第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
                }
            ],
            evidence={
                "document_count": 1,
                "citation_count": 1,
                "support_verdict": {"status": "supported"},
            },
            citations=["contract_chunk_1"],
            retrievers_used=["vector", "graph"],
            graph_paths=["第八条 违约责任 -> 违约责任"],
            communities=[],
            prompt_version="extract-v2",
            query_prompt_version="query-v3",
            index_version={"vector": "vector_v2", "graph": "graph_v2"},
            community_version="community-v1",
            trace_metadata={"support_verdict": {"status": "supported"}},
        )

    monkeypatch.setattr(workspace_module.KnowledgeQueryService, "query", fake_project_query)

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_contract"],
        retrieval_mode="graphrag",
    )

    context = asyncio.run(agent._prefetch_knowledge_context("这份合同是否约定了违约责任？"))

    assert context is not None
    result = context["result"]
    assert result["support_verdict"]["status"] == "supported"
    assert result["evidence_bundle"]["citation_count"] == 1
    assert result["metadata"]["support_verdict"]["status"] == "supported"
    assert result["metadata"]["evidence_bundle"]["document_count"] == 1

    payload = agent._build_retrieval_event_payload(result, phase="retrieval")
    assert payload["status"] == "END"
    assert payload["graphrag_project_id"] == "contract_review"
    assert payload["support_verdict"]["status"] == "supported"
    assert payload["evidence_bundle"]["citation_count"] == 1


def test_workspace_prefetch_exposes_insufficient_contract_review_evidence(monkeypatch):
    _ensure_runtime_paths()

    workspace_module = importlib.import_module("zuno.services.workspace.simple_agent")
    WorkSpaceSimpleAgent = importlib.import_module("zuno.services.workspace.simple_agent").WorkSpaceSimpleAgent
    KnowledgeQueryResult = importlib.import_module("zuno.services.graphrag.query_service").KnowledgeQueryResult

    monkeypatch.setattr(workspace_module.ModelManager, "get_user_model", lambda **_: SimpleNamespace())

    async def fake_project_query(self, *, user_id, knowledge_ids, query, query_method=None, top_k=None):
        assert "72" in query
        assert knowledge_ids == ["kb_contract"]
        return KnowledgeQueryResult(
            graphrag_project_id="contract_review",
            answer="第八条 违约责任：借款人未按约定期限还款的，应承担违约责任。",
            requested_query_method="auto",
            resolved_query_method="local",
            fallback_reason=None,
            documents=[{"chunk_id": "contract_chunk_1", "knowledge_id": "kb_contract"}],
            evidence={
                "document_count": 1,
                "citation_count": 1,
                "support_verdict": {
                    "status": "insufficient_evidence",
                    "reason": "evidence_not_query_aligned",
                },
            },
            citations=["contract_chunk_1"],
            retrievers_used=["vector", "graph"],
            graph_paths=["第八条 违约责任 -> 违约责任"],
            communities=[],
            prompt_version="extract-v2",
            query_prompt_version="query-v3",
            index_version={"vector": "vector_v2", "graph": "graph_v2"},
            community_version="community-v1",
            trace_metadata={
                "support_verdict": {
                    "status": "insufficient_evidence",
                    "reason": "evidence_not_query_aligned",
                }
            },
        )

    monkeypatch.setattr(workspace_module.KnowledgeQueryService, "query", fake_project_query)

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_contract"],
        retrieval_mode="graphrag",
    )

    context = asyncio.run(agent._prefetch_knowledge_context("这份合同是否要求 72 小时内删除数据？"))

    assert context is not None
    result = context["result"]
    assert result["support_verdict"]["status"] == "insufficient_evidence"
    assert result["support_verdict"]["reason"] == "evidence_not_query_aligned"
    assert result["metadata"]["support_verdict"]["status"] == "insufficient_evidence"
    assert result["metadata"]["evidence_bundle"]["citation_count"] == 1

    payload = agent._build_retrieval_event_payload(result, phase="retrieval")
    assert payload["status"] == "END"
    assert payload["support_verdict"]["status"] == "insufficient_evidence"
    assert payload["evidence_bundle"]["document_count"] == 1

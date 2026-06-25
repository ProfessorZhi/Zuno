import asyncio
from types import SimpleNamespace


def test_workspace_prefetch_uses_project_query_runtime_when_available(monkeypatch):
    from zuno.services.graphrag.query_service import KnowledgeQueryResult
    from zuno.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "zuno.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    async def fake_project_query(self, *, user_id, knowledge_ids, query, query_method=None, top_k=None):
        assert user_id == "u_1"
        assert knowledge_ids == ["kb_1"]
        assert query_method is None
        assert top_k is None
        return KnowledgeQueryResult(
            graphrag_project_id="contract_review",
            answer="结论\n合同存在终止条款风险。",
            requested_query_method="auto",
            resolved_query_method="local",
            fallback_reason=None,
            documents=[{"chunk_id": "chunk-1"}],
            evidence={"document_count": 1},
            citations=["chunk-1"],
            retrievers_used=["vector", "graph"],
            graph_paths=[],
            communities=[],
            prompt_version="extract-v2",
            query_prompt_version="query-v3",
            index_version={"vector": "v1", "graph": "g1"},
            community_version="c1",
            trace_metadata={"resolved_query_method": "local"},
        )

    monkeypatch.setattr("zuno.services.workspace.simple_agent.KnowledgeQueryService.query", fake_project_query)

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="graphrag",
    )

    context = asyncio.run(agent._prefetch_knowledge_context("请审查终止条款"))

    assert context is not None
    assert "终止条款风险" in context["content"]
    assert context["result"]["domain_pack_id"] is None
    assert context["result"]["graphrag_project_id"] == "contract_review"


def test_workspace_retrieval_event_payload_exposes_domain_pack_failure(monkeypatch):
    from zuno.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "zuno.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="graphrag",
    )

    payload = agent._build_retrieval_event_payload(
        {
            "domain_pack_id": "contract_review",
            "metadata": {
                "domain_pack_trace": {"nodes": [{"node": "retrieve_evidence"}]},
                "domain_pack_cost": {"status": "failed", "failed_node": "retrieve_evidence"},
                "domain_pack_failure": {"node": "retrieve_evidence", "error": "retrieval backend unavailable"},
            },
        }
    )

    assert payload["status"] == "ERROR"
    assert payload["domain_pack_failure"]["node"] == "retrieve_evidence"
    assert payload["domain_pack_cost"]["failed_node"] == "retrieve_evidence"


def test_workspace_legacy_multi_agent_runtime_is_not_current_path(monkeypatch):
    from zuno.services.workspace.simple_agent import WorkSpaceSimpleAgent

    monkeypatch.setattr(
        "zuno.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="graphrag",
    )

    assert not hasattr(agent, "domain_qa_runtime")
    assert not hasattr(agent, "_run_domain_pack_query")

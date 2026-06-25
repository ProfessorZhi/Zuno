import asyncio
from types import SimpleNamespace


def _patch_model(monkeypatch):
    monkeypatch.setattr(
        "zuno.services.workspace.simple_agent.ModelManager.get_user_model",
        lambda **_: SimpleNamespace(),
    )


def test_workspace_agent_does_not_expose_legacy_agent_runtime(monkeypatch):
    from zuno.services.workspace import simple_agent as workspace_module
    from zuno.services.workspace.simple_agent import WorkSpaceSimpleAgent

    _patch_model(monkeypatch)

    agent = WorkSpaceSimpleAgent(
        model_config={},
        user_id="u_1",
        session_id="s_1",
        knowledge_ids=["kb_1"],
        retrieval_mode="graphrag",
    )

    assert "AgentRuntime" not in vars(workspace_module)
    assert "domain_qa_runtime" not in vars(agent)


def test_workspace_prefetch_uses_project_query_runtime(monkeypatch):
    from zuno.services.graphrag.query_service import KnowledgeQueryResult
    from zuno.services.workspace.simple_agent import WorkSpaceSimpleAgent

    _patch_model(monkeypatch)

    async def fake_project_query(self, *, user_id, knowledge_ids, query, query_method=None, top_k=None):
        assert user_id == "u_1"
        assert knowledge_ids == ["kb_1"]
        assert "终止条款" in query
        assert query_method is None
        assert top_k is None
        return KnowledgeQueryResult(
            graphrag_project_id="contract_review",
            answer="第八条约定了终止条款风险。",
            requested_query_method="auto",
            resolved_query_method="local",
            fallback_reason=None,
            documents=[{"chunk_id": "chunk-1", "file_name": "contract.md"}],
            evidence={"document_count": 1, "citation_coverage": 1.0},
            citations=["chunk-1"],
            retrievers_used=["vector", "graph"],
            graph_paths=[{"source": "第八条", "target": "终止条款"}],
            communities=[],
            prompt_version="extract-v2",
            query_prompt_version="query-v3",
            index_version={"vector": "v1", "graph": "g1"},
            community_version="c1",
            trace_metadata={"resolved_query_method": "local"},
        )

    monkeypatch.setattr(
        "zuno.services.workspace.simple_agent.KnowledgeQueryService.query",
        fake_project_query,
    )

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
    assert context["result"]["graphrag_project_id"] == "contract_review"
    assert context["result"]["domain_pack_id"] is None
    assert context["result"]["metadata"]["resolved_query_method"] == "local"

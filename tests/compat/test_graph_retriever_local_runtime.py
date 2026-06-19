import asyncio


def test_graph_retriever_adapter_uses_local_runtime_graph_retriever(monkeypatch):
    from zuno.services.retrieval.retrievers import GraphRetrieverAdapter

    class FakeLocalGraphRetriever:
        async def retrieve(
            self,
            query,
            knowledge_id,
            graph_hop_limit=2,
            max_paths_per_entity=10,
            domain_pack_id=None,
            **_kwargs,
        ):
            return {
                "content": "local graph content",
                "entities": ["Agent Server"],
                "paths": ["Agent Server -> PostgreSQL"],
                "documents": [{"chunk_id": "c1", "content": "Agent Server persists into PostgreSQL"}],
                "domain_pack_id": domain_pack_id,
                "graph_hop_limit": graph_hop_limit,
            }

    async def fake_get_runtime_settings(_knowledge_id):
        return {
            "domain_pack_id": None,
            "graph_retriever": FakeLocalGraphRetriever(),
        }

    monkeypatch.setattr(
        "zuno.services.retrieval.retrievers.KnowledgeService.get_runtime_settings",
        fake_get_runtime_settings,
    )

    adapter = GraphRetrieverAdapter()
    result = asyncio.run(adapter.retrieve("谁负责持久化？", ["stackless_eval_1"], {"graph_hop_limit": 3}))
    assert result["content"] == "local graph content"
    assert result["graph_hop_limit"] == 3
    assert result["paths"] == ["Agent Server -> PostgreSQL"]

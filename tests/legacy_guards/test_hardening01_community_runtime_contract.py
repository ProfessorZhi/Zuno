import asyncio


def _community_row():
    return {
        "community_id": "kb_1::community::0",
        "knowledge_id": "kb_1",
        "level": 0,
        "entities": ["付款期限", "违约责任"],
        "relation_count": 1,
        "supporting_chunks": ["c1"],
        "relations": [
            {"source": "付款期限", "target": "违约责任", "relation_type": "triggers"},
        ],
        "report": "付款期限会触发违约责任。",
        "community_version": "v0",
        "status": "ready",
    }


def test_graph_community_can_be_restored_from_neo4j_row():
    from zuno.services.graphrag.community.models import GraphCommunity

    community = GraphCommunity.from_dict(_community_row())

    assert community.community_id == "kb_1::community::0"
    assert community.level == 0
    assert community.entities == ["付款期限", "违约责任"]
    assert community.report == "付款期限会触发违约责任。"


def test_load_communities_converts_dict_rows_into_graph_community_objects():
    from zuno.services.graphrag.community.models import GraphCommunity
    from zuno.services.graphrag.community.service import CommunityGraphService

    class FakeClient:
        async def fetch_communities(self, knowledge_id, *, status=None, community_version=None):
            assert knowledge_id == "kb_1"
            return [_community_row()]

    communities = asyncio.run(
        CommunityGraphService(client=FakeClient()).load_communities(
            "kb_1",
            status="ready",
            community_version="v0",
        )
    )

    assert len(communities) == 1
    assert isinstance(communities[0], GraphCommunity)
    assert communities[0].report == "付款期限会触发违约责任。"


def test_search_reports_accepts_loaded_graph_community_objects():
    from zuno.services.graphrag.community.service import CommunityGraphService

    class FakeClient:
        async def fetch_communities(self, knowledge_id, *, status=None, community_version=None):
            return [_community_row()]

    service = CommunityGraphService(client=FakeClient())
    communities = asyncio.run(service.load_communities("kb_1", status="ready", community_version="v0"))
    result = service.search_reports("付款期限", communities, limit=1)

    assert result["used_communities"] == ["kb_1::community::0"]
    assert result["reports"][0]["report"] == "付款期限会触发违约责任。"


def test_community_global_path_runs_with_neo4j_style_rows():
    from zuno.services.retrieval.orchestrator import RetrievalOrchestrator

    class FakeClient:
        async def fetch_communities(self, knowledge_id, *, status=None, community_version=None):
            return [_community_row()]

    orchestrator = RetrievalOrchestrator(community_service=__import__(
        "zuno.services.graphrag.community.service",
        fromlist=["CommunityGraphService"],
    ).CommunityGraphService(client=FakeClient()))

    result = asyncio.run(
        orchestrator._run_community_global(
            "付款期限",
            ["kb_1"],
            {"index_health": {"community_version": "v0"}, "top_k": 3},
        )
    )

    assert result["used_communities"] == ["kb_1::community::0"]
    assert result["community_trace"]["community_version"] == "v0"


def test_drift_like_path_runs_single_follow_up_with_neo4j_style_rows():
    from zuno.services.retrieval.orchestrator import RetrievalOrchestrator

    class FakeClient:
        async def fetch_communities(self, knowledge_id, *, status=None, community_version=None):
            return [_community_row()]

    class FakeGraphRetriever:
        async def retrieve(self, query, knowledge_ids, options=None):
            return {
                "content": "条款证据：付款期限逾期会触发违约责任。",
                "documents": [
                    {
                        "chunk_id": "c1",
                        "knowledge_id": "kb_1",
                        "file_id": "f1",
                        "file_name": "contract.md",
                        "content": "付款期限逾期会触发违约责任。",
                        "score": 0.9,
                    }
                ],
                "paths": ["付款期限 -> 违约责任"],
                "entities": ["付款期限", "违约责任"],
            }

    orchestrator = RetrievalOrchestrator(
        community_service=__import__(
            "zuno.services.graphrag.community.service",
            fromlist=["CommunityGraphService"],
        ).CommunityGraphService(client=FakeClient()),
        graph_retriever=FakeGraphRetriever(),
    )

    result = asyncio.run(
        orchestrator._run_drift_like(
            "付款风险",
            ["kb_1"],
            {"index_health": {"community_version": "v0"}, "top_k": 3},
        )
    )

    assert result["used_communities"] == ["kb_1::community::0"]
    assert result["drift_trace"]["follow_up_count"] == 1
    assert result["citation_chunks"] == ["c1"]

import asyncio
from types import SimpleNamespace


def _edges():
    return [
        {
            "source": "付款期限",
            "target": "违约责任",
            "relation_type": "triggers",
            "chunk_ids": ["c1", "c2"],
        },
        {
            "source": "违约责任",
            "target": "解除合同",
            "relation_type": "enables",
            "chunk_ids": ["c3"],
        },
        {
            "source": "保密义务",
            "target": "数据删除",
            "relation_type": "requires",
            "chunk_ids": ["c4"],
        },
    ]


def test_phase3_detects_level0_communities_from_entity_relation_edges():
    from zuno.services.graphrag.community.detector import CommunityDetector

    communities = CommunityDetector.detect_level0(knowledge_id="kb_1", edges=_edges(), community_version="v0")

    assert len(communities) == 2
    first = communities[0]
    second = communities[1]

    assert first.level == 0
    assert first.knowledge_id == "kb_1"
    assert set(first.entities) == {"付款期限", "违约责任", "解除合同"}
    assert set(second.entities) == {"保密义务", "数据删除"}


def test_phase3_generates_community_report_with_entities_relations_and_chunks():
    from zuno.services.graphrag.community.models import GraphCommunity
    from zuno.services.graphrag.community.reporter import CommunityReportBuilder

    community = GraphCommunity(
        community_id="kb_1::community::0",
        knowledge_id="kb_1",
        level=0,
        entities=["付款期限", "违约责任", "解除合同"],
        relation_count=2,
        supporting_chunks=["c1", "c2", "c3"],
        relations=[
            {"source": "付款期限", "target": "违约责任", "relation_type": "triggers"},
            {"source": "违约责任", "target": "解除合同", "relation_type": "enables"},
        ],
        report="",
        community_version="v0",
    )

    report = CommunityReportBuilder().build_report(community)

    assert "付款期限" in report
    assert "违约责任" in report
    assert "解除合同" in report
    assert "c1" in report


def test_phase3_service_builds_and_persists_communities(monkeypatch):
    from zuno.services.graphrag.community.service import CommunityGraphService

    captured = {}

    class FakeClient:
        async def fetch_relation_edges(self, knowledge_id, index_version=None, status=None):
            captured["fetch"] = (knowledge_id, index_version, status)
            return _edges()

        async def replace_communities(self, knowledge_id, communities, community_version=None, status=None):
            captured["replace"] = {
                "knowledge_id": knowledge_id,
                "communities": communities,
                "community_version": community_version,
                "status": status,
            }

    service = CommunityGraphService(client=FakeClient())
    summary = asyncio.run(
        service.build_level0_communities(
            knowledge_id="kb_1",
            index_version="graph_v1",
            status="active",
            community_version="v0",
        )
    )

    assert captured["fetch"] == ("kb_1", "graph_v1", "active")
    assert captured["replace"]["knowledge_id"] == "kb_1"
    assert len(captured["replace"]["communities"]) == 2
    assert summary["community_count"] == 2
    assert summary["community_detection_status"] == "ready"
    assert summary["community_report_status"] == "ready"


def test_phase3_search_reports_returns_global_search_ready_metadata():
    from zuno.services.graphrag.community.models import GraphCommunity
    from zuno.services.graphrag.community.service import CommunityGraphService

    service = CommunityGraphService(client=None)
    communities = [
        GraphCommunity(
            community_id="kb_1::community::0",
            knowledge_id="kb_1",
            level=0,
            entities=["付款期限", "违约责任", "解除合同"],
            relation_count=2,
            supporting_chunks=["c1", "c2", "c3"],
            relations=[
                {"source": "付款期限", "target": "违约责任", "relation_type": "triggers"},
            ],
            report="该社区主要讨论付款期限、违约责任和解除合同。",
            community_version="v0",
        ),
        GraphCommunity(
            community_id="kb_1::community::1",
            knowledge_id="kb_1",
            level=0,
            entities=["保密义务", "数据删除"],
            relation_count=1,
            supporting_chunks=["c4"],
            relations=[
                {"source": "保密义务", "target": "数据删除", "relation_type": "requires"},
            ],
            report="该社区主要讨论保密义务和数据删除。",
            community_version="v0",
        ),
    ]

    result = service.search_reports("这批合同整体有哪些违约风险", communities, limit=1)

    assert result["used_communities"] == ["kb_1::community::0"]
    assert result["supporting_chunks"] == ["c1", "c2", "c3"]
    assert "community_trace" in result
    assert result["reports"][0]["community_id"] == "kb_1::community::0"


def test_phase3_knowledge_service_marks_community_state_stale(monkeypatch):
    from zuno.api.services.knowledge import KnowledgeService

    captured = {}

    async def fake_select_user_by_id(knowledge_id):
        return SimpleNamespace(
            to_dict=lambda: {
                "knowledge_config": {
                    "index_capability": "rag_graph",
                    "graph_index_settings": {
                        "community_detection_status": "ready",
                        "community_report_status": "ready",
                        "community_version": "v0",
                    },
                    "retrieval_settings": {"default_mode": "rag_graph"},
                },
                "default_retrieval_mode": "rag_graph",
            }
        )

    async def fake_update_knowledge_by_id(
        knowledge_id,
        knowledge_desc,
        knowledge_name,
        default_retrieval_mode=None,
        knowledge_config=None,
    ):
        captured["knowledge_id"] = knowledge_id
        captured["knowledge_config"] = knowledge_config

    monkeypatch.setattr("zuno.api.services.knowledge.KnowledgeDao.select_user_by_id", fake_select_user_by_id)
    monkeypatch.setattr("zuno.api.services.knowledge.KnowledgeDao.update_knowledge_by_id", fake_update_knowledge_by_id)

    asyncio.run(KnowledgeService.mark_community_stale("kb_1"))

    graph_settings = captured["knowledge_config"]["graph_index_settings"]
    assert captured["knowledge_id"] == "kb_1"
    assert graph_settings["community_detection_status"] == "stale"
    assert graph_settings["community_report_status"] == "stale"


def test_phase3_pipeline_marks_community_stale_after_graph_refresh(monkeypatch):
    from zuno.services.pipeline.manager import KnowledgePipelineManager

    captured = {"stale": 0}

    async def fake_load_task(task_id):
        return SimpleNamespace(
            id=task_id,
            knowledge_id="kb_1",
            knowledge_file_id="file_1",
            payload={},
            result_summary={},
        )

    async def fake_get_knowledge_config(knowledge_id):
        return {
            "index_capability": "rag_graph",
            "index_settings": {"status": "active"},
            "graph_index_settings": {"index_version": "v1"},
        }

    async def fake_get_runtime_settings(knowledge_id):
        return {"domain_pack": None, "domain_pack_id": None}

    async def fake_parse_chunks(task):
        return []

    async def fake_record_stage(*args, **kwargs):
        return None

    async def fake_mark_community_stale(knowledge_id):
        captured["stale"] += 1

    async def fake_mark_task_finished(*args, **kwargs):
        return None

    async def fake_create_task_event(*args, **kwargs):
        return None

    async def fake_update_pipeline_fields(*args, **kwargs):
        return None

    monkeypatch.setattr(KnowledgePipelineManager, "_load_task", staticmethod(fake_load_task))
    monkeypatch.setattr(KnowledgePipelineManager, "_parse_chunks", staticmethod(fake_parse_chunks))
    monkeypatch.setattr(KnowledgePipelineManager, "_record_stage", staticmethod(fake_record_stage))
    monkeypatch.setattr("zuno.services.pipeline.manager.KnowledgeService.get_knowledge_config", fake_get_knowledge_config)
    monkeypatch.setattr("zuno.services.pipeline.manager.KnowledgeService.get_runtime_settings", fake_get_runtime_settings)
    monkeypatch.setattr("zuno.services.pipeline.manager.KnowledgeService.mark_community_stale", fake_mark_community_stale)
    monkeypatch.setattr("zuno.services.pipeline.manager.KnowledgeTaskDao.mark_task_finished", fake_mark_task_finished)
    monkeypatch.setattr("zuno.services.pipeline.manager.KnowledgeTaskDao.create_task_event", fake_create_task_event)
    monkeypatch.setattr("zuno.services.pipeline.manager.KnowledgeFileDao.update_pipeline_fields", fake_update_pipeline_fields)
    monkeypatch.setattr("zuno.services.pipeline.manager.Neo4jClient.is_enabled", classmethod(lambda cls: False))

    manager = KnowledgePipelineManager(enable_graph_indexing=True, enable_elasticsearch=False)
    asyncio.run(manager.run_graph_stage("task_1"))

    assert captured["stale"] == 1

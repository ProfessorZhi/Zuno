import asyncio

from zuno.services.retrieval.models import ProcessedQuery, RetrievalRequest
from zuno.services.retrieval.orchestrator import RetrievalOrchestrator
from zuno.services.retrieval.planner import RetrievalPlanner


def _processed(
    query: str,
    *,
    global_question: bool = False,
    evidence_required: bool = False,
):
    return ProcessedQuery(
        original_query=query,
        normalized_query=query,
        rewritten_queries=[query],
        intent_labels=[],
        query_features={
            "relation_question": False,
            "global_question": global_question,
            "evidence_required": evidence_required,
        },
        route_hints=[],
    )


class _FakeRetriever:
    def __init__(self, payload):
        self.payload = payload

    async def retrieve(self, query, knowledge_ids, options=None):
        return self.payload


class _FakeExpander:
    async def expand(self, query: str):
        return [query]


class _FakeCommunityService:
    def __init__(self):
        self.calls = []

    async def load_communities(self, knowledge_id, *, status=None, community_version=None):
        self.calls.append(("load", knowledge_id, status, community_version))
        return [
            {
                "community_id": "kb_1::community::0",
                "knowledge_id": "kb_1",
                "level": 0,
                "entities": ["付款期限", "违约责任", "解除合同"],
                "relation_count": 2,
                "supporting_chunks": ["c1", "c2", "c3"],
                "report": "该社区主要讨论付款期限、违约责任和解除合同。",
                "community_version": "v0",
            },
            {
                "community_id": "kb_1::community::1",
                "knowledge_id": "kb_1",
                "level": 0,
                "entities": ["保密义务", "数据删除"],
                "relation_count": 1,
                "supporting_chunks": ["c4"],
                "report": "该社区主要讨论保密义务和数据删除。",
                "community_version": "v0",
            },
        ]

    def search_reports(self, query, communities, *, limit=3):
        self.calls.append(("search", query, limit))
        return {
            "reports": [communities[0]],
            "used_communities": ["kb_1::community::0"],
            "supporting_chunks": ["c1", "c2", "c3"],
            "community_trace": {
                "query": query,
                "selected_count": 1,
                "community_version": "v0",
            },
        }

    def build_global_answer(self, query, report_payload):
        self.calls.append(("global", query))
        return {
            "content": "全局总结：付款风险集中在期限、违约责任与解除合同。",
            "map_results": [
                {
                    "community_id": "kb_1::community::0",
                    "answer": "社区 0 主要是付款与违约责任。",
                }
            ],
            "reduce_trace": {
                "combined": 1,
                "strategy": "single_reduce",
            },
        }

    def build_drift_plan(self, query, report_payload):
        self.calls.append(("drift", query))
        return {
            "broad_answer": "先看整体风险，付款与违约责任最突出。",
            "follow_up_questions": [
                "付款期限如何触发违约责任？",
            ],
            "used_communities": report_payload["used_communities"],
        }


class _GlobalQueryProcessor:
    async def process(self, query: str):
        return _processed(query, global_question=True)


class _DriftQueryProcessor:
    async def process(self, query: str):
        return _processed(query, global_question=True, evidence_required=True)


def test_phase4_planner_routes_global_plus_evidence_to_drift_like_when_community_ready():
    planner = RetrievalPlanner(enable_keyword_recall=True)

    plan = planner.build_plan(
        RetrievalRequest(
            query="这批合同整体有哪些风险 并给出条款依据",
            knowledge_ids=["kb_1"],
            mode="rag_graph",
            index_health={"graph": "ready", "community": "ready"},
        ),
        _processed("这批合同整体有哪些风险 并给出条款依据", global_question=True, evidence_required=True),
        knowledge_capability="rag_graph",
    )

    assert plan.resolved_mode == "rag_graph_deep"
    assert plan.internal_route == "drift_like"


def test_phase4_orchestrator_runs_community_global_and_emits_map_reduce_trace():
    orchestrator = RetrievalOrchestrator(
        rag_retriever=_FakeRetriever({"content": "", "raw_content": "", "documents": [], "document_count": 0}),
        keyword_retriever=_FakeRetriever({"content": "", "raw_content": "", "documents": []}),
        graph_retriever=_FakeRetriever({"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}),
        query_expander=_FakeExpander(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        query_processor=_GlobalQueryProcessor(),
        community_service=_FakeCommunityService(),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="rag_graph",
            query="这批合同整体有哪些高频风险",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "ready"},
                "trace_policy": {"enabled": True},
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert result["content"].startswith("全局总结")
    assert metadata["internal_route"] == "community_global"
    assert metadata["used_communities"] == ["kb_1::community::0"]
    assert metadata["supporting_chunks"] == ["c1", "c2", "c3"]
    assert metadata["map_results"][0]["community_id"] == "kb_1::community::0"
    assert metadata["reduce_trace"]["strategy"] == "single_reduce"


def test_phase4_orchestrator_runs_single_round_drift_like_and_emits_drift_trace():
    graph_payload = {
        "content": "条款证据：付款期限逾期会触发违约责任。",
        "raw_content": "条款证据：付款期限逾期会触发违约责任。",
        "documents": [
            {
                "chunk_id": "c1",
                "knowledge_id": "kb_1",
                "file_id": "f1",
                "file_name": "contract.md",
                "content": "付款期限逾期会触发违约责任。",
                "score": 0.91,
            }
        ],
        "entities": ["付款期限", "违约责任"],
        "paths": ["付款期限 -> 违约责任"],
        "structured_paths": [{"source": "付款期限", "target": "违约责任"}],
    }

    orchestrator = RetrievalOrchestrator(
        rag_retriever=_FakeRetriever({"content": "", "raw_content": "", "documents": [], "document_count": 0}),
        keyword_retriever=_FakeRetriever({"content": "", "raw_content": "", "documents": []}),
        graph_retriever=_FakeRetriever(graph_payload),
        query_expander=_FakeExpander(),
        planner=RetrievalPlanner(enable_keyword_recall=True),
        query_processor=_DriftQueryProcessor(),
        community_service=_FakeCommunityService(),
    )

    result = asyncio.run(
        orchestrator.run(
            mode="rag_graph",
            query="这批合同整体有哪些风险 并给出条款依据",
            knowledge_ids=["kb_1"],
            retrieval_options={
                "knowledge_capability": "rag_graph",
                "index_health": {"graph": "ready", "community": "ready"},
                "trace_policy": {"enabled": True},
                "top_k": 5,
            },
        )
    )

    metadata = result["metadata"]

    assert metadata["internal_route"] == "drift_like"
    assert metadata["follow_up_questions"] == ["付款期限如何触发违约责任？"]
    assert metadata["used_communities"] == ["kb_1::community::0"]
    assert metadata["used_paths"] == ["付款期限 -> 违约责任"]
    assert metadata["drift_trace"]["follow_up_count"] == 1
    assert "条款证据" in result["content"]

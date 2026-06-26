import asyncio
from types import SimpleNamespace


def test_graph_retriever_adapter_does_not_fallback_to_runtime_domain_pack_id(monkeypatch):
    from zuno.services.retrieval.retrievers import GraphRetrieverAdapter

    captured = {}

    async def fake_runtime_settings(_knowledge_id):
        return {"domain_pack_id": "contract_review"}

    class FakeRetriever:
        async def retrieve(self, query, knowledge_id, **kwargs):
            captured["query"] = query
            captured["knowledge_id"] = knowledge_id
            captured["kwargs"] = kwargs
            return {
                "content": "",
                "documents": [],
                "graphrag_project_id": kwargs.get("graphrag_project_id"),
                "domain_pack_id": kwargs.get("domain_pack_id"),
            }

    monkeypatch.setattr(
        "zuno.services.retrieval.retrievers.KnowledgeService.get_runtime_settings",
        fake_runtime_settings,
    )

    adapter = GraphRetrieverAdapter(retriever=FakeRetriever())
    result = asyncio.run(adapter.retrieve("find termination clause", ["kb_1"], {"graph_hop_limit": 3}))

    assert captured["knowledge_id"] == "kb_1"
    assert captured["kwargs"]["graph_hop_limit"] == 3
    assert captured["kwargs"]["domain_pack_id"] is None
    assert result["domain_pack_id"] is None


def test_graph_retriever_adapter_uses_project_payload_runtime_settings(monkeypatch):
    from zuno.services.retrieval.retrievers import GraphRetrieverAdapter

    captured = {}

    async def fake_runtime_settings(_knowledge_id):
        return {
            "project_payload": {
                "id": "contract_review",
                "retrieval_policy_data": {"graph_hop_limit": 4},
            },
        }

    class FakeRetriever:
        async def retrieve(self, query, knowledge_id, **kwargs):
            captured["query"] = query
            captured["knowledge_id"] = knowledge_id
            captured["kwargs"] = kwargs
            return {
                "content": "",
                "documents": [],
                "graphrag_project_id": kwargs.get("graphrag_project_id"),
                "domain_pack_id": kwargs.get("domain_pack_id"),
            }

    monkeypatch.setattr(
        "zuno.services.retrieval.retrievers.KnowledgeService.get_runtime_settings",
        fake_runtime_settings,
    )

    adapter = GraphRetrieverAdapter(retriever=FakeRetriever())
    result = asyncio.run(adapter.retrieve("find termination clause", ["kb_1"], {}))

    assert captured["knowledge_id"] == "kb_1"
    assert captured["kwargs"]["graphrag_project_id"] == "contract_review"
    assert captured["kwargs"]["domain_pack_id"] is None
    assert captured["kwargs"]["query_policy"]["graph_hop_limit"] == 4
    assert result["graphrag_project_id"] == "contract_review"
    assert result["domain_pack_id"] is None


def test_retrieval_orchestrator_prefers_explicit_knowledge_capability():
    from zuno.services.retrieval.models import ProcessedQuery
    from zuno.services.retrieval.orchestrator import RetrievalOrchestrator

    class FakePlanner:
        def __init__(self):
            self.last_capability = None

        def build_plan(
            self,
            request,
            processed_query,
            knowledge_capability=None,
            rerank_available=None,
        ):
            self.last_capability = knowledge_capability
            return SimpleNamespace(
                enabled_retrievers=[],
                resolved_mode=request.mode,
                internal_route="standard_rag",
                to_dict=lambda: {
                    "requested_mode": request.mode,
                    "resolved_mode": request.mode,
                    "internal_route": "standard_rag",
                    "requested_profile": "auto",
                    "resolved_profile": "auto",
                    "enabled_retrievers": [],
                    "route_trace": {},
                    "budget_policy": {},
                    "fallback_policy": {},
                    "trace_policy": {},
                    "scope_policy": {},
                    "index_version": {},
                    "index_health": {},
                    "rerank_policy": {},
                },
            )

    class FakeProcessor:
        async def process(self, query):
            return ProcessedQuery(
                original_query=query,
                normalized_query=query,
                rewritten_queries=[query],
                intent_labels=[],
                query_features={},
                route_hints=[],
            )

    planner = FakePlanner()
    orchestrator = RetrievalOrchestrator(planner=planner, query_processor=FakeProcessor())

    result = asyncio.run(
        orchestrator.run(
            mode="rag",
            query="contract risk",
            knowledge_ids=["kb_1"],
            retrieval_options={"knowledge_capability": "rag", "needs_query_rewrite": False},
        )
    )

    assert planner.last_capability == "rag"
    assert result["metadata"]["retrieval_options"]["knowledge_capability"] == "rag"


def test_agent_table_accepts_domain_pack_id():
    from zuno.database.models.agent import AgentTable

    agent = AgentTable(
        name="contract agent",
        system_prompt="review contracts",
        llm_id="llm_1",
        domain_pack_id="contract_review",
    )

    assert agent.domain_pack_id == "contract_review"

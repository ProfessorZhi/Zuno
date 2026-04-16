import asyncio
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src" / "backend"))


def test_retrieval_modes_include_graphrag():
    from agentchat.services.graphrag.models import RETRIEVAL_MODES

    assert "rag" in RETRIEVAL_MODES
    assert "graphrag" in RETRIEVAL_MODES
    assert "hybrid" in RETRIEVAL_MODES
    assert "auto" in RETRIEVAL_MODES


def test_retrieval_orchestrator_combines_rag_and_graph_results():
    from agentchat.services.graphrag.orchestrator import RetrievalOrchestrator

    class FakeRagRetriever:
        async def retrieve(self, query: str, knowledge_ids: list[str]):
            return {"content": "rag-context", "documents": ["rag-context"]}

    class FakeGraphRetriever:
        async def retrieve(self, query: str, knowledge_id: str):
            return {"content": "graph-context", "entities": ["EntityA"], "paths": ["EntityA->EntityB"]}

    async def run_test():
        orchestrator = RetrievalOrchestrator(
            rag_retriever=FakeRagRetriever(),
            graph_retriever=FakeGraphRetriever(),
        )
        result = await orchestrator.run(
            mode="hybrid",
            query="EntityA 和 EntityB 有什么关系？",
            knowledge_ids=["k_1"],
        )
        assert result["actual_mode"] == "hybrid"
        assert "rag-context" in result["content"]
        assert "graph-context" in result["content"]
        assert result["graph_result"]["entities"] == ["EntityA"]

    asyncio.run(run_test())

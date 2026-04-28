import asyncio


class _FakeRagRetriever:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    async def retrieve(self, query: str, knowledge_ids: list[str]):
        self.calls.append((query, tuple(knowledge_ids)))
        if self._responses:
            return self._responses.pop(0)
        return {
            "content": "",
            "raw_content": "",
            "documents": [],
            "document_count": 0,
            "requested_top_k": 5,
            "top_score": None,
            "score_threshold": 0.4,
        }


class _FakeGraphRetriever:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    async def retrieve(self, query: str, knowledge_id: str):
        self.calls.append((query, knowledge_id))
        if self._responses:
            return self._responses.pop(0)
        return {
            "content": "",
            "raw_content": "",
            "entities": [],
            "paths": [],
        }


class _FakeQueryExpander:
    def __init__(self, variations):
        self.variations = variations
        self.calls = []

    async def expand(self, query: str) -> list[str]:
        self.calls.append(query)
        return list(self.variations)


def _rag_result(content: str, document_count: int, *, top_score: float | None = 0.91):
    return {
        "content": content,
        "raw_content": content,
        "documents": [{"page_content": content}] if content else [],
        "document_count": document_count,
        "requested_top_k": 5,
        "top_score": top_score,
        "score_threshold": 0.4,
    }


def _graph_result(content: str = "", *, entities=None, paths=None):
    return {
        "content": content,
        "raw_content": content,
        "entities": entities or [],
        "paths": paths or [],
    }


def test_retrieval_orchestrator_broadens_to_hybrid_when_rag_is_too_weak():
    from agentchat.services.graphrag.orchestrator import RetrievalOrchestrator

    rag = _FakeRagRetriever(
        [
            _rag_result("too weak", 1, top_score=0.2),
            _rag_result("stronger hybrid result", 3, top_score=0.92),
        ]
    )
    graph = _FakeGraphRetriever([_graph_result("graph evidence", entities=[{"id": "e1"}], paths=[{"id": "p1"}])])
    expander = _FakeQueryExpander(["how refund works"])

    orchestrator = RetrievalOrchestrator(
        rag_retriever=rag,
        graph_retriever=graph,
        query_expander=expander,
    )

    result = asyncio.run(orchestrator.run("rag", "how refund works", ["kb_1"]))

    assert result["first_mode"] == "rag"
    assert result["final_mode"] == "hybrid"
    assert result["second_pass_used"] is True
    assert result["fallback_reason"] == "too_few_documents"
    assert result["round_count"] == 2
    assert result["metadata"]["rounds"][1]["trigger"] == "route_broadening"
    assert "stronger hybrid result" in result["content"]
    assert "graph evidence" in result["content"]


def test_retrieval_orchestrator_uses_rewritten_query_on_third_round_when_needed():
    from agentchat.services.graphrag.orchestrator import RetrievalOrchestrator

    rag = _FakeRagRetriever(
        [
            _rag_result("", 0, top_score=None),
            _rag_result("", 0, top_score=None),
            _rag_result("rewritten query hit", 4, top_score=0.95),
        ]
    )
    graph = _FakeGraphRetriever(
        [
            _graph_result(),
            _graph_result(),
        ]
    )
    expander = _FakeQueryExpander(["invoice policy", "invoice reimbursement policy"])

    orchestrator = RetrievalOrchestrator(
        rag_retriever=rag,
        graph_retriever=graph,
        query_expander=expander,
        max_rounds=3,
    )

    result = asyncio.run(orchestrator.run("rag", "invoice policy", ["kb_1"]))

    assert result["first_mode"] == "rag"
    assert result["final_mode"] == "hybrid"
    assert result["round_count"] == 3
    assert result["second_pass_used"] is True
    assert result["metadata"]["rewritten_query_used"] is True
    assert result["metadata"]["query_variants"] == ["invoice policy", "invoice reimbursement policy"]
    assert [item["trigger"] for item in result["metadata"]["rounds"]] == [
        "initial",
        "route_broadening",
        "query_rewrite_retry",
    ]
    assert result["metadata"]["rounds"][-1]["query"] == "invoice reimbursement policy"
    assert result["content"] == "rewritten query hit"

from __future__ import annotations

import asyncio

from zuno.api.services.knowledge import KnowledgeService
from zuno.api.services import knowledge as knowledge_service_module


class _Result:
    graphrag_project_id = "graph:one"
    answer = "answer"
    requested_query_method = "auto"
    resolved_query_method = "basic"
    fallback_reason = None
    documents = []
    evidence = {}
    citations = []
    retrievers_used = ["BM25", "VECTOR"]
    graph_paths = []
    communities = []
    prompt_version = "default"
    query_prompt_version = "default"
    index_version = {}
    community_version = "v0"
    trace_metadata = {}

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "requested_query_method": self.requested_query_method,
            "resolved_query_method": self.resolved_query_method,
            "fallback_reason": self.fallback_reason,
            "documents": self.documents,
            "evidence": self.evidence,
            "citations": self.citations,
            "retrievers_used": self.retrievers_used,
            "graph_paths": self.graph_paths,
            "communities": self.communities,
            "trace_metadata": self.trace_metadata,
        }


class _PartialNoResult(_Result):
    retrievers_used = ["BM25"]


def test_goal03_knowledge_search_records_query_run(monkeypatch) -> None:
    recorded: list[dict] = []

    class _QueryService:
        async def query(self, **kwargs):
            assert kwargs["knowledge_ids"] == ["knowledge-a"]
            return _Result()

    monkeypatch.setattr(
        "zuno.services.application.knowledge.KnowledgeQueryService",
        _QueryService,
    )
    monkeypatch.setattr(
        KnowledgeService,
        "record_search_query_run",
        staticmethod(lambda **kwargs: recorded.append(kwargs)),
    )

    payload = asyncio.run(
        KnowledgeService.search_knowledge(
            user_id="principal-a",
            knowledge_ids=["knowledge-a"],
            query="renewal",
            product_mode="auto",
            query_method=None,
            top_k=5,
        )
    )

    assert payload["content"] == "answer"
    assert recorded[0]["knowledge_ids"] == ["knowledge-a"]
    assert recorded[0]["result"].retrievers_used == ["BM25", "VECTOR"]


def test_goal03_knowledge_record_requires_active_snapshot() -> None:
    source = (
        __import__("pathlib").Path("src/backend/zuno/api/services/knowledge.py").read_text(encoding="utf-8")
    )
    assert "active_snapshot_id" in source
    assert "requires an ACTIVE Knowledge Snapshot" in source
    assert "start_query_run" in source
    assert "start_retrieval_round" in source


def test_goal03_knowledge_search_requires_active_snapshot_and_records_run(monkeypatch) -> None:
    class _QueryService:
        async def query(self, **kwargs):
            assert kwargs["knowledge_ids"] == ["knowledge-a"]
            return _Result()

    class _Repo:
        def active_snapshot_id(self, **kwargs):
            assert kwargs == {
                "tenant_id": "user:principal-a",
                "knowledge_space_id": "knowledge-a",
            }
            return "snapshot-a"

        def start_query_run(self, **kwargs):
            assert kwargs["snapshot_id"] == "snapshot-a"
            assert kwargs["request_payload"]["strict_grounding"] is True
            assert kwargs["request_payload"]["retrievers_expected"] == ["bm25", "vector"]
            assert kwargs["request_payload"]["retrievers_used"] == ["bm25", "vector"]
            assert kwargs["request_payload"]["retriever_availability"] == {
                "bm25": "used",
                "vector": "used",
            }
            assert kwargs["request_payload"]["partial_retrieval"] is False
            assert kwargs["request_payload"]["no_result"] is True
            assert kwargs["request_payload"]["retrieval_semantics"] == "no_result"

        def start_retrieval_round(self, **kwargs):
            assert kwargs["status"] == "COMPLETED"
            assert kwargs["retriever_set"]["retrieval_semantics"] == "no_result"

        def mark_query_run_status(self, **kwargs):
            assert kwargs["status"] == "PARTIAL_EVIDENCE"

    class _Uow:
        def __enter__(self):
            return _Repo()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        "zuno.services.application.knowledge.KnowledgeQueryService",
        _QueryService,
    )
    monkeypatch.setattr(knowledge_service_module, "KnowledgeUnitOfWork", lambda engine: _Uow())

    payload = asyncio.run(
        KnowledgeService.search_knowledge(
            user_id="principal-a",
            knowledge_ids=["knowledge-a"],
            query="renewal",
            product_mode="auto",
            query_method=None,
            top_k=5,
        )
    )

    assert payload["query_run_persistence"] == {"status": "recorded"}
    assert payload["content"] == "answer"


def test_goal03_knowledge_query_run_records_partial_no_result_semantics(monkeypatch) -> None:
    class _QueryService:
        async def query(self, **kwargs):
            assert kwargs["knowledge_ids"] == ["knowledge-a"]
            return _PartialNoResult()

    class _Repo:
        def active_snapshot_id(self, **kwargs):
            return "snapshot-a"

        def start_query_run(self, **kwargs):
            payload = kwargs["request_payload"]
            assert payload["retrievers_expected"] == ["bm25", "vector"]
            assert payload["retrievers_used"] == ["bm25"]
            assert payload["retriever_availability"] == {
                "bm25": "used",
                "vector": "missing",
            }
            assert payload["partial_retrieval"] is True
            assert payload["no_result"] is True
            assert payload["retrieval_semantics"] == "partial_no_result"

        def start_retrieval_round(self, **kwargs):
            retriever_set = kwargs["retriever_set"]
            assert retriever_set["retriever_availability"]["vector"] == "missing"
            assert retriever_set["partial_retrieval"] is True
            assert retriever_set["no_result"] is True
            assert retriever_set["retrieval_semantics"] == "partial_no_result"
            assert kwargs["status"] == "COMPLETED"

        def mark_query_run_status(self, **kwargs):
            assert kwargs["status"] == "PARTIAL_EVIDENCE"

    class _Uow:
        def __enter__(self):
            return _Repo()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        "zuno.services.application.knowledge.KnowledgeQueryService",
        _QueryService,
    )
    monkeypatch.setattr(knowledge_service_module, "KnowledgeUnitOfWork", lambda engine: _Uow())

    payload = asyncio.run(
        KnowledgeService.search_knowledge(
            user_id="principal-a",
            knowledge_ids=["knowledge-a"],
            query="renewal",
            product_mode="auto",
            query_method=None,
            top_k=5,
        )
    )

    assert payload["query_run_persistence"] == {"status": "recorded"}
    assert payload["content"] == "answer"


def test_goal03_knowledge_search_blocks_without_active_snapshot(monkeypatch) -> None:
    class _QueryService:
        async def query(self, **kwargs):
            return _Result()

    class _Repo:
        def active_snapshot_id(self, **kwargs):
            return None

    class _Uow:
        def __enter__(self):
            return _Repo()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(
        "zuno.services.application.knowledge.KnowledgeQueryService",
        _QueryService,
    )
    monkeypatch.setattr(knowledge_service_module, "KnowledgeUnitOfWork", lambda engine: _Uow())

    payload = asyncio.run(
        KnowledgeService.search_knowledge(
            user_id="principal-a",
            knowledge_ids=["knowledge-a"],
            query="renewal",
            product_mode="auto",
            query_method=None,
            top_k=5,
        )
    )

    assert payload["query_run_persistence"]["status"] == "blocked"
    assert "requires an ACTIVE Knowledge Snapshot" in payload["query_run_persistence"]["reason"]


def test_goal03_knowledge_reindex_publishes_version_and_snapshot(monkeypatch) -> None:
    class _Knowledge:
        def to_dict(self) -> dict:
            return {
                "name": "knowledge-a",
                "user_id": "principal-a",
                "knowledge_config": {
                    "retrieval_settings": {"default_mode": "rag_graph"},
                    "index_capability": "rag_graph",
                },
                "default_retrieval_mode": "rag_graph",
            }

    class _File:
        def __init__(self, file_id: str) -> None:
            self.id = file_id
            self.file_name = "doc.txt"
            self.oss_url = "oss://bucket/doc.txt"
            self.status = "success"
            self.parse_status = "ready"
            self.rag_index_status = "ready"
            self.graph_index_status = "ready"
            self.file_size = 12

    calls: list[tuple[str, dict]] = []

    class _Repo:
        def next_version_no(self, **kwargs):
            calls.append(("next_version_no", kwargs))
            return 7

        def create_version(self, draft):
            calls.append(("create_version", draft))

        def append_chunk(self, **kwargs):
            calls.append(("append_chunk", kwargs))

        def record_index_visibility(self, **kwargs):
            calls.append(("record_index_visibility", kwargs))

        def mark_ready(self, **kwargs):
            calls.append(("mark_ready", kwargs))

        def create_snapshot(self, **kwargs):
            calls.append(("create_snapshot", kwargs))

        def next_cutover_expected_generation(self, **kwargs):
            calls.append(("next_cutover_expected_generation", kwargs))
            return 2

        def cutover(self, **kwargs):
            calls.append(("cutover", kwargs))

    class _Uow:
        def __enter__(self):
            return _Repo()

        def __exit__(self, exc_type, exc, tb):
            return False

    async def _select_user_by_id(knowledge_id: str):
        return _Knowledge()

    async def _select_knowledge_file(knowledge_id: str):
        return [_File("file-1")]

    monkeypatch.setattr(knowledge_service_module.KnowledgeDao, "select_user_by_id", staticmethod(_select_user_by_id))
    monkeypatch.setattr(knowledge_service_module.KnowledgeFileDao, "select_knowledge_file", staticmethod(_select_knowledge_file))
    monkeypatch.setattr(knowledge_service_module, "KnowledgeUnitOfWork", lambda engine: _Uow())

    result = asyncio.run(KnowledgeService.run_reindex_action("knowledge-a", "full_rebuild"))

    assert result["status"] == "published"
    assert any(name == "create_version" for name, _ in calls)
    assert any(name == "create_snapshot" for name, _ in calls)
    assert any(name == "cutover" for name, _ in calls)

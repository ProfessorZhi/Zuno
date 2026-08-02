import asyncio
import hashlib
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
for runtime_root in (str(BACKEND_ROOT),):
    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)


def _canonical_chunk(
    *,
    chunk_id: str,
    content: str,
    file_id: str = "file_1",
    file_name: str = "runtime.txt",
    update_time: str = "2026-06-10T10:00:00",
    knowledge_id: str = "k1",
    source_url: str = "oss://runtime.txt",
    source_chunk_id: str | None = None,
) -> dict:
    document_hash = hashlib.sha1(f"{knowledge_id}|{file_id}|{file_name}|{source_url}".encode("utf-8")).hexdigest()
    chunk_hash = hashlib.sha1(f"{document_hash}|{chunk_id}|{content}".encode("utf-8")).hexdigest()
    return {
        "chunk_id": chunk_id,
        "content": content,
        "file_id": file_id,
        "file_name": file_name,
        "update_time": update_time,
        "knowledge_id": knowledge_id,
        "source_url": source_url,
        "source_chunk_id": source_chunk_id or chunk_id,
        "document_hash": document_hash,
        "chunk_hash": chunk_hash,
    }


def test_graph_writer_attaches_runtime_metadata_fields():
    from zuno.platform.services.graphrag.graph_store.graph_writer import GraphWriter

    writer = GraphWriter()

    entity_payload = writer.build_entity_payload(
        {"name": "Redis", "knowledge_id": "k1"},
        domain_pack_id="ops",
        index_version="graph_v2",
        status="active",
    )
    relation_payload = writer.build_relation_payload(
        {"source": "Redis", "target": "PostgreSQL", "knowledge_id": "k1"},
        domain_pack_id="ops",
        index_version="graph_v2",
        status="active",
    )

    assert entity_payload["domain_pack_id"] == "ops"
    assert entity_payload["index_version"] == "graph_v2"
    assert entity_payload["status"] == "active"
    assert relation_payload["domain_pack_id"] == "ops"
    assert relation_payload["index_version"] == "graph_v2"
    assert relation_payload["status"] == "active"


def test_graph_writer_attaches_project_id_as_primary_graph_scope():
    from zuno.platform.services.graphrag.graph_store.graph_writer import GraphWriter

    writer = GraphWriter()

    entity_payload = writer.build_entity_payload(
        {"name": "Redis", "knowledge_id": "k1"},
        graphrag_project_id="ops",
    )
    relation_payload = writer.build_relation_payload(
        {"source": "Redis", "target": "PostgreSQL", "knowledge_id": "k1"},
        graphrag_project_id="ops",
    )

    assert entity_payload["graphrag_project_id"] == "ops"
    assert "domain_pack_id" not in entity_payload
    assert relation_payload["graphrag_project_id"] == "ops"
    assert "domain_pack_id" not in relation_payload


def test_neo4j_client_uses_project_id_property_as_primary_graph_scope():
    graph_client_content = (BACKEND_ROOT / "zuno/platform/services/graphrag/client.py").read_text(encoding="utf-8")

    assert "e.graphrag_project_id = $graphrag_project_id" in graph_client_content
    assert "r.graphrag_project_id = $graphrag_project_id" in graph_client_content
    assert "s.graphrag_project_id = COALESCE($graphrag_project_id, s.graphrag_project_id)" in graph_client_content
    assert "t.graphrag_project_id = COALESCE($graphrag_project_id, t.graphrag_project_id)" in graph_client_content
    assert "e.domain_pack_id = $domain_pack_id" not in graph_client_content
    assert "r.domain_pack_id = $domain_pack_id" not in graph_client_content


def test_graph_retriever_adapter_forwards_scope_status_and_graph_index_version(monkeypatch):
    from zuno.platform.services.retrieval.retrievers import GraphRetrieverAdapter, KnowledgeService

    captured = {}

    class FakeGraphRetriever:
        async def retrieve(self, query, knowledge_id, **kwargs):
            captured["query"] = query
            captured["knowledge_id"] = knowledge_id
            captured["kwargs"] = kwargs
            return {"content": "", "documents": []}

    async def fake_runtime_settings(_knowledge_id):
        return {
            "graph_retriever": FakeGraphRetriever(),
        }

    monkeypatch.setattr(KnowledgeService, "get_runtime_settings", staticmethod(fake_runtime_settings))

    asyncio.run(
        GraphRetrieverAdapter().retrieve(
            "Redis 和 PostgreSQL 的关系是什么",
            ["k1"],
            {
                "graph_hop_limit": 3,
                "max_paths_per_entity": 7,
                "domain_pack_id": "ops",
                "scope_policy": {"status": "archived"},
                "index_version": {"graph": "graph_v9"},
            },
        )
    )

    assert captured["query"] == "Redis 和 PostgreSQL 的关系是什么"
    assert captured["knowledge_id"] == "k1"
    assert captured["kwargs"]["graph_hop_limit"] == 3
    assert captured["kwargs"]["max_paths_per_entity"] == 7
    assert captured["kwargs"]["domain_pack_id"] == "ops"
    assert captured["kwargs"]["status"] == "archived"
    assert captured["kwargs"]["index_version"] == "graph_v9"


def test_graph_retriever_adapter_maps_project_scope_to_legacy_storage_filter(monkeypatch):
    from zuno.platform.services.retrieval.retrievers import GraphRetrieverAdapter, KnowledgeService

    captured = {}

    class FakeGraphRetriever:
        async def retrieve(self, query, knowledge_id, **kwargs):
            captured["query"] = query
            captured["knowledge_id"] = knowledge_id
            captured["kwargs"] = kwargs
            return {"content": "", "documents": []}

    async def fake_runtime_settings(_knowledge_id):
        return {
            "graph_retriever": FakeGraphRetriever(),
        }

    monkeypatch.setattr(KnowledgeService, "get_runtime_settings", staticmethod(fake_runtime_settings))

    asyncio.run(
        GraphRetrieverAdapter().retrieve(
            "Redis 和 PostgreSQL 的关系是什么",
            ["k1"],
            {
                "scope_policy": {
                    "graphrag_project_id": "ops",
                    "status": "active",
                },
            },
        )
    )

    assert captured["knowledge_id"] == "k1"
    assert captured["kwargs"]["graphrag_project_id"] == "ops"
    assert captured["kwargs"]["domain_pack_id"] is None
    assert captured["kwargs"]["status"] == "active"


def test_graph_retriever_passes_status_and_graph_index_version_to_client():
    from zuno.platform.services.graphrag.retriever import GraphRetriever

    captured = []

    class FakeClient:
        async def query_neighbors(self, entity_name, knowledge_id, **kwargs):
            captured.append(
                {
                    "entity_name": entity_name,
                    "knowledge_id": knowledge_id,
                    "kwargs": kwargs,
                }
            )
            return []

    class FakeChunkStore:
        async def get_documents_by_chunk_ids(self, knowledge_id, chunk_ids):
            return []

    retriever = GraphRetriever(client=FakeClient(), chunk_store=FakeChunkStore())

    result = asyncio.run(
        retriever.retrieve(
            "Redis 和 PostgreSQL 的关系是什么",
            "k1",
            graph_hop_limit=3,
            max_paths_per_entity=4,
            graphrag_project_id="ops",
            index_version="graph_v3",
            status="active",
        )
    )

    assert result["documents"] == []
    assert captured
    assert all(item["knowledge_id"] == "k1" for item in captured)
    assert all(item["kwargs"]["graphrag_project_id"] == "ops" for item in captured)
    assert all(item["kwargs"]["domain_pack_id"] is None for item in captured)
    assert all(item["kwargs"]["index_version"] == "graph_v3" for item in captured)
    assert all(item["kwargs"]["status"] == "active" for item in captured)


def test_graph_pipeline_passes_index_version_and_status_into_writer():
    content = (BACKEND_ROOT / "zuno/platform/services/pipeline/manager.py").read_text(encoding="utf-8")

    assert 'graph_index_version = str(knowledge_config.get("graph_index_settings", {}).get("index_version") or "v1")' in content
    assert 'graph_status = str(knowledge_config.get("index_settings", {}).get("status") or "active")' in content
    assert 'index_version=graph_index_version' in content
    assert 'status=graph_status' in content


def test_graph_writer_attaches_source_file_metadata():
    from zuno.platform.services.graphrag.graph_store.graph_writer import GraphWriter

    writer = GraphWriter()

    entity_payload = writer.build_entity_payload(
        {"name": "Redis", "knowledge_id": "k1", "chunk_id": "chunk_1"},
        knowledge_file_id="file_1",
    )
    relation_payload = writer.build_relation_payload(
        {"source": "Redis", "target": "PostgreSQL", "knowledge_id": "k1", "chunk_id": "chunk_1"},
        knowledge_file_id="file_1",
    )

    assert entity_payload["knowledge_file_id"] == "file_1"
    assert entity_payload["source_chunk_id"] == "chunk_1"
    assert relation_payload["knowledge_file_id"] == "file_1"
    assert relation_payload["source_chunk_id"] == "chunk_1"


def test_dynamic_reindex_pipeline_clears_old_file_documents_before_rebuild():
    manager_content = (BACKEND_ROOT / "zuno/platform/services/pipeline/manager.py").read_text(encoding="utf-8")
    knowledge_file_service_content = (BACKEND_ROOT / "zuno/api/services/knowledge_file.py").read_text(encoding="utf-8")
    rag_handler_content = (BACKEND_ROOT / "zuno/platform/services/rag/handler.py").read_text(encoding="utf-8")
    graph_client_content = (BACKEND_ROOT / "zuno/platform/services/graphrag/client.py").read_text(encoding="utf-8")

    assert "await RagHandler.delete_documents_by_file(task.knowledge_file_id, task.knowledge_id)" in manager_content
    assert "await RagHandler.delete_documents_by_file(knowledge_file.id, knowledge_file.knowledge_id)" in knowledge_file_service_content
    assert "async def delete_documents_by_file(cls, file_id, knowledge_id):" in rag_handler_content
    assert "await graph_client.delete_by_knowledge_file(file_id, knowledge_id)" in rag_handler_content
    assert "async def delete_by_knowledge_file(self, knowledge_file_id: str, knowledge_id: str):" in graph_client_content


def test_canonical_chunk_payload_exposes_document_hash_and_chunk_hash():
    chunk = _canonical_chunk(
        chunk_id="chunk_1",
        content="Redis stores ephemeral state.",
        file_id="file_1",
        file_name="runtime.txt",
        update_time="2026-06-10T10:00:00",
        knowledge_id="k1",
        source_url="oss://runtime.txt",
    )

    assert chunk["document_hash"]
    assert chunk["chunk_hash"]


def test_hash_fields_flow_through_vector_and_graph_runtime_contracts():
    vector_payload = (BACKEND_ROOT / "zuno/knowledge/ingestion/vector_payload.py").read_text(encoding="utf-8")
    search_schema = (BACKEND_ROOT / "zuno/api/dto/search.py").read_text(encoding="utf-8")
    milvus_client = (BACKEND_ROOT / "zuno/platform/services/rag/vector_db/milvus_lite_client.py").read_text(encoding="utf-8")
    es_index = (BACKEND_ROOT / "zuno/platform/config/es_index.py").read_text(encoding="utf-8")
    graph_writer = (BACKEND_ROOT / "zuno/platform/services/graphrag/graph_store/graph_writer.py").read_text(encoding="utf-8")
    graph_extractor = (BACKEND_ROOT / "zuno/platform/services/graphrag/extractor.py").read_text(encoding="utf-8")

    assert '"document_hash": document_hash' in vector_payload
    assert '"chunk_hash": chunk_hash' in vector_payload
    assert '"document_hash": self.document_hash' in search_schema
    assert '"chunk_hash": self.chunk_hash' in search_schema
    assert 'FieldSchema(name="document_hash", dtype=DataType.VARCHAR, max_length=128)' in milvus_client
    assert 'FieldSchema(name="chunk_hash", dtype=DataType.VARCHAR, max_length=128)' in milvus_client
    assert '"document_hash"' in es_index
    assert '"chunk_hash"' in es_index
    assert 'payload.setdefault("document_hash"' in graph_writer
    assert 'payload.setdefault("chunk_hash"' in graph_writer
    assert '"document_hash": chunk.get("document_hash")' in graph_extractor
    assert '"chunk_hash": chunk.get("chunk_hash")' in graph_extractor


def test_chunk_hash_is_deterministic_and_changes_with_content():
    base = dict(
        file_id="file_1",
        file_name="runtime.txt",
        update_time="2026-06-10T10:00:00",
        knowledge_id="k1",
        source_url="oss://runtime.txt",
    )

    chunk_a1 = _canonical_chunk(chunk_id="chunk_1", content="Redis stores state.", **base)
    chunk_a2 = _canonical_chunk(chunk_id="chunk_1", content="Redis stores state.", **base)
    chunk_b = _canonical_chunk(chunk_id="chunk_1", content="Redis stores ephemeral state.", **base)

    assert chunk_a1["document_hash"] == chunk_a2["document_hash"]
    assert chunk_a1["chunk_hash"] == chunk_a2["chunk_hash"]
    assert chunk_a1["document_hash"] == chunk_b["document_hash"]
    assert chunk_a1["chunk_hash"] != chunk_b["chunk_hash"]


def test_parse_gateway_vector_payloads_include_hash_identity():
    from zuno.knowledge.ingestion import ParseDocumentRequest, ParseGateway, canonical_ir_to_vector_payloads

    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = Path(tmp_dir) / "runtime.txt"
        file_path.write_text("Redis stores state.\nPostgreSQL stores records.\n", encoding="utf-8")
        result = ParseGateway.parse_document(
            ParseDocumentRequest(
                document_id="file_1",
                workspace_id="workspace_graph",
                source_uri=file_path.as_uri(),
                mime_type="text/plain",
            )
        )
        assert result.document is not None
        chunks = canonical_ir_to_vector_payloads(result.document, knowledge_id="k1", update_time="2026-08-02T00:00:00+00:00")

    assert chunks
    assert all(chunk["document_hash"] for chunk in chunks)
    assert all(chunk["chunk_hash"] for chunk in chunks)
    assert len({chunk["document_hash"] for chunk in chunks}) == 1
    assert len({chunk["chunk_hash"] for chunk in chunks}) == len(chunks)
    assert all(chunk["source_chunk_id"] for chunk in chunks)
    assert len({chunk["source_chunk_id"] for chunk in chunks}) == len(chunks)


def test_source_chunk_id_is_stable_when_content_changes():
    base = dict(
        file_id="file_1",
        file_name="runtime.txt",
        update_time="2026-06-10T10:00:00",
        knowledge_id="k1",
        source_url="oss://runtime.txt",
        source_chunk_id="file_1_chunk_0",
    )

    chunk_a = _canonical_chunk(chunk_id="chunk_old", content="Redis stores state.", **base)
    chunk_b = _canonical_chunk(chunk_id="chunk_new", content="Redis stores ephemeral state.", **base)

    assert chunk_a["source_chunk_id"] == chunk_b["source_chunk_id"]
    assert chunk_a["chunk_hash"] != chunk_b["chunk_hash"]


def test_chunk_level_graph_refresh_contract_is_present():
    manager_content = (BACKEND_ROOT / "zuno/platform/services/pipeline/manager.py").read_text(encoding="utf-8")
    graph_client_content = (BACKEND_ROOT / "zuno/platform/services/graphrag/client.py").read_text(encoding="utf-8")
    graph_writer_content = (BACKEND_ROOT / "zuno/platform/services/graphrag/graph_store/graph_writer.py").read_text(encoding="utf-8")
    graph_extractor_content = (BACKEND_ROOT / "zuno/platform/services/graphrag/extractor.py").read_text(encoding="utf-8")
    vector_payload_content = (BACKEND_ROOT / "zuno/knowledge/ingestion/vector_payload.py").read_text(encoding="utf-8")

    assert "await client.delete_by_source_chunk(task.knowledge_file_id, task.knowledge_id, source_chunk_id)" in manager_content
    assert "async def delete_by_source_chunk(self, knowledge_file_id: str, knowledge_id: str, source_chunk_id: str):" in graph_client_content
    assert 'payload.setdefault("source_chunk_id", source_chunk_id)' in graph_writer_content
    assert '"source_chunk_id": chunk.get("source_chunk_id")' in graph_extractor_content
    assert '"source_chunk_id": metadata.get("source_span", {}).get("chunk_id") or chunk_id' in vector_payload_content

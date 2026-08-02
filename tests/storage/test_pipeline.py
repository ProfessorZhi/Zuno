import asyncio
from pathlib import Path
from types import SimpleNamespace
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api" / "src"))


def test_pipeline_stage_flow():
    from zuno.platform.services.pipeline.models import PIPELINE_STAGES

    assert PIPELINE_STAGES[0] == "uploaded"
    assert PIPELINE_STAGES[-1] == "completed"
    assert "rag_indexing" in PIPELINE_STAGES
    assert "graph_indexing" in PIPELINE_STAGES


def test_pipeline_manager_updates_task_and_file_state(monkeypatch, tmp_path):
    from zuno.platform.services.pipeline.manager import KnowledgePipelineManager
    from zuno.platform.services.pipeline.models import (
        KnowledgeTaskStage,
        KnowledgeTaskStatus,
    )

    task = SimpleNamespace(
        id="task_1",
        knowledge_id="k_1",
        knowledge_file_id="f_1",
        task_type="ingest",
        status=KnowledgeTaskStatus.pending,
        current_stage=KnowledgeTaskStage.uploaded,
        retry_count=0,
        error_message=None,
    )

    task_updates = []
    task_events = []
    file_updates = []

    async def fake_select_task_by_id(task_id):
        assert task_id == "task_1"
        return task

    async def fake_update_task(task_id, **kwargs):
        task_updates.append((task_id, kwargs))
        for key, value in kwargs.items():
            setattr(task, key, value)

    async def fake_create_task_event(task_id, stage, status, message, detail=None):
        task_events.append((task_id, stage, status, message, detail))

    async def fake_update_pipeline_fields(knowledge_file_id, **kwargs):
        file_updates.append((knowledge_file_id, kwargs))

    source = tmp_path / "demo.txt"
    source.write_text("hello from canonical parse stage", encoding="utf-8")

    async def fake_index_milvus_documents(
        knowledge_id,
        chunks,
        text_embedding_config=None,
        vl_embedding_config=None,
    ):
        assert knowledge_id == "k_1"
        assert len(chunks) == 1
        assert text_embedding_config is None
        assert vl_embedding_config is None

    async def fake_index_es_documents(knowledge_id, chunks):
        assert knowledge_id == "k_1"
        assert len(chunks) == 1

    async def fake_delete_documents_by_file(file_id, knowledge_id):
        assert file_id == "f_1"
        assert knowledge_id == "k_1"

    async def fake_get_knowledge_config(knowledge_id):
        assert knowledge_id == "k_1"
        return {"index_capability": "rag"}

    async def fake_get_runtime_settings(knowledge_id):
        assert knowledge_id == "k_1"
        return {}

    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_task.KnowledgeTaskDao.select_task_by_id",
        fake_select_task_by_id,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_task.KnowledgeTaskDao.update_task",
        fake_update_task,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_task.KnowledgeTaskDao.create_task_event",
        fake_create_task_event,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_file.KnowledgeFileDao.update_pipeline_fields",
        fake_update_pipeline_fields,
    )
    monkeypatch.setattr(
        "zuno.platform.services.rag.handler.RagHandler.index_milvus_documents",
        fake_index_milvus_documents,
    )
    monkeypatch.setattr(
        "zuno.platform.services.rag.handler.RagHandler.delete_documents_by_file",
        fake_delete_documents_by_file,
    )
    monkeypatch.setattr(
        "zuno.platform.services.rag.handler.RagHandler.index_es_documents",
        fake_index_es_documents,
    )
    monkeypatch.setattr(
        "zuno.api.services.knowledge.KnowledgeService.get_knowledge_config",
        fake_get_knowledge_config,
    )
    monkeypatch.setattr(
        "zuno.api.services.knowledge.KnowledgeService.get_runtime_settings",
        fake_get_runtime_settings,
    )

    asyncio.run(
        KnowledgePipelineManager(enable_graph_indexing=True, enable_elasticsearch=True).run_sync(
            "task_1",
            file_path=str(source),
        )
    )

    assert task.status == KnowledgeTaskStatus.success
    assert task.current_stage == KnowledgeTaskStage.completed
    assert any(event[1] == KnowledgeTaskStage.parsing for event in task_events)
    assert any(event[1] == KnowledgeTaskStage.rag_indexing for event in task_events)
    assert any(event[1] == KnowledgeTaskStage.completed for event in task_events)
    assert any(update[1].get("parse_status") == "success" for update in file_updates)
    assert any(update[1].get("rag_index_status") == "success" for update in file_updates)
    assert any(update[1].get("graph_index_status") == "success" for update in file_updates)


def test_pipeline_parse_stage_uses_canonical_ir_without_chunk_projection(monkeypatch, tmp_path):
    from zuno.platform.services.pipeline.manager import KnowledgePipelineManager
    from zuno.platform.services.pipeline.models import (
        KnowledgeTaskStage,
        KnowledgeTaskStatus,
    )

    source = tmp_path / "policy.md"
    source.write_text("# Policy\nRenewal notice is required.", encoding="utf-8")
    task = SimpleNamespace(
        id="task_parse",
        knowledge_id="k_parse",
        knowledge_file_id="f_parse",
        task_type="ingest",
        payload={"file_path": str(source), "file_name": "policy.md"},
        result_summary={},
    )
    task_updates = []
    task_events = []

    async def fake_select_task_by_id(task_id):
        assert task_id == "task_parse"
        return task

    async def fake_update_task(task_id, **kwargs):
        task_updates.append((task_id, kwargs))
        for key, value in kwargs.items():
            setattr(task, key, value)

    async def fake_create_task_event(task_id, stage, status, message, detail=None):
        task_events.append((task_id, stage, status, message, detail or {}))

    async def fake_update_pipeline_fields(_knowledge_file_id, **_kwargs):
        return None

    async def fake_get_knowledge_config(knowledge_id):
        assert knowledge_id == "k_parse"
        return {"index_capability": "rag"}

    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_task.KnowledgeTaskDao.select_task_by_id",
        fake_select_task_by_id,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_task.KnowledgeTaskDao.update_task",
        fake_update_task,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_task.KnowledgeTaskDao.create_task_event",
        fake_create_task_event,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_file.KnowledgeFileDao.update_pipeline_fields",
        fake_update_pipeline_fields,
    )
    monkeypatch.setattr(
        "zuno.api.services.knowledge.KnowledgeService.get_knowledge_config",
        fake_get_knowledge_config,
    )

    asyncio.run(KnowledgePipelineManager().run_parse_stage("task_parse"))

    parsing_completed = [
        event
        for event in task_events
        if event[1] == KnowledgeTaskStage.parsing
        and event[2] == KnowledgeTaskStatus.running
        and event[3] == "parsing completed"
    ][0]
    assert parsing_completed[4]["projection"] == "canonical_document_ir_blocks"
    assert parsing_completed[4]["chunk_count"] >= 1
    assert any(
        update[1].get("result_summary", {}).get("chunk_count")
        == parsing_completed[4]["chunk_count"]
        for update in task_updates
    )
    import zuno.platform.services.pipeline.manager as pipeline_manager

    assert not hasattr(pipeline_manager, "parse_file_into_chunk_model_projection")


def test_pipeline_graph_stage_passes_project_payload_to_extractor(monkeypatch):
    from zuno.platform.services.pipeline.manager import KnowledgePipelineManager

    project_payload = {"id": "contract_review"}
    captured = {}

    async def fake_load_task(task_id):
        return SimpleNamespace(
            id=task_id,
            knowledge_id="kb_1",
            knowledge_file_id="file_1",
            payload={},
            result_summary={},
        )

    async def fake_get_knowledge_config(_knowledge_id):
        return {
            "index_capability": "rag_graph",
            "index_settings": {"status": "active"},
            "graph_index_settings": {"index_version": "v1"},
        }

    async def fake_get_runtime_settings(_knowledge_id):
        return {
            "project_payload": project_payload,
            "domain_pack_id": "contract_review",
        }

    async def fake_parse_graph_documents(_task):
        return [{"chunk_id": "chunk_1", "source_chunk_id": "source_1", "content": "contract clause"}]

    async def fake_record_stage(*args, **kwargs):
        return None

    async def fake_mark_community_stale(_knowledge_id):
        return None

    async def fake_mark_task_finished(*args, **kwargs):
        return None

    async def fake_create_task_event(*args, **kwargs):
        return None

    async def fake_update_pipeline_fields(*args, **kwargs):
        return None

    class FakeExtractor:
        async def extract_from_chunk(self, chunk, knowledge_id, project_payload=None):
            captured["chunk"] = chunk
            captured["knowledge_id"] = knowledge_id
            captured["project_payload"] = project_payload
            return {
                "entities": [{"name": "Contract", "knowledge_id": knowledge_id}],
                "relations": [],
            }

    class FakeGraphWriter:
        def build_entity_payload(self, entity, **kwargs):
            captured["entity_kwargs"] = kwargs
            return dict(entity)

        def build_relation_payload(self, relation, **kwargs):
            return dict(relation)

    class FakeNeo4jClient:
        @classmethod
        def is_enabled(cls):
            return True

        async def delete_by_source_chunk(self, *args, **kwargs):
            return None

        async def upsert_entity(self, *args, **kwargs):
            return None

        async def upsert_relation(self, *args, **kwargs):
            return None

    monkeypatch.setattr(KnowledgePipelineManager, "_load_task", staticmethod(fake_load_task))
    monkeypatch.setattr(KnowledgePipelineManager, "_parse_graph_documents", staticmethod(fake_parse_graph_documents))
    monkeypatch.setattr(KnowledgePipelineManager, "_record_stage", staticmethod(fake_record_stage))
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeService.get_knowledge_config", fake_get_knowledge_config)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeService.get_runtime_settings", fake_get_runtime_settings)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeService.mark_community_stale", fake_mark_community_stale)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeTaskDao.mark_task_finished", fake_mark_task_finished)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeTaskDao.create_task_event", fake_create_task_event)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeFileDao.update_pipeline_fields", fake_update_pipeline_fields)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.Neo4jClient", FakeNeo4jClient)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.CachedGraphExtractor", FakeExtractor)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.GraphWriter", FakeGraphWriter)

    manager = KnowledgePipelineManager(enable_graph_indexing=True, enable_elasticsearch=False)
    asyncio.run(manager.run_graph_stage("task_1"))

    assert captured["knowledge_id"] == "kb_1"
    assert captured["project_payload"] == project_payload
    assert captured["chunk"]["chunk_id"] == "chunk_1"
    assert captured["entity_kwargs"]["graphrag_project_id"] == "contract_review"


def test_pipeline_graph_stage_uses_canonical_handoff_without_chunk_projection(monkeypatch, tmp_path):
    from zuno.platform.services.pipeline.manager import KnowledgePipelineManager

    source = tmp_path / "contract.md"
    source.write_text("# Contract\nPayment obligations create audit evidence.", encoding="utf-8")
    captured = {}

    async def fake_load_task(task_id):
        return SimpleNamespace(
            id=task_id,
            knowledge_id="kb_graph",
            knowledge_file_id="file_graph",
            payload={"file_path": str(source), "file_name": "contract.md"},
            result_summary={},
        )

    async def fake_get_knowledge_config(_knowledge_id):
        return {
            "index_capability": "rag_graph",
            "index_settings": {"status": "active"},
            "graph_index_settings": {"index_version": "v1"},
        }

    async def fake_get_runtime_settings(_knowledge_id):
        return {"project_payload": {"id": "contract_review"}}

    async def fake_record_stage(*args, **kwargs):
        return None

    async def fake_mark_community_stale(_knowledge_id):
        return None

    async def fake_mark_task_finished(*args, **kwargs):
        return None

    async def fake_create_task_event(*args, **kwargs):
        return None

    async def fake_update_pipeline_fields(*args, **kwargs):
        return None

    class FakeExtractor:
        async def extract_from_chunk(self, chunk, knowledge_id, project_payload=None):
            captured.setdefault("chunks", []).append(dict(chunk))
            captured["project_payload"] = project_payload
            return {"entities": [], "relations": []}

    class FakeNeo4jClient:
        @classmethod
        def is_enabled(cls):
            return True

        async def delete_by_source_chunk(self, *args, **kwargs):
            captured.setdefault("deleted_source_chunks", []).append(args)

        async def upsert_entity(self, *args, **kwargs):
            return None

        async def upsert_relation(self, *args, **kwargs):
            return None

    monkeypatch.setattr(KnowledgePipelineManager, "_load_task", staticmethod(fake_load_task))
    monkeypatch.setattr(KnowledgePipelineManager, "_record_stage", staticmethod(fake_record_stage))
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeService.get_knowledge_config", fake_get_knowledge_config)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeService.get_runtime_settings", fake_get_runtime_settings)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeService.mark_community_stale", fake_mark_community_stale)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeTaskDao.mark_task_finished", fake_mark_task_finished)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeTaskDao.create_task_event", fake_create_task_event)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeFileDao.update_pipeline_fields", fake_update_pipeline_fields)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.Neo4jClient", FakeNeo4jClient)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.CachedGraphExtractor", FakeExtractor)

    asyncio.run(KnowledgePipelineManager(enable_graph_indexing=True).run_graph_stage("task_graph"))

    assert captured["chunks"]
    assert captured["project_payload"] == {"id": "contract_review"}
    assert all("content" in chunk for chunk in captured["chunks"])
    assert all("source_chunk_id" in chunk for chunk in captured["chunks"])
    import zuno.platform.services.pipeline.manager as pipeline_manager

    assert not hasattr(pipeline_manager, "parse_file_into_chunk_model_projection")


def test_pipeline_rag_stage_uses_canonical_handoff_without_chunk_projection(monkeypatch, tmp_path):
    from zuno.platform.services.pipeline.manager import KnowledgePipelineManager

    source = tmp_path / "policy.md"
    source.write_text("# Policy\nRenewal notice is required.", encoding="utf-8")
    task = SimpleNamespace(
        id="task_rag",
        knowledge_id="kb_rag",
        knowledge_file_id="file_rag",
        payload={"file_path": str(source), "file_name": "policy.md"},
        result_summary={},
    )
    captured = {}

    async def fake_load_task(task_id):
        assert task_id == "task_rag"
        return task

    async def fake_get_knowledge_config(_knowledge_id):
        return {"index_capability": "rag"}

    async def fake_get_runtime_settings(_knowledge_id):
        return {"text_embedding_config": {"provider": "test"}, "vl_embedding_config": None}

    async def fake_record_stage(*args, **kwargs):
        captured.setdefault("stage_details", []).append(kwargs.get("detail") or {})

    async def fake_update_task(_task_id, **kwargs):
        captured.setdefault("task_updates", []).append(kwargs)

    async def fake_update_pipeline_fields(*args, **kwargs):
        return None

    async def fake_delete_documents_by_file(file_id, knowledge_id):
        captured["delete"] = (file_id, knowledge_id)

    async def fake_index_milvus_documents(knowledge_id, chunks, **kwargs):
        captured["milvus"] = (knowledge_id, list(chunks), kwargs)

    async def fake_index_es_documents(knowledge_id, chunks):
        captured["es"] = (knowledge_id, list(chunks))

    monkeypatch.setattr(KnowledgePipelineManager, "_load_task", staticmethod(fake_load_task))
    monkeypatch.setattr(KnowledgePipelineManager, "_record_stage", staticmethod(fake_record_stage))
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeService.get_knowledge_config", fake_get_knowledge_config)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeService.get_runtime_settings", fake_get_runtime_settings)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeTaskDao.update_task", fake_update_task)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.KnowledgeFileDao.update_pipeline_fields", fake_update_pipeline_fields)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.RagHandler.delete_documents_by_file", fake_delete_documents_by_file)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.RagHandler.index_milvus_documents", fake_index_milvus_documents)
    monkeypatch.setattr("zuno.platform.services.pipeline.manager.RagHandler.index_es_documents", fake_index_es_documents)

    asyncio.run(KnowledgePipelineManager(enable_elasticsearch=True).run_rag_index_stage("task_rag"))

    assert captured["delete"] == ("file_rag", "kb_rag")
    knowledge_id, chunks, kwargs = captured["milvus"]
    assert knowledge_id == "kb_rag"
    assert kwargs["text_embedding_config"] == {"provider": "test"}
    assert chunks
    assert all(isinstance(chunk, dict) for chunk in chunks)
    assert all(chunk["file_id"] == "file_rag" for chunk in chunks)
    assert all(chunk["knowledge_id"] == "kb_rag" for chunk in chunks)
    assert all(chunk["modality"] == "text" for chunk in chunks)
    assert captured["es"][1] == chunks
    assert any(
        detail.get("projection") == "canonical_index_handoff_vector_documents"
        for detail in captured["stage_details"]
    )
    import zuno.platform.services.pipeline.manager as pipeline_manager

    assert not hasattr(pipeline_manager, "parse_file_into_chunk_model_projection")


def test_milvus_lite_client_accepts_canonical_dict_chunks(monkeypatch):
    from zuno.platform.services.rag.vector_db.milvus_lite_client import MilvusLiteClient

    inserted = {}

    class FakeCollection:
        def insert(self, data):
            inserted["data"] = data

        def flush(self):
            inserted["flushed"] = True

    client = MilvusLiteClient.__new__(MilvusLiteClient)
    client.collections = {"kb": FakeCollection()}
    monkeypatch.setattr(client, "_get_collection_safe", lambda _name: client.collections["kb"])

    chunk = {
        "chunk_id": "chunk_1",
        "document_hash": "doc_hash",
        "chunk_hash": "chunk_hash",
        "content": "hello",
        "summary": "",
        "file_id": "file_1",
        "file_name": "file.md",
        "knowledge_id": "kb",
        "update_time": "2026-08-02T00:00:00+00:00",
        "source_url": "file:///file.md",
    }

    asyncio.run(client._insert_collection("kb", [chunk], [[0.1, 0.2]]))

    assert inserted["flushed"] is True
    assert inserted["data"][0] == ["chunk_1"]
    assert inserted["data"][3] == ["hello"]
    assert inserted["data"][6] == ["file_1"]


def test_es_client_accepts_canonical_dict_chunks(monkeypatch):
    from zuno.platform.services.rag.es_client import ESClient

    indexed = []

    class FakeIndices:
        def exists(self, index):
            assert index == "kb"
            return True

    class FakeClient:
        indices = FakeIndices()

        def index(self, index, body):
            indexed.append((index, body))

    client = ESClient.__new__(ESClient)
    client.client = FakeClient()

    async def fake_close():
        return None

    monkeypatch.setattr(client, "close", fake_close)

    asyncio.run(
        client.insert_documents(
            "kb",
            [
                {
                    "chunk_id": "chunk_1",
                    "content": "hello",
                    "file_id": "file_1",
                    "file_name": "file.md",
                    "knowledge_id": "kb",
                    "update_time": "2026-08-02T00:00:00+00:00",
                    "summary": "",
                }
            ],
        )
    )

    assert indexed == [
        (
            "kb",
            {
                "chunk_id": "chunk_1",
                "content": "hello",
                "file_id": "file_1",
                "file_name": "file.md",
                "knowledge_id": "kb",
                "update_time": "2026-08-02T00:00:00+00:00",
                "summary": "",
            },
        )
    ]


def test_retry_task_creates_new_task_and_redispatches(monkeypatch):
    from zuno.api.services.knowledge_file import KnowledgeFileService

    original_task = SimpleNamespace(
        id="task_old",
        knowledge_id="knowledge_1",
        knowledge_file_id="file_1",
        task_type="ingest",
        payload={"file_path": "demo.txt", "oss_url": "minio/demo.txt"},
    )

    create_calls = []
    update_calls = []
    dispatch_calls = []

    async def fake_select_task_by_id(task_id):
        assert task_id == "task_old"
        return original_task

    async def fake_create_task(**kwargs):
        create_calls.append(kwargs)
        return "task_new"

    async def fake_update_pipeline_fields(knowledge_file_id, **kwargs):
        update_calls.append((knowledge_file_id, kwargs))

    async def fake_dispatch(task_id, knowledge_file_id, knowledge_id):
        dispatch_calls.append((task_id, knowledge_file_id, knowledge_id))
        return "sync"

    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_task.KnowledgeTaskDao.select_task_by_id",
        fake_select_task_by_id,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_task.KnowledgeTaskDao.create_task",
        fake_create_task,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_file.KnowledgeFileDao.update_pipeline_fields",
        fake_update_pipeline_fields,
    )
    monkeypatch.setattr(KnowledgeFileService, "_dispatch_task", fake_dispatch)

    result = asyncio.run(KnowledgeFileService.retry_task("task_old"))

    assert result["task_id"] == "task_new"
    assert result["previous_task_id"] == "task_old"
    assert result["knowledge_file_id"] == "file_1"
    assert result["dispatch_mode"] == "sync"
    assert create_calls == [{
        "knowledge_id": "knowledge_1",
        "knowledge_file_id": "file_1",
        "task_type": "ingest",
        "payload": {"file_name": "", "oss_url": "minio/demo.txt"},
    }]
    assert update_calls == [(
        "file_1",
        {
            "last_task_id": "task_new",
            "status": "process",
            "parse_status": "pending",
            "rag_index_status": "pending",
            "graph_index_status": "pending",
            "last_error": None,
        },
    )]
    assert dispatch_calls == [("task_new", "file_1", "knowledge_1")]


def test_bulk_reindex_knowledge_files_creates_tasks_for_all_files(monkeypatch):
    from zuno.api.services.knowledge_file import KnowledgeFileService

    files = [
        SimpleNamespace(id="file_1", file_name="a.pdf", oss_url="oss/a.pdf"),
        SimpleNamespace(id="file_2", file_name="b.docx", oss_url="oss/b.docx"),
    ]

    permission_calls = []
    create_calls = []
    update_calls = []
    dispatch_calls = []

    async def fake_verify_user_permission(knowledge_id, user_id):
        permission_calls.append((knowledge_id, user_id))

    async def fake_select_knowledge_file(knowledge_id):
        assert knowledge_id == "knowledge_1"
        return files

    async def fake_create_task(**kwargs):
        create_calls.append(kwargs)
        return f"task_{len(create_calls)}"

    async def fake_update_pipeline_fields(knowledge_file_id, **kwargs):
        update_calls.append((knowledge_file_id, kwargs))

    async def fake_dispatch(task_id, knowledge_file_id, knowledge_id):
        dispatch_calls.append((task_id, knowledge_file_id, knowledge_id))
        if knowledge_file_id == "file_2":
            raise RuntimeError("queue down")
        return "sync"

    monkeypatch.setattr(
        "zuno.api.services.knowledge.KnowledgeService.verify_user_permission",
        fake_verify_user_permission,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_file.KnowledgeFileDao.select_knowledge_file",
        fake_select_knowledge_file,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_task.KnowledgeTaskDao.create_task",
        fake_create_task,
    )
    monkeypatch.setattr(
        "zuno.platform.database.dao.knowledge_file.KnowledgeFileDao.update_pipeline_fields",
        fake_update_pipeline_fields,
    )
    monkeypatch.setattr(KnowledgeFileService, "_dispatch_task", fake_dispatch)

    result = asyncio.run(KnowledgeFileService.bulk_reindex_knowledge_files("knowledge_1", "u_test"))

    assert permission_calls == [("knowledge_1", "u_test")]
    assert result["summary"] == {
        "knowledge_id": "knowledge_1",
        "total_files": 2,
        "created_tasks": 2,
        "dispatched_tasks": 1,
        "failed_tasks": 1,
    }
    assert result["task_ids"] == ["task_1", "task_2"]
    assert result["file_ids"] == ["file_1", "file_2"]
    assert create_calls == [
        {
            "knowledge_id": "knowledge_1",
            "knowledge_file_id": "file_1",
            "task_type": "reindex",
            "payload": {"file_name": "a.pdf", "oss_url": "oss/a.pdf"},
        },
        {
            "knowledge_id": "knowledge_1",
            "knowledge_file_id": "file_2",
            "task_type": "reindex",
            "payload": {"file_name": "b.docx", "oss_url": "oss/b.docx"},
        },
    ]
    assert update_calls == [
        (
            "file_1",
            {
                "last_task_id": "task_1",
                "status": "process",
                "parse_status": "pending",
                "rag_index_status": "pending",
                "graph_index_status": "pending",
                "last_error": None,
            },
        ),
        (
            "file_2",
            {
                "last_task_id": "task_2",
                "status": "process",
                "parse_status": "pending",
                "rag_index_status": "pending",
                "graph_index_status": "pending",
                "last_error": None,
            },
        ),
    ]
    assert dispatch_calls == [
        ("task_1", "file_1", "knowledge_1"),
        ("task_2", "file_2", "knowledge_1"),
    ]


def test_pipeline_resolve_file_path_uses_public_url_helper(monkeypatch, tmp_path):
    from zuno.platform.services.pipeline.manager import KnowledgePipelineManager

    download_calls = []

    def fake_download_file(object_name, local_file):
        download_calls.append((object_name, local_file))

    fake_client = SimpleNamespace(download_file=fake_download_file)
    monkeypatch.setattr(
        "zuno.platform.services.pipeline.manager.storage_client._get_client",
        lambda: fake_client,
    )

    task = SimpleNamespace(
        knowledge_file_id="file_1",
        payload={
            "file_name": "demo.txt",
            "file_path": str(tmp_path / "missing.txt"),
            "oss_url": "http://127.0.0.1:9000/zuno/files/2026-4-17/txt/demo.txt",
        },
    )

    file_path, cleanup = asyncio.run(KnowledgePipelineManager()._resolve_file_path(task))

    assert cleanup is True
    assert file_path.endswith("demo.txt")
    assert download_calls
    assert download_calls[0][0] == "files/2026-4-17/txt/demo.txt"


def test_pipeline_resolve_file_path_uses_local_fixture_for_reindex():
    from zuno.platform.services.pipeline.manager import KnowledgePipelineManager

    task = SimpleNamespace(
        knowledge_file_id="file_1",
        payload={
            "file_name": "zuno_ascii_kb_2.md",
            "oss_url": "local://zuno_ascii_kb_2.md",
        },
    )

    file_path, cleanup = asyncio.run(KnowledgePipelineManager()._resolve_file_path(task))

    assert cleanup is False
    assert file_path.endswith("zuno_ascii_kb_2.md")
    assert Path(file_path).exists()


def test_graph_extractor_accepts_canonical_vector_payload_dict():
    from zuno.platform.services.graphrag.extractor import GraphExtractor

    chunk = {
        "chunk_id": "chunk_1",
        "content": "Alice works with Bob at OpenAI.",
        "file_id": "file_1",
        "file_name": "demo.txt",
        "update_time": "2026-04-17T19:00:00",
        "knowledge_id": "knowledge_1",
        "source_chunk_id": "source_chunk_1",
        "document_hash": "doc_hash_1",
        "chunk_hash": "chunk_hash_1",
    }

    result = asyncio.run(GraphExtractor().extract_from_chunk(chunk, "knowledge_1"))

    entity_names = {entity["name"] for entity in result["entities"]}
    relation_pairs = {
        (relation["source"], relation["target"])
        for relation in result["relations"]
    }

    assert entity_names == {"Alice", "Bob", "OpenAI"}
    assert relation_pairs
    assert {name for pair in relation_pairs for name in pair}.issubset(entity_names)

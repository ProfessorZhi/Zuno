import asyncio
from pathlib import Path
from types import SimpleNamespace
import sys


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src" / "backend"))


def test_pipeline_stage_flow():
    from agentchat.services.pipeline.models import PIPELINE_STAGES

    assert PIPELINE_STAGES[0] == "uploaded"
    assert PIPELINE_STAGES[-1] == "completed"
    assert "rag_indexing" in PIPELINE_STAGES
    assert "graph_indexing" in PIPELINE_STAGES


def test_pipeline_manager_updates_task_and_file_state(monkeypatch):
    from agentchat.services.pipeline.manager import KnowledgePipelineManager
    from agentchat.services.pipeline.models import (
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

    async def fake_parse_doc_into_chunks(file_id, file_path, knowledge_id, source_url=None):
        assert file_id == "f_1"
        assert file_path == "demo.txt"
        assert knowledge_id == "k_1"
        assert source_url is None
        return [{"chunk_id": "c_1", "content": "hello"}]

    async def fake_index_milvus_documents(knowledge_id, chunks):
        assert knowledge_id == "k_1"
        assert len(chunks) == 1

    async def fake_index_es_documents(knowledge_id, chunks):
        assert knowledge_id == "k_1"
        assert len(chunks) == 1

    monkeypatch.setattr(
        "agentchat.database.dao.knowledge_task.KnowledgeTaskDao.select_task_by_id",
        fake_select_task_by_id,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.knowledge_task.KnowledgeTaskDao.update_task",
        fake_update_task,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.knowledge_task.KnowledgeTaskDao.create_task_event",
        fake_create_task_event,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.knowledge_file.KnowledgeFileDao.update_pipeline_fields",
        fake_update_pipeline_fields,
    )
    monkeypatch.setattr(
        "agentchat.services.rag.parser.doc_parser.parse_doc_into_chunks",
        fake_parse_doc_into_chunks,
    )
    monkeypatch.setattr(
        "agentchat.services.rag.handler.RagHandler.index_milvus_documents",
        fake_index_milvus_documents,
    )
    monkeypatch.setattr(
        "agentchat.services.rag.handler.RagHandler.index_es_documents",
        fake_index_es_documents,
    )

    asyncio.run(
        KnowledgePipelineManager(enable_graph_indexing=True, enable_elasticsearch=True).run_sync(
            "task_1",
            file_path="demo.txt",
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


def test_retry_task_creates_new_task_and_redispatches(monkeypatch):
    from agentchat.api.services.knowledge_file import KnowledgeFileService

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
        "agentchat.database.dao.knowledge_task.KnowledgeTaskDao.select_task_by_id",
        fake_select_task_by_id,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.knowledge_task.KnowledgeTaskDao.create_task",
        fake_create_task,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.knowledge_file.KnowledgeFileDao.update_pipeline_fields",
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
    from agentchat.api.services.knowledge_file import KnowledgeFileService

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
        "agentchat.api.services.knowledge.KnowledgeService.verify_user_permission",
        fake_verify_user_permission,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.knowledge_file.KnowledgeFileDao.select_knowledge_file",
        fake_select_knowledge_file,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.knowledge_task.KnowledgeTaskDao.create_task",
        fake_create_task,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.knowledge_file.KnowledgeFileDao.update_pipeline_fields",
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
    from agentchat.services.pipeline.manager import KnowledgePipelineManager

    download_calls = []

    def fake_download_file(object_name, local_file):
        download_calls.append((object_name, local_file))

    fake_client = SimpleNamespace(download_file=fake_download_file)
    monkeypatch.setattr(
        "agentchat.services.pipeline.manager.storage_client._get_client",
        lambda: fake_client,
    )

    task = SimpleNamespace(
        knowledge_file_id="file_1",
        payload={
            "file_name": "demo.txt",
            "file_path": str(tmp_path / "missing.txt"),
            "oss_url": "http://127.0.0.1:9000/agentchat/files/2026-4-17/txt/demo.txt",
        },
    )

    file_path, cleanup = asyncio.run(KnowledgePipelineManager()._resolve_file_path(task))

    assert cleanup is True
    assert file_path.endswith("demo.txt")
    assert download_calls
    assert download_calls[0][0] == "files/2026-4-17/txt/demo.txt"


def test_pipeline_resolve_file_path_uses_local_fixture_for_reindex():
    from agentchat.services.pipeline.manager import KnowledgePipelineManager

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


def test_graph_extractor_accepts_chunk_model():
    from agentchat.schema.chunk import ChunkModel
    from agentchat.services.graphrag.extractor import GraphExtractor

    chunk = ChunkModel(
        chunk_id="chunk_1",
        content="Alice works with Bob at OpenAI.",
        file_id="file_1",
        file_name="demo.txt",
        update_time="2026-04-17T19:00:00",
        knowledge_id="knowledge_1",
    )

    result = asyncio.run(GraphExtractor().extract_from_chunk(chunk, "knowledge_1"))

    assert [entity["name"] for entity in result["entities"]] == ["Alice", "Bob", "OpenAI"]
    assert result["relations"][0]["source"] == "Alice"
    assert result["relations"][0]["target"] == "Bob"

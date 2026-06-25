import asyncio
from types import SimpleNamespace


def test_reindex_knowledge_files_requeues_every_file(monkeypatch):
    from zuno.api.services.knowledge_file import KnowledgeFileService

    knowledge_files = [
        SimpleNamespace(id="file_1", file_name="a.md", oss_url="oss://bucket/a.md", last_task_id="task_old_1"),
        SimpleNamespace(id="file_2", file_name="b.pdf", oss_url="oss://bucket/b.pdf", last_task_id="task_old_2"),
    ]

    async def fake_select_knowledge_file(knowledge_id):
        assert knowledge_id == "knowledge_1"
        return knowledge_files

    async def fake_create_task(**kwargs):
        return f"task_for_{kwargs['knowledge_file_id']}"

    updated = []

    async def fake_update_pipeline_fields(knowledge_file_id, **kwargs):
        updated.append((knowledge_file_id, kwargs))

    dispatched = []

    async def fake_dispatch_task(task_id, knowledge_file_id, knowledge_id):
        dispatched.append((task_id, knowledge_file_id, knowledge_id))
        return "sync"

    monkeypatch.setattr(
        "zuno.api.services.knowledge_file.KnowledgeFileDao.select_knowledge_file",
        fake_select_knowledge_file,
    )
    monkeypatch.setattr(
        "zuno.api.services.knowledge_file.KnowledgeTaskDao.create_task",
        fake_create_task,
    )
    monkeypatch.setattr(
        "zuno.api.services.knowledge_file.KnowledgeFileDao.update_pipeline_fields",
        fake_update_pipeline_fields,
    )
    monkeypatch.setattr(KnowledgeFileService, "_dispatch_task", fake_dispatch_task)

    result = asyncio.run(KnowledgeFileService.reindex_knowledge_files("knowledge_1"))

    assert result["summary"]["knowledge_id"] == "knowledge_1"
    assert result["summary"]["total_files"] == 2
    assert result["summary"]["created_tasks"] == 2
    assert result["summary"]["dispatched_tasks"] == 2
    assert result["summary"]["failed_tasks"] == 0
    assert result["task_ids"] == ["task_for_file_1", "task_for_file_2"]
    assert result["file_ids"] == ["file_1", "file_2"]
    assert [item[0] for item in updated] == ["file_1", "file_2"]
    assert dispatched == [
        ("task_for_file_1", "file_1", "knowledge_1"),
        ("task_for_file_2", "file_2", "knowledge_1"),
    ]


def test_reindex_knowledge_files_collects_failures(monkeypatch):
    from zuno.api.services.knowledge_file import KnowledgeFileService

    knowledge_files = [
        SimpleNamespace(id="file_1", file_name="a.md", oss_url="oss://bucket/a.md", last_task_id="task_old_1"),
        SimpleNamespace(id="file_2", file_name="b.pdf", oss_url="oss://bucket/b.pdf", last_task_id="task_old_2"),
    ]

    async def fake_select_knowledge_file(_knowledge_id):
        return knowledge_files

    async def fake_create_task(**kwargs):
        return f"task_for_{kwargs['knowledge_file_id']}"

    async def fake_update_pipeline_fields(*_args, **_kwargs):
        return None

    async def fake_dispatch_task(task_id, knowledge_file_id, knowledge_id):
        if knowledge_file_id == "file_2":
            raise ValueError("dispatch failed")
        return "sync"

    monkeypatch.setattr(
        "zuno.api.services.knowledge_file.KnowledgeFileDao.select_knowledge_file",
        fake_select_knowledge_file,
    )
    monkeypatch.setattr(
        "zuno.api.services.knowledge_file.KnowledgeTaskDao.create_task",
        fake_create_task,
    )
    monkeypatch.setattr(
        "zuno.api.services.knowledge_file.KnowledgeFileDao.update_pipeline_fields",
        fake_update_pipeline_fields,
    )
    monkeypatch.setattr(KnowledgeFileService, "_dispatch_task", fake_dispatch_task)

    result = asyncio.run(KnowledgeFileService.reindex_knowledge_files("knowledge_1"))

    assert result["summary"]["created_tasks"] == 2
    assert result["summary"]["dispatched_tasks"] == 1
    assert result["summary"]["failed_tasks"] == 1
    assert result["task_ids"] == ["task_for_file_1", "task_for_file_2"]
    assert result["file_ids"] == ["file_1", "file_2"]

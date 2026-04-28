import asyncio
from types import SimpleNamespace


def test_reindex_knowledge_files_requeues_every_file(monkeypatch):
    from agentchat.api.services.knowledge_file import KnowledgeFileService

    knowledge_files = [
        SimpleNamespace(id="file_1", file_name="a.md", oss_url="oss://bucket/a.md", last_task_id="task_old_1"),
        SimpleNamespace(id="file_2", file_name="b.pdf", oss_url="oss://bucket/b.pdf", last_task_id="task_old_2"),
    ]

    async def fake_select_knowledge_file(knowledge_id):
        assert knowledge_id == "knowledge_1"
        return knowledge_files

    async def fake_queue_file_task(**kwargs):
        return {
            "task_id": f"task_for_{kwargs['knowledge_file_id']}",
            "knowledge_file_id": kwargs["knowledge_file_id"],
            "dispatch_mode": "sync",
            "previous_task_id": kwargs.get("previous_task_id"),
        }

    monkeypatch.setattr(
        "agentchat.api.services.knowledge_file.KnowledgeFileDao.select_knowledge_file",
        fake_select_knowledge_file,
    )
    monkeypatch.setattr(KnowledgeFileService, "_queue_file_task", fake_queue_file_task)

    result = asyncio.run(KnowledgeFileService.reindex_knowledge_files("knowledge_1"))

    assert result["knowledge_id"] == "knowledge_1"
    assert result["total_files"] == 2
    assert result["queued_files"] == 2
    assert result["failed_files"] == 0
    assert [task["knowledge_file_id"] for task in result["tasks"]] == ["file_1", "file_2"]


def test_reindex_knowledge_files_collects_failures(monkeypatch):
    from agentchat.api.services.knowledge_file import KnowledgeFileService

    knowledge_files = [
        SimpleNamespace(id="file_1", file_name="a.md", oss_url="oss://bucket/a.md", last_task_id="task_old_1"),
        SimpleNamespace(id="file_2", file_name="b.pdf", oss_url="oss://bucket/b.pdf", last_task_id="task_old_2"),
    ]

    async def fake_select_knowledge_file(_knowledge_id):
        return knowledge_files

    async def fake_queue_file_task(**kwargs):
        if kwargs["knowledge_file_id"] == "file_2":
            raise ValueError("dispatch failed")
        return {
            "task_id": "task_for_file_1",
            "knowledge_file_id": "file_1",
            "dispatch_mode": "sync",
            "previous_task_id": kwargs.get("previous_task_id"),
        }

    monkeypatch.setattr(
        "agentchat.api.services.knowledge_file.KnowledgeFileDao.select_knowledge_file",
        fake_select_knowledge_file,
    )
    monkeypatch.setattr(KnowledgeFileService, "_queue_file_task", fake_queue_file_task)

    result = asyncio.run(KnowledgeFileService.reindex_knowledge_files("knowledge_1"))

    assert result["queued_files"] == 1
    assert result["failed_files"] == 1
    assert result["failures"][0]["knowledge_file_id"] == "file_2"


def test_reindex_knowledge_endpoint_checks_permission(monkeypatch):
    from agentchat.api.v1.knowledge_file import reindex_knowledge_files

    captured = {}

    async def fake_verify_user_permission(knowledge_id, user_id):
        captured["permission"] = (knowledge_id, user_id)

    async def fake_reindex(knowledge_id):
        captured["reindex"] = knowledge_id
        return {"knowledge_id": knowledge_id, "total_files": 0, "queued_files": 0, "failed_files": 0, "tasks": []}

    monkeypatch.setattr(
        "agentchat.api.v1.knowledge_file.KnowledgeService.verify_user_permission",
        fake_verify_user_permission,
    )
    monkeypatch.setattr(
        "agentchat.api.v1.knowledge_file.KnowledgeFileService.reindex_knowledge_files",
        fake_reindex,
    )

    login_user = SimpleNamespace(user_id="user_1")
    response = asyncio.run(reindex_knowledge_files(knowledge_id="knowledge_1", login_user=login_user))

    assert response.status_code == 200
    assert captured["permission"] == ("knowledge_1", "user_1")
    assert captured["reindex"] == "knowledge_1"

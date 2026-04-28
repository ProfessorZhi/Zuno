import asyncio
from types import SimpleNamespace


def _sample_knowledge_config():
    return {
        "model_refs": {
            "text_embedding_model_id": "llm_embed_text",
            "vl_embedding_model_id": "llm_embed_vl",
            "rerank_model_id": "llm_rerank",
        },
        "index_settings": {
            "chunk_mode": "parent_child",
            "chunk_size": 768,
            "overlap": 128,
            "separator": "\n\n",
            "replace_consecutive_spaces": True,
            "remove_urls_emails": True,
            "image_indexing_mode": "dual",
        },
        "retrieval_settings": {
            "default_mode": "hybrid",
            "top_k": 6,
            "rerank_enabled": True,
            "rerank_top_k": 4,
            "score_threshold": 0.42,
        },
    }


def test_knowledge_create_request_accepts_knowledge_config_and_ignores_legacy_default_retrieval_mode():
    from agentchat.schema.knowledge import KnowledgeCreateRequest

    request = KnowledgeCreateRequest(
        knowledge_name="PyIndex",
        knowledge_desc="Python knowledge base for tests.",
        knowledge_config=_sample_knowledge_config(),
        default_retrieval_mode="graphrag",
    )

    dumped = request.model_dump()

    assert dumped["knowledge_name"] == "PyIndex"
    assert dumped["knowledge_desc"] == "Python knowledge base for tests."
    assert dumped["knowledge_config"]["retrieval_settings"]["default_mode"] == "hybrid"
    assert "default_retrieval_mode" not in dumped


def test_create_knowledge_endpoint_passes_knowledge_config(monkeypatch):
    from agentchat.api.v1.knowledge import upload_knowledge
    from agentchat.schema.knowledge import KnowledgeCreateRequest

    captured = {}

    async def fake_create_knowledge(knowledge_name, knowledge_desc, user_id, knowledge_config=None):
        captured["knowledge_name"] = knowledge_name
        captured["knowledge_desc"] = knowledge_desc
        captured["user_id"] = user_id
        captured["knowledge_config"] = knowledge_config

    monkeypatch.setattr(
        "agentchat.api.v1.knowledge.KnowledgeService.create_knowledge",
        fake_create_knowledge,
    )

    login_user = SimpleNamespace(user_id="u_test")
    request = KnowledgeCreateRequest(
        knowledge_name="PyIndex",
        knowledge_desc="Python knowledge base for tests.",
        knowledge_config=_sample_knowledge_config(),
        default_retrieval_mode="hybrid",
    )

    response = asyncio.run(upload_knowledge(knowledge_req=request, login_user=login_user))

    assert response.status_code == 200
    assert captured == {
        "knowledge_name": "PyIndex",
        "knowledge_desc": "Python knowledge base for tests.",
        "user_id": "u_test",
        "knowledge_config": _sample_knowledge_config(),
    }


def test_update_knowledge_endpoint_passes_knowledge_config_patch(monkeypatch):
    from agentchat.api.v1.knowledge import update_knowledge
    from agentchat.schema.knowledge import KnowledgeUpdateRequest

    captured = {}

    async def fake_verify_user_permission(knowledge_id, user_id):
        captured["permission_check"] = (knowledge_id, user_id)

    async def fake_update_knowledge(knowledge_id, knowledge_name, knowledge_desc, knowledge_config=None):
        captured["update"] = (knowledge_id, knowledge_name, knowledge_desc, knowledge_config)

    monkeypatch.setattr(
        "agentchat.api.v1.knowledge.KnowledgeService.verify_user_permission",
        fake_verify_user_permission,
    )
    monkeypatch.setattr(
        "agentchat.api.v1.knowledge.KnowledgeService.update_knowledge",
        fake_update_knowledge,
    )

    login_user = SimpleNamespace(user_id="u_test")
    request = KnowledgeUpdateRequest(
        knowledge_id="k_test",
        knowledge_name="PyIndex2",
        knowledge_desc="Updated Python knowledge base.",
        knowledge_config={
            "retrieval_settings": {
                "default_mode": "graphrag",
                "top_k": 8,
            }
        },
        default_retrieval_mode="graphrag",
    )

    response = asyncio.run(update_knowledge(knowledge_req=request, login_user=login_user))

    assert response.status_code == 200
    assert captured["permission_check"] == ("k_test", "u_test")
    assert captured["update"] == (
        "k_test",
        "PyIndex2",
        "Updated Python knowledge base.",
        {
            "retrieval_settings": {
                "default_mode": "graphrag",
                "top_k": 8,
            }
        },
    )


def test_select_knowledge_exposes_normalized_knowledge_config(monkeypatch):
    from agentchat.api.services.knowledge import KnowledgeService

    async def fake_get_knowledge_by_user(_user_id):
        return [
            SimpleNamespace(
                to_dict=lambda: {
                    "id": "k1",
                    "name": "PyIndex",
                    "description": "Knowledge description",
                    "default_retrieval_mode": "graphrag",
                    "knowledge_config": {
                        "retrieval_settings": {
                            "top_k": 9,
                        }
                    },
                }
            )
        ]

    async def fake_select_knowledge_file(_knowledge_id):
        return []

    monkeypatch.setattr(
        "agentchat.api.services.knowledge.KnowledgeDao.get_knowledge_by_user",
        fake_get_knowledge_by_user,
    )
    monkeypatch.setattr(
        "agentchat.api.services.knowledge.KnowledgeFileDao.select_knowledge_file",
        fake_select_knowledge_file,
    )

    results = asyncio.run(KnowledgeService.select_knowledge("u_test"))

    assert len(results) == 1
    assert results[0]["name"] == "PyIndex"
    assert "default_retrieval_mode" not in results[0]
    assert results[0]["knowledge_config"]["retrieval_settings"]["default_mode"] == "graphrag"
    assert results[0]["knowledge_config"]["retrieval_settings"]["top_k"] == 9
    assert results[0]["knowledge_config"]["index_settings"]["chunk_mode"] == "general"


def test_update_knowledge_service_merges_partial_knowledge_config(monkeypatch):
    from agentchat.api.services.knowledge import KnowledgeService

    captured = {}

    async def fake_select_user_by_id(_knowledge_id):
        return SimpleNamespace(
            to_dict=lambda: {
                "id": "k_test",
                "knowledge_config": _sample_knowledge_config(),
                "default_retrieval_mode": "rag",
            }
        )

    async def fake_update_knowledge_by_id(
        knowledge_id,
        knowledge_desc,
        knowledge_name,
        default_retrieval_mode=None,
        knowledge_config=None,
    ):
        captured["update"] = (
            knowledge_id,
            knowledge_desc,
            knowledge_name,
            default_retrieval_mode,
            knowledge_config,
        )

    monkeypatch.setattr(
        "agentchat.api.services.knowledge.KnowledgeDao.select_user_by_id",
        fake_select_user_by_id,
    )
    monkeypatch.setattr(
        "agentchat.api.services.knowledge.KnowledgeDao.update_knowledge_by_id",
        fake_update_knowledge_by_id,
    )

    asyncio.run(
        KnowledgeService.update_knowledge(
            "k_test",
            "PyIndex2",
            "Updated Python knowledge base.",
            {
                "retrieval_settings": {
                    "top_k": 2,
                },
                "index_settings": {
                    "chunk_size": 512,
                },
            },
        )
    )

    assert captured["update"][3] == "hybrid"
    merged_config = captured["update"][4]
    assert merged_config["retrieval_settings"]["default_mode"] == "hybrid"
    assert merged_config["retrieval_settings"]["top_k"] == 2
    assert merged_config["index_settings"]["chunk_size"] == 512
    assert merged_config["index_settings"]["overlap"] == 128
    assert merged_config["model_refs"]["rerank_model_id"] == "llm_rerank"


def test_knowledge_service_rejects_encoding_damaged_text(monkeypatch):
    from agentchat.api.services.knowledge import KnowledgeService

    async def fake_create_knowledge(*_args, **_kwargs):
        raise AssertionError("damaged text should be rejected before database write")

    monkeypatch.setattr(
        "agentchat.api.services.knowledge.KnowledgeDao.create_knowledge",
        fake_create_knowledge,
    )

    try:
        asyncio.run(
            KnowledgeService.create_knowledge(
                "??5479",
                "?????? Zuno ??????????????????",
                "u_test",
            )
        )
    except ValueError as err:
        assert "编码损坏" in str(err)
    else:
        raise AssertionError("expected encoding damage validation error")


def test_reindex_knowledge_files_endpoint_passes_knowledge_id(monkeypatch):
    from agentchat.api.v1.knowledge_file import reindex_knowledge_files

    captured = {}

    async def fake_verify_user_permission(knowledge_id, user_id):
        captured["permission"] = (knowledge_id, user_id)

    async def fake_reindex_knowledge_files(knowledge_id):
        captured["reindex"] = knowledge_id
        return {
            "summary": {
                "knowledge_id": knowledge_id,
                "total_files": 2,
                "created_tasks": 2,
                "dispatched_tasks": 2,
                "failed_tasks": 0,
            },
            "task_ids": ["task_1", "task_2"],
            "file_ids": ["file_1", "file_2"],
    }

    monkeypatch.setattr(
        "agentchat.api.v1.knowledge_file.KnowledgeService.verify_user_permission",
        fake_verify_user_permission,
    )
    monkeypatch.setattr(
        "agentchat.api.v1.knowledge_file.KnowledgeFileService.reindex_knowledge_files",
        fake_reindex_knowledge_files,
    )

    login_user = SimpleNamespace(user_id="u_test")

    response = asyncio.run(reindex_knowledge_files(knowledge_id="k_test", login_user=login_user))

    assert response.status_code == 200
    assert captured["permission"] == ("k_test", "u_test")
    assert captured["reindex"] == "k_test"
    assert response.data["summary"]["created_tasks"] == 2
    assert response.data["task_ids"] == ["task_1", "task_2"]
    assert response.data["file_ids"] == ["file_1", "file_2"]


def test_retrieval_knowledge_endpoint_returns_retrieval_metadata(monkeypatch):
    from agentchat.api.v1.knowledge import retrieval_knowledge

    async def fake_retrieve_ranked_documents_with_metadata(*args, **kwargs):
        return {
            "content": "final-context",
            "first_mode": "rag",
            "final_mode": "hybrid",
            "second_pass_used": True,
            "fallback_triggered": True,
            "fallback_reason": "too_few_documents",
        }

    monkeypatch.setattr(
        "agentchat.api.v1.knowledge.RagHandler.retrieve_ranked_documents_with_metadata",
        fake_retrieve_ranked_documents_with_metadata,
    )

    response = asyncio.run(
        retrieval_knowledge(
            query="请补充知识库内容",
            knowledge_id="k_test",
            retrieval_mode="auto",
        )
    )

    assert response.status_code == 200
    assert response.data["content"] == "final-context"
    assert response.data["second_pass_used"] is True
    assert response.data["final_mode"] == "hybrid"

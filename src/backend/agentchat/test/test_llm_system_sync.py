import asyncio
from types import SimpleNamespace


def test_insert_llm_to_mysql_syncs_conversation_embedding_vl_embedding_and_rerank(monkeypatch):
    from agentchat.database.init_data import insert_llm_to_mysql
    from agentchat.settings import app_settings

    original_multi_models = app_settings.multi_models
    created_records = []

    async def fake_get_llm_by_user(_user_id):
        return []

    async def fake_create_llm(**kwargs):
        created_records.append(kwargs)

    monkeypatch.setattr(
        "agentchat.database.dao.llm.LLMDao.get_llm_by_user",
        fake_get_llm_by_user,
    )
    monkeypatch.setattr(
        "agentchat.api.services.llm.LLMService.create_llm",
        fake_create_llm,
    )

    app_settings.multi_models = SimpleNamespace(
        conversation_model=SimpleNamespace(
            model_name="qwen-plus",
            api_key="conv-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            is_configured=lambda: True,
        ),
        embedding=SimpleNamespace(
            model_name="text-embedding-v4",
            api_key="embed-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            is_configured=lambda: True,
        ),
        vl_embedding=SimpleNamespace(
            model_name="qwen3-vl-embedding",
            api_key="vl-embed-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            is_configured=lambda: True,
        ),
        rerank=SimpleNamespace(
            model_name="gte-rerank-v2",
            api_key="rerank-key",
            base_url="https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank",
            is_configured=lambda: True,
        ),
    )

    try:
        has_default_llm = asyncio.run(insert_llm_to_mysql())
    finally:
        app_settings.multi_models = original_multi_models

    assert has_default_llm is True
    assert {
        (record["model"], record["llm_type"], record.get("model_slot"))
        for record in created_records
    } == {
        ("qwen-plus", "LLM", "conversation_model"),
        ("text-embedding-v4", "Embedding", "embedding"),
        ("qwen3-vl-embedding", "Embedding", "vl_embedding"),
        ("gte-rerank-v2", "Rerank", "rerank"),
    }


def test_get_visible_llm_normalizes_legacy_reranker_type(monkeypatch):
    from agentchat.api.services.llm import LLMService

    llms = [
        {
            "llm_id": "llm_1",
            "model": "qwen-plus",
            "provider": "通义千问",
            "llm_type": "LLM",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key": "secret-1",
            "user_id": "0",
            "update_time": "",
            "create_time": "",
        },
        {
            "llm_id": "llm_2",
            "model": "gte-rerank-v2",
            "provider": "通义千问",
            "llm_type": "Reranker",
            "base_url": "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank",
            "api_key": "secret-2",
            "user_id": "0",
            "update_time": "",
            "create_time": "",
        },
    ]

    async def fake_get_llm_by_user(user_id):
        return [
            SimpleNamespace(to_dict=lambda value=item: dict(value))
            for item in llms
            if item["user_id"] == user_id
        ]

    monkeypatch.setattr(
        "agentchat.database.dao.llm.LLMDao.get_llm_by_user",
        fake_get_llm_by_user,
    )

    result = asyncio.run(LLMService.get_visible_llm("u_test"))

    assert "Rerank" in result
    assert result["Rerank"][0]["model"] == "gte-rerank-v2"
    assert result["Rerank"][0]["api_key"] == "************"


def test_activate_model_slot_replaces_previous_binding(monkeypatch):
    import asyncio
    from types import SimpleNamespace

    from agentchat.api.services.llm import LLMService

    operations = []

    async def fake_get_llm_by_id(_llm_id):
        return SimpleNamespace(llm_id="llm_2", llm_type="Embedding", user_id="0")

    async def fake_clear_model_slot(model_slot):
        operations.append(("clear", model_slot))

    async def fake_update_llm(**kwargs):
        operations.append(("update", kwargs))

    monkeypatch.setattr(
        "agentchat.database.dao.llm.LLMDao.get_llm_by_id",
        fake_get_llm_by_id,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.llm.LLMDao.clear_model_slot",
        fake_clear_model_slot,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.llm.LLMDao.update_llm",
        fake_update_llm,
    )

    asyncio.run(LLMService.activate_model_slot("llm_2", "embedding"))

    assert operations == [
        ("clear", "embedding"),
        ("update", {"llm_id": "llm_2", "model_slot": "embedding"}),
    ]


def test_model_manager_prefers_active_slot_over_yaml(monkeypatch):
    from types import SimpleNamespace

    from agentchat.core.models.manager import ModelManager
    from agentchat.settings import app_settings

    original_embedding = app_settings.multi_models.embedding

    monkeypatch.setattr(
        "agentchat.database.dao.llm.LLMDao.get_llm_by_slot",
        lambda _slot: SimpleNamespace(
            model="active-embedding",
            api_key="active-key",
            base_url="https://active.example.com/v1",
        ),
    )

    app_settings.multi_models.embedding = SimpleNamespace(
        model_name="fallback-embedding",
        api_key="fallback-key",
        base_url="https://fallback.example.com/v1",
        is_configured=lambda: True,
    )

    try:
        config = ModelManager.get_model_config("embedding", "Embedding 模型")
    finally:
        app_settings.multi_models.embedding = original_embedding

    assert config.model_name == "active-embedding"
    assert config.api_key == "active-key"
    assert config.base_url == "https://active.example.com/v1"

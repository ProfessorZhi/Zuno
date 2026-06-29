import asyncio
from types import SimpleNamespace


def test_completion_passes_dialog_id_into_general_agent(monkeypatch):
    from zuno.api.v1.completion import completion
    from zuno.schema.completion import CompletionReq

    captured = {}

    class FakeAgent:
        def __init__(self, agent_config):
            captured["dialog_id"] = agent_config.dialog_id
            captured["product_mode"] = agent_config.product_mode
            captured["query_method"] = agent_config.query_method

        async def init_agent(self):
            return None

        async def astream(self, messages):
            yield {
                "type": "response_chunk",
                "timestamp": 0.0,
                "data": {"chunk": "ok", "accumulated": "ok"},
            }

        def stop_streaming_callback(self):
            return None

    async def fake_get_agent_by_dialog_id(dialog_id):
        assert dialog_id == "dialog_42"
        return {
            "user_id": "u_agent",
            "llm_id": "",
            "mcp_ids": [],
            "knowledge_ids": ["kb_1"],
            "domain_pack_id": "contract_review",
            "tool_ids": [],
            "agent_skill_ids": [],
            "system_prompt": "review contract",
            "enable_memory": False,
            "name": "contract-agent",
        }

    async def fake_select_history(dialog_id):
        return []

    async def fake_save_chat_history(**kwargs):
        return None

    monkeypatch.setattr("zuno.api.v1.completion.GeneralAgent", FakeAgent)
    monkeypatch.setattr("zuno.api.v1.completion.DialogService.get_agent_by_dialog_id", fake_get_agent_by_dialog_id)
    monkeypatch.setattr("zuno.api.v1.completion.HistoryService.select_history", fake_select_history)
    monkeypatch.setattr("zuno.api.v1.completion.HistoryService.save_chat_history", fake_save_chat_history)

    response = asyncio.run(
        completion(
            req=CompletionReq(user_input="审查合同", dialog_id="dialog_42", file_url=None),
            login_user=SimpleNamespace(user_id="u_login"),
        )
    )

    assert captured["dialog_id"] == "dialog_42"
    assert captured["product_mode"] == "auto"
    assert captured["query_method"] is None
    assert response.media_type == "text/event-stream"


def test_completion_can_enable_multi_agent_runtime(monkeypatch):
    from zuno.api.v1.completion import completion
    from zuno.schema.completion import CompletionReq

    captured = {}

    class FakeAgent:
        def __init__(self, agent_config):
            captured["multi_agent_enabled"] = agent_config.multi_agent_enabled
            captured["product_mode"] = agent_config.product_mode
            captured["query_method"] = agent_config.query_method

        async def init_agent(self):
            return None

        async def astream(self, messages):
            yield {
                "type": "response_chunk",
                "timestamp": 0.0,
                "data": {"chunk": "ok", "accumulated": "ok"},
            }

        def stop_streaming_callback(self):
            return None

    async def fake_get_agent_by_dialog_id(dialog_id):
        assert dialog_id == "dialog_multi"
        return {
            "user_id": "u_agent",
            "llm_id": "",
            "mcp_ids": [],
            "knowledge_ids": ["kb_1"],
            "domain_pack_id": "contract_review",
            "tool_ids": [],
            "agent_skill_ids": [],
            "system_prompt": "review contract",
            "enable_memory": False,
            "name": "contract-agent",
        }

    async def fake_select_history(dialog_id):
        return []

    async def fake_save_chat_history(**kwargs):
        return None

    monkeypatch.setattr("zuno.api.v1.completion.GeneralAgent", FakeAgent)
    monkeypatch.setattr("zuno.api.v1.completion.DialogService.get_agent_by_dialog_id", fake_get_agent_by_dialog_id)
    monkeypatch.setattr("zuno.api.v1.completion.HistoryService.select_history", fake_select_history)
    monkeypatch.setattr("zuno.api.v1.completion.HistoryService.save_chat_history", fake_save_chat_history)

    response = asyncio.run(
        completion(
            req=CompletionReq(
                user_input="用多 agent 审查合同",
                dialog_id="dialog_multi",
                file_url=None,
                multi_agent_enabled=True,
                product_mode="enhanced",
                query_method="local",
            ),
            login_user=SimpleNamespace(user_id="u_login"),
        )
    )

    assert captured["multi_agent_enabled"] is True
    assert captured["product_mode"] == "enhanced"
    assert captured["query_method"] == "local"
    assert response.media_type == "text/event-stream"

import asyncio
from types import SimpleNamespace


def _agent(**overrides):
    payload = {
        "id": "agent_1",
        "name": "user agent",
        "user_id": "user_1",
        "is_custom": True,
        "tool_ids": [],
    }
    payload.update(overrides)
    return SimpleNamespace(to_dict=lambda: dict(payload))


def test_init_default_agent_does_not_seed_system_agents(monkeypatch):
    from agentchat.database.init_data import init_default_agent

    calls = []

    async def fake_cleanup():
        calls.append("cleanup")

    async def fake_insert_tools():
        calls.append("tools")

    async def fake_insert_llms():
        calls.append("llms")
        return True

    async def fake_insert_agents():
        calls.append("agents")

    monkeypatch.setattr("agentchat.database.init_data.cleanup_duplicate_system_data", fake_cleanup)
    monkeypatch.setattr("agentchat.database.init_data.insert_tools_to_mysql", fake_insert_tools)
    monkeypatch.setattr("agentchat.database.init_data.insert_llm_to_mysql", fake_insert_llms)
    monkeypatch.setattr("agentchat.database.init_data.insert_agent_to_mysql", fake_insert_agents)

    asyncio.run(init_default_agent())

    assert calls == ["cleanup", "tools", "llms"]


def test_agent_list_returns_only_current_user_agents(monkeypatch):
    from agentchat.api.services.agent import AgentService

    async def fake_get_agent_by_user_id(user_id):
        if user_id == "user_1":
            return [_agent(id="user_agent", name="my agent", user_id="user_1")]
        if user_id == "0":
            return [_agent(id="system_agent", name="weather agent", user_id="0", is_custom=False)]
        return []

    monkeypatch.setattr(
        "agentchat.database.dao.agent.AgentDao.get_agent_by_user_id",
        fake_get_agent_by_user_id,
    )

    agents = asyncio.run(AgentService.get_all_agent_by_user_id("user_1"))

    assert [agent["id"] for agent in agents] == ["user_agent"]


def test_agent_search_returns_only_current_user_agents(monkeypatch):
    from agentchat.api.services.agent import AgentService

    async def fake_search_agent_name(name, user_id):
        return [
            _agent(id="system_agent", name=name, user_id="0", is_custom=False),
            _agent(id="user_agent", name=name, user_id=user_id),
        ]

    monkeypatch.setattr(
        "agentchat.database.dao.agent.AgentDao.search_agent_name",
        fake_search_agent_name,
    )

    agents = asyncio.run(AgentService.search_agent_name("weather", "user_1"))

    assert agents == [{"id": "user_agent", "name": "weather", "user_id": "user_1", "is_custom": True, "tool_ids": []}]


def test_cleanup_legacy_seeded_system_agents_deletes_only_builtin_agents(monkeypatch):
    from agentchat.database.init_data import cleanup_legacy_seeded_system_agents

    deleted_ids = []

    async def fake_get_personal_agent_by_user_id(user_id):
        assert user_id == "0"
        return [
            {"id": "builtin_1", "user_id": "0", "is_custom": False},
            {"id": "custom_system_agent", "user_id": "0", "is_custom": True},
        ]

    async def fake_delete_agent_by_id(agent_id):
        deleted_ids.append(agent_id)

    monkeypatch.setattr(
        "agentchat.api.services.agent.AgentService.get_personal_agent_by_user_id",
        fake_get_personal_agent_by_user_id,
    )
    monkeypatch.setattr(
        "agentchat.database.dao.agent.AgentDao.delete_agent_by_id",
        fake_delete_agent_by_id,
    )

    deleted_count = asyncio.run(cleanup_legacy_seeded_system_agents())

    assert deleted_count == 1
    assert deleted_ids == ["builtin_1"]

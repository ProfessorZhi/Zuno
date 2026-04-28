import asyncio
from datetime import datetime
from types import SimpleNamespace


def _usage(agent="Simple-Agent", model="MiniMax-M2.5", input_tokens=10, output_tokens=2):
    return SimpleNamespace(
        agent=agent,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        create_time=datetime(2026, 4, 28, 12, 0, 0),
    )


def test_blank_usage_filters_are_treated_as_all(monkeypatch):
    from agentchat.api.services.usage_stats import UsageStatsService

    calls = []

    async def fake_get_agent_model_time_usage(user_id, agent=None, model=None, delta_days=10000):
        calls.append({"user_id": user_id, "agent": agent, "model": model, "delta_days": delta_days})
        return [_usage()]

    monkeypatch.setattr(
        "agentchat.database.dao.usage_stats.UsageStatsDao.get_agent_model_time_usage",
        fake_get_agent_model_time_usage,
    )

    result = asyncio.run(
        UsageStatsService.get_usage_by_agent_model(
            user_id="user_1",
            agent="",
            model="",
            delta_days=30,
        )
    )

    assert calls == [{"user_id": "user_1", "agent": None, "model": None, "delta_days": 30}]
    assert result["2026-04-28"]["model"]["MiniMax-M2.5"]["total_tokens"] == 12


def test_specific_usage_filters_are_preserved(monkeypatch):
    from agentchat.api.services.usage_stats import UsageStatsService

    calls = []

    async def fake_get_agent_model_time_usage(user_id, agent=None, model=None, delta_days=10000):
        calls.append({"user_id": user_id, "agent": agent, "model": model, "delta_days": delta_days})
        return [_usage()]

    monkeypatch.setattr(
        "agentchat.database.dao.usage_stats.UsageStatsDao.get_agent_model_time_usage",
        fake_get_agent_model_time_usage,
    )

    asyncio.run(
        UsageStatsService.get_usage_count_by_agent_model(
            user_id="user_1",
            agent="Simple-Agent",
            model="MiniMax-M2.5",
            delta_days=30,
        )
    )

    assert calls == [
        {
            "user_id": "user_1",
            "agent": "Simple-Agent",
            "model": "MiniMax-M2.5",
            "delta_days": 30,
        }
    ]

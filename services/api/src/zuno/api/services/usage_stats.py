from collections import defaultdict
from datetime import datetime
from typing import DefaultDict, Dict, List, Optional

from zuno.database.dao.usage_stats import UsageStats, UsageStatsDao


class UsageStatsService:
    @staticmethod
    def _normalize_filter(value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @classmethod
    async def create_usage_stats(cls, agent, model, user_id, input_tokens=0, output_tokens=0):
        usage_stats = UsageStats(
            agent=agent,
            model=model,
            user_id=user_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        await UsageStatsDao.create_usage_stats(usage_stats)

    @classmethod
    def sync_create_usage_stats(cls, agent, model, user_id, input_tokens=0, output_tokens=0):
        usage_stats = UsageStats(
            agent=agent,
            model=model,
            user_id=user_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        UsageStatsDao.sync_create_usage_stats(usage_stats)

    @classmethod
    async def get_usage_agents(cls, user_id) -> List[str]:
        return await UsageStatsDao.get_usage_agents(user_id)

    @classmethod
    async def get_usage_models(cls, user_id) -> List[str]:
        return await UsageStatsDao.get_usage_models(user_id)

    @classmethod
    async def get_usage_by_agent_model(
        cls,
        user_id: str,
        agent: Optional[str] = None,
        model: Optional[str] = None,
        delta_days: int = 10000,
    ):
        agent = cls._normalize_filter(agent)
        model = cls._normalize_filter(model)
        results = await UsageStatsDao.get_agent_model_time_usage(user_id, agent, model, delta_days)
        results.sort(key=lambda x: x.create_time.date() if x.create_time else datetime.min.date())
        date_usage_dict: DefaultDict[str, Dict[str, Dict]] = defaultdict(
            lambda: {"agent": defaultdict(dict), "model": defaultdict(dict)}
        )
        for item in results:
            date_key = item.create_time.date().isoformat() if item.create_time else "unknown-date"
            agent_key = item.agent or "unknown-agent"
            if not date_usage_dict[date_key]["agent"][agent_key]:
                date_usage_dict[date_key]["agent"][agent_key] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                }
            date_usage_dict[date_key]["agent"][agent_key]["input_tokens"] += item.input_tokens
            date_usage_dict[date_key]["agent"][agent_key]["output_tokens"] += item.output_tokens
            date_usage_dict[date_key]["agent"][agent_key]["total_tokens"] += item.input_tokens + item.output_tokens

            model_key = item.model or "unknown-model"
            if not date_usage_dict[date_key]["model"][model_key]:
                date_usage_dict[date_key]["model"][model_key] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                }
            date_usage_dict[date_key]["model"][model_key]["input_tokens"] += item.input_tokens
            date_usage_dict[date_key]["model"][model_key]["output_tokens"] += item.output_tokens
            date_usage_dict[date_key]["model"][model_key]["total_tokens"] += item.input_tokens + item.output_tokens
        return dict(date_usage_dict)

    @classmethod
    async def get_usage_count_by_agent_model(
        cls,
        user_id: str,
        agent: Optional[str] = None,
        model: Optional[str] = None,
        delta_days: int = 10000,
    ):
        agent = cls._normalize_filter(agent)
        model = cls._normalize_filter(model)
        results = await UsageStatsDao.get_agent_model_time_usage(user_id, agent, model, delta_days)
        results.sort(key=lambda x: x.create_time.date() if x.create_time else datetime.min.date())
        date_usage_dict: DefaultDict[str, Dict[str, Dict]] = defaultdict(
            lambda: {"agent": defaultdict(int), "model": defaultdict(int)}
        )
        for item in results:
            date_key = item.create_time.date().isoformat() if item.create_time else "unknown-date"
            agent_key = item.agent or "unknown-agent"
            model_key = item.model or "unknown-model"
            date_usage_dict[date_key]["agent"][agent_key] += 1
            date_usage_dict[date_key]["model"][model_key] += 1
        return dict(date_usage_dict)


__all__ = ["UsageStatsService"]

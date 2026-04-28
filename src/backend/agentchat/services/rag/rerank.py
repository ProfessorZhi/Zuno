import asyncio
import json

import aiohttp

from agentchat.core.models.manager import ModelManager
from agentchat.schema.rerank import RerankResultModel
from agentchat.settings import app_settings, initialize_app_settings


def _normalize_model_config(config_override):
    if not config_override:
        return None
    if hasattr(config_override, "model_name"):
        return config_override
    return type("RerankConfig", (), config_override)()


class Reranker:
    @classmethod
    def _get_config(cls, config_override=None):
        return _normalize_model_config(config_override) or ModelManager.get_model_config("rerank", "Rerank 模型")

    @classmethod
    def _is_configured(cls, config_override=None) -> bool:
        try:
            config = cls._get_config(config_override)
        except ValueError:
            return False
        return bool(config and config.api_key and config.base_url and config.model_name)

    @classmethod
    def _fallback_documents(cls, query, documents):
        return [
            RerankResultModel(
                query=query,
                content=document,
                score=float(len(documents) - index),
                index=index,
            )
            for index, document in enumerate(documents)
        ]

    @classmethod
    async def request_rerank(cls, query, documents, *, config_override=None, top_n=None):
        if not documents:
            return []
        config = cls._get_config(config_override)

        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        default_top_k = app_settings.rag.retrival.get("top_k") or len(documents)
        payload = {
            "model": config.model_name,
            "input": {
                "query": query,
                "documents": documents,
            },
            "parameters": {
                "return_documents": True,
                "top_n": top_n or (default_top_k * 2),
            },
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=config.base_url, headers=headers, data=json.dumps(payload)) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["output"]["results"]
                response.raise_for_status()

    @classmethod
    async def rerank_documents(cls, query, documents, *, config_override=None, top_n=None):
        final_documents = []
        original_documents = documents

        if not documents:
            return []
        if not cls._is_configured(config_override):
            return cls._fallback_documents(query, documents)

        results = await cls.request_rerank(query, documents, config_override=config_override, top_n=top_n)
        if not results:
            return cls._fallback_documents(query, documents)

        for result in results:
            result["document"] = original_documents[result["index"]]
            final_documents.append(
                RerankResultModel(
                    query=query,
                    content=result["document"],
                    score=result["relevance_score"],
                    index=result["index"],
                )
            )
        return final_documents


if __name__ == "__main__":
    asyncio.run(initialize_app_settings("../../config.yaml"))
    asyncio.run(
        Reranker.rerank_documents(
            query="什么是文本排序模型",
            documents=[
                "文本排序模型广泛用于搜索引擎和推荐系统中，它们根据文本相关性对候选文本进行排序。",
                "量子计算是计算科学的一个前沿领域。",
                "预训练语言模型的发展给文本排序模型带来了新的进展。",
            ],
        )
    )

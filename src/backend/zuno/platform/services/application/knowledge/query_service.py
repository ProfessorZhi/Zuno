from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from zuno.services.graphrag.project.loader import GraphRAGProjectLoader
from zuno.services.graphrag.prompts.registry import GraphRAGPromptRegistry
from zuno.services.graphrag.query_service import (
    GraphRAGProjectSnapshot,
    GraphRAGQueryService,
    KnowledgeQueryResult,
)


ConfigLoader = Callable[[str], Awaitable[dict[str, Any]]]


async def _default_config_loader(knowledge_id: str) -> dict[str, Any]:
    from zuno.api.services.knowledge import KnowledgeService

    return await KnowledgeService.get_knowledge_config(knowledge_id)


class KnowledgeQueryService:
    def __init__(
        self,
        *,
        config_loader: ConfigLoader | None = None,
        project_loader: GraphRAGProjectLoader | None = None,
        query_service: GraphRAGQueryService | None = None,
    ):
        self.config_loader = config_loader or _default_config_loader
        self.project_loader = project_loader or GraphRAGProjectLoader()
        self.query_service = query_service or GraphRAGQueryService()

    async def query(
        self,
        *,
        user_id: str,
        knowledge_ids: list[str],
        query: str,
        product_mode: str | None = None,
        query_method: str | None = None,
        top_k: int | None = None,
    ) -> KnowledgeQueryResult:
        if not knowledge_ids:
            raise ValueError("knowledge_ids is required")
        snapshot = await self.build_project_snapshot(
            user_id=user_id,
            knowledge_id=knowledge_ids[0],
        )
        return await self.query_service.query(
            query=query,
            knowledge_ids=knowledge_ids,
            snapshot=snapshot,
            product_mode=product_mode,
            query_method=query_method,
            top_k=top_k,
        )

    async def build_project_snapshot(
        self,
        *,
        user_id: str,
        knowledge_id: str,
    ) -> GraphRAGProjectSnapshot:
        del user_id
        config = dict(await self.config_loader(knowledge_id) or {})
        project_config = dict(config.get("graphrag_project") or {})
        project_id = config.get("graphrag_project_id") or project_config.get("graphrag_project_id")
        project = self.project_loader.load(project_id) if project_id else None

        contract = dict(project.contract.model_dump() if project else project_config)
        readiness = dict(project.readiness.to_dict() if project else {})
        prompt_categories: list[str] = []
        query_policy: dict[str, Any] = {}
        settings: dict[str, Any] = {}
        if project:
            prompt_registry = GraphRAGPromptRegistry.from_project(project)
            prompt_categories = prompt_registry.categories()
            settings = dict(project.settings)
            query_policy = dict(settings.get("query_policy") or settings.get("retrieval_policy") or {})

        retrieval_settings = dict(config.get("retrieval_settings") or {})
        index_settings = dict(config.get("index_settings") or {})
        graph_settings = dict(config.get("graph_index_settings") or {})
        community_status = (
            graph_settings.get("community_report_status")
            or graph_settings.get("community_detection_status")
            or "not_built"
        )
        prompt_version = contract.get("prompt_version") or project_config.get("prompt_version") or "default"
        query_prompt_version = contract.get("query_prompt_version") or project_config.get("query_prompt_version") or "default"
        community_version = (
            contract.get("community_version")
            or graph_settings.get("community_version")
            or project_config.get("community_version")
            or "v0"
        )

        return GraphRAGProjectSnapshot(
            graphrag_project_id=str(project_id) if project_id else None,
            contract=contract,
            readiness=readiness,
            prompt_categories=prompt_categories,
            retrieval_settings=retrieval_settings,
            index_version={
                "vector": str(index_settings.get("index_version") or "v1"),
                "graph": str(graph_settings.get("index_version") or "v1"),
                "community": str(community_version),
                "prompt": str(prompt_version),
                "query_prompt": str(query_prompt_version),
            },
            index_health={
                "vector": str(index_settings.get("health_status") or "ready"),
                "graph": str(graph_settings.get("health_status") or "ready"),
                "community": str(community_status),
            },
            knowledge_capability=str(config.get("index_capability") or "rag"),
            query_policy=query_policy,
            settings=settings,
        )


__all__ = ["KnowledgeQueryService"]

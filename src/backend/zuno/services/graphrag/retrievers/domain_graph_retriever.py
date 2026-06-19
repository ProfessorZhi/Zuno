from __future__ import annotations

from zuno.services.graphrag.retriever import GraphRetriever


class DomainGraphRetriever(GraphRetriever):
    async def retrieve(
        self,
        query: str,
        knowledge_id: str,
        *,
        graph_hop_limit: int = 2,
        max_paths_per_entity: int = 10,
        domain_pack: dict | None = None,
    ) -> dict:
        result = await super().retrieve(
            query,
            knowledge_id,
            graph_hop_limit=graph_hop_limit,
            max_paths_per_entity=max_paths_per_entity,
        )
        if domain_pack:
            result["domain_pack_id"] = domain_pack.get("id")
        return result

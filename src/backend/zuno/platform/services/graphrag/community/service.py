from __future__ import annotations

import re

from zuno.services.graphrag.client import Neo4jClient
from zuno.services.graphrag.community.detector import CommunityDetector
from zuno.services.graphrag.community.models import GraphCommunity
from zuno.services.graphrag.community.reporter import CommunityReportBuilder


class CommunityGraphService:
    def __init__(self, client: Neo4jClient | None = None):
        self.client = client or Neo4jClient()
        self.report_builder = CommunityReportBuilder()

    async def build_level0_communities(
        self,
        *,
        knowledge_id: str,
        index_version: str | None = None,
        status: str | None = None,
        community_version: str = "v0",
    ) -> dict:
        edges = await self.client.fetch_relation_edges(
            knowledge_id,
            index_version=index_version,
            status=status,
        )
        communities = CommunityDetector.detect_level0(
            knowledge_id=knowledge_id,
            edges=edges,
            community_version=community_version,
        )
        for community in communities:
            community.report = self.report_builder.build_report(community)

        await self.client.replace_communities(
            knowledge_id,
            communities,
            community_version=community_version,
            status=status or "ready",
        )
        return {
            "knowledge_id": knowledge_id,
            "community_count": len(communities),
            "community_detection_status": "ready",
            "community_report_status": "ready",
            "community_version": community_version,
            "communities": [community.to_dict() for community in communities],
        }

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[\w\u4e00-\u9fff]+", str(text or "").lower())

    def search_reports(self, query: str, communities: list[GraphCommunity], *, limit: int = 3) -> dict:
        query_terms = set(self._tokenize(query))
        ranked = sorted(
            communities,
            key=lambda community: (
                sum(1 for term in query_terms if term in community.report.lower()),
                sum(1 for term in query_terms if any(term in entity.lower() for entity in community.entities)),
                community.relation_count,
            ),
            reverse=True,
        )
        selected = ranked[: max(1, limit)]
        used_communities = [community.community_id for community in selected]
        supporting_chunks: list[str] = []
        seen_chunks: set[str] = set()
        for community in selected:
            for chunk_id in community.supporting_chunks:
                if chunk_id in seen_chunks:
                    continue
                seen_chunks.add(chunk_id)
                supporting_chunks.append(chunk_id)

        return {
            "reports": [community.to_dict() for community in selected],
            "used_communities": used_communities,
            "supporting_chunks": supporting_chunks,
            "community_trace": {
                "query": query,
                "selected_count": len(selected),
                "community_version": selected[0].community_version if selected else "v0",
            },
        }

    async def load_communities(
        self,
        knowledge_id: str,
        *,
        status: str | None = None,
        community_version: str | None = None,
    ) -> list[GraphCommunity]:
        rows = await self.client.fetch_communities(
            knowledge_id,
            status=status,
            community_version=community_version,
        )
        return [GraphCommunity.from_dict(row) for row in rows]

    def build_global_answer(self, query: str, report_payload: dict) -> dict:
        reports = list(report_payload.get("reports") or [])
        map_results = [
            {
                "community_id": report.get("community_id"),
                "answer": str(report.get("report") or ""),
            }
            for report in reports
        ]
        combined = " ".join(
            result["answer"] for result in map_results if result.get("answer")
        ).strip()
        return {
            "content": combined or "No community report available.",
            "map_results": map_results,
            "reduce_trace": {
                "query": query,
                "combined": len(map_results),
                "strategy": "single_reduce",
            },
        }

    def build_drift_plan(self, query: str, report_payload: dict) -> dict:
        reports = list(report_payload.get("reports") or [])
        broad_answer = " ".join(
            str(report.get("report") or "") for report in reports[:1]
        ).strip()
        first_entities = list((reports[0] or {}).get("entities") or []) if reports else []
        if len(first_entities) >= 2:
            follow_up_questions = [f"{first_entities[0]} 如何影响 {first_entities[1]}？"]
        elif first_entities:
            follow_up_questions = [f"{first_entities[0]} 的关键关系是什么？"]
        else:
            follow_up_questions = [f"{query} 的关键证据链是什么？"]
        return {
            "broad_answer": broad_answer or "No broad community answer available.",
            "follow_up_questions": follow_up_questions[:1],
            "used_communities": list(report_payload.get("used_communities") or []),
        }


__all__ = ["CommunityGraphService"]

from __future__ import annotations

from zuno.services.graphrag.community.models import GraphCommunity


class CommunityReportBuilder:
    def build_report(self, community: GraphCommunity) -> str:
        entity_preview = "、".join(community.entities[:5]) if community.entities else "无实体"
        relation_preview = "；".join(
            f"{relation.get('source')} -> {relation.get('target')}"
            for relation in community.relations[:3]
        ) or "暂无关系摘要"
        chunk_preview = "、".join(community.supporting_chunks[:5]) if community.supporting_chunks else "无 chunk"
        return (
            f"Community {community.community_id} 聚焦于 {entity_preview}。"
            f" 该社区包含 {community.relation_count} 条关系。"
            f" 代表性路径：{relation_preview}。"
            f" 支撑 chunks：{chunk_preview}。"
        )


__all__ = ["CommunityReportBuilder"]

from __future__ import annotations

from collections import defaultdict, deque

from zuno.services.graphrag.community.models import GraphCommunity


class CommunityDetector:
    @staticmethod
    def detect_level0(
        *,
        knowledge_id: str,
        edges: list[dict],
        community_version: str = "v0",
    ) -> list[GraphCommunity]:
        adjacency: dict[str, set[str]] = defaultdict(set)
        normalized_edges: list[dict] = []
        for edge in edges or []:
            source = str(edge.get("source") or "").strip()
            target = str(edge.get("target") or "").strip()
            if not source or not target:
                continue
            adjacency[source].add(target)
            adjacency[target].add(source)
            normalized_edges.append(
                {
                    "source": source,
                    "target": target,
                    "relation_type": str(edge.get("relation_type") or "related_to"),
                    "chunk_ids": list(edge.get("chunk_ids") or []),
                }
            )

        communities: list[GraphCommunity] = []
        visited: set[str] = set()
        index = 0
        for entity in sorted(adjacency):
            if entity in visited:
                continue
            queue = deque([entity])
            component: set[str] = set()
            while queue:
                current = queue.popleft()
                if current in visited:
                    continue
                visited.add(current)
                component.add(current)
                for neighbor in sorted(adjacency.get(current) or []):
                    if neighbor not in visited:
                        queue.append(neighbor)

            community_relations = [
                edge
                for edge in normalized_edges
                if edge["source"] in component and edge["target"] in component
            ]
            chunk_ids: list[str] = []
            seen_chunks: set[str] = set()
            for relation in community_relations:
                for chunk_id in relation.get("chunk_ids") or []:
                    if chunk_id in seen_chunks:
                        continue
                    seen_chunks.add(chunk_id)
                    chunk_ids.append(chunk_id)

            communities.append(
                GraphCommunity(
                    community_id=f"{knowledge_id}::community::{index}",
                    knowledge_id=knowledge_id,
                    level=0,
                    entities=sorted(component),
                    relation_count=len(community_relations),
                    supporting_chunks=chunk_ids,
                    relations=community_relations,
                    community_version=community_version,
                )
            )
            index += 1
        return communities


__all__ = ["CommunityDetector"]

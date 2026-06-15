from __future__ import annotations

from zuno.services.retrieval.models import FusionResult, RetrievedDocument


class RetrievalFusion:
    @staticmethod
    def _graph_rank_adjustment(item: RetrievedDocument) -> tuple[int, int]:
        matched_by = set(item.metadata.get("matched_by") or [])
        graph_support = int(item.metadata.get("graph_support_count") or 0)
        graph_seed_hits = int(item.metadata.get("graph_seed_hit_count") or 0)
        graph_file_focus = int(item.metadata.get("graph_file_focus") or 0)
        if item.source_type != "graph" and "graph" not in matched_by:
            return (2, 0)
        if "vector" in matched_by:
            return (4 if graph_file_focus >= 2 else 3, graph_support + graph_seed_hits + graph_file_focus)
        if graph_file_focus >= 2 and graph_seed_hits >= 1:
            return (3, graph_support + graph_seed_hits + graph_file_focus)
        if graph_seed_hits >= 2:
            return (2, graph_support + graph_seed_hits + graph_file_focus)
        if graph_seed_hits >= 1 and graph_support >= 2:
            return (1, graph_support + graph_seed_hits + graph_file_focus)
        return (0, graph_support + graph_seed_hits + graph_file_focus)

    @staticmethod
    def _rank_key(query: str, item: RetrievedDocument) -> tuple[int, int, int, float]:
        from zuno.services.rag.handler import RagHandler

        class Proxy:
            pass

        proxy = Proxy()
        proxy.file_name = item.file_name
        proxy.content = item.content
        proxy.summary = item.summary
        proxy.score = item.score
        local_score, base_score = RagHandler._local_priority_score(query, proxy)
        graph_tier, graph_signal = RetrievalFusion._graph_rank_adjustment(item)
        return (graph_tier, local_score, graph_signal, base_score)

    def merge(
        self,
        *,
        query: str,
        documents_by_source: dict[str, list[RetrievedDocument]],
        top_k: int | None,
    ) -> FusionResult:
        merged: dict[str, RetrievedDocument] = {}
        dropped: list[RetrievedDocument] = []
        seen_fallback = 0

        for source_name, docs in documents_by_source.items():
            for doc in docs:
                key = doc.chunk_id or f"{source_name}:{seen_fallback}"
                if not doc.chunk_id:
                    seen_fallback += 1
                if key not in merged:
                    doc.metadata.setdefault("matched_by", [source_name])
                    merged[key] = doc
                    continue

                current = merged[key]
                matched_by = current.metadata.setdefault("matched_by", [])
                if source_name not in matched_by:
                    matched_by.append(source_name)
                current.metadata.setdefault("source_scores", {})[source_name] = doc.score
                if doc.score > current.score:
                    current.score = doc.score
                dropped.append(doc)

        ordered = sorted(merged.values(), key=lambda item: self._rank_key(query, item), reverse=True)
        if top_k:
            ordered = ordered[:top_k]

        return FusionResult(
            documents=ordered,
            dropped_documents=dropped,
            fusion_metadata={"merged_count": len(merged)},
            rerank_metadata={},
        )

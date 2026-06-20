from __future__ import annotations

from zuno.services.retrieval.models import FusionResult, RetrievedDocument


class RetrievalFusion:
    GRAPH_PROMOTION_THRESHOLD = 6

    @classmethod
    def _graph_signal(cls, item: RetrievedDocument) -> int:
        return (
            int(item.metadata.get("graph_support_count") or 0)
            + int(item.metadata.get("graph_seed_hit_count") or 0)
            + int(item.metadata.get("graph_file_focus") or 0)
            + int(item.metadata.get("graph_path_count") or 0)
        )

    @classmethod
    def _candidate_group(cls, item: RetrievedDocument) -> int:
        matched_by = set(item.metadata.get("matched_by") or [])
        has_vector = "vector" in matched_by or item.source_type == "vector"
        has_bm25 = "bm25" in matched_by or "keyword" in matched_by or item.source_type in {"bm25", "keyword"}
        has_graph = "graph" in matched_by or item.source_type == "graph"
        graph_signal = cls._graph_signal(item)

        if has_vector and has_graph and graph_signal >= cls.GRAPH_PROMOTION_THRESHOLD:
            return 0
        if has_vector or has_bm25:
            return 1
        if has_graph and graph_signal >= cls.GRAPH_PROMOTION_THRESHOLD + 3:
            return 1
        if has_graph and graph_signal >= cls.GRAPH_PROMOTION_THRESHOLD:
            return 2
        return 3

    @classmethod
    def _baseline_rank(cls, item: RetrievedDocument) -> int:
        vector_rank = int(item.metadata.get("vector_rank") or 10_000)
        keyword_rank = int(item.metadata.get("bm25_rank") or item.metadata.get("keyword_rank") or 10_000)
        baseline_rank = min(vector_rank, keyword_rank)
        if baseline_rank < 10_000:
            return baseline_rank
        graph_rank = int(item.metadata.get("graph_rank") or 10_000)
        if cls._graph_signal(item) >= cls.GRAPH_PROMOTION_THRESHOLD + 3:
            return min(graph_rank + 1, 10_000)
        return baseline_rank

    @staticmethod
    def _graph_rank_adjustment(item: RetrievedDocument) -> tuple[int, int]:
        matched_by = set(item.metadata.get("matched_by") or [])
        graph_support = int(item.metadata.get("graph_support_count") or 0)
        graph_seed_hits = int(item.metadata.get("graph_seed_hit_count") or 0)
        graph_file_focus = int(item.metadata.get("graph_file_focus") or 0)
        graph_path_count = int(item.metadata.get("graph_path_count") or 0)
        if item.source_type != "graph" and "graph" not in matched_by:
            return (2, 0)
        if "vector" in matched_by:
            return (
                4 if graph_file_focus >= 2 else 3,
                graph_support + graph_seed_hits + graph_file_focus + graph_path_count,
            )
        if graph_file_focus >= 2 and graph_seed_hits >= 1:
            return (3, graph_support + graph_seed_hits + graph_file_focus + graph_path_count)
        if graph_seed_hits >= 2:
            return (2, graph_support + graph_seed_hits + graph_file_focus + graph_path_count)
        if graph_seed_hits >= 1 and graph_support >= 2:
            return (1, graph_support + graph_seed_hits + graph_file_focus + graph_path_count)
        return (0, graph_support + graph_seed_hits + graph_file_focus + graph_path_count)

    @classmethod
    def _rank_key(cls, query: str, item: RetrievedDocument) -> tuple[int, int, int, int, float]:
        from zuno.services.rag.handler import RagHandler

        class Proxy:
            pass

        proxy = Proxy()
        proxy.file_name = item.file_name
        proxy.content = item.content
        proxy.summary = item.summary
        proxy.score = item.score
        local_score, base_score = RagHandler._local_priority_score(query, proxy)
        graph_tier, graph_signal = cls._graph_rank_adjustment(item)
        candidate_group = cls._candidate_group(item)
        baseline_rank = cls._baseline_rank(item)
        item.metadata["fusion_score"] = (
            (100 - candidate_group * 20)
            + (20 - min(baseline_rank, 20))
            + (graph_tier * 3)
            + graph_signal
            + local_score
            + base_score
        )
        return (candidate_group, baseline_rank, -graph_tier, -graph_signal, -(local_score + base_score))

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
            for index, doc in enumerate(docs, start=1):
                if source_name == "vector":
                    doc.metadata["vector_rank"] = index
                elif source_name in {"bm25", "keyword"}:
                    doc.metadata["bm25_rank"] = index
                elif source_name == "graph":
                    doc.metadata["graph_rank"] = index
                key = doc.chunk_id or f"{source_name}:{seen_fallback}"
                if not doc.chunk_id:
                    seen_fallback += 1
                if key not in merged:
                    doc.metadata.setdefault("matched_by", [source_name])
                    doc.metadata.setdefault("source", source_name)
                    merged[key] = doc
                    continue

                current = merged[key]
                matched_by = current.metadata.setdefault("matched_by", [])
                if source_name not in matched_by:
                    matched_by.append(source_name)
                current.metadata.setdefault("source_scores", {})[source_name] = doc.score
                if source_name == "vector":
                    current.metadata["vector_rank"] = index
                elif source_name in {"bm25", "keyword"}:
                    current.metadata["bm25_rank"] = index
                elif source_name == "graph":
                    current.metadata["graph_rank"] = index
                if doc.score > current.score:
                    current.score = doc.score
                dropped.append(doc)

        ordered = sorted(merged.values(), key=lambda item: self._rank_key(query, item))
        if top_k:
            ordered = ordered[:top_k]

        for item in ordered:
            item.metadata["source"] = "fused" if len(set(item.metadata.get("matched_by") or [])) > 1 else item.source_type

        return FusionResult(
            documents=ordered,
            dropped_documents=dropped,
            fusion_metadata={"merged_count": len(merged), "strategy": "baseline_preserving"},
            rerank_metadata={},
        )

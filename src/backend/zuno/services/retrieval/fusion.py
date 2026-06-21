from __future__ import annotations

import re

from zuno.services.retrieval.models import FusionResult, RetrievedDocument


class RetrievalFusion:
    GRAPH_PROMOTION_THRESHOLD = 6
    COMPARISON_SELECTION_SIZE = 3
    COMPARISON_MIN_SEEDS = 2
    BRIDGE_SELECTION_SIZE = 3
    BRIDGE_PROTECTED_TOP = 2
    BRIDGE_MIN_SEEDS = 2
    ENTITY_STOPWORDS = {
        "same",
        "nationality",
        "country",
        "birthplace",
        "city",
        "older",
        "younger",
        "earlier",
        "later",
        "larger",
        "smaller",
    }
    QUERY_ENTITY_PREFIX_PATTERN = re.compile(
        r"^(were|was|are|is|do|did|does|the|a|an|which|what|who)\s+",
        re.IGNORECASE,
    )
    QUERY_ENTITY_PHRASE_PATTERN = re.compile(r"[A-Z][A-Za-z0-9'_-]*(?:\s+[A-Z][A-Za-z0-9'_-]*)*")
    BRIDGE_RELATION_CUES = (
        "founded by",
        "founder of",
        "father of",
        "mother of",
        "professor at",
        "located in what city",
        "based in what city",
        "hail from",
        "where does",
        "director of",
        "author of",
        "performer of",
        "spouse of",
        "managed",
        "administration of",
        "born in what year",
        "served during what years",
        "population of",
    )

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
        chain_score = int(item.metadata.get("chain_completeness_score") or 0)
        if chain_score >= 4 and graph_rank < 10_000:
            return max(graph_rank - 1, 1)
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
    def _normalize_entity(cls, value: str) -> str:
        normalized = re.sub(r"\([^)]*\)", " ", str(value or ""))
        normalized = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff\s_-]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip().lower()
        return normalized

    @classmethod
    def _extract_comparison_seeds(cls, query: str, items: list[RetrievedDocument]) -> list[str]:
        from zuno.services.graphrag.retriever import GraphRetriever

        ordered: list[str] = []
        for phrase in cls.QUERY_ENTITY_PHRASE_PATTERN.findall(str(query or "")):
            normalized = cls._normalize_entity(cls.QUERY_ENTITY_PREFIX_PATTERN.sub("", phrase))
            if not normalized or normalized in cls.ENTITY_STOPWORDS:
                continue
            if len(normalized) < 3:
                continue
            if " " not in normalized:
                continue
            if any(normalized == seed or normalized in seed or seed in normalized for seed in ordered):
                continue
            ordered.append(normalized)
            if len(ordered) >= cls.COMPARISON_MIN_SEEDS:
                return ordered[: cls.COMPARISON_MIN_SEEDS]

        candidate_context = {
            "documents": [
                {
                    "title": item.file_name,
                    "file_name": item.file_name,
                }
                for item in items[:8]
            ]
        }
        raw_candidates = GraphRetriever._build_seed_entities_with_source(
            query,
            candidate_context=candidate_context,
            max_seed_entities=8,
        )
        for candidate in raw_candidates:
            normalized = cls._normalize_entity(candidate.get("value") or "")
            if not normalized or normalized in cls.ENTITY_STOPWORDS:
                continue
            if len(normalized) < 3:
                continue
            if " " not in normalized and any(normalized in seed.split() for seed in ordered):
                continue
            if any(normalized == seed or normalized in seed for seed in ordered):
                continue
            ordered.append(normalized)
            if len(ordered) >= cls.COMPARISON_MIN_SEEDS:
                break
        return ordered[: cls.COMPARISON_MIN_SEEDS]

    @classmethod
    def _seed_coverage(cls, item: RetrievedDocument, seeds: list[str]) -> set[str]:
        haystack = cls._normalize_entity(
            " ".join(
                [
                    item.file_name,
                    item.content,
                    item.summary,
                ]
            )
        )
        coverage: set[str] = set()
        for seed in seeds:
            if seed and seed in haystack:
                coverage.add(seed)
        return coverage

    @staticmethod
    def _is_baseline_candidate(item: RetrievedDocument) -> bool:
        matched_by = set(item.metadata.get("matched_by") or [])
        return item.source_type in {"vector", "bm25", "keyword"} or bool({"vector", "bm25", "keyword"} & matched_by)

    @staticmethod
    def _is_graph_only(item: RetrievedDocument) -> bool:
        matched_by = set(item.metadata.get("matched_by") or [])
        has_graph = item.source_type == "graph" or "graph" in matched_by
        has_baseline = bool({"vector", "bm25", "keyword"} & matched_by) or item.source_type in {"vector", "bm25", "keyword"}
        return has_graph and not has_baseline

    @classmethod
    def _annotate_comparison_metadata(
        cls,
        *,
        query: str,
        items: list[RetrievedDocument],
    ) -> dict[str, object]:
        from zuno.services.graphrag.retriever import GraphRetriever

        comparison_question = GraphRetriever._is_comparison_query(query)
        seeds = cls._extract_comparison_seeds(query, items) if comparison_question else []
        for item in items:
            coverage = cls._seed_coverage(item, seeds)
            connects_two = bool(item.metadata.get("graph_connects_two_seeds")) or len(coverage) >= 2
            item.metadata["comparison_question"] = comparison_question
            item.metadata["candidate_seed_coverage"] = sorted(coverage)
            item.metadata["connects_two_seeds"] = connects_two
            item.metadata["covers_missing_seed"] = False
            item.metadata["protects_chain_evidence"] = False
            item.metadata["promotion_blocked_reason"] = None
            item.metadata["chain_completeness_score"] = len(coverage) + (2 if connects_two else 0)
        return {
            "comparison_question": comparison_question,
            "comparison_seed_entities": seeds,
        }

    @classmethod
    def _extract_bridge_relation_cues(cls, query: str) -> list[str]:
        query_lower = str(query or "").lower()
        return [cue for cue in cls.BRIDGE_RELATION_CUES if cue in query_lower]

    @classmethod
    def _extract_bridge_seeds(cls, query: str, items: list[RetrievedDocument]) -> list[str]:
        ordered: list[str] = []
        for phrase in cls.QUERY_ENTITY_PHRASE_PATTERN.findall(str(query or "")):
            normalized = cls._normalize_entity(cls.QUERY_ENTITY_PREFIX_PATTERN.sub("", phrase))
            if not normalized or normalized in cls.ENTITY_STOPWORDS:
                continue
            if len(normalized) < 3:
                continue
            if " " not in normalized:
                continue
            if len(normalized.split()) > 4:
                continue
            if any(normalized == seed or normalized in seed or seed in normalized for seed in ordered):
                continue
            ordered.append(normalized)
            if len(ordered) >= cls.BRIDGE_MIN_SEEDS:
                return ordered[: cls.BRIDGE_MIN_SEEDS]

        baseline_candidates = [item for item in items if cls._is_baseline_candidate(item)]
        for candidate in baseline_candidates[:5]:
            normalized = cls._normalize_entity(candidate.file_name)
            if not normalized or normalized in cls.ENTITY_STOPWORDS:
                continue
            if len(normalized) < 3:
                continue
            if any(normalized == seed or normalized in seed or seed in normalized for seed in ordered):
                continue
            ordered.append(normalized)
            if len(ordered) >= cls.BRIDGE_MIN_SEEDS:
                break
        return ordered[: cls.BRIDGE_MIN_SEEDS]

    @classmethod
    def _bridge_relation_match_count(cls, item: RetrievedDocument, cues: list[str]) -> int:
        haystack = cls._normalize_entity(" ".join([item.file_name, item.content, item.summary]))
        return sum(1 for cue in cues if cls._normalize_entity(cue) in haystack)

    @classmethod
    def _annotate_bridge_metadata(
        cls,
        *,
        query: str,
        items: list[RetrievedDocument],
    ) -> dict[str, object]:
        from zuno.services.graphrag.retriever import GraphRetriever

        bridge_question = GraphRetriever._is_bridge_relation_query(query)
        bridge_seeds = cls._extract_bridge_seeds(query, items) if bridge_question else []
        bridge_cues = cls._extract_bridge_relation_cues(query) if bridge_question else []
        for item in items:
            coverage = cls._seed_coverage(item, bridge_seeds)
            relation_match_count = cls._bridge_relation_match_count(item, bridge_cues)
            item.metadata["bridge_relation_question"] = bridge_question
            item.metadata["bridge_seed_coverage"] = sorted(coverage)
            item.metadata["bridge_relation_cues"] = list(bridge_cues)
            item.metadata["bridge_chain_score"] = len(coverage) + relation_match_count
            item.metadata["bridge_promotion_blocked_reason"] = None
            item.metadata["noisy_bridge_graph_only"] = False
        return {
            "bridge_relation_question": bridge_question,
            "bridge_seed_entities": bridge_seeds,
            "bridge_relation_cues": bridge_cues,
        }

    @staticmethod
    def _combined_seed_coverage(items: list[RetrievedDocument]) -> set[str]:
        combined: set[str] = set()
        for item in items:
            combined.update(item.metadata.get("candidate_seed_coverage") or [])
        return combined

    @classmethod
    def _mark_chain_protection(cls, items: list[RetrievedDocument], seeds: set[str]) -> None:
        overall = cls._combined_seed_coverage(items)
        for item in items:
            coverage = set(item.metadata.get("candidate_seed_coverage") or [])
            remaining = overall - coverage
            protects = bool(coverage) and (remaining != overall) and not (remaining >= seeds)
            item.metadata["protects_chain_evidence"] = protects

    @classmethod
    def _pick_replacement_candidate(
        cls,
        *,
        remaining: list[RetrievedDocument],
        missing_seeds: set[str],
    ) -> RetrievedDocument | None:
        for candidate in remaining:
            coverage = set(candidate.metadata.get("candidate_seed_coverage") or [])
            connects_two = bool(candidate.metadata.get("connects_two_seeds"))
            if connects_two or coverage.intersection(missing_seeds):
                candidate.metadata["covers_missing_seed"] = bool(coverage.intersection(missing_seeds))
                return candidate
        return None

    @classmethod
    def _pick_removal_index(
        cls,
        *,
        selected: list[RetrievedDocument],
        forced_replacement: bool,
    ) -> int | None:
        combined = cls._combined_seed_coverage(selected)
        removable: list[tuple[int, int]] = []
        for index, item in enumerate(selected):
            coverage = set(item.metadata.get("candidate_seed_coverage") or [])
            remaining = combined - coverage
            removes_chain = combined != remaining and remaining != combined and bool(coverage)
            if not forced_replacement and removes_chain:
                continue
            remove_priority = 0
            if cls._is_graph_only(item):
                remove_priority += 3
            if not coverage:
                remove_priority += 2
            if not item.metadata.get("connects_two_seeds"):
                remove_priority += 1
            removable.append((remove_priority, index))
        if not removable:
            return None
        removable.sort(reverse=True)
        return removable[0][1]

    @classmethod
    def _apply_comparison_guardrail(
        cls,
        *,
        ordered: list[RetrievedDocument],
        comparison_seed_entities: list[str],
    ) -> list[RetrievedDocument]:
        if len(ordered) <= cls.COMPARISON_SELECTION_SIZE or len(comparison_seed_entities) < cls.COMPARISON_MIN_SEEDS:
            return ordered

        seeds = set(comparison_seed_entities)
        selected = list(ordered[: cls.COMPARISON_SELECTION_SIZE])
        remaining = list(ordered[cls.COMPARISON_SELECTION_SIZE :])

        while True:
            selected_coverage = cls._combined_seed_coverage(selected)
            missing_seeds = seeds - selected_coverage
            if not missing_seeds:
                break
            replacement = cls._pick_replacement_candidate(remaining=remaining, missing_seeds=missing_seeds)
            if replacement is None:
                break
            removal_index = cls._pick_removal_index(selected=selected, forced_replacement=True)
            if removal_index is None:
                break
            removed = selected[removal_index]
            selected[removal_index] = replacement
            remaining.remove(replacement)
            remaining.append(removed)

        if cls._combined_seed_coverage(selected) >= seeds:
            for index, item in list(enumerate(selected)):
                if not cls._is_graph_only(item):
                    continue
                if item.metadata.get("connects_two_seeds"):
                    continue
                remaining_sorted = sorted(remaining, key=lambda doc: ordered.index(doc))
                replacement = next(
                    (
                        candidate
                        for candidate in remaining_sorted
                        if cls._is_baseline_candidate(candidate)
                        and cls._combined_seed_coverage(selected[:index] + selected[index + 1 :] + [candidate]) >= seeds
                    ),
                    None,
                )
                if replacement is None:
                    continue
                item.metadata["promotion_blocked_reason"] = "comparison_chain_protection"
                selected[index] = replacement
                remaining.remove(replacement)
                remaining.append(item)

        cls._mark_chain_protection(selected, seeds)
        selected_ids = {id(item) for item in selected}
        selected = sorted(selected, key=lambda item: ordered.index(item))
        remainder = [item for item in ordered if id(item) not in selected_ids]
        return selected + remainder

    @classmethod
    def _apply_bridge_guardrail(
        cls,
        *,
        ordered: list[RetrievedDocument],
        bridge_seed_entities: list[str],
    ) -> list[RetrievedDocument]:
        if len(ordered) <= cls.BRIDGE_PROTECTED_TOP or len(bridge_seed_entities) < cls.BRIDGE_MIN_SEEDS:
            return ordered

        seeds = set(bridge_seed_entities)
        baseline_ordered = [item for item in ordered if cls._is_baseline_candidate(item)]
        baseline_top = baseline_ordered[: cls.BRIDGE_PROTECTED_TOP]
        baseline_coverage = set()
        for item in baseline_top:
            baseline_coverage.update(item.metadata.get("bridge_seed_coverage") or [])
        if baseline_coverage < seeds:
            return ordered

        selected = list(ordered[: cls.BRIDGE_SELECTION_SIZE])
        protected = selected[: cls.BRIDGE_PROTECTED_TOP]
        available_replacements = [
            item
            for item in baseline_top
            if all(id(item) != id(current) for current in protected)
        ]

        for index, item in enumerate(protected):
            coverage = set(item.metadata.get("bridge_seed_coverage") or [])
            if not cls._is_graph_only(item):
                continue
            if coverage >= seeds:
                continue
            replacement = next(
                (
                    candidate
                    for candidate in available_replacements
                    if candidate.metadata.get("bridge_seed_coverage")
                ),
                None,
            )
            if replacement is None:
                continue
            item.metadata["bridge_promotion_blocked_reason"] = "bridge_chain_protection"
            item.metadata["noisy_bridge_graph_only"] = not bool(coverage)
            selected[index] = replacement
            available_replacements.remove(replacement)

        selected_ids = {id(item) for item in selected}
        selected = sorted(selected, key=lambda item: ordered.index(item))
        remainder = [item for item in ordered if id(item) not in selected_ids]
        return selected + remainder

    @classmethod
    def _rank_key(cls, query: str, item: RetrievedDocument) -> tuple[int, int, int, int, int, float]:
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
        chain_score = int(item.metadata.get("chain_completeness_score") or 0)
        item.metadata["fusion_score"] = (
            (100 - candidate_group * 20)
            + (20 - min(baseline_rank, 20))
            + (graph_tier * 3)
            + graph_signal
            + local_score
            + base_score
            + chain_score * 2
        )
        return (candidate_group, baseline_rank, -chain_score, -graph_tier, -graph_signal, -(local_score + base_score))

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
                elif source_name == "requery":
                    doc.metadata["requery_rank"] = index
                    doc.metadata.setdefault("vector_rank", index)
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
                elif source_name == "requery":
                    current.metadata["requery_rank"] = index
                    current.metadata.setdefault("vector_rank", index)
                elif source_name in {"bm25", "keyword"}:
                    current.metadata["bm25_rank"] = index
                elif source_name == "graph":
                    current.metadata["graph_rank"] = index
                if doc.score > current.score:
                    current.score = doc.score
                dropped.append(doc)

        comparison_metadata = self._annotate_comparison_metadata(query=query, items=list(merged.values()))
        bridge_metadata = self._annotate_bridge_metadata(query=query, items=list(merged.values()))
        ordered = sorted(merged.values(), key=lambda item: self._rank_key(query, item))
        if comparison_metadata["comparison_question"]:
            ordered = self._apply_comparison_guardrail(
                ordered=ordered,
                comparison_seed_entities=list(comparison_metadata["comparison_seed_entities"]),
            )
        if bridge_metadata["bridge_relation_question"]:
            ordered = self._apply_bridge_guardrail(
                ordered=ordered,
                bridge_seed_entities=list(bridge_metadata["bridge_seed_entities"]),
            )
        if top_k:
            ordered = ordered[:top_k]

        for item in ordered:
            item.metadata["source"] = "fused" if len(set(item.metadata.get("matched_by") or [])) > 1 else item.source_type

        return FusionResult(
            documents=ordered,
            dropped_documents=dropped,
            fusion_metadata={
                "merged_count": len(merged),
                "strategy": "baseline_preserving",
                **comparison_metadata,
                **bridge_metadata,
            },
            rerank_metadata={},
        )

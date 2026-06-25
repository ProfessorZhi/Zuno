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
    GENEALOGY_PROTECTED_TOP = 5
    GENEALOGY_PROMOTION_SIGNAL_THRESHOLD = 2
    GENEALOGY_FULL_CHAIN_THRESHOLD = 3
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
    GENEALOGY_RELATION_CUES = (
        "maternal grandfather",
        "paternal grandfather",
        "grandfather",
        "grandmother",
        "father of",
        "mother of",
        "parent of",
        "child of",
        "son of",
        "daughter of",
        "spouse of",
        "wife of",
        "husband of",
        "sibling of",
        "brother of",
        "sister of",
        "family of",
        "born to",
        "relative of",
        "descendant of",
        "ancestor of",
        "married to",
        "children of",
        "who is the father",
        "who is the mother",
        "whose spouse",
        "whose child",
    )
    GENEALOGY_RELATION_TOKEN_MAP = {
        "maternal grandfather": ("maternal", "grandfather", "mother", "father"),
        "paternal grandfather": ("paternal", "grandfather", "father"),
        "grandfather": ("grandfather", "father"),
        "grandmother": ("grandmother", "mother"),
        "father of": ("father", "parent"),
        "mother of": ("mother", "parent"),
        "parent of": ("parent", "father", "mother"),
        "child of": ("child", "son", "daughter"),
        "son of": ("son", "child"),
        "daughter of": ("daughter", "child"),
        "spouse of": ("spouse", "wife", "husband", "married"),
        "wife of": ("wife", "spouse", "married"),
        "husband of": ("husband", "spouse", "married"),
        "sibling of": ("sibling", "brother", "sister"),
        "brother of": ("brother", "sibling"),
        "sister of": ("sister", "sibling"),
        "family of": ("family", "relative", "ancestor", "descendant"),
        "born to": ("born", "mother", "father", "parent"),
        "relative of": ("relative", "family"),
        "descendant of": ("descendant", "ancestor"),
        "ancestor of": ("ancestor", "descendant"),
        "married to": ("married", "spouse", "wife", "husband"),
        "children of": ("children", "child", "son", "daughter"),
        "who is the father": ("father", "parent"),
        "who is the mother": ("mother", "parent"),
        "whose spouse": ("spouse", "wife", "husband", "married"),
        "whose child": ("child", "son", "daughter"),
    }
    REQUERY_GENERIC_SEEDS = {
        "japanese",
        "american",
        "british",
        "canadian",
        "chinese",
        "french",
        "german",
        "italian",
        "korean",
        "russian",
        "spanish",
        "manga",
        "series",
        "band",
        "film",
        "movie",
        "novel",
        "song",
        "album",
        "city",
        "country",
        "university",
    }
    REQUERY_RELATION_TOKEN_MAP = {
        "born in what year": ("born", "birth", "year"),
        "hail from": ("from", "origin", "country", "canadian", "japanese"),
        "but where does": ("from", "origin", "country", "city"),
        "located in what city": ("city", "located", "based", "new york"),
        "based in what city": ("city", "located", "based", "new york"),
        "professor at": ("professor", "university", "city", "located"),
        "founded by": ("founded", "founder"),
        "father of": ("father", "founder"),
        "mother of": ("mother",),
        "director of": ("director",),
        "author of": ("author", "written", "illustrated"),
        "administration of": ("president", "administration", "served"),
        "served during what years": ("served", "years", "president"),
        "managed": ("managed", "timeframe", "years"),
        "population of": ("population", "inhabitants", "country"),
    }

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

        if cls._is_requery_only(item):
            confidence = int(item.metadata.get("requery_confidence_score") or 0)
            if item.metadata.get("requery_promotion_allowed") and confidence >= 2:
                return 1
            return 3

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

    @staticmethod
    def _is_requery_only(item: RetrievedDocument) -> bool:
        matched_by = {str(value or "").strip().lower() for value in (item.metadata.get("matched_by") or [])}
        return "requery" in matched_by and not bool({"vector", "bm25", "keyword", "graph"} & (matched_by - {"requery"}))

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
    def _extract_genealogy_relation_cues(cls, query: str) -> list[str]:
        query_lower = str(query or "").lower()
        return [cue for cue in cls.GENEALOGY_RELATION_CUES if cue in query_lower]

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

    @classmethod
    def _genealogy_relation_match_count(cls, item: RetrievedDocument, cues: list[str]) -> int:
        haystack = cls._normalize_entity(" ".join([item.file_name, item.content, item.summary]))
        relation_labels = [
            cls._normalize_entity(value)
            for value in (item.metadata.get("graph_path_relation_labels") or [])
            if cls._normalize_entity(value)
        ]
        count = 0
        for cue in cues:
            token_hits = cls.GENEALOGY_RELATION_TOKEN_MAP.get(cue, ())
            if any(token in haystack for token in token_hits):
                count += 1
                continue
            if any(token in " ".join(relation_labels) for token in token_hits):
                count += 1
        return count

    @staticmethod
    def _metadata_int(item: RetrievedDocument, key: str) -> int:
        return int(item.metadata.get(key) or 0)

    @classmethod
    def _genealogy_template_match(cls, item: RetrievedDocument) -> str | None:
        value = str(item.metadata.get("genealogy_path_template_match") or item.metadata.get("graph_path_template_match") or "").strip()
        return value or None

    @classmethod
    def _genealogy_relation_types(cls, item: RetrievedDocument) -> list[str]:
        raw_values = item.metadata.get("normalized_relation_types") or item.metadata.get("graph_path_relation_labels") or []
        ordered: list[str] = []
        seen: set[str] = set()
        for value in raw_values:
            normalized = cls._normalize_entity(str(value or "")).replace(" ", "_")
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)
        return ordered

    @classmethod
    def _relation_label_mismatch(cls, item: RetrievedDocument, cues: list[str], template_match: str | None) -> bool:
        if template_match:
            return False
        relation_types = cls._genealogy_relation_types(item)
        if not relation_types:
            return False
        family_hits = {"mother", "father", "parent", "child", "spouse", "wife", "husband", "sibling", "ancestor", "descendant"}
        if any(token in relation_type for relation_type in relation_types for token in family_hits):
            return False
        return bool(cues)

    @classmethod
    def _strong_genealogy_signal_count(
        cls,
        item: RetrievedDocument,
        *,
        relation_cue_match: bool,
        template_match: str | None,
        seed_entity_coverage: int,
        bridge_entity_coverage: int,
        text_support_count: int,
    ) -> int:
        strong_signals = [
            relation_cue_match,
            bool(template_match),
            seed_entity_coverage > 0,
            bridge_entity_coverage > 0,
            text_support_count > 0,
        ]
        return sum(1 for signal in strong_signals if signal)

    @classmethod
    def _extract_genealogy_seeds(cls, query: str, items: list[RetrievedDocument]) -> list[str]:
        ordered: list[str] = []
        for phrase in cls.QUERY_ENTITY_PHRASE_PATTERN.findall(str(query or "")):
            normalized = cls._normalize_entity(cls.QUERY_ENTITY_PREFIX_PATTERN.sub("", phrase))
            if not normalized or normalized in cls.ENTITY_STOPWORDS:
                continue
            if len(normalized) < 3:
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
    def _annotate_genealogy_metadata(
        cls,
        *,
        query: str,
        items: list[RetrievedDocument],
    ) -> dict[str, object]:
        genealogy_cues = cls._extract_genealogy_relation_cues(query)
        genealogy_question = bool(genealogy_cues)
        genealogy_seeds = cls._extract_genealogy_seeds(query, items) if genealogy_question else []
        for item in items:
            coverage = cls._seed_coverage(item, genealogy_seeds)
            relation_match_count = cls._genealogy_relation_match_count(item, genealogy_cues)
            relation_cue_match = bool(item.metadata.get("relation_cue_match")) or relation_match_count >= 1
            template_match = cls._genealogy_template_match(item)
            direct_relation_path = bool(item.metadata.get("direct_relation_path")) or bool(template_match)
            indirect_family_noise_path = bool(item.metadata.get("indirect_family_noise_path"))
            seed_entity_coverage = max(len(coverage), cls._metadata_int(item, "seed_entity_coverage"))
            bridge_entity_coverage = cls._metadata_int(item, "bridge_entity_coverage")
            text_support_count = max(cls._metadata_int(item, "text_unit_support_count"), cls._metadata_int(item, "graph_support_count"))
            high_degree_entity_noise = bool(item.metadata.get("high_degree_entity_noise"))
            graph_only_without_text_support = cls._is_graph_only(item) and text_support_count <= 0
            relation_label_mismatch = cls._relation_label_mismatch(item, genealogy_cues, template_match)
            community_only_support = "community" in set(item.metadata.get("matched_by") or []) and not cls._is_baseline_candidate(item)
            off_type_candidate = relation_label_mismatch and not relation_cue_match and not template_match
            strong_signal_count = cls._strong_genealogy_signal_count(
                item,
                relation_cue_match=relation_cue_match,
                template_match=template_match,
                seed_entity_coverage=seed_entity_coverage,
                bridge_entity_coverage=bridge_entity_coverage,
                text_support_count=text_support_count,
            )
            precision = (
                strong_signal_count
                + relation_match_count
                + (1 if direct_relation_path else 0)
                - (3 if indirect_family_noise_path else 0)
                - (2 if relation_label_mismatch else 0)
                - (2 if high_degree_entity_noise else 0)
            )
            allowed = (
                (strong_signal_count >= cls.GENEALOGY_PROMOTION_SIGNAL_THRESHOLD and not graph_only_without_text_support)
                or (bool(template_match) and text_support_count > 0)
            ) and not relation_label_mismatch and not indirect_family_noise_path and not high_degree_entity_noise and not community_only_support
            item.metadata["genealogy_bridge_question"] = genealogy_question
            item.metadata["genealogy_relation_cues"] = list(genealogy_cues)
            item.metadata["genealogy_seed_entities"] = list(genealogy_seeds)
            item.metadata["genealogy_seed_coverage"] = sorted(coverage)
            item.metadata["graph_path_relation_labels"] = list(item.metadata.get("graph_path_relation_labels") or [])
            item.metadata["normalized_relation_types"] = list(item.metadata.get("normalized_relation_types") or cls._genealogy_relation_types(item))
            item.metadata["graph_relation_cue_match"] = relation_cue_match
            item.metadata["relation_cue_match"] = relation_cue_match
            item.metadata["graph_path_template_match"] = template_match
            item.metadata["genealogy_path_template_match"] = template_match
            item.metadata["graph_text_support_count"] = text_support_count
            item.metadata["text_unit_support_count"] = text_support_count
            item.metadata["seed_entity_coverage"] = seed_entity_coverage
            item.metadata["bridge_entity_coverage"] = bridge_entity_coverage
            item.metadata["direct_relation_path"] = direct_relation_path
            item.metadata["indirect_family_noise_path"] = indirect_family_noise_path
            item.metadata["graph_only_without_text_support"] = graph_only_without_text_support
            item.metadata["high_degree_entity_noise"] = high_degree_entity_noise
            item.metadata["relation_label_mismatch"] = relation_label_mismatch
            item.metadata["community_only_support"] = community_only_support
            item.metadata["off_type_candidate"] = off_type_candidate
            item.metadata["graph_challenger_signal_count"] = strong_signal_count
            item.metadata["genealogy_path_precision_score"] = precision
            item.metadata["genealogy_promotion_allowed"] = allowed if genealogy_question else None
            item.metadata["genealogy_promotion_blocked_reason"] = None
            item.metadata["noisy_genealogy_graph_only"] = False
            if genealogy_question and cls._is_graph_only(item) and not allowed:
                blocked_reason = "low_precision_genealogy"
                if graph_only_without_text_support:
                    blocked_reason = "graph_only_without_text_support"
                elif relation_label_mismatch:
                    blocked_reason = "relation_label_mismatch"
                elif indirect_family_noise_path:
                    blocked_reason = "indirect_family_noise_path"
                elif high_degree_entity_noise:
                    blocked_reason = "high_degree_entity_noise"
                elif community_only_support:
                    blocked_reason = "community_only_support"
                elif off_type_candidate:
                    blocked_reason = "off_type_candidate"
                item.metadata["genealogy_promotion_blocked_reason"] = blocked_reason
                item.metadata["noisy_genealogy_graph_only"] = indirect_family_noise_path or not bool(coverage) or graph_only_without_text_support
        return {
            "genealogy_bridge_question": genealogy_question,
            "genealogy_relation_cues": list(genealogy_cues),
            "genealogy_seed_entities": list(genealogy_seeds),
        }

    @classmethod
    def _graph_challenger_rank_key(cls, item: RetrievedDocument) -> tuple[int, int, int, float]:
        return (
            int(item.metadata.get("graph_challenger_signal_count") or 0),
            int(item.metadata.get("graph_text_support_count") or 0),
            int(item.metadata.get("genealogy_path_precision_score") or 0),
            float(item.score or 0.0),
        )

    @classmethod
    def _genealogy_floor_has_full_chain(cls, selected: list[RetrievedDocument], genealogy_relation_cues: list[str]) -> bool:
        for item in selected:
            relation_match_count = cls._genealogy_relation_match_count(item, genealogy_relation_cues)
            text_support_count = max(cls._metadata_int(item, "graph_text_support_count"), cls._metadata_int(item, "text_unit_support_count"))
            template_match = cls._genealogy_template_match(item)
            if relation_match_count >= 1 and (template_match or text_support_count > 0):
                return True
        return False

    @classmethod
    def _extract_requery_seed_entities(cls, query: str) -> list[str]:
        ordered: list[str] = []
        for phrase in cls.QUERY_ENTITY_PHRASE_PATTERN.findall(str(query or "")):
            normalized = cls._normalize_entity(cls.QUERY_ENTITY_PREFIX_PATTERN.sub("", phrase))
            if not normalized or normalized in cls.ENTITY_STOPWORDS:
                continue
            if len(normalized) < 3:
                continue
            if normalized in cls.REQUERY_GENERIC_SEEDS:
                continue
            if any(normalized == seed or normalized in seed or seed in normalized for seed in ordered):
                continue
            ordered.append(normalized)
        return ordered[:4]

    @classmethod
    def _extract_requery_relation_cues(cls, query: str) -> list[str]:
        query_lower = str(query or "").lower()
        return [cue for cue in cls.REQUERY_RELATION_TOKEN_MAP if cue in query_lower]

    @classmethod
    def _annotate_requery_metadata(
        cls,
        *,
        query: str,
        items: list[RetrievedDocument],
    ) -> dict[str, object]:
        seed_entities = cls._extract_requery_seed_entities(query)
        relation_cues = cls._extract_requery_relation_cues(query)
        baseline_titles = [
            cls._normalize_entity(item.file_name)
            for item in items
            if cls._is_baseline_candidate(item) and not cls._is_requery_only(item)
        ][:5]
        for item in items:
            item.metadata["requery_confidence_score"] = None
            item.metadata["requery_promotion_allowed"] = None
            item.metadata["requery_promotion_blocked_reason"] = None
            item.metadata["requery_help_reason"] = None
            item.metadata["requery_noise_reason"] = None
            if not cls._is_requery_only(item):
                continue
            coverage = cls._seed_coverage(item, seed_entities)
            haystack = cls._normalize_entity(" ".join([item.file_name, item.content, item.summary]))
            baseline_anchor_match = 1 if any(anchor and anchor in haystack for anchor in baseline_titles) else 0
            relation_match = 0
            for cue in relation_cues:
                token_hits = cls.REQUERY_RELATION_TOKEN_MAP.get(cue, ())
                if any(token in haystack for token in token_hits):
                    relation_match = 1
                    break
            confidence = len(coverage) * 2 + baseline_anchor_match + relation_match
            allowed = confidence >= 2
            item.metadata["requery_seed_coverage"] = sorted(coverage)
            item.metadata["requery_relation_cues"] = list(relation_cues)
            item.metadata["requery_confidence_score"] = confidence
            item.metadata["requery_promotion_allowed"] = allowed
            if allowed:
                item.metadata["requery_help_reason"] = "seed_or_relation_supported"
            else:
                item.metadata["requery_promotion_blocked_reason"] = "low_confidence_requery"
                item.metadata["requery_noise_reason"] = "weak_related_neighbor"
        return {
            "requery_seed_entities": seed_entities,
            "requery_relation_cues": relation_cues,
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

        for item in ordered:
            if not cls._is_graph_only(item):
                continue
            coverage = set(item.metadata.get("bridge_seed_coverage") or [])
            if coverage >= seeds:
                continue
            item.metadata["bridge_promotion_blocked_reason"] = "bridge_chain_protection"
            item.metadata["noisy_bridge_graph_only"] = not bool(coverage)

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
    def _apply_genealogy_guardrail(
        cls,
        *,
        ordered: list[RetrievedDocument],
        genealogy_relation_cues: list[str],
    ) -> tuple[list[RetrievedDocument], dict[str, object]]:
        if len(ordered) <= cls.BRIDGE_PROTECTED_TOP or not genealogy_relation_cues:
            return ordered, {
                "graph_challenger_pool_size": 0,
                "graph_promotion_allowed": None,
                "graph_promotion_blocked_reason": None,
                "final_top5_floor_preserved": None,
            }

        baseline_floor = [item for item in ordered if cls._is_baseline_candidate(item)][: cls.GENEALOGY_PROTECTED_TOP]
        selected = list(baseline_floor or ordered[: cls.GENEALOGY_PROTECTED_TOP])
        remaining = [item for item in ordered if item not in selected]
        challenger_pool = [item for item in ordered if cls._is_graph_only(item)]
        promotion_allowed = False
        blocked_reason = None
        full_chain_floor = cls._genealogy_floor_has_full_chain(selected, genealogy_relation_cues)

        promoted_candidate = None
        promotion_candidates = [
            item
            for item in challenger_pool
            if item.metadata.get("genealogy_promotion_allowed") is True and item not in selected
        ]
        if promotion_candidates:
            candidate = sorted(promotion_candidates, key=cls._graph_challenger_rank_key, reverse=True)[0]
            candidate_signal_count = int(candidate.metadata.get("graph_challenger_signal_count") or 0)
            if full_chain_floor and candidate_signal_count < cls.GENEALOGY_FULL_CHAIN_THRESHOLD:
                blocked_reason = "standard_floor_full_chain"
                candidate.metadata["genealogy_promotion_blocked_reason"] = blocked_reason
            else:
                weakest_baseline = next(
                    (
                        item
                        for item in reversed(selected)
                        if cls._is_baseline_candidate(item)
                    ),
                    None,
                )
                if weakest_baseline is not None:
                    weakest_index = selected.index(weakest_baseline)
                    selected[weakest_index] = candidate
                    remaining.append(weakest_baseline)
                    if candidate in remaining:
                        remaining.remove(candidate)
                    promoted_candidate = candidate
                    promotion_allowed = True

        if not promotion_allowed and not blocked_reason:
            blocked_reason = next(
                (
                    str(item.metadata.get("genealogy_promotion_blocked_reason") or "").strip()
                    for item in challenger_pool
                    if str(item.metadata.get("genealogy_promotion_blocked_reason") or "").strip()
                ),
                None,
            )

        selected_ids = {id(item) for item in selected}
        selected = sorted(selected, key=lambda item: ordered.index(item) if item in ordered else 10_000)
        remainder = [item for item in ordered if id(item) not in selected_ids]
        final_top = selected[: cls.GENEALOGY_PROTECTED_TOP]
        floor_preserved = promoted_candidate is None
        return selected + remainder, {
            "graph_challenger_pool_size": len(challenger_pool),
            "graph_promotion_allowed": promotion_allowed,
            "graph_promotion_blocked_reason": blocked_reason,
            "final_top5_floor_preserved": floor_preserved,
        }

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
        genealogy_metadata = self._annotate_genealogy_metadata(query=query, items=list(merged.values()))
        requery_metadata = self._annotate_requery_metadata(query=query, items=list(merged.values()))
        ordered = sorted(merged.values(), key=lambda item: self._rank_key(query, item))
        genealogy_guardrail_metadata = {
            "graph_challenger_pool_size": 0,
            "graph_promotion_allowed": None,
            "graph_promotion_blocked_reason": None,
            "final_top5_floor_preserved": None,
        }
        if genealogy_metadata["genealogy_bridge_question"]:
            ordered, genealogy_guardrail_metadata = self._apply_genealogy_guardrail(
                ordered=ordered,
                genealogy_relation_cues=list(genealogy_metadata["genealogy_relation_cues"]),
            )
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
                **genealogy_metadata,
                **genealogy_guardrail_metadata,
                **requery_metadata,
            },
            rerank_metadata={},
        )

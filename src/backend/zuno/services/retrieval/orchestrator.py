from __future__ import annotations
import re

from zuno.services.graphrag.retriever import GraphRetriever
from zuno.services.graphrag.models import normalize_retrieval_mode
from zuno.services.graphrag.community.service import CommunityGraphService
from zuno.services.retrieval.fusion import RetrievalFusion
from zuno.services.retrieval.models import ProcessedQuery, RetrievalRequest, RetrievedDocument
from zuno.services.retrieval.planner import RetrievalPlanner
from zuno.services.retrieval.retrievers import (
    BM25RetrieverAdapter,
    GraphRetrieverAdapter,
    QueryProcessor,
    RagRetrieverAdapter,
    VectorRetrieverAdapter,
)


class QueryExpanderAdapter:
    async def expand(self, query: str) -> list[str]:
        from zuno.services.rewrite.query_write import query_rewriter

        variations = await query_rewriter.rewrite(query)
        ordered = [query]
        seen = {query.strip().lower()}
        for item in variations:
            text = str(item or "").strip()
            if not text:
                continue
            normalized = text.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            ordered.append(text)
        return ordered


class RetrievalOrchestrator:
    PROACTIVE_REQUERY_PATTERNS = (
        (r"\bbut where does\b", "bridge_attribute_pattern"),
        (r"\bhail from\b", "bridge_attribute_pattern"),
        (r"\blocated in what city\b", "bridge_attribute_pattern"),
        (r"\bbased in what city\b", "bridge_attribute_pattern"),
        (r"\bprofessor at\b", "bridge_attribute_pattern"),
        (r"\bfounded by\b", "bridge_attribute_pattern"),
        (r"\bfather of\b", "bridge_attribute_pattern"),
        (r"\bmother of\b", "bridge_attribute_pattern"),
        (r"\bdirector of\b", "bridge_attribute_pattern"),
        (r"\bauthor of\b", "bridge_attribute_pattern"),
        (r"\bmanaged .* during what timeframe\b", "bridge_attribute_pattern"),
        (r"\badministration of\b", "bridge_attribute_pattern"),
        (r"\bborn in what year\b", "bridge_attribute_pattern"),
        (r"\bserved during what years\b", "bridge_attribute_pattern"),
        (r"\bpopulation of\b", "bridge_attribute_pattern"),
        (r"\bcountry .* population\b", "bridge_attribute_pattern"),
    )

    def __init__(
        self,
        rag_retriever=None,
        graph_retriever=None,
        query_expander=None,
        *,
        planner: RetrievalPlanner | None = None,
        query_processor: QueryProcessor | None = None,
        fusion: RetrievalFusion | None = None,
        keyword_retriever=None,
        community_service: CommunityGraphService | None = None,
        max_rounds: int = 3,
    ):
        self.rag_retriever = rag_retriever or RagRetrieverAdapter()
        self.keyword_retriever = keyword_retriever or BM25RetrieverAdapter()
        self.graph_retriever = graph_retriever or GraphRetrieverAdapter()
        self.query_expander = query_expander or QueryExpanderAdapter()
        self.planner = planner or RetrievalPlanner()
        self.query_processor = query_processor or QueryProcessor()
        self.fusion = fusion or RetrievalFusion()
        self.community_service = community_service or CommunityGraphService()
        self.max_rounds = max(1, min(int(max_rounds or 1), 3))

    async def _run_community_global(
        self,
        query: str,
        knowledge_ids: list[str],
        retrieval_options: dict,
    ) -> dict:
        knowledge_id = knowledge_ids[0] if knowledge_ids else ""
        index_health = dict(retrieval_options.get("index_health") or {})
        community_version = str(index_health.get("community_version") or "v0")
        communities = await self.community_service.load_communities(
            knowledge_id,
            status="ready",
            community_version=community_version,
        )
        report_payload = self.community_service.search_reports(query, communities, limit=retrieval_options.get("top_k") or 3)
        answer_payload = self.community_service.build_global_answer(query, report_payload)
        return {
            "content": answer_payload.get("content") or "",
            "used_communities": list(report_payload.get("used_communities") or []),
            "supporting_chunks": list(report_payload.get("supporting_chunks") or []),
            "community_trace": dict(report_payload.get("community_trace") or {}),
            "map_results": list(answer_payload.get("map_results") or []),
            "reduce_trace": dict(answer_payload.get("reduce_trace") or {}),
        }

    async def _run_drift_like(
        self,
        query: str,
        knowledge_ids: list[str],
        retrieval_options: dict,
    ) -> dict:
        knowledge_id = knowledge_ids[0] if knowledge_ids else ""
        index_health = dict(retrieval_options.get("index_health") or {})
        community_version = str(index_health.get("community_version") or "v0")
        communities = await self.community_service.load_communities(
            knowledge_id,
            status="ready",
            community_version=community_version,
        )
        report_payload = self.community_service.search_reports(query, communities, limit=retrieval_options.get("top_k") or 3)
        drift_plan = self.community_service.build_drift_plan(query, report_payload)

        follow_up_questions = list(drift_plan.get("follow_up_questions") or [])[:1]
        evidence_parts: list[str] = []
        used_paths: list[str] = []
        citation_chunks: list[str] = []
        final_graph_result = {"used_communities": list(report_payload.get("used_communities") or []), "follow_up_questions": follow_up_questions}
        for follow_up in follow_up_questions:
            graph_result = await self.graph_retriever.retrieve(follow_up, knowledge_ids, retrieval_options)
            final_graph_result = graph_result | final_graph_result
            content = str(graph_result.get("content") or "").strip()
            if content:
                evidence_parts.append(content)
            used_paths.extend(list(graph_result.get("paths") or []))
            for document in graph_result.get("documents") or []:
                chunk_id = document.get("chunk_id")
                if chunk_id and chunk_id not in citation_chunks:
                    citation_chunks.append(chunk_id)

        final_content_parts = [str(drift_plan.get("broad_answer") or "").strip()]
        final_content_parts.extend(part for part in evidence_parts if part)
        final_content = "\n".join(part for part in final_content_parts if part)
        return {
            "content": final_content,
            "used_communities": list(report_payload.get("used_communities") or []),
            "supporting_chunks": list(report_payload.get("supporting_chunks") or []),
            "community_trace": dict(report_payload.get("community_trace") or {}),
            "follow_up_questions": follow_up_questions,
            "used_paths": used_paths,
            "drift_trace": {
                "broad_answer": drift_plan.get("broad_answer"),
                "follow_up_count": len(follow_up_questions),
            },
            "graph_result": final_graph_result,
            "citation_chunks": citation_chunks,
        }

    def _should_use_rag_entry_chunk(self, query: str, retrieval_options: dict) -> bool:
        if not retrieval_options.get("use_rag_entry_chunk", True):
            return False
        extractor = getattr(self.graph_retriever, "_extract_query_seeds", None)
        needs_entry_chunk = getattr(self.graph_retriever, "_needs_entry_chunk", None)
        worthy = getattr(self.graph_retriever, "_is_graph_worthy_query", None)
        if not callable(extractor) or not callable(worthy):
            return True
        seed_entities = extractor(query)
        if callable(needs_entry_chunk) and needs_entry_chunk(query, seed_entities):
            return True
        return not worthy(query, seed_entities)

    @staticmethod
    def _result_quality(mode: str, result: dict) -> str | None:
        internal_route = str(result.get("internal_route") or mode or "").strip().lower()
        raw_content = (result.get("raw_content") or result.get("content") or "").strip()
        if not raw_content or raw_content == "No relevant documents found.":
            return "empty_result"
        if internal_route == "local_graphrag":
            if not result.get("paths") and not result.get("entities"):
                return "graph_result_empty"
            return None
        document_count = result.get("document_count")
        requested_top_k = result.get("requested_top_k") or 0
        min_document_count = min(2, requested_top_k) if requested_top_k else 2
        if document_count is not None and document_count < min_document_count:
            return "too_few_documents"
        top_score = result.get("top_score")
        score_threshold = result.get("score_threshold")
        if top_score is not None and score_threshold is not None and top_score < score_threshold:
            return "low_rerank_score"
        if document_count == 0:
            return "no_relevant_documents"
        return None

    def _build_retry_plan(
        self,
        *,
        first_mode: str,
        fallback_reason: str | None,
        candidate_queries: list[str],
        fallback_policy: dict | None = None,
    ) -> list[dict]:
        fallback_policy = dict(fallback_policy or {})
        if not fallback_reason or not fallback_policy.get("allow_retry", True):
            return []
        attempts: list[dict] = []
        if fallback_policy.get("route_broadening", True) and first_mode in {"rag", "graphrag"}:
            attempts.append({"mode": "hybrid", "query": candidate_queries[0], "trigger": "route_broadening"})
        alternate_query = next(
            (
                candidate
                for candidate in candidate_queries[1:]
                if candidate.strip().lower() != candidate_queries[0].strip().lower()
            ),
            None,
        )
        if alternate_query and fallback_policy.get("query_rewrite_retry", True):
            attempts.append({"mode": "hybrid", "query": alternate_query, "trigger": "query_rewrite_retry"})
        max_rounds = int(fallback_policy.get("max_rounds") or self.max_rounds)
        max_rounds = max(1, min(max_rounds, 3))
        return attempts[: max(max_rounds - 1, 0)]

    @staticmethod
    def _dict_to_document(item: dict, *, source_type: str, source_backend: str) -> RetrievedDocument:
        metadata = dict(item.get("metadata") or {})
        for field_name in (
            "graph_support_count",
            "graph_seed_hit_count",
            "graph_file_focus",
            "modality",
            "source_url",
            "update_time",
        ):
            if field_name in item:
                metadata[field_name] = item.get(field_name)
        return RetrievedDocument(
            chunk_id=str(item.get("chunk_id") or ""),
            knowledge_id=str(item.get("knowledge_id") or ""),
            file_id=str(item.get("file_id") or ""),
            file_name=str(item.get("file_name") or item.get("source") or ""),
            content=str(item.get("content") or item.get("page_content") or item.get("text") or ""),
            summary=str(item.get("summary") or ""),
            score=float(item.get("score") or 0.0),
            normalized_score=item.get("normalized_score"),
            source_type=source_type,
            source_backend=source_backend,
            retrieval_reason=source_type,
            metadata=metadata,
        )

    @staticmethod
    def _serialize_documents(documents: list[RetrievedDocument]) -> list[dict]:
        return [doc.to_dict() for doc in documents]

    @staticmethod
    def _merge_document_content(documents: list[RetrievedDocument]) -> str:
        return "\n".join(doc.content for doc in documents if str(doc.content or "").strip())

    @staticmethod
    def _documents_include_source(documents: list[dict], source_name: str) -> bool:
        normalized = str(source_name or "").strip().lower()
        for item in documents:
            source_type = str(item.get("source_type") or "").strip().lower()
            matched_by = {str(value or "").strip().lower() for value in (item.get("metadata") or {}).get("matched_by") or []}
            if source_type == normalized or normalized in matched_by:
                return True
        return False

    @classmethod
    def _proactive_requery_reason(cls, query: str) -> str | None:
        query_text = str(query or "").strip().lower()
        for pattern, reason in cls.PROACTIVE_REQUERY_PATTERNS:
            if re.search(pattern, query_text):
                return reason
        return None

    @staticmethod
    def _standard_floor_gap(*, standard_floor_documents: list[dict], top_k: int | None) -> bool:
        required = min(int(top_k or 5), 5)
        return len(list(standard_floor_documents or [])) < max(required, 1)

    @staticmethod
    def _collect_candidate_blocked_reasons(documents: list[dict]) -> list[str]:
        reasons: list[str] = []
        for document in documents or []:
            metadata = dict(document.get("metadata") or {})
            for key in (
                "candidate_blocked_reason",
                "genealogy_promotion_blocked_reason",
                "requery_promotion_blocked_reason",
            ):
                value = str(metadata.get(key) or "").strip()
                if value and value not in reasons:
                    reasons.append(value)
        return reasons

    @staticmethod
    def _graph_activation_reason(
        *,
        query: str,
        graph_route_attempted: bool,
        graph_worthy: bool,
        fusion_metadata: dict,
    ) -> str | None:
        if not graph_route_attempted:
            return None
        if fusion_metadata.get("genealogy_bridge_question"):
            return "genealogy_bridge_pattern"
        if GraphRetriever._is_genealogy_relation_query(query):
            return "genealogy_bridge_pattern"
        if GraphRetriever._is_comparison_query(query):
            return "comparison_bridge_pattern"
        if GraphRetriever._is_bridge_relation_query(query):
            return "bridge_relation_pattern"
        if graph_worthy:
            return "graph_worthy_relation_question"
        return "graph_route_attempted"

    @staticmethod
    def _enhanced_activation_reason(
        *,
        normalized_mode: str,
        graph_route_attempted: bool,
        requery_attempted: bool,
        graph_contributed: bool,
        requery_contributed: bool,
        standard_floor_reused: bool,
        enhanced_noop: bool,
        enhanced_fallback_to_floor: bool,
        graph_activation_reason: str | None,
        requery_activation_reason: str | None,
    ) -> str | None:
        if normalized_mode != "rag_graph_deep":
            return None
        if graph_contributed and requery_contributed:
            return "graph_and_requery_confidence_gated"
        if graph_contributed:
            return graph_activation_reason or "graph_relation_activation"
        if requery_contributed:
            return requery_activation_reason or "requery_bridge_activation"
        if enhanced_fallback_to_floor:
            return "standard_floor_preserved_after_low_confidence_enhancement"
        if enhanced_noop or standard_floor_reused:
            return "standard_floor_only"
        if graph_route_attempted:
            return graph_activation_reason or "graph_route_attempted_without_gain"
        if requery_attempted:
            return requery_activation_reason or "requery_attempted_without_gain"
        return None

    @staticmethod
    def _missed_opportunity_trigger_reason(
        *,
        normalized_mode: str,
        route_selection_reason: str,
        standard_floor_gap: bool,
        graph_route_attempted: bool,
        graph_contributed: bool,
        requery_attempted: bool,
        requery_contributed: bool,
        graph_activation_reason: str | None,
        requery_activation_reason: str | None,
    ) -> str | None:
        if normalized_mode != "rag_graph_deep" or not standard_floor_gap:
            return None
        if route_selection_reason == "relation_question" and not graph_route_attempted and not requery_attempted:
            return "relation_floor_gap_without_activation"
        if graph_route_attempted and not graph_contributed and requery_attempted and not requery_contributed:
            return "graph_and_requery_recovery_incomplete"
        if graph_route_attempted and not graph_contributed:
            return graph_activation_reason or "graph_recovery_incomplete"
        if requery_attempted and not requery_contributed:
            return requery_activation_reason or "requery_recovery_incomplete"
        return None

    @staticmethod
    def _floor_preserved_reason(
        *,
        standard_floor_gap: bool,
        standard_floor_reused: bool,
        enhanced_noop: bool,
        enhanced_fallback_to_floor: bool,
        blocked_reasons: list[str],
    ) -> str | None:
        if standard_floor_gap:
            return None
        if blocked_reasons:
            return "standard_floor_chain_protection"
        if enhanced_fallback_to_floor:
            return "enhancement_channel_low_confidence"
        if enhanced_noop or standard_floor_reused:
            return "standard_floor_topk_complete"
        return None

    async def _run_single_pass(self, mode: str, query: str, knowledge_ids: list[str], retrieval_options: dict | None = None) -> dict:
        retrieval_options = retrieval_options or {}
        route_policy = str(retrieval_options.get("route_policy") or "auto").strip().lower()
        processed_payload = await self.query_processor.process(query)
        processed_query = (
            processed_payload
            if isinstance(processed_payload, ProcessedQuery)
            else ProcessedQuery(**processed_payload)
        )
        if route_policy == "force_graph":
            processed_query.query_features["relation_question"] = True
            processed_query.route_hints.append("force_graph_eval")
        elif route_policy == "force_deep":
            processed_query.query_features["global_question"] = True
            processed_query.query_features["evidence_required"] = True
            processed_query.route_hints.append("force_deep_eval")
        seed_entities = None
        graph_worthy = None
        seed_extractor = getattr(self.graph_retriever, "_extract_query_seeds", None)
        graph_worthy_checker = getattr(self.graph_retriever, "_is_graph_worthy_query", None)
        if callable(seed_extractor):
            seed_entities = list(seed_extractor(query))
        if callable(graph_worthy_checker):
            graph_worthy = bool(graph_worthy_checker(query, seed_entities or []))
        request = RetrievalRequest(
            query=query,
            knowledge_ids=knowledge_ids,
            mode=mode,
            requested_profile=retrieval_options.get("requested_profile") or retrieval_options.get("profile") or "auto",
            top_k=retrieval_options.get("top_k"),
            score_threshold=retrieval_options.get("score_threshold"),
            rerank_enabled=retrieval_options.get("rerank_enabled"),
            rerank_top_k=retrieval_options.get("rerank_top_k"),
            graph_hop_limit=retrieval_options.get("graph_hop_limit"),
            max_paths_per_entity=retrieval_options.get("max_paths_per_entity"),
            needs_query_rewrite=retrieval_options.get("needs_query_rewrite", True),
            trace_enabled=bool((retrieval_options.get("trace_policy") or {}).get("enabled", True)),
            budget_policy=dict(retrieval_options.get("budget_policy") or {}),
            fallback_policy=dict(retrieval_options.get("fallback_policy") or {}),
            trace_policy=dict(retrieval_options.get("trace_policy") or {}),
            scope_policy=dict(retrieval_options.get("scope_policy") or {}),
            index_version=dict(retrieval_options.get("index_version") or {}),
            index_health=dict(retrieval_options.get("index_health") or {}),
        )
        knowledge_capability = retrieval_options.get("knowledge_capability") or ("rag_graph" if knowledge_ids else "rag")
        plan = self.planner.build_plan(
            request,
            processed_query,
            knowledge_capability=knowledge_capability,
            rerank_available=bool(retrieval_options.get("rerank_available", True)),
        )

        documents_by_source: dict[str, list[RetrievedDocument]] = {}
        retriever_runs: list[dict] = []
        rag_result = {"content": "", "raw_content": "", "documents": [], "document_count": 0}
        keyword_result = {"content": "", "raw_content": "", "documents": []}
        graph_result = {"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}
        community_result = {
            "content": "",
            "used_communities": [],
            "supporting_chunks": [],
            "community_trace": {},
            "map_results": [],
            "reduce_trace": {},
            "follow_up_questions": [],
            "used_paths": [],
            "drift_trace": {},
            "citation_chunks": [],
        }

        if "vector" in plan.enabled_retrievers:
            rag_result = await self.rag_retriever.retrieve(query, knowledge_ids, retrieval_options)
            docs = [self._dict_to_document(item, source_type="vector", source_backend="milvus") for item in rag_result.get("documents") or []]
            documents_by_source["vector"] = docs
            retriever_runs.append({"source": "vector", "result_count": len(docs), "mode": mode})

        proactive_requery_queries = [
            candidate
            for candidate in (retrieval_options.get("proactive_requery_queries") or [])
            if str(candidate or "").strip() and str(candidate).strip().lower() != str(query).strip().lower()
        ]
        if proactive_requery_queries and "vector" in plan.enabled_retrievers and plan.internal_route in {"standard_rag", "local_graphrag"}:
            requery_documents: list[RetrievedDocument] = []
            for requery_query in proactive_requery_queries:
                requery_result = await self.rag_retriever.retrieve(requery_query, knowledge_ids, retrieval_options)
                requery_docs = [
                    self._dict_to_document(item, source_type="vector", source_backend="milvus")
                    for item in requery_result.get("documents") or []
                ]
                for index, requery_doc in enumerate(requery_docs, start=1):
                    requery_doc.metadata["matched_by"] = ["requery"]
                    requery_doc.metadata["requery_query"] = requery_query
                    requery_doc.metadata["requery_rank"] = index
                requery_documents.extend(requery_docs)
                retriever_runs.append(
                    {
                        "source": "requery",
                        "result_count": len(requery_docs),
                        "mode": mode,
                        "query": requery_query,
                    }
                )
            if requery_documents:
                documents_by_source["requery"] = requery_documents

        if "bm25" in plan.enabled_retrievers:
            keyword_result = await self.keyword_retriever.retrieve(query, knowledge_ids, retrieval_options)
            docs = [self._dict_to_document(item, source_type="bm25", source_backend="elasticsearch") for item in keyword_result.get("documents") or []]
            documents_by_source["bm25"] = docs
            retriever_runs.append({"source": "bm25", "result_count": len(docs), "mode": mode})

        if "graph" in plan.enabled_retrievers:
            graph_query = query
            candidate_context = {
                "documents": [
                    {
                        "title": document.get("file_name") or document.get("title"),
                        "file_name": document.get("file_name") or document.get("title"),
                    }
                    for document in rag_result.get("documents", [])[:5]
                ]
            }
            if self._should_use_rag_entry_chunk(query, retrieval_options) and rag_result.get("documents"):
                entry_text = "\n".join(
                    str(document.get("content") or document.get("page_content") or "")
                    for document in rag_result.get("documents", [])[:3]
                )
                graph_query = f"{query}\n{entry_text[:2000]}"
            graph_options = dict(retrieval_options)
            graph_options["candidate_context"] = candidate_context
            try:
                graph_result = await self.graph_retriever.retrieve(graph_query, knowledge_ids, graph_options)
            except TypeError:
                graph_result = await self.graph_retriever.retrieve(
                    graph_query,
                    knowledge_ids[0] if knowledge_ids else "",
                    graph_hop_limit=retrieval_options.get("graph_hop_limit", 2),
                    max_paths_per_entity=retrieval_options.get("max_paths_per_entity", 10),
                    candidate_context=candidate_context,
                )
            docs = [self._dict_to_document(item, source_type="graph", source_backend="neo4j") for item in graph_result.get("documents") or []]
            documents_by_source["graph"] = docs
            retriever_runs.append({"source": "graph", "result_count": len(docs), "mode": mode})

        if plan.internal_route == "community_global":
            community_result = await self._run_community_global(query, knowledge_ids, retrieval_options)
            retriever_runs.append(
                {
                    "source": "community",
                    "result_count": len(community_result.get("used_communities") or []),
                    "mode": mode,
                }
            )
        elif plan.internal_route == "drift_like":
            community_result = await self._run_drift_like(query, knowledge_ids, retrieval_options)
            graph_result = dict(community_result.get("graph_result") or graph_result)
            retriever_runs.append(
                {
                    "source": "community",
                    "result_count": len(community_result.get("used_communities") or []),
                    "mode": mode,
                }
            )

        baseline_documents_by_source = {
            source_name: list(source_docs)
            for source_name, source_docs in documents_by_source.items()
            if source_name in {"vector", "bm25"} and source_docs
        }
        standard_floor_result = self.fusion.merge(
            query=query,
            documents_by_source=baseline_documents_by_source,
            top_k=retrieval_options.get("top_k"),
        ) if baseline_documents_by_source else None
        fusion_result = self.fusion.merge(query=query, documents_by_source=documents_by_source, top_k=retrieval_options.get("top_k"))
        merged_content = "\n".join(doc.content for doc in fusion_result.documents if doc.content.strip())
        if plan.internal_route == "local_graphrag":
            content = merged_content or graph_result.get("content") or rag_result.get("content") or ""
        elif plan.internal_route in {"community_global", "drift_like"}:
            parts: list[str] = []
            for part in [community_result.get("content"), graph_result.get("content"), merged_content, rag_result.get("content"), keyword_result.get("content")]:
                cleaned = str(part or "").strip()
                if cleaned and cleaned not in parts:
                    parts.append(cleaned)
            content = "\n".join(parts)
        elif mode in {"hybrid", "hybrid_rag"}:
            if merged_content:
                parts = [merged_content]
                graph_content = str(graph_result.get("content") or "").strip()
                if graph_content and not (graph_result.get("documents") or []) and graph_content not in parts:
                    parts.append(graph_content)
                content = "\n".join(parts)
            else:
                parts: list[str] = []
                for part in [graph_result.get("content"), rag_result.get("content"), keyword_result.get("content")]:
                    cleaned = str(part or "").strip()
                    if cleaned and cleaned not in parts:
                        parts.append(cleaned)
                content = "\n".join(parts)
        else:
            content = merged_content or rag_result.get("content") or keyword_result.get("content") or ""

        top_score = max((doc.score for doc in fusion_result.documents), default=rag_result.get("top_score"))
        return {
            "mode": plan.resolved_mode,
            "internal_route": plan.internal_route,
            "content": content or "No relevant documents found.",
            "raw_content": content or "",
            "documents": [doc.to_dict() for doc in fusion_result.documents],
            "document_count": len(fusion_result.documents),
            "requested_top_k": retrieval_options.get("top_k"),
            "top_score": top_score,
            "score_threshold": retrieval_options.get("score_threshold"),
            "entities": graph_result.get("entities", []),
            "paths": graph_result.get("paths", []),
            "structured_paths": graph_result.get("structured_paths", []),
            "domain_pack_id": graph_result.get("domain_pack_id") or retrieval_options.get("domain_pack_id"),
            "rag_result": rag_result,
            "keyword_result": keyword_result,
            "graph_result": graph_result,
            "community_result": community_result,
            "fusion_metadata": dict(fusion_result.fusion_metadata or {}),
            "rerank_metadata": dict(fusion_result.rerank_metadata or {}),
            "standard_floor_documents": self._serialize_documents(standard_floor_result.documents) if standard_floor_result else [],
            "standard_floor_content": self._merge_document_content(standard_floor_result.documents) if standard_floor_result else "",
            "standard_floor_fusion_metadata": dict(standard_floor_result.fusion_metadata or {}) if standard_floor_result else {},
            "plan": plan.to_dict(),
            "retriever_runs": retriever_runs,
            "processed_query": {
                "original_query": processed_query.original_query,
                "normalized_query": processed_query.normalized_query,
                "rewritten_queries": list(processed_query.rewritten_queries),
                "intent_labels": list(processed_query.intent_labels),
                "query_features": dict(processed_query.query_features),
                "route_hints": list(processed_query.route_hints),
            },
            "seed_entities": seed_entities,
            "seed_entities_with_source": list(graph_result.get("seed_entities_with_source") or []),
            "graph_worthy": graph_worthy,
        }

    async def run(self, mode: str, query: str, knowledge_ids: list[str], retrieval_options: dict | None = None) -> dict:
        retrieval_options = retrieval_options or {}
        route_policy = str(retrieval_options.get("route_policy") or "auto").strip().lower()
        normalized_mode = normalize_retrieval_mode(mode)
        if retrieval_options.get("needs_query_rewrite", True):
            candidate_queries = await self.query_expander.expand(query)
        else:
            candidate_queries = [query]
        if not candidate_queries:
            candidate_queries = [query]
        proactive_requery_reason = None
        proactive_requery_queries: list[str] = []
        first_pass_options = dict(retrieval_options)
        if normalized_mode == "rag_graph_deep" and len(candidate_queries) > 1:
            proactive_requery_reason = self._proactive_requery_reason(query)
            if proactive_requery_reason:
                proactive_requery_queries = list(candidate_queries[1:2])
                first_pass_options["proactive_requery_queries"] = proactive_requery_queries
                first_pass_options["proactive_requery_reason"] = proactive_requery_reason

        first_pass = await self._run_single_pass(
            normalized_mode,
            candidate_queries[0],
            knowledge_ids,
            first_pass_options,
        )
        first_plan = dict(first_pass.get("plan") or {})
        first_mode = first_pass["mode"]
        first_internal_route = first_pass.get("internal_route") or first_plan.get("internal_route")
        first_quality = self._result_quality(first_mode, first_pass)
        rounds = [{
            "round": 1,
            "mode": first_mode,
            "internal_route": first_internal_route,
            "query": candidate_queries[0],
            "trigger": "initial",
            "quality_reason": first_quality,
            "document_count": first_pass.get("document_count"),
            "top_score": first_pass.get("top_score"),
            "score_threshold": first_pass.get("score_threshold"),
            "path_count": len(first_pass.get("paths") or []),
            "entity_count": len(first_pass.get("entities") or []),
            "content_found": bool(first_pass.get("raw_content")),
        }]
        attempts = self._build_retry_plan(
            first_mode=first_mode,
            fallback_reason=first_quality,
            candidate_queries=candidate_queries,
            fallback_policy=first_plan.get("fallback_policy"),
        )
        final_pass = first_pass
        final_quality = first_quality
        for index, attempt in enumerate(attempts, start=2):
            if final_quality is None:
                break
            current_pass = await self._run_single_pass(attempt["mode"], attempt["query"], knowledge_ids, retrieval_options)
            current_quality = self._result_quality(attempt["mode"], current_pass)
            rounds.append({
                "round": index,
                "mode": current_pass["mode"],
                "internal_route": current_pass.get("internal_route"),
                "query": attempt["query"],
                "trigger": attempt["trigger"],
                "quality_reason": current_quality,
                "document_count": current_pass.get("document_count"),
                "top_score": current_pass.get("top_score"),
                "score_threshold": current_pass.get("score_threshold"),
                "path_count": len(current_pass.get("paths") or []),
                "entity_count": len(current_pass.get("entities") or []),
                "content_found": bool(current_pass.get("raw_content")),
            })
            final_pass = current_pass
            final_quality = current_quality

        final_mode = final_pass["mode"]
        final_plan = dict(final_pass.get("plan") or first_plan)
        final_internal_route = final_pass.get("internal_route") or final_plan.get("internal_route")
        second_pass_used = len(rounds) >= 2
        processed_query_payload = final_pass.get("processed_query") or first_pass.get("processed_query") or {}
        query_features = dict(processed_query_payload.get("query_features") or {})
        internal_route = final_internal_route
        community_available = str((retrieval_options.get("index_health") or {}).get("community") or "").strip().lower() in {"ready", "active"}
        graph_available = (
            retrieval_options.get("knowledge_capability") == "rag_graph"
            and str((retrieval_options.get("index_health") or {}).get("graph") or "ready").strip().lower()
            not in {"unavailable", "failed", "stale"}
        )
        graph_route_attempted = internal_route in {"local_graphrag", "drift_like"}
        graph_route_used = bool(
            (final_pass.get("graph_result") or {}).get("documents")
            or (final_pass.get("graph_result") or {}).get("paths")
            or any(run.get("source") == "graph" for run in (final_pass.get("retriever_runs") or []))
        )
        requery_used = any(round_info["query"].strip().lower() != query.strip().lower() for round_info in rounds)
        requery_attempted = any(run.get("source") == "requery" for run in (final_pass.get("retriever_runs") or []))
        community_used = bool((final_pass.get("community_result") or {}).get("used_communities"))
        drift_used = internal_route == "drift_like"
        standard_floor_documents = list(final_pass.get("standard_floor_documents") or [])
        standard_floor_content = str(final_pass.get("standard_floor_content") or "")
        graph_contributed = self._documents_include_source(list(final_pass.get("documents") or []), "graph")
        requery_contributed = self._documents_include_source(list(final_pass.get("documents") or []), "requery")
        enhancement_channel_used = bool(graph_contributed or requery_contributed or community_used or drift_used)
        standard_floor_reused = False
        enhanced_noop = False
        enhanced_noop_reason = None
        enhanced_fallback_to_floor = False
        if normalized_mode == "rag_graph_deep" and standard_floor_documents and not enhancement_channel_used:
            final_pass["documents"] = list(standard_floor_documents)
            if standard_floor_content:
                final_pass["content"] = standard_floor_content
                final_pass["raw_content"] = standard_floor_content
            standard_floor_reused = True
            if graph_route_attempted or graph_route_used or requery_attempted:
                enhanced_fallback_to_floor = True
                enhanced_noop_reason = "enhancement_channel_low_confidence"
            else:
                enhanced_noop = True
                enhanced_noop_reason = "no_enhancement_channel_used"
        requery_fallback_to_floor = bool(requery_attempted and not requery_contributed)
        requery_documents = [
            doc for doc in (final_pass.get("documents") or [])
            if (doc.get("metadata") or {}).get("requery_confidence_score") is not None
        ]
        requery_confidences = [
            int((doc.get("metadata") or {}).get("requery_confidence_score") or 0)
            for doc in requery_documents
        ]
        requery_blocked_reasons = [
            (doc.get("metadata") or {}).get("requery_promotion_blocked_reason")
            for doc in requery_documents
            if (doc.get("metadata") or {}).get("requery_promotion_blocked_reason")
        ]
        if query_features.get("global_question") and query_features.get("evidence_required"):
            route_selection_reason = "global_question_with_evidence"
        elif query_features.get("global_question"):
            route_selection_reason = "global_question"
        elif query_features.get("relation_question"):
            route_selection_reason = "relation_question"
        else:
            route_selection_reason = "standard_question"
        fusion_metadata = dict(final_pass.get("fusion_metadata") or {})
        standard_floor_gap = self._standard_floor_gap(
            standard_floor_documents=standard_floor_documents,
            top_k=retrieval_options.get("top_k"),
        )
        blocked_reasons = self._collect_candidate_blocked_reasons(list(final_pass.get("documents") or []))
        for blocked_reason in requery_blocked_reasons:
            if blocked_reason and blocked_reason not in blocked_reasons:
                blocked_reasons.append(blocked_reason)
        graph_activation_reason = self._graph_activation_reason(
            query=query,
            graph_route_attempted=graph_route_attempted,
            graph_worthy=bool(final_pass.get("graph_worthy")),
            fusion_metadata=fusion_metadata,
        )
        requery_activation_reason = proactive_requery_reason if (requery_attempted or proactive_requery_queries) else None
        enhanced_activation_reason = self._enhanced_activation_reason(
            normalized_mode=normalized_mode,
            graph_route_attempted=graph_route_attempted,
            requery_attempted=requery_attempted,
            graph_contributed=graph_contributed,
            requery_contributed=requery_contributed,
            standard_floor_reused=standard_floor_reused,
            enhanced_noop=enhanced_noop,
            enhanced_fallback_to_floor=enhanced_fallback_to_floor,
            graph_activation_reason=graph_activation_reason,
            requery_activation_reason=requery_activation_reason,
        )
        missed_opportunity_trigger_reason = self._missed_opportunity_trigger_reason(
            normalized_mode=normalized_mode,
            route_selection_reason=route_selection_reason,
            standard_floor_gap=standard_floor_gap,
            graph_route_attempted=graph_route_attempted,
            graph_contributed=graph_contributed,
            requery_attempted=requery_attempted,
            requery_contributed=requery_contributed,
            graph_activation_reason=graph_activation_reason,
            requery_activation_reason=requery_activation_reason,
        )
        floor_preserved_reason = self._floor_preserved_reason(
            standard_floor_gap=standard_floor_gap,
            standard_floor_reused=standard_floor_reused,
            enhanced_noop=enhanced_noop,
            enhanced_fallback_to_floor=enhanced_fallback_to_floor,
            blocked_reasons=blocked_reasons,
        )
        metadata = {
            "plan": final_plan,
            "initial_plan": first_plan,
            "processed_query": processed_query_payload,
            "retriever_runs": final_pass.get("retriever_runs") or [],
            "requested_mode": first_plan.get("requested_mode"),
            "requested_profile": first_plan.get("requested_profile"),
            "resolved_mode": final_plan.get("resolved_mode") or final_mode,
            "internal_route": final_internal_route,
            "route_trace": dict(final_plan.get("route_trace") or {}),
            "resolved_profile": final_plan.get("resolved_profile"),
            "enabled_retrievers": list(final_plan.get("enabled_retrievers") or []),
            "seed_entities": final_pass.get("seed_entities"),
            "seed_entities_with_source": list(final_pass.get("seed_entities_with_source") or []),
            "graph_worthy": final_pass.get("graph_worthy"),
            "used_vector": any(
                run.get("source") == "vector" for run in (final_pass.get("retriever_runs") or [])
            ),
            "used_bm25": any(run.get("source") == "bm25" for run in (final_pass.get("retriever_runs") or [])),
            "used_graph": any(run.get("source") == "graph" for run in (final_pass.get("retriever_runs") or [])),
            "vector_used": any(
                run.get("source") == "vector" for run in (final_pass.get("retriever_runs") or [])
            ),
            "bm25_used": any(run.get("source") == "bm25" for run in (final_pass.get("retriever_runs") or [])),
            "graph_used": any(run.get("source") == "graph" for run in (final_pass.get("retriever_runs") or [])),
            "fusion_used": bool((final_pass.get("documents") or []) or (final_pass.get("retriever_runs") or [])),
            "rerank_used": bool((final_plan.get("rerank_policy") or {}).get("enabled")),
            "bm25_available": bool(retrieval_options.get("bm25_available", False)),
            "rerank_available": bool(retrieval_options.get("rerank_available", True)),
            "bm25_fallback_reason": (
                "bm25_backend_unavailable"
                if not bool(retrieval_options.get("bm25_available", False))
                else None
            ),
            "standard_floor_used": bool(
                any(run.get("source") == "vector" for run in (final_pass.get("retriever_runs") or []))
                or any(run.get("source") == "bm25" for run in (final_pass.get("retriever_runs") or []))
            ),
            "graph_route_attempted": graph_route_attempted,
            "graph_route_used": graph_route_used,
            "requery_available": bool(retrieval_options.get("needs_query_rewrite", True)),
            "requery_used": bool(requery_attempted or requery_used),
            "requery_triggered_reason": proactive_requery_reason,
            "requery_activation_reason": requery_activation_reason,
            "requery_queries": proactive_requery_queries,
            "requery_result_count": sum(
                int(run.get("result_count") or 0)
                for run in (final_pass.get("retriever_runs") or [])
                if run.get("source") == "requery"
            ),
            "requery_confidence_summary": {
                "count": len(requery_documents),
                "max_score": max(requery_confidences) if requery_confidences else None,
                "min_score": min(requery_confidences) if requery_confidences else None,
                "promoted_count": sum(
                    1
                    for doc in requery_documents
                    if (doc.get("metadata") or {}).get("requery_promotion_allowed") is True
                ),
                "blocked_count": sum(
                    1
                    for doc in requery_documents
                    if (doc.get("metadata") or {}).get("requery_promotion_allowed") is False
                ),
                "blocked_reasons": sorted(set(requery_blocked_reasons)),
            },
            "requery_fallback_to_floor": requery_fallback_to_floor,
            "community_available": community_available,
            "community_used": community_used,
            "drift_available": bool(graph_available and community_available),
            "drift_used": drift_used,
            "standard_floor_reused": standard_floor_reused,
            "enhanced_noop": enhanced_noop,
            "enhanced_noop_reason": enhanced_noop_reason,
            "enhanced_fallback_to_floor": enhanced_fallback_to_floor,
            "enhanced_activation_reason": enhanced_activation_reason,
            "graph_activation_reason": graph_activation_reason,
            "missed_opportunity_trigger_reason": missed_opportunity_trigger_reason,
            "candidate_blocked_reason": blocked_reasons[0] if blocked_reasons else None,
            "floor_preserved_reason": floor_preserved_reason,
            "graph_challenger_pool_size": fusion_metadata.get("graph_challenger_pool_size"),
            "graph_promotion_allowed": fusion_metadata.get("graph_promotion_allowed"),
            "graph_promotion_blocked_reason": fusion_metadata.get("graph_promotion_blocked_reason"),
            "final_top5_floor_preserved": fusion_metadata.get("final_top5_floor_preserved"),
            "confidence_gated_fusion_used": (
                str(fusion_metadata.get("strategy") or "").strip().lower()
                == "baseline_preserving"
            ),
            "final_rerank_used": bool((final_plan.get("rerank_policy") or {}).get("enabled")),
            "route_selection_reason": route_selection_reason,
            "used_communities": list(final_pass.get("community_result", {}).get("used_communities") or []),
            "used_paths": list(final_pass.get("community_result", {}).get("used_paths") or final_pass.get("paths") or []),
            "supporting_chunks": list(final_pass.get("community_result", {}).get("supporting_chunks") or []),
            "follow_up_questions": list(final_pass.get("community_result", {}).get("follow_up_questions") or []),
            "map_results": list(final_pass.get("community_result", {}).get("map_results") or []),
            "reduce_trace": dict(final_pass.get("community_result", {}).get("reduce_trace") or {}),
            "community_trace": dict(final_pass.get("community_result", {}).get("community_trace") or {}),
            "drift_trace": dict(final_pass.get("community_result", {}).get("drift_trace") or {}),
            "budget_policy": dict(final_plan.get("budget_policy") or {}),
            "fallback_policy": dict(final_plan.get("fallback_policy") or {}),
            "trace_policy": dict(final_plan.get("trace_policy") or {}),
            "scope_policy": dict(final_plan.get("scope_policy") or {}),
            "index_version": dict(final_plan.get("index_version") or {}),
            "index_health": dict(final_plan.get("index_health") or {}),
            "first_mode": first_mode,
            "final_mode": final_mode,
            "second_pass_used": second_pass_used,
            "fallback_triggered": second_pass_used,
            "fallback_reason": first_quality if second_pass_used else None,
            "final_quality_reason": final_quality,
            "round_count": len(rounds),
            "rounds": rounds,
            "query_variants": candidate_queries,
            "rewritten_query_used": any(round_info["query"].strip().lower() != query.strip().lower() for round_info in rounds),
            "rerank_info": dict(final_plan.get("rerank_policy") or {}),
            "citation_chunks": list(final_pass.get("community_result", {}).get("citation_chunks") or [
                doc.get("chunk_id")
                for doc in final_pass.get("documents", [])
                if doc.get("chunk_id")
            ]),
            "fusion_metadata": fusion_metadata,
            "fusion_strategy": fusion_metadata.get("strategy"),
            "first_pass_quality": {
                "document_count": first_pass.get("document_count"),
                "top_score": first_pass.get("top_score"),
                "score_threshold": first_pass.get("score_threshold"),
                "path_count": len(first_pass.get("paths") or []),
                "entity_count": len(first_pass.get("entities") or []),
            },
            "retrieval_options": retrieval_options,
            "route_policy": route_policy,
        }
        return {
            "actual_mode": final_mode,
            "first_mode": first_mode,
            "final_mode": final_mode,
            "domain_pack_id": final_pass.get("domain_pack_id"),
            "second_pass_used": second_pass_used,
            "fallback_triggered": second_pass_used,
            "fallback_reason": metadata["fallback_reason"],
            "round_count": metadata["round_count"],
            "content": final_pass["content"],
            "metadata": metadata,
            "first_pass_result": first_pass,
            "final_pass_result": final_pass,
            "rag_result": final_pass["rag_result"],
            "graph_result": final_pass["graph_result"],
        }

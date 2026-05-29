from __future__ import annotations

from dataclasses import asdict

from agentchat.services.graphrag.models import normalize_retrieval_mode
from agentchat.services.retrieval.fusion import RetrievalFusion
from agentchat.services.retrieval.models import ProcessedQuery, RetrievalRequest, RetrievedDocument
from agentchat.services.retrieval.planner import RetrievalPlanner
from agentchat.services.retrieval.retrievers import (
    BM25RetrieverAdapter,
    GraphRetrieverAdapter,
    QueryProcessor,
    VectorRetrieverAdapter,
)
from agentchat.settings import app_settings


class QueryExpanderAdapter:
    async def expand(self, query: str) -> list[str]:
        from agentchat.services.rewrite.query_write import query_rewriter

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


class RagRetrieverAdapter(VectorRetrieverAdapter):
    pass


class RetrievalOrchestrator:
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
        max_rounds: int = 3,
    ):
        self.rag_retriever = rag_retriever or RagRetrieverAdapter()
        self.keyword_retriever = keyword_retriever or BM25RetrieverAdapter()
        self.graph_retriever = graph_retriever or GraphRetrieverAdapter()
        self.query_expander = query_expander or QueryExpanderAdapter()
        self.planner = planner or RetrievalPlanner(enable_keyword_recall=app_settings.rag.enable_elasticsearch)
        self.query_processor = query_processor or QueryProcessor()
        self.fusion = fusion or RetrievalFusion()
        self.max_rounds = max(1, min(int(max_rounds or 1), 3))

    def _should_use_rag_entry_chunk(self, query: str, retrieval_options: dict) -> bool:
        if not retrieval_options.get("use_rag_entry_chunk", True):
            return False
        extractor = getattr(self.graph_retriever, "_extract_query_seeds", None)
        worthy = getattr(self.graph_retriever, "_is_graph_worthy_query", None)
        if not callable(extractor) or not callable(worthy):
            return True
        seed_entities = extractor(query)
        return not worthy(query, seed_entities)

    @staticmethod
    def _result_quality(mode: str, result: dict) -> str | None:
        raw_content = (result.get("raw_content") or result.get("content") or "").strip()
        if not raw_content or raw_content == "No relevant documents found.":
            return "empty_result"
        if mode == "graphrag":
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

    def _build_retry_plan(self, *, first_mode: str, fallback_reason: str | None, candidate_queries: list[str]) -> list[dict]:
        if not fallback_reason:
            return []
        attempts: list[dict] = []
        if first_mode in {"rag", "graphrag"}:
            attempts.append({"mode": "hybrid", "query": candidate_queries[0], "trigger": "route_broadening"})
        alternate_query = next(
            (
                candidate
                for candidate in candidate_queries[1:]
                if candidate.strip().lower() != candidate_queries[0].strip().lower()
            ),
            None,
        )
        if alternate_query:
            attempts.append({"mode": "hybrid", "query": alternate_query, "trigger": "query_rewrite_retry"})
        return attempts[: max(self.max_rounds - 1, 0)]

    @staticmethod
    def _dict_to_document(item: dict, *, source_type: str, source_backend: str) -> RetrievedDocument:
        metadata = dict(item.get("metadata") or {})
        for field_name in ("graph_support_count", "graph_seed_hit_count", "modality", "source_url", "update_time"):
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

    async def _run_single_pass(self, mode: str, query: str, knowledge_ids: list[str], retrieval_options: dict | None = None) -> dict:
        retrieval_options = retrieval_options or {}
        processed_payload = await self.query_processor.process(query)
        processed_query = (
            processed_payload
            if isinstance(processed_payload, ProcessedQuery)
            else ProcessedQuery(**processed_payload)
        )
        request = RetrievalRequest(
            query=query,
            knowledge_ids=knowledge_ids,
            mode=mode,
            top_k=retrieval_options.get("top_k"),
            score_threshold=retrieval_options.get("score_threshold"),
            rerank_enabled=retrieval_options.get("rerank_enabled"),
            rerank_top_k=retrieval_options.get("rerank_top_k"),
            graph_hop_limit=retrieval_options.get("graph_hop_limit"),
            max_paths_per_entity=retrieval_options.get("max_paths_per_entity"),
            needs_query_rewrite=retrieval_options.get("needs_query_rewrite", True),
            trace_enabled=True,
        )
        knowledge_capability = "rag_graph" if knowledge_ids else "rag"
        plan = self.planner.build_plan(request, processed_query, knowledge_capability=knowledge_capability)

        documents_by_source: dict[str, list[RetrievedDocument]] = {}
        retriever_runs: list[dict] = []
        rag_result = {"content": "", "raw_content": "", "documents": [], "document_count": 0}
        keyword_result = {"content": "", "raw_content": "", "documents": []}
        graph_result = {"content": "", "raw_content": "", "documents": [], "entities": [], "paths": []}

        if "vector" in plan.enabled_retrievers:
            rag_result = await self.rag_retriever.retrieve(query, knowledge_ids, retrieval_options)
            docs = [self._dict_to_document(item, source_type="vector", source_backend="milvus") for item in rag_result.get("documents") or []]
            documents_by_source["vector"] = docs
            retriever_runs.append({"source": "vector", "result_count": len(docs), "mode": mode})

        if "bm25" in plan.enabled_retrievers:
            keyword_result = await self.keyword_retriever.retrieve(query, knowledge_ids, retrieval_options)
            docs = [self._dict_to_document(item, source_type="bm25", source_backend="elasticsearch") for item in keyword_result.get("documents") or []]
            documents_by_source["bm25"] = docs
            retriever_runs.append({"source": "bm25", "result_count": len(docs), "mode": mode})

        if "graph" in plan.enabled_retrievers:
            graph_query = query
            if self._should_use_rag_entry_chunk(query, retrieval_options) and rag_result.get("documents"):
                entry_text = "\n".join(
                    str(document.get("content") or document.get("page_content") or "")
                    for document in rag_result.get("documents", [])[:3]
                )
                graph_query = f"{query}\n{entry_text[:2000]}"
            try:
                graph_result = await self.graph_retriever.retrieve(graph_query, knowledge_ids, retrieval_options)
            except TypeError:
                graph_result = await self.graph_retriever.retrieve(
                    graph_query,
                    knowledge_ids[0] if knowledge_ids else "",
                    graph_hop_limit=retrieval_options.get("graph_hop_limit", 2),
                    max_paths_per_entity=retrieval_options.get("max_paths_per_entity", 10),
                )
            docs = [self._dict_to_document(item, source_type="graph", source_backend="neo4j") for item in graph_result.get("documents") or []]
            documents_by_source["graph"] = docs
            retriever_runs.append({"source": "graph", "result_count": len(docs), "mode": mode})

        fusion_result = self.fusion.merge(query=query, documents_by_source=documents_by_source, top_k=retrieval_options.get("top_k"))
        merged_content = "\n".join(doc.content for doc in fusion_result.documents if doc.content.strip())
        if mode == "graphrag":
            content = merged_content or graph_result.get("content") or rag_result.get("content") or ""
        elif mode == "hybrid":
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
            "content": content or "No relevant documents found.",
            "raw_content": content or "",
            "documents": [doc.to_dict() for doc in fusion_result.documents],
            "document_count": len(fusion_result.documents),
            "requested_top_k": retrieval_options.get("top_k"),
            "top_score": top_score,
            "score_threshold": retrieval_options.get("score_threshold"),
            "entities": graph_result.get("entities", []),
            "paths": graph_result.get("paths", []),
            "rag_result": rag_result,
            "keyword_result": keyword_result,
            "graph_result": graph_result,
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
        }

    async def run(self, mode: str, query: str, knowledge_ids: list[str], retrieval_options: dict | None = None) -> dict:
        retrieval_options = retrieval_options or {}
        normalized_mode = normalize_retrieval_mode(mode)
        if retrieval_options.get("needs_query_rewrite", True):
            candidate_queries = await self.query_expander.expand(query)
        else:
            candidate_queries = [query]
        if not candidate_queries:
            candidate_queries = [query]

        first_pass = await self._run_single_pass(
            "hybrid" if normalized_mode == "auto" and "关系" in query else ("rag" if normalized_mode == "auto" else normalized_mode),
            candidate_queries[0],
            knowledge_ids,
            retrieval_options,
        )
        first_mode = first_pass["mode"]
        first_quality = self._result_quality(first_mode, first_pass)
        rounds = [{
            "round": 1,
            "mode": first_mode,
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
        attempts = self._build_retry_plan(first_mode=first_mode, fallback_reason=first_quality, candidate_queries=candidate_queries)
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
        second_pass_used = len(rounds) >= 2
        metadata = {
            "plan": final_pass.get("plan") or first_pass.get("plan") or {},
            "processed_query": final_pass.get("processed_query") or first_pass.get("processed_query") or {},
            "retriever_runs": final_pass.get("retriever_runs") or [],
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
            "first_pass_quality": {
                "document_count": first_pass.get("document_count"),
                "top_score": first_pass.get("top_score"),
                "score_threshold": first_pass.get("score_threshold"),
                "path_count": len(first_pass.get("paths") or []),
                "entity_count": len(first_pass.get("entities") or []),
            },
            "retrieval_options": retrieval_options,
        }
        return {
            "actual_mode": final_mode,
            "first_mode": first_mode,
            "final_mode": final_mode,
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

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from langgraph.constants import END, START
from langgraph.graph import StateGraph

from zuno.core.graphs.states import DomainQAState
from zuno.services.rag.handler import RagHandler
from zuno.services.retrieval.fusion import RetrievalFusion
from zuno.services.retrieval.models import ProcessedQuery, RetrievalRequest, RetrievedDocument
from zuno.services.retrieval.planner import RetrievalPlanner
from zuno.services.retrieval.retrievers import (
    BM25RetrieverAdapter,
    GraphRetrieverAdapter,
    QueryProcessor,
    VectorRetrieverAdapter,
)


class DomainQAGraph:
    _QUERY_FILLER_PATTERNS = (
        r"请用多\s*agent",
        r"请问",
        r"这份合同",
        r"这份",
        r"合同里",
        r"合同中",
        r"合同",
        r"是否",
        r"有没有",
        r"有无",
        r"能否",
        r"约定了",
        r"约定",
        r"要求",
        r"需要",
        r"请",
        r"吗",
        r"呢",
    )

    def __init__(
        self,
        retrieval_runner=None,
        *,
        planner: RetrievalPlanner | None = None,
        query_processor: QueryProcessor | None = None,
        vector_retriever=None,
        keyword_retriever=None,
        graph_retriever=None,
        fusion: RetrievalFusion | None = None,
    ):
        self.retrieval_runner = retrieval_runner
        self.planner = planner or RetrievalPlanner()
        self.query_processor = query_processor or QueryProcessor()
        self.vector_retriever = vector_retriever or VectorRetrieverAdapter()
        self.keyword_retriever = keyword_retriever or BM25RetrieverAdapter()
        self.graph_retriever = graph_retriever or GraphRetrieverAdapter()
        self.fusion = fusion or RetrievalFusion()
        self._compiled_graph = None

    def build_initial_state(
        self,
        *,
        user_id: str,
        agent_id: str,
        dialog_id: str,
        query: str,
        knowledge_ids: list[str] | None = None,
        domain_pack_id: str | None = None,
        runtime_settings: dict | None = None,
        domain_pack: dict | None = None,
    ) -> DomainQAState:
        return {
            "user_id": user_id,
            "agent_id": agent_id,
            "dialog_id": dialog_id,
            "query": query,
            "knowledge_ids": list(knowledge_ids or []),
            "domain_pack_id": domain_pack_id,
            "runtime_settings": runtime_settings,
            "domain_pack": domain_pack,
            "rewritten_queries": [query],
            "processed_query": None,
            "retrieval_plan": None,
            "retrieval_rounds": [],
            "retriever_runs": [],
            "documents_by_source": {},
            "vector_contexts": [],
            "graph_paths": [],
            "graph_path_strings": [],
            "tool_results": [],
            "retrieval_result": None,
            "draft_answer": None,
            "report_markdown": None,
            "citations": [],
            "evidence_bundle": {"items": [], "document_count": 0, "citation_count": 0},
            "evidence_quality": {
                "document_count": 0,
                "citation_count": 0,
                "graph_path_count": 0,
                "support_verdict": "not_evaluated",
                "status": "pending",
            },
            "fallback_decision": None,
            "support_verdict": {
                "status": "insufficient_evidence",
                "reason": "not_evaluated",
            },
            "final_answer": None,
            "trace_metadata": {},
            "cost_metadata": {},
            "status": "pending",
            "failure_metadata": None,
        }

    def append_trace(
        self,
        state: DomainQAState,
        *,
        node: str,
        payload: dict | None = None,
    ) -> DomainQAState:
        next_state = deepcopy(state)
        trace = dict(next_state.get("trace_metadata") or {})
        trace.setdefault("nodes", []).append({"node": node, "payload": payload or {}})
        next_state["trace_metadata"] = trace
        return next_state

    def _with_trace(
        self,
        state: DomainQAState,
        *,
        node: str,
        payload: dict | None = None,
    ) -> dict[str, Any]:
        updated = self.append_trace(state, node=node, payload=payload)
        return {"trace_metadata": updated.get("trace_metadata") or {}}

    def _failure_update(
        self,
        state: DomainQAState,
        *,
        node: str,
        error: Exception,
    ) -> dict[str, Any]:
        error_text = str(error).strip() or error.__class__.__name__
        updates = self._with_trace(
            state,
            node=node,
            payload={"status": "ERROR", "error": error_text},
        )
        updates["status"] = "failed"
        updates["failure_metadata"] = {"node": node, "error": error_text}
        return updates

    @staticmethod
    def _route_after_success_or_failure(state: DomainQAState, success_node: str) -> str:
        if str(state.get("status") or "").lower() == "failed":
            return "finalize"
        return success_node

    @staticmethod
    def _route_after_retry_decision(state: DomainQAState) -> str:
        if str(state.get("status") or "").lower() == "failed":
            return "finalize"
        decision = dict(state.get("fallback_decision") or {})
        action = str(decision.get("action") or "continue")
        if action == "retry":
            return "retrieve_evidence"
        return "generate_answer"

    @staticmethod
    def _merge_retrieval_options(
        runtime_settings: dict | None,
        domain_pack: dict | None,
    ) -> tuple[str, dict]:
        knowledge_config = (runtime_settings or {}).get("knowledge_config", {})
        retrieval_settings = dict(knowledge_config.get("retrieval_settings") or {})
        graph_index_settings = dict(knowledge_config.get("graph_index_settings") or {})
        retrieval_policy = dict((domain_pack or {}).get("retrieval_policy_data") or {})
        merged = {
            "top_k": retrieval_settings.get("top_k"),
            "score_threshold": retrieval_settings.get("score_threshold"),
            "needs_query_rewrite": True,
            "rerank_enabled": retrieval_settings.get("rerank_enabled"),
            "rerank_top_k": retrieval_settings.get("rerank_top_k"),
            "graph_hop_limit": retrieval_settings.get("graph_hop_limit", 2),
            "max_paths_per_entity": retrieval_settings.get("max_paths_per_entity", 10),
            "use_rag_entry_chunk": graph_index_settings.get("use_rag_entry_chunk", True),
            "knowledge_capability": knowledge_config.get("index_capability", "rag"),
            "domain_pack_id": (domain_pack or {}).get("id"),
            "requested_profile": retrieval_settings.get("profile", "auto"),
            "budget_policy": {},
            "fallback_policy": {},
            "trace_policy": {"enabled": True},
            "scope_policy": {
                "knowledge_ids": [],
                "domain_pack_id": (domain_pack or {}).get("id"),
                "status": str(
                    (runtime_settings or {}).get("knowledge_status")
                    or knowledge_config.get("index_settings", {}).get("status")
                    or "active"
                ),
            },
            "index_version": {
                "vector": str(
                    knowledge_config.get("index_settings", {}).get("index_version") or "v1"
                ),
                "graph": str(
                    knowledge_config.get("graph_index_settings", {}).get("index_version")
                    or "v1"
                ),
            },
            "index_health": {
                "vector": str(
                    knowledge_config.get("index_settings", {}).get("health_status") or "ready"
                ),
                "graph": str(
                    knowledge_config.get("graph_index_settings", {}).get("health_status")
                    or (
                        "ready"
                        if knowledge_config.get("index_capability") == "rag_graph"
                        else "unavailable"
                    )
                ),
            },
        }
        merged.update(retrieval_policy)
        merged["scope_policy"] = {
            "knowledge_ids": [],
            **dict(merged.get("scope_policy") or {}),
        }
        merged["budget_policy"] = {
            "top_k": merged.get("top_k"),
            "rerank_top_k": merged.get("rerank_top_k"),
            "graph_hop_limit": merged.get("graph_hop_limit"),
            "max_paths_per_entity": merged.get("max_paths_per_entity"),
            "rewrite_enabled": merged.get("needs_query_rewrite", True),
            **dict(merged.get("budget_policy") or {}),
        }
        merged["fallback_policy"] = {
            "allow_retry": True,
            "route_broadening": True,
            "query_rewrite_retry": True,
            **dict(merged.get("fallback_policy") or {}),
        }
        merged["trace_policy"] = {
            "enabled": True,
            **dict(merged.get("trace_policy") or {}),
        }
        default_mode = retrieval_settings.get("default_mode") or "rag"
        return str(default_mode), merged

    @classmethod
    def _query_terms(cls, query: str) -> set[str]:
        normalized = str(query or "").lower()
        normalized = re.sub(r"[^\w\u4e00-\u9fff]+", " ", normalized)
        for pattern in cls._QUERY_FILLER_PATTERNS:
            normalized = re.sub(pattern, " ", normalized)
        return {
            token
            for token in re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]+", normalized)
            if len(token) > 1
        }

    @staticmethod
    def _build_evidence_bundle(
        documents: list[dict[str, Any]],
        citations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        cited_keys = {
            (
                str(item.get("knowledge_id") or "").strip(),
                str(item.get("file_name") or "").strip(),
                str(item.get("chunk_id") or "").strip(),
            )
            for item in citations
        }
        items: list[dict[str, Any]] = []
        for document in documents[:5]:
            knowledge_id = str(document.get("knowledge_id") or "").strip()
            file_name = str(document.get("file_name") or "").strip()
            chunk_id = str(document.get("chunk_id") or "").strip()
            items.append(
                {
                    "knowledge_id": knowledge_id,
                    "file_name": file_name,
                    "chunk_id": chunk_id,
                    "excerpt": str(document.get("content") or "").strip()[:280],
                    "is_cited": (knowledge_id, file_name, chunk_id) in cited_keys,
                }
            )
        return {
            "items": items,
            "document_count": len(documents),
            "citation_count": len(citations),
        }

    @classmethod
    def _build_support_verdict(
        cls,
        *,
        query: str,
        documents: list[dict[str, Any]],
        citations: list[dict[str, Any]],
        graph_paths: list[dict[str, Any]],
        retrieval_plan: dict | None,
        domain_pack: dict | None = None,
    ) -> dict[str, Any]:
        retrieval_policy = dict((domain_pack or {}).get("retrieval_policy_data") or {})
        citation_strictness = str(retrieval_policy.get("citation_strictness") or "high").strip().lower()
        if not documents:
            return {"status": "insufficient_evidence", "reason": "no_documents"}
        if not citations and citation_strictness in {"medium", "high"}:
            return {"status": "insufficient_evidence", "reason": "missing_citations"}
        query_terms = cls._query_terms(query)
        if query_terms:
            cited_text = " ".join(
                str(item.get("content") or "")
                for item in documents[:5]
            ).lower()
            overlap = sum(1 for term in query_terms if term in cited_text)
            if overlap == 0:
                return {
                    "status": "insufficient_evidence",
                    "reason": "evidence_not_query_aligned",
                }
        resolved_mode = str((retrieval_plan or {}).get("resolved_mode") or "")
        if resolved_mode in {"graphrag", "hybrid"} and not graph_paths:
            return {"status": "insufficient_evidence", "reason": "missing_graph_paths"}
        return {"status": "supported", "reason": "cited_documents_present"}

    @staticmethod
    def _assess_evidence_quality(
        *,
        documents: list[dict[str, Any]],
        citations: list[dict[str, Any]],
        graph_paths: list[dict[str, Any]],
        support_verdict: dict[str, Any],
    ) -> dict[str, Any]:
        status = "ready" if support_verdict.get("status") == "supported" else "needs_retry"
        return {
            "document_count": len(documents),
            "citation_count": len(citations),
            "graph_path_count": len(graph_paths),
            "support_verdict": str(support_verdict.get("status") or "unknown"),
            "status": status,
        }

    @staticmethod
    def _dict_to_document(
        item: dict,
        *,
        source_type: str,
        source_backend: str,
    ) -> RetrievedDocument:
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

    async def _load_agent_config_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            runtime_settings = deepcopy(state.get("runtime_settings") or {})
            domain_pack = runtime_settings.get("domain_pack") or state.get("domain_pack")
            updates = self._with_trace(
                state,
                node="load_agent_config",
                payload={
                    "knowledge_ids": list(state.get("knowledge_ids") or []),
                    "has_domain_pack": bool(domain_pack),
                    "status": "OK",
                },
            )
            updates["runtime_settings"] = runtime_settings
            if domain_pack:
                updates["domain_pack"] = domain_pack
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="load_agent_config", error=err)

    async def _resolve_domain_pack_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            runtime_settings = state.get("runtime_settings") or {}
            domain_pack = state.get("domain_pack") or runtime_settings.get("domain_pack")
            domain_pack_id = (
                state.get("domain_pack_id")
                or runtime_settings.get("domain_pack_id")
                or (domain_pack or {}).get("id")
            )
            if domain_pack_id and not domain_pack:
                from zuno.services.domain_pack.loader import DomainPackLoader

                loaded_pack = DomainPackLoader().load(domain_pack_id)
                domain_pack = loaded_pack.to_dict() if loaded_pack else None
            updates = self._with_trace(
                state,
                node="resolve_domain_pack",
                payload={
                    "domain_pack_id": domain_pack_id,
                    "knowledge_ids": state.get("knowledge_ids") or [],
                    "status": "OK",
                },
            )
            updates["domain_pack_id"] = domain_pack_id
            updates["domain_pack"] = domain_pack
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="resolve_domain_pack", error=err)

    async def _route_intent_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            query = str(state.get("query") or "").strip()
            intent = "domain_qa" if query else "empty_query"
            updates = self._with_trace(
                state,
                node="route_intent",
                payload={"intent": intent, "status": "OK"},
            )
            updates["intent"] = intent
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="route_intent", error=err)

    async def _rewrite_query_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            query = str(state.get("query") or "").strip()
            rewritten_queries = [query] if query else []
            compact_query = " ".join(query.split()) if query else ""
            if compact_query and compact_query not in rewritten_queries:
                rewritten_queries.append(compact_query)
            updates = self._with_trace(
                state,
                node="rewrite_query",
                payload={
                    "rewritten_query_count": len(rewritten_queries),
                    "status": "OK",
                },
            )
            updates["rewritten_queries"] = rewritten_queries or list(
                state.get("rewritten_queries") or []
            )
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="rewrite_query", error=err)

    async def _plan_retrieval_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            runtime_settings = state.get("runtime_settings") or {}
            domain_pack = state.get("domain_pack") or {}
            mode, retrieval_options = self._merge_retrieval_options(runtime_settings, domain_pack)
            retrieval_options["scope_policy"] = {
                "knowledge_ids": list(state.get("knowledge_ids") or []),
                **dict(retrieval_options.get("scope_policy") or {}),
            }
            retrieval_query = str(
                (state.get("rewritten_queries") or [state.get("query") or ""])[-1]
            )
            processed_payload = await self.query_processor.process(retrieval_query)
            processed_query = (
                processed_payload
                if isinstance(processed_payload, ProcessedQuery)
                else ProcessedQuery(**processed_payload)
            )
            request = RetrievalRequest(
                query=retrieval_query,
                knowledge_ids=list(state.get("knowledge_ids") or []),
                mode=mode,
                requested_profile=retrieval_options.get("requested_profile")
                or retrieval_options.get("profile")
                or "auto",
                top_k=retrieval_options.get("top_k"),
                score_threshold=retrieval_options.get("score_threshold"),
                rerank_enabled=retrieval_options.get("rerank_enabled"),
                rerank_top_k=retrieval_options.get("rerank_top_k"),
                graph_hop_limit=retrieval_options.get("graph_hop_limit"),
                max_paths_per_entity=retrieval_options.get("max_paths_per_entity"),
                needs_query_rewrite=retrieval_options.get("needs_query_rewrite", True),
                trace_enabled=bool(
                    (retrieval_options.get("trace_policy") or {}).get("enabled", True)
                ),
                budget_policy=dict(retrieval_options.get("budget_policy") or {}),
                fallback_policy=dict(retrieval_options.get("fallback_policy") or {}),
                trace_policy=dict(retrieval_options.get("trace_policy") or {}),
                scope_policy=dict(retrieval_options.get("scope_policy") or {}),
                index_version=dict(retrieval_options.get("index_version") or {}),
                index_health=dict(retrieval_options.get("index_health") or {}),
            )
            plan = self.planner.build_plan(
                request,
                processed_query,
                knowledge_capability=retrieval_options.get("knowledge_capability", "rag"),
            )
            plan_dict = plan.to_dict()
            updates = self._with_trace(
                state,
                node="plan_retrieval",
                payload={
                    "resolved_mode": plan_dict.get("resolved_mode"),
                    "enabled_retrievers": plan_dict.get("enabled_retrievers"),
                    "requested_profile": plan_dict.get("requested_profile"),
                    "resolved_profile": plan_dict.get("resolved_profile"),
                    "status": "OK",
                },
            )
            updates["processed_query"] = {
                "original_query": processed_query.original_query,
                "normalized_query": processed_query.normalized_query,
                "rewritten_queries": list(processed_query.rewritten_queries),
                "intent_labels": list(processed_query.intent_labels),
                "query_features": dict(processed_query.query_features),
                "route_hints": list(processed_query.route_hints),
            }
            updates["retrieval_plan"] = plan_dict
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="plan_retrieval", error=err)

    async def _run_planned_retrievers(
        self,
        *,
        query: str,
        knowledge_ids: list[str],
        retrieval_plan: dict[str, Any],
        retrieval_options: dict[str, Any],
    ) -> tuple[dict[str, list[dict]], list[dict], dict, dict]:
        documents_by_source: dict[str, list[dict]] = {}
        retriever_runs: list[dict] = []
        rag_result = {"content": "", "raw_content": "", "documents": [], "document_count": 0}
        keyword_result = {"content": "", "raw_content": "", "documents": []}
        graph_result = {
            "content": "",
            "raw_content": "",
            "documents": [],
            "entities": [],
            "paths": [],
            "structured_paths": [],
        }
        enabled_retrievers = list(retrieval_plan.get("enabled_retrievers") or [])
        if self.retrieval_runner is not None:
            custom_result = await self.retrieval_runner(
                query=query,
                knowledge_ids=knowledge_ids,
                runtime_settings={"knowledge_config": {"retrieval_settings": retrieval_options}},
                domain_pack={"retrieval_policy_data": retrieval_options},
            )
            final_pass = dict(custom_result.get("final_pass_result") or {})
            documents_by_source["vector"] = list(final_pass.get("documents") or [])
            retriever_runs.append(
                {
                    "source": "custom_runner",
                    "result_count": len(documents_by_source["vector"]),
                    "mode": custom_result.get("actual_mode") or retrieval_plan.get("resolved_mode"),
                }
            )
            return documents_by_source, retriever_runs, custom_result, {
                "rag_result": rag_result,
                "keyword_result": keyword_result,
                "graph_result": dict(custom_result.get("graph_result") or {}),
            }

        if "vector" in enabled_retrievers:
            rag_result = await self.vector_retriever.retrieve(query, knowledge_ids, retrieval_options)
            documents_by_source["vector"] = list(rag_result.get("documents") or [])
            retriever_runs.append(
                {
                    "source": "vector",
                    "result_count": len(documents_by_source["vector"]),
                    "mode": retrieval_plan.get("resolved_mode"),
                }
            )

        if "bm25" in enabled_retrievers:
            keyword_result = await self.keyword_retriever.retrieve(query, knowledge_ids, retrieval_options)
            documents_by_source["bm25"] = list(keyword_result.get("documents") or [])
            retriever_runs.append(
                {
                    "source": "bm25",
                    "result_count": len(documents_by_source["bm25"]),
                    "mode": retrieval_plan.get("resolved_mode"),
                }
            )

        if "graph" in enabled_retrievers:
            graph_result = await self.graph_retriever.retrieve(query, knowledge_ids, retrieval_options)
            documents_by_source["graph"] = list(graph_result.get("documents") or [])
            retriever_runs.append(
                {
                    "source": "graph",
                    "result_count": len(documents_by_source["graph"]),
                    "mode": retrieval_plan.get("resolved_mode"),
                }
            )

        actual_mode = str(retrieval_plan.get("resolved_mode") or "rag")
        retrieval_result = {
            "actual_mode": actual_mode,
            "content": rag_result.get("content") or keyword_result.get("content") or graph_result.get("content") or "",
            "final_pass_result": {
                "documents": list(rag_result.get("documents") or []),
                "paths": list(graph_result.get("paths") or []),
                "structured_paths": list(graph_result.get("structured_paths") or []),
            },
            "graph_result": graph_result,
            "metadata": {
                "requested_mode": retrieval_plan.get("requested_mode"),
                "requested_profile": retrieval_plan.get("requested_profile"),
                "resolved_profile": retrieval_plan.get("resolved_profile"),
                "fallback_triggered": False,
                "scope_policy": dict(retrieval_plan.get("scope_policy") or {}),
                "index_version": dict(retrieval_plan.get("index_version") or {}),
                "index_health": dict(retrieval_plan.get("index_health") or {}),
                "plan": retrieval_plan,
                "retriever_runs": retriever_runs,
                "round_count": 1,
            },
            "round_count": 1,
        }
        return documents_by_source, retriever_runs, retrieval_result, {
            "rag_result": rag_result,
            "keyword_result": keyword_result,
            "graph_result": graph_result,
        }

    async def _retrieve_evidence_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            retrieval_plan = dict(state.get("retrieval_plan") or {})
            processed_query = dict(state.get("processed_query") or {})
            query = str(
                (processed_query.get("rewritten_queries") or state.get("rewritten_queries") or [state.get("query") or ""])[-1]
            )
            runtime_settings = state.get("runtime_settings") or {}
            domain_pack = state.get("domain_pack") or {}
            _, retrieval_options = self._merge_retrieval_options(runtime_settings, domain_pack)
            retrieval_options["scope_policy"] = dict(retrieval_plan.get("scope_policy") or {})
            retrieval_options["index_version"] = dict(retrieval_plan.get("index_version") or {})
            retrieval_options["index_health"] = dict(retrieval_plan.get("index_health") or {})
            retrieval_options["requested_profile"] = retrieval_plan.get("resolved_profile")
            retrieval_options["domain_pack_id"] = state.get("domain_pack_id")
            documents_by_source, retriever_runs, retrieval_result, raw_results = await self._run_planned_retrievers(
                query=query,
                knowledge_ids=list(state.get("knowledge_ids") or []),
                retrieval_plan=retrieval_plan,
                retrieval_options=retrieval_options,
            )
            graph_result = dict(raw_results.get("graph_result") or {})
            retrieval_rounds = list(state.get("retrieval_rounds") or [])
            retrieval_rounds.append(
                {
                    "round": len(retrieval_rounds) + 1,
                    "mode": retrieval_plan.get("resolved_mode"),
                    "query": query,
                    "enabled_retrievers": list(retrieval_plan.get("enabled_retrievers") or []),
                    "retriever_runs": retriever_runs,
                }
            )
            updates = self._with_trace(
                state,
                node="retrieve_evidence",
                payload={
                    "resolved_mode": retrieval_plan.get("resolved_mode"),
                    "retriever_runs": retriever_runs,
                    "round_count": len(retrieval_rounds),
                    "status": "OK",
                },
            )
            updates["documents_by_source"] = documents_by_source
            updates["retriever_runs"] = retriever_runs
            updates["retrieval_rounds"] = retrieval_rounds
            updates["retrieval_result"] = retrieval_result
            updates["graph_paths"] = list(graph_result.get("structured_paths") or [])
            updates["graph_path_strings"] = list(graph_result.get("paths") or [])
            updates["tool_results"] = [{"type": "retrieval", "result": retrieval_result}]
            updates["status"] = "running"
            return updates
        except Exception as err:
            updates = self._failure_update(state, node="retrieve_evidence", error=err)
            updates["documents_by_source"] = {}
            updates["retriever_runs"] = []
            updates["retrieval_result"] = None
            updates["graph_paths"] = []
            updates["graph_path_strings"] = []
            return updates

    async def _fuse_evidence_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            documents_by_source = dict(state.get("documents_by_source") or {})
            query = str((state.get("processed_query") or {}).get("normalized_query") or state.get("query") or "")
            converted_by_source: dict[str, list[RetrievedDocument]] = {}
            for source_name, docs in documents_by_source.items():
                backend = "neo4j" if source_name == "graph" else ("elasticsearch" if source_name == "bm25" else "milvus")
                converted_by_source[source_name] = [
                    self._dict_to_document(doc, source_type=source_name, source_backend=backend)
                    for doc in docs
                ]
            top_k = (state.get("retrieval_plan") or {}).get("budget_policy", {}).get("top_k")
            fusion_result = self.fusion.merge(
                query=query,
                documents_by_source=converted_by_source,
                top_k=top_k,
            )
            fused_documents = [doc.to_dict() for doc in fusion_result.documents]
            citations = [
                {
                    "chunk_id": str(doc.get("chunk_id") or ""),
                    "file_name": str(doc.get("file_name") or ""),
                    "knowledge_id": str(doc.get("knowledge_id") or ""),
                }
                for doc in fused_documents[:5]
            ]
            evidence_bundle = self._build_evidence_bundle(fused_documents, citations)
            updates = self._with_trace(
                state,
                node="fuse_evidence",
                payload={
                    "document_count": len(fused_documents),
                    "citation_count": len(citations),
                    "status": "OK",
                },
            )
            updates["vector_contexts"] = fused_documents
            updates["citations"] = citations
            updates["evidence_bundle"] = evidence_bundle
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="fuse_evidence", error=err)

    async def _verify_evidence_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            documents = list(state.get("vector_contexts") or [])
            citations = list(state.get("citations") or [])
            graph_paths = list(state.get("graph_paths") or [])
            retrieval_plan = dict(state.get("retrieval_plan") or {})
            support_verdict = self._build_support_verdict(
                query=str(state.get("query") or ""),
                documents=documents,
                citations=citations,
                graph_paths=graph_paths,
                retrieval_plan=retrieval_plan,
                domain_pack=state.get("domain_pack"),
            )
            evidence_quality = self._assess_evidence_quality(
                documents=documents,
                citations=citations,
                graph_paths=graph_paths,
                support_verdict=support_verdict,
            )
            updates = self._with_trace(
                state,
                node="verify_evidence",
                payload={
                    "citation_count": evidence_quality.get("citation_count"),
                    "graph_path_count": evidence_quality.get("graph_path_count"),
                    "support_verdict": support_verdict.get("status"),
                    "status": "OK",
                },
            )
            updates["support_verdict"] = support_verdict
            updates["evidence_quality"] = evidence_quality
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="verify_evidence", error=err)

    async def _maybe_retry_or_fallback_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            evidence_quality = dict(state.get("evidence_quality") or {})
            retrieval_plan = dict(state.get("retrieval_plan") or {})
            retrieval_rounds = list(state.get("retrieval_rounds") or [])
            fallback_policy = dict(retrieval_plan.get("fallback_policy") or {})
            should_retry = (
                evidence_quality.get("status") == "needs_retry"
                and fallback_policy.get("allow_retry", True)
                and len(retrieval_rounds) < 2
            )
            if should_retry:
                next_plan = dict(retrieval_plan)
                next_plan["resolved_mode"] = "hybrid"
                if "graph" not in next_plan.get("enabled_retrievers", []):
                    next_plan["enabled_retrievers"] = list(
                        dict.fromkeys(list(next_plan.get("enabled_retrievers", [])) + ["graph"])
                    )
                decision = {
                    "action": "retry",
                    "reason": evidence_quality.get("support_verdict"),
                    "next_mode": next_plan.get("resolved_mode"),
                }
                updates = self._with_trace(
                    state,
                    node="maybe_retry_or_fallback",
                    payload={**decision, "status": "OK"},
                )
                updates["retrieval_plan"] = next_plan
                updates["fallback_decision"] = decision
                updates["status"] = "running"
                return updates

            decision = {
                "action": "continue",
                "reason": evidence_quality.get("support_verdict"),
                "next_mode": retrieval_plan.get("resolved_mode"),
            }
            updates = self._with_trace(
                state,
                node="maybe_retry_or_fallback",
                payload={**decision, "status": "OK"},
            )
            updates["fallback_decision"] = decision
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="maybe_retry_or_fallback", error=err)

    @staticmethod
    def _render_template(template_text: str, values: dict[str, str]) -> str:
        rendered = template_text
        for key, value in values.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        return rendered

    @classmethod
    def _build_answer_markdown(cls, state: DomainQAState) -> tuple[str, str]:
        domain_pack = state.get("domain_pack") or {}
        documents = list(state.get("vector_contexts") or [])
        graph_paths = list(state.get("graph_paths") or [])
        graph_path_strings = list(state.get("graph_path_strings") or [])
        citations = list(state.get("citations") or [])
        top_document = documents[0] if documents else {}
        top_excerpt = str(top_document.get("content") or "").strip()
        top_excerpt = top_excerpt[:500] if top_excerpt else "未检索到明确条款片段。"
        path_lines = graph_path_strings[:5] or [
            f"{item.get('source')} -> {item.get('target')}"
            for item in graph_paths[:5]
        ]
        citation_lines = [
            f"- {item.get('file_name') or 'unknown'}#{item.get('chunk_id') or 'n/a'}"
            for item in citations
        ] or ["- 无"]
        risk_lines = path_lines or ["- 需要结合检索到的条款进一步人工确认风险。"]
        risk_block = "\n".join(risk_lines)
        citation_block = "\n".join(citation_lines)
        recommendation_text = "建议结合上述证据与风险点进一步补充人工审查意见。"
        answer = "\n".join(
            [
                "# Answer",
                "",
                "## Conclusion",
                top_excerpt,
                "",
                "## Evidence",
                top_excerpt,
                "",
                "## Graph Paths",
                risk_block,
                "",
                "## Citations",
                citation_block,
            ]
        )
        report = "\n".join(
            [
                "# Report",
                "",
                "## Summary",
                top_excerpt,
                "",
                "## Risks",
                risk_block,
                "",
                "## Evidence",
                top_excerpt,
                "",
                "## Recommendations",
                recommendation_text,
            ]
        )

        answer_template = str(domain_pack.get("answer_template_text") or "").strip()
        report_template = str(domain_pack.get("report_template_text") or "").strip()
        if answer_template:
            if "{{" in answer_template:
                answer = cls._render_template(
                    answer_template,
                    {
                        "conclusion": top_excerpt,
                        "evidence": top_excerpt,
                        "risks": risk_block,
                        "citations": citation_block,
                    },
                )
            else:
                answer = f"{answer_template}\n\n{answer}"
        if report_template:
            if "{{" in report_template:
                report = cls._render_template(
                    report_template,
                    {
                        "summary": top_excerpt,
                        "risks": risk_block,
                        "evidence": top_excerpt,
                        "recommendations": recommendation_text,
                    },
                )
            else:
                report = f"{report_template}\n\n{report}"
        return answer, report

    async def _generate_answer_node(self, state: DomainQAState) -> dict[str, Any]:
        if str(state.get("status") or "").lower() == "failed":
            failure = state.get("failure_metadata") or {}
            node = str(failure.get("node") or "unknown")
            error_text = str(failure.get("error") or "unknown error")
            answer = f"领域问答流程在 `{node}` 节点失败：{error_text}"
            report = "\n".join(
                [
                    "# Domain QA Failure Report",
                    "",
                    f"- failed_node: `{node}`",
                    f"- error: `{error_text}`",
                    f"- query: `{state.get('query') or ''}`",
                ]
            )
            updates = self._with_trace(
                state,
                node="generate_answer",
                payload={"status": "SKIPPED_AFTER_FAILURE", "failed_node": node},
            )
            updates["draft_answer"] = answer
            updates["report_markdown"] = report
            return updates
        try:
            answer, report = self._build_answer_markdown(state)
            updates = self._with_trace(
                state,
                node="generate_answer",
                payload={
                    "citation_count": len(state.get("citations") or []),
                    "path_count": len(state.get("graph_paths") or []),
                    "status": "OK",
                },
            )
            updates["draft_answer"] = answer
            updates["report_markdown"] = report
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="generate_answer", error=err)

    async def _citation_check_node(self, state: DomainQAState) -> dict[str, Any]:
        if str(state.get("status") or "").lower() == "failed":
            return self._with_trace(
                state,
                node="citation_check",
                payload={"status": "SKIPPED_AFTER_FAILURE"},
            )
        try:
            normalized: list[dict[str, Any]] = []
            seen: set[tuple[str, str, str]] = set()
            for citation in list(state.get("citations") or []):
                item = {
                    "chunk_id": str(citation.get("chunk_id") or "").strip(),
                    "file_name": str(citation.get("file_name") or "").strip(),
                    "knowledge_id": str(citation.get("knowledge_id") or "").strip(),
                }
                key = (item["knowledge_id"], item["file_name"], item["chunk_id"])
                if key in seen:
                    continue
                seen.add(key)
                normalized.append(item)
            support_verdict = self._build_support_verdict(
                query=str(state.get("query") or ""),
                documents=list(state.get("vector_contexts") or []),
                citations=normalized,
                graph_paths=list(state.get("graph_paths") or []),
                retrieval_plan=dict(state.get("retrieval_plan") or {}),
                domain_pack=state.get("domain_pack"),
            )
            evidence_quality = self._assess_evidence_quality(
                documents=list(state.get("vector_contexts") or []),
                citations=normalized,
                graph_paths=list(state.get("graph_paths") or []),
                support_verdict=support_verdict,
            )
            updates = self._with_trace(
                state,
                node="citation_check",
                payload={
                    "citation_count": len(normalized),
                    "graph_path_count": len(state.get("graph_paths") or []),
                    "support_verdict": support_verdict.get("status"),
                    "status": "OK",
                },
            )
            updates["citations"] = normalized
            updates["evidence_bundle"] = self._build_evidence_bundle(
                list(state.get("vector_contexts") or []),
                normalized,
            )
            updates["support_verdict"] = support_verdict
            updates["evidence_quality"] = evidence_quality
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="citation_check", error=err)

    async def _finalize_node(self, state: DomainQAState) -> dict[str, Any]:
        retrieval_result = state.get("retrieval_result") or {}
        failure = state.get("failure_metadata") or {}
        final_answer = state.get("draft_answer") or str(retrieval_result.get("content") or "")
        if str(state.get("status") or "").lower() == "failed" and not final_answer:
            failed_node = str(failure.get("node") or "unknown")
            error_text = str(failure.get("error") or "unknown error")
            final_answer = f"领域问答流程在 `{failed_node}` 节点失败：{error_text}"
        cost_metadata = {
            "document_count": len(state.get("vector_contexts") or []),
            "citation_count": len(state.get("citations") or []),
            "path_count": len(state.get("graph_paths") or []),
            "support_status": (state.get("support_verdict") or {}).get("status"),
            "used_domain_pack": bool(state.get("domain_pack_id")),
            "status": "failed" if str(state.get("status") or "").lower() == "failed" else "completed",
            "failed_node": failure.get("node"),
            "round_count": len(state.get("retrieval_rounds") or []),
        }
        updates = self._with_trace(state, node="finalize", payload=cost_metadata)
        updates["final_answer"] = final_answer
        updates["cost_metadata"] = cost_metadata
        updates["status"] = cost_metadata["status"]
        return updates

    async def _get_graph(self):
        if self._compiled_graph is None:
            workflow = StateGraph(DomainQAState)
            workflow.add_node("load_agent_config", self._load_agent_config_node)
            workflow.add_node("resolve_domain_pack", self._resolve_domain_pack_node)
            workflow.add_node("route_intent", self._route_intent_node)
            workflow.add_node("rewrite_query", self._rewrite_query_node)
            workflow.add_node("plan_retrieval", self._plan_retrieval_node)
            workflow.add_node("retrieve_evidence", self._retrieve_evidence_node)
            workflow.add_node("fuse_evidence", self._fuse_evidence_node)
            workflow.add_node("verify_evidence", self._verify_evidence_node)
            workflow.add_node("maybe_retry_or_fallback", self._maybe_retry_or_fallback_node)
            workflow.add_node("generate_answer", self._generate_answer_node)
            workflow.add_node("citation_check", self._citation_check_node)
            workflow.add_node("finalize", self._finalize_node)
            workflow.add_edge(START, "load_agent_config")
            workflow.add_conditional_edges(
                "load_agent_config",
                lambda state: self._route_after_success_or_failure(state, "resolve_domain_pack"),
                {"resolve_domain_pack": "resolve_domain_pack", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "resolve_domain_pack",
                lambda state: self._route_after_success_or_failure(state, "route_intent"),
                {"route_intent": "route_intent", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "route_intent",
                lambda state: self._route_after_success_or_failure(state, "rewrite_query"),
                {"rewrite_query": "rewrite_query", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "rewrite_query",
                lambda state: self._route_after_success_or_failure(state, "plan_retrieval"),
                {"plan_retrieval": "plan_retrieval", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "plan_retrieval",
                lambda state: self._route_after_success_or_failure(state, "retrieve_evidence"),
                {"retrieve_evidence": "retrieve_evidence", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "retrieve_evidence",
                lambda state: self._route_after_success_or_failure(state, "fuse_evidence"),
                {"fuse_evidence": "fuse_evidence", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "fuse_evidence",
                lambda state: self._route_after_success_or_failure(state, "verify_evidence"),
                {"verify_evidence": "verify_evidence", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "verify_evidence",
                lambda state: self._route_after_success_or_failure(state, "maybe_retry_or_fallback"),
                {"maybe_retry_or_fallback": "maybe_retry_or_fallback", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "maybe_retry_or_fallback",
                self._route_after_retry_decision,
                {
                    "retrieve_evidence": "retrieve_evidence",
                    "generate_answer": "generate_answer",
                    "finalize": "finalize",
                },
            )
            workflow.add_conditional_edges(
                "generate_answer",
                lambda state: self._route_after_success_or_failure(state, "citation_check"),
                {"citation_check": "citation_check", "finalize": "finalize"},
            )
            workflow.add_edge("citation_check", "finalize")
            workflow.add_edge("finalize", END)
            self._compiled_graph = workflow.compile()
        return self._compiled_graph

    async def ainvoke(self, state: DomainQAState) -> DomainQAState:
        graph = await self._get_graph()
        return await graph.ainvoke(state)

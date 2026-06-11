from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from langgraph.constants import END, START
from langgraph.graph import StateGraph

from agentchat.core.graphs.states import DomainQAState
from agentchat.services.rag.handler import RagHandler


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

    def __init__(self, retrieval_runner=None):
        self.retrieval_runner = retrieval_runner or self._default_retrieval_runner
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
            "vector_contexts": [],
            "graph_paths": [],
            "graph_path_strings": [],
            "tool_results": [],
            "draft_answer": None,
            "report_markdown": None,
            "citations": [],
            "evidence_bundle": {"items": [], "document_count": 0, "citation_count": 0},
            "support_verdict": {"status": "insufficient_evidence", "reason": "not_evaluated"},
            "final_answer": None,
            "trace_metadata": {},
            "cost_metadata": {},
            "status": "pending",
            "failure_metadata": None,
        }

    def append_trace(self, state: DomainQAState, *, node: str, payload: dict | None = None) -> DomainQAState:
        next_state = deepcopy(state)
        trace = dict(next_state.get("trace_metadata") or {})
        trace.setdefault("nodes", []).append({"node": node, "payload": payload or {}})
        next_state["trace_metadata"] = trace
        return next_state

    def _with_trace(self, state: DomainQAState, *, node: str, payload: dict | None = None) -> dict[str, Any]:
        updated = self.append_trace(state, node=node, payload=payload)
        return {"trace_metadata": updated.get("trace_metadata") or {}}

    @staticmethod
    def _build_evidence_bundle(documents: list[dict[str, Any]], citations: list[dict[str, Any]]) -> dict[str, Any]:
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

    @staticmethod
    def _build_support_verdict(documents: list[dict[str, Any]], citations: list[dict[str, Any]]) -> dict[str, Any]:
        if not documents:
            return {"status": "insufficient_evidence", "reason": "no_documents"}
        if not citations:
            return {"status": "insufficient_evidence", "reason": "missing_citations"}
        return {"status": "supported", "reason": "cited_documents_present"}

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

    @classmethod
    def _build_query_aware_support_verdict(
        cls,
        *,
        query: str,
        documents: list[dict[str, Any]],
        citations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        base = cls._build_support_verdict(documents, citations)
        if base.get("status") != "supported":
            return base
        query_terms = cls._query_terms(query)
        if not query_terms:
            return base
        cited_text = " ".join(
            str(item.get("excerpt") or item.get("content") or "")
            for item in cls._build_evidence_bundle(documents, citations).get("items", [])
            if item.get("is_cited")
        ).lower()
        overlap = sum(1 for term in query_terms if term in cited_text)
        if overlap == 0:
            return {"status": "insufficient_evidence", "reason": "evidence_not_query_aligned"}
        return base

    def _failure_update(self, state: DomainQAState, *, node: str, error: Exception) -> dict[str, Any]:
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
    def _merge_retrieval_options(runtime_settings: dict | None, domain_pack: dict | None) -> tuple[str, dict]:
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
                "vector": str(knowledge_config.get("index_settings", {}).get("index_version") or "v1"),
                "graph": str(knowledge_config.get("graph_index_settings", {}).get("index_version") or "v1"),
            },
            "index_health": {
                "vector": str(knowledge_config.get("index_settings", {}).get("health_status") or "ready"),
                "graph": str(
                    knowledge_config.get("graph_index_settings", {}).get("health_status")
                    or ("ready" if knowledge_config.get("index_capability") == "rag_graph" else "unavailable")
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

    @staticmethod
    async def _default_retrieval_runner(
        *,
        query: str,
        knowledge_ids: list[str],
        runtime_settings: dict | None,
        domain_pack: dict | None,
    ) -> dict:
        mode, retrieval_options = DomainQAGraph._merge_retrieval_options(runtime_settings, domain_pack)
        retrieval_options["scope_policy"] = {
            "knowledge_ids": list(knowledge_ids or []),
            **dict(retrieval_options.get("scope_policy") or {}),
        }
        return await RagHandler.retrieve_ranked_documents_with_metadata(
            query,
            knowledge_ids,
            knowledge_ids,
            retrieval_mode=mode,
            retrieval_options=retrieval_options,
        )

    async def _resolve_domain_pack_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            runtime_settings = state.get("runtime_settings") or {}
            domain_pack = state.get("domain_pack") or runtime_settings.get("domain_pack")
            domain_pack_id = (
                state.get("domain_pack_id")
                or runtime_settings.get("domain_pack_id")
                or (domain_pack or {}).get("id")
            )
            updates = self._with_trace(
                state,
                node="resolve_domain_pack",
                payload={"domain_pack_id": domain_pack_id, "knowledge_ids": state.get("knowledge_ids") or [], "status": "OK"},
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
                payload={"rewritten_query_count": len(rewritten_queries), "status": "OK"},
            )
            updates["rewritten_queries"] = rewritten_queries or list(state.get("rewritten_queries") or [])
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="rewrite_query", error=err)

    async def _retrieve_evidence_node(self, state: DomainQAState) -> dict[str, Any]:
        try:
            runtime_settings = state.get("runtime_settings") or {}
            domain_pack = state.get("domain_pack") or {}
            retrieval_query = str((state.get("rewritten_queries") or [state["query"]])[-1] or state["query"])
            result = await self.retrieval_runner(
                query=retrieval_query,
                knowledge_ids=state.get("knowledge_ids") or [],
                runtime_settings=runtime_settings,
                domain_pack=domain_pack,
            )
            final_pass = result.get("final_pass_result") or {}
            documents = list(final_pass.get("documents") or [])
            citations = [
                {
                    "chunk_id": str(doc.get("chunk_id") or ""),
                    "file_name": str(doc.get("file_name") or ""),
                    "knowledge_id": str(doc.get("knowledge_id") or ""),
                }
                for doc in documents[:5]
            ]
            evidence_bundle = self._build_evidence_bundle(documents, citations)
            support_verdict = self._build_query_aware_support_verdict(
                query=str(state.get("query") or ""),
                documents=documents,
                citations=citations,
            )
            updates = self._with_trace(
                state,
                node="retrieve_evidence",
                payload={
                    "actual_mode": result.get("actual_mode"),
                    "requested_mode": (result.get("metadata") or {}).get("requested_mode"),
                    "requested_profile": (result.get("metadata") or {}).get("requested_profile"),
                    "resolved_profile": (result.get("metadata") or {}).get("resolved_profile"),
                    "fallback_triggered": bool((result.get("metadata") or {}).get("fallback_triggered")),
                    "scope_status": ((result.get("metadata") or {}).get("scope_policy") or {}).get("status"),
                    "index_version": (result.get("metadata") or {}).get("index_version"),
                    "index_health": (result.get("metadata") or {}).get("index_health"),
                    "domain_pack_id": result.get("domain_pack_id"),
                    "document_count": len(documents),
                    "support_status": support_verdict.get("status"),
                    "status": "OK",
                },
            )
            updates.update(
                {
                    "retrieval_result": result,
                    "vector_contexts": documents,
                    "graph_paths": list((final_pass.get("structured_paths") or result.get("graph_result", {}).get("structured_paths") or [])),
                    "graph_path_strings": list((final_pass.get("paths") or result.get("graph_result", {}).get("paths") or [])),
                    "tool_results": [{"type": "retrieval", "result": result}],
                    "citations": citations,
                    "evidence_bundle": evidence_bundle,
                    "support_verdict": support_verdict,
                    "status": "running",
                }
            )
            return updates
        except Exception as err:
            updates = self._failure_update(state, node="retrieve_evidence", error=err)
            updates.update(
                {
                    "retrieval_result": None,
                    "vector_contexts": [],
                    "graph_paths": [],
                    "graph_path_strings": [],
                    "tool_results": [],
                    "citations": [],
                    "evidence_bundle": {"items": [], "document_count": 0, "citation_count": 0},
                    "support_verdict": {"status": "insufficient_evidence", "reason": "retrieval_error"},
                }
            )
            return updates

    @staticmethod
    def _build_answer_markdown(state: DomainQAState) -> tuple[str, str]:
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

        answer = "\n".join(
            [
                "结论",
                top_excerpt,
                "",
                "条款依据",
                top_excerpt,
                "",
                "风险点",
                *risk_lines,
                "",
                "引用",
                *citation_lines,
            ]
        )
        report = "\n".join(
            [
                "# Contract Review Report",
                "",
                "## 审查结论",
                top_excerpt,
                "",
                "## 风险列表",
                *risk_lines,
                "",
                "## 条款依据",
                top_excerpt,
                "",
                "## 修改建议",
                "建议结合上述条款与风险点进一步补充人工审查意见。",
            ]
        )

        answer_template = str(domain_pack.get("answer_template_text") or "").strip()
        report_template = str(domain_pack.get("report_template_text") or "").strip()
        if answer_template:
            answer = f"{answer_template}\n\n{answer}"
        if report_template:
            report = f"{report_template}\n\n{report}"
        return answer, report

    async def _draft_answer_node(self, state: DomainQAState) -> dict[str, Any]:
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
                node="draft_answer",
                payload={"status": "SKIPPED_AFTER_FAILURE", "failed_node": node},
            )
            updates["draft_answer"] = answer
            updates["report_markdown"] = report
            return updates
        try:
            answer, report = self._build_answer_markdown(state)
            updates = self._with_trace(
                state,
                node="draft_answer",
                payload={"citation_count": len(state.get("citations") or []), "path_count": len(state.get("graph_paths") or []), "status": "OK"},
            )
            updates["draft_answer"] = answer
            updates["report_markdown"] = report
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="draft_answer", error=err)

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
            updates = self._with_trace(
                state,
                node="citation_check",
                payload={
                    "citation_count": len(normalized),
                    "support_status": self._build_query_aware_support_verdict(
                        query=str(state.get("query") or ""),
                        documents=list(state.get("vector_contexts") or []),
                        citations=normalized,
                    ).get("status"),
                    "status": "OK",
                },
            )
            updates["citations"] = normalized
            updates["evidence_bundle"] = self._build_evidence_bundle(list(state.get("vector_contexts") or []), normalized)
            updates["support_verdict"] = self._build_query_aware_support_verdict(
                query=str(state.get("query") or ""),
                documents=list(state.get("vector_contexts") or []),
                citations=normalized,
            )
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
        }
        updates = self._with_trace(state, node="finalize", payload=cost_metadata)
        updates["final_answer"] = final_answer
        updates["cost_metadata"] = cost_metadata
        updates["status"] = cost_metadata["status"]
        return updates

    async def _get_graph(self):
        if self._compiled_graph is None:
            workflow = StateGraph(DomainQAState)
            workflow.add_node("resolve_domain_pack", self._resolve_domain_pack_node)
            workflow.add_node("route_intent", self._route_intent_node)
            workflow.add_node("rewrite_query", self._rewrite_query_node)
            workflow.add_node("retrieve_evidence", self._retrieve_evidence_node)
            workflow.add_node("draft_answer", self._draft_answer_node)
            workflow.add_node("citation_check", self._citation_check_node)
            workflow.add_node("finalize", self._finalize_node)
            workflow.add_edge(START, "resolve_domain_pack")
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
                lambda state: self._route_after_success_or_failure(state, "retrieve_evidence"),
                {"retrieve_evidence": "retrieve_evidence", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "retrieve_evidence",
                lambda state: self._route_after_success_or_failure(state, "draft_answer"),
                {"draft_answer": "draft_answer", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "draft_answer",
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

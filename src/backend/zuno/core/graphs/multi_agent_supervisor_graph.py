from __future__ import annotations

from copy import deepcopy
from typing import Any

from langgraph.constants import END, START
from langgraph.graph import StateGraph

from zuno.core.graphs.domain_qa_graph import DomainQAGraph
from zuno.core.graphs.states import MultiAgentSupervisorState


class MultiAgentSupervisorGraph:
    def __init__(self, domain_qa_runner=None, citation_verifier_runner=None):
        self.domain_qa_runner = domain_qa_runner or self._default_domain_qa_runner
        self.citation_verifier_runner = citation_verifier_runner or self._default_citation_verifier_runner
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
    ) -> MultiAgentSupervisorState:
        return {
            "user_id": user_id,
            "agent_id": agent_id,
            "dialog_id": dialog_id,
            "query": query,
            "knowledge_ids": list(knowledge_ids or []),
            "domain_pack_id": domain_pack_id,
            "runtime_settings": runtime_settings,
            "domain_pack": domain_pack,
            "planned_agents": [],
            "specialist_outputs": [],
            "vector_contexts": [],
            "graph_paths": [],
            "citations": [],
            "evidence_bundle": {"items": [], "document_count": 0, "citation_count": 0},
            "support_verdict": {"status": "insufficient_evidence", "reason": "not_evaluated"},
            "draft_answer": None,
            "report_markdown": None,
            "final_answer": None,
            "trace_metadata": {},
            "cost_metadata": {},
            "status": "pending",
            "failure_metadata": None,
        }

    def append_trace(self, state: MultiAgentSupervisorState, *, node: str, payload: dict | None = None) -> MultiAgentSupervisorState:
        next_state = deepcopy(state)
        trace = dict(next_state.get("trace_metadata") or {})
        trace.setdefault("nodes", []).append({"node": node, "payload": payload or {}})
        next_state["trace_metadata"] = trace
        return next_state

    def _with_trace(self, state: MultiAgentSupervisorState, *, node: str, payload: dict | None = None) -> dict[str, Any]:
        updated = self.append_trace(state, node=node, payload=payload)
        return {"trace_metadata": updated.get("trace_metadata") or {}}

    def _failure_update(self, state: MultiAgentSupervisorState, *, node: str, error: Exception) -> dict[str, Any]:
        error_text = str(error).strip() or error.__class__.__name__
        updates = self._with_trace(state, node=node, payload={"status": "ERROR", "error": error_text})
        updates["status"] = "failed"
        updates["failure_metadata"] = {"node": node, "error": error_text}
        return updates

    @staticmethod
    def _route_after_success_or_failure(state: MultiAgentSupervisorState, success_node: str) -> str:
        if str(state.get("status") or "").lower() == "failed":
            return "finalize"
        return success_node

    async def _default_domain_qa_runner(self, state: MultiAgentSupervisorState) -> dict[str, Any]:
        subgraph = DomainQAGraph()
        sub_state = subgraph.build_initial_state(
            user_id=state["user_id"],
            agent_id=state["agent_id"],
            dialog_id=state["dialog_id"],
            query=state["query"],
            knowledge_ids=state.get("knowledge_ids") or [],
            domain_pack_id=state.get("domain_pack_id"),
            runtime_settings=state.get("runtime_settings"),
            domain_pack=state.get("domain_pack"),
        )
        return await subgraph.ainvoke(sub_state)

    @staticmethod
    async def _default_citation_verifier_runner(state: MultiAgentSupervisorState) -> dict[str, Any]:
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
        return {
            "verified_citations": normalized,
            "verdict": "verified" if normalized else "missing_citations",
        }

    async def _plan_specialists_node(self, state: MultiAgentSupervisorState) -> dict[str, Any]:
        try:
            planned_agents = ["domain_qa_specialist", "citation_verifier_specialist"]
            updates = self._with_trace(
                state,
                node="plan_specialists",
                payload={"planned_agents": planned_agents, "status": "OK"},
            )
            updates["planned_agents"] = planned_agents
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="plan_specialists", error=err)

    async def _domain_qa_specialist_node(self, state: MultiAgentSupervisorState) -> dict[str, Any]:
        try:
            result = await self.domain_qa_runner(state)
            specialist_outputs = list(state.get("specialist_outputs") or [])
            specialist_outputs.append(
                {
                    "agent": "domain_qa_specialist",
                    "status": str(result.get("status") or "completed"),
                    "citation_count": len(result.get("citations") or []),
                    "path_count": len(result.get("graph_paths") or []),
                }
            )
            updates = self._with_trace(
                state,
                node="domain_qa_specialist",
                payload={
                    "status": "OK",
                    "citation_count": len(result.get("citations") or []),
                    "path_count": len(result.get("graph_paths") or []),
                },
            )
            updates.update(
                {
                    "specialist_outputs": specialist_outputs,
                    "vector_contexts": list(result.get("vector_contexts") or []),
                    "graph_paths": list(result.get("graph_paths") or []),
                    "citations": list(result.get("citations") or []),
                    "evidence_bundle": dict(result.get("evidence_bundle") or {"items": [], "document_count": 0, "citation_count": 0}),
                    "support_verdict": dict(result.get("support_verdict") or {"status": "insufficient_evidence", "reason": "not_evaluated"}),
                    "draft_answer": result.get("draft_answer"),
                    "report_markdown": result.get("report_markdown"),
                    "final_answer": result.get("final_answer"),
                    "status": "running",
                }
            )
            return updates
        except Exception as err:
            return self._failure_update(state, node="domain_qa_specialist", error=err)

    async def _citation_verifier_specialist_node(self, state: MultiAgentSupervisorState) -> dict[str, Any]:
        if str(state.get("status") or "").lower() == "failed":
            return self._with_trace(state, node="citation_verifier_specialist", payload={"status": "SKIPPED_AFTER_FAILURE"})
        try:
            result = await self.citation_verifier_runner(state)
            verified_citations = list(result.get("verified_citations") or [])
            verdict = str(result.get("verdict") or "unknown")
            specialist_outputs = list(state.get("specialist_outputs") or [])
            specialist_outputs.append(
                {
                    "agent": "citation_verifier_specialist",
                    "status": verdict,
                    "citation_count": len(verified_citations),
                }
            )
            updates = self._with_trace(
                state,
                node="citation_verifier_specialist",
                payload={"status": "OK", "verdict": verdict, "citation_count": len(verified_citations)},
            )
            updates["specialist_outputs"] = specialist_outputs
            updates["citations"] = verified_citations
            updates["evidence_bundle"] = dict(state.get("evidence_bundle") or {"items": [], "document_count": 0, "citation_count": 0})
            updates["support_verdict"] = {
                "status": "supported" if verified_citations else "insufficient_evidence",
                "reason": "verified_citations_present" if verified_citations else "missing_citations",
            }
            updates["status"] = "running"
            return updates
        except Exception as err:
            return self._failure_update(state, node="citation_verifier_specialist", error=err)

    async def _finalize_node(self, state: MultiAgentSupervisorState) -> dict[str, Any]:
        failure = state.get("failure_metadata") or {}
        final_answer = state.get("final_answer") or state.get("draft_answer") or ""
        if str(state.get("status") or "").lower() == "failed" and not final_answer:
            failed_node = str(failure.get("node") or "unknown")
            error_text = str(failure.get("error") or "unknown error")
            final_answer = f"multi-agent supervisor failed at `{failed_node}`: {error_text}"

        cost_metadata = {
            "planned_agent_count": len(state.get("planned_agents") or []),
            "specialist_count": len(state.get("specialist_outputs") or []),
            "citation_count": len(state.get("citations") or []),
            "path_count": len(state.get("graph_paths") or []),
            "support_status": (state.get("support_verdict") or {}).get("status"),
            "status": "failed" if str(state.get("status") or "").lower() == "failed" else "completed",
            "failed_node": failure.get("node"),
        }
        updates = self._with_trace(state, node="finalize", payload=cost_metadata)
        updates["cost_metadata"] = cost_metadata
        updates["final_answer"] = final_answer
        updates["status"] = cost_metadata["status"]
        return updates

    async def _get_graph(self):
        if self._compiled_graph is None:
            workflow = StateGraph(MultiAgentSupervisorState)
            workflow.add_node("plan_specialists", self._plan_specialists_node)
            workflow.add_node("domain_qa_specialist", self._domain_qa_specialist_node)
            workflow.add_node("citation_verifier_specialist", self._citation_verifier_specialist_node)
            workflow.add_node("finalize", self._finalize_node)
            workflow.add_edge(START, "plan_specialists")
            workflow.add_conditional_edges(
                "plan_specialists",
                lambda state: self._route_after_success_or_failure(state, "domain_qa_specialist"),
                {"domain_qa_specialist": "domain_qa_specialist", "finalize": "finalize"},
            )
            workflow.add_conditional_edges(
                "domain_qa_specialist",
                lambda state: self._route_after_success_or_failure(state, "citation_verifier_specialist"),
                {"citation_verifier_specialist": "citation_verifier_specialist", "finalize": "finalize"},
            )
            workflow.add_edge("citation_verifier_specialist", "finalize")
            workflow.add_edge("finalize", END)
            self._compiled_graph = workflow.compile()
        return self._compiled_graph

    async def ainvoke(self, state: MultiAgentSupervisorState) -> MultiAgentSupervisorState:
        graph = await self._get_graph()
        return await graph.ainvoke(state)

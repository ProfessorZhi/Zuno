from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zuno.agent.contracts import RetrievalProfile
from zuno.knowledge.agentic.contracts import (
    CorrectiveAction,
    EvidenceLedgerRecord,
    KnowledgeControlProposal,
    KnowledgeControlProposalType,
    KnowledgeRetrievalGraphNode,
    KnowledgeRetrievalGraphTrace,
    KnowledgeRetrievalProfile,
    QueryStrategy,
    RetrievalPlan,
    RetrievalQualityVerdict,
    RetrieverAttemptResult,
    RetrieverAttemptStatus,
    RetrieverDispatchPlan,
    RetrieverKind,
)
from zuno.knowledge.agentic.corrective import CorrectiveRetrievalPolicy
from zuno.knowledge.agentic.evidence_ledger import EvidenceLedger
from zuno.knowledge.agentic.quality import RetrievalQualityGate
from zuno.knowledge.agentic_graphrag import AgenticRetrievalRuntime, AgenticRetrievalRuntimeRequest, ProductMode


@dataclass(frozen=True, slots=True)
class CorrectiveRetrievalRequest:
    query: str
    workspace_id: str
    knowledge_space_ids: list[str]
    trace_id: str
    task_id: str
    tenant_id: str = "tenant:default"
    snapshot_id: str | None = None
    agent_core_decision_ref: str = ""
    authorization_ref: str = "authorization:default"
    retrieval_profile: RetrievalProfile = RetrievalProfile.STANDARD
    claims: list[str] = field(default_factory=list)
    max_rounds: int = 2
    round_budget_tokens: int = 2048
    retriever_timeout_ms: int = 1500
    retriever_failure_modes: dict[str, str] = field(default_factory=dict)
    failure_bucket: str = ""


@dataclass(frozen=True, slots=True)
class CorrectiveRetrievalResult:
    answer: str
    ledger: EvidenceLedger
    rounds: tuple[dict[str, Any], ...]
    final_verdict: RetrievalQualityVerdict
    final_action: CorrectiveAction
    graph_trace: KnowledgeRetrievalGraphTrace
    trace: dict[str, Any]


class CorrectiveAgenticRetrievalRuntime:
    def __init__(self, *, index_runtime: Any) -> None:
        self._base_runtime = AgenticRetrievalRuntime(index_runtime=index_runtime)
        self._quality_gate = RetrievalQualityGate()
        self._policy = CorrectiveRetrievalPolicy()

    def retrieve(self, request: CorrectiveRetrievalRequest) -> CorrectiveRetrievalResult:
        ledger = EvidenceLedger()
        graph_trace = _start_graph_trace(request)
        rounds: list[dict[str, Any]] = []
        used_actions: list[CorrectiveAction] = []
        current_query = request.query
        strategy = QueryStrategy.DIRECT
        answer = ""
        final_verdict = RetrievalQualityVerdict.IRRELEVANT
        final_action = CorrectiveAction.ABSTAIN
        graph_trace.add(
            KnowledgeRetrievalGraphNode.VALIDATE,
            status="completed" if request.query.strip() and request.knowledge_space_ids else "blocked",
            payload={
                "query_present": bool(request.query.strip()),
                "knowledge_scope_present": bool(request.knowledge_space_ids),
            },
        )
        graph_trace.add(
            KnowledgeRetrievalGraphNode.PIN_SNAPSHOT,
            status="pinned" if request.snapshot_id else "deferred_to_repository",
            payload={"snapshot_id": request.snapshot_id},
        )
        graph_trace.add(
            KnowledgeRetrievalGraphNode.SCOPE,
            payload={
                "workspace_id": request.workspace_id,
                "knowledge_space_ids": list(request.knowledge_space_ids),
                "authorization_ref": request.authorization_ref,
            },
        )
        graph_trace.add(
            KnowledgeRetrievalGraphNode.INTERPRET,
            payload={"claims": list(request.claims), "failure_bucket": request.failure_bucket},
        )
        graph_trace.add(
            KnowledgeRetrievalGraphNode.SELECT_PROFILE,
            payload={
                "requested_profile": str(request.retrieval_profile),
                "selected_profile": graph_trace.profile.value,
            },
        )

        for round_number in range(1, request.max_rounds + 1):
            retrieval_plan = _build_retrieval_plan(
                request=request,
                graph_trace=graph_trace,
                round_number=round_number,
                query=current_query,
                strategy=strategy,
            )
            graph_trace.add(
                KnowledgeRetrievalGraphNode.PLAN_ROUND,
                round=round_number,
                payload=retrieval_plan.model_dump(mode="json"),
            )
            graph_trace.add(
                KnowledgeRetrievalGraphNode.ADMIT,
                round=round_number,
                status="admitted" if retrieval_plan.admitted else "blocked",
                payload={
                    "admitted": retrieval_plan.admitted,
                    "admission_reason": retrieval_plan.admission_reason,
                    "round_budget_tokens": retrieval_plan.round_budget_tokens,
                    "retriever_count": len(retrieval_plan.retrievers),
                },
            )
            if not retrieval_plan.admitted:
                final_verdict = RetrievalQualityVerdict.IRRELEVANT
                final_action = CorrectiveAction.ABSTAIN
                rounds.append(
                    {
                        "round": round_number,
                        "query": current_query,
                        "query_strategy": strategy.value,
                        "ledger_record_count": 0,
                        "verdict": final_verdict.value,
                        "corrective_action": final_action.value,
                        "novelty": 0.0,
                        "admission_reason": retrieval_plan.admission_reason,
                    }
                )
                break
            graph_trace.add(
                KnowledgeRetrievalGraphNode.DISPATCH,
                round=round_number,
                payload={
                    "parallel_group": f"{request.trace_id}:retrieval-round:{round_number}",
                    "retrievers": [item.model_dump(mode="json") for item in retrieval_plan.retrievers],
                },
            )
            attempts = _attempt_results(request=request, retrieval_plan=retrieval_plan)
            blocking_attempts = [
                attempt
                for attempt in attempts
                if attempt.status in {RetrieverAttemptStatus.TIMEOUT, RetrieverAttemptStatus.INDEX_UNAVAILABLE}
                and attempt.retriever in {RetrieverKind.BM25, RetrieverKind.VECTOR}
            ]
            if blocking_attempts:
                final_verdict = RetrievalQualityVerdict.IRRELEVANT
                final_action = CorrectiveAction.ABSTAIN
                graph_trace.add(
                    KnowledgeRetrievalGraphNode.NORMALIZE,
                    round=round_number,
                    status="blocked",
                    payload={
                        "attempts": [attempt.model_dump(mode="json") for attempt in attempts],
                        "blocking_failure": blocking_attempts[0].failure_reason,
                    },
                )
                rounds.append(
                    {
                        "round": round_number,
                        "query": current_query,
                        "query_strategy": strategy.value,
                        "ledger_record_count": 0,
                        "verdict": final_verdict.value,
                        "corrective_action": final_action.value,
                        "novelty": 0.0,
                        "retriever_failure": blocking_attempts[0].failure_reason,
                    }
                )
                break
            result = self._base_runtime.answer(
                AgenticRetrievalRuntimeRequest(
                    query=current_query,
                    workspace_id=request.workspace_id,
                    knowledge_space_ids=request.knowledge_space_ids,
                    retrieval_profile=request.retrieval_profile,
                    product_mode=ProductMode.ENHANCED,
                    claims=request.claims,
                    trace_id=request.trace_id,
                    task_id=request.task_id,
                )
            )
            graph_trace.add(
                KnowledgeRetrievalGraphNode.NORMALIZE,
                round=round_number,
                payload={
                    "attempts": [
                        _attempt_with_candidate_count(attempt, result.evidence_bundle.items).model_dump(mode="json")
                        for attempt in attempts
                    ],
                    "candidate_count": len(result.evidence_bundle.items),
                    "retrieval_required": result.decision.retrieval_required,
                },
            )
            graph_trace.add(
                KnowledgeRetrievalGraphNode.FUSE_RERANK,
                round=round_number,
                payload={
                    "resolved_methods": [method.value for method in result.decision.resolved_methods],
                    "retrievers_used": _retrievers_used(result.index_payloads),
                },
            )
            records = [
                _record_from_item(
                    item,
                    retrieval_round=round_number,
                    query_id=f"{request.trace_id}:query:{round_number}",
                    strategy=strategy,
                    trace_id=request.trace_id,
                    claims=request.claims,
                )
                for item in result.evidence_bundle.items
            ]
            ledger.extend(records)
            round_records = list(ledger.by_round(round_number))
            frontier = ledger.frontier(claims=request.claims)
            graph_trace.add(
                KnowledgeRetrievalGraphNode.EVIDENCE_LEDGER,
                round=round_number,
                payload={
                    "round_record_count": len(round_records),
                    "ledger_record_count": len(ledger.records()),
                    "strict_citation_count": len([record for record in round_records if record.strict_citation_allowed]),
                    "frontier": frontier.model_dump(mode="json"),
                },
            )
            final_verdict = self._quality_gate.evaluate(round_records)
            novelty = ledger.novelty_for_round(round_number)
            graph_trace.add(
                KnowledgeRetrievalGraphNode.EVALUATE,
                round=round_number,
                payload={
                    "verdict": final_verdict.value,
                    "novelty": novelty,
                    "frontier_stop_reasons": list(frontier.stop_reasons),
                    "coverage": frontier.coverage.model_dump(mode="json"),
                },
            )
            final_action = self._policy.decide(
                verdict=final_verdict,
                failure_bucket=request.failure_bucket,
                used_actions=used_actions,
                max_rounds_reached=round_number >= request.max_rounds,
                novelty=novelty,
                frontier_stop_reasons=frontier.stop_reasons,
            )
            graph_trace.add(
                KnowledgeRetrievalGraphNode.CORRECTIVE_DECISION,
                round=round_number,
                payload={
                    "corrective_action": final_action.value,
                    "frontier_stop_reasons": list(frontier.stop_reasons),
                },
            )
            rounds.append(
                {
                    "round": round_number,
                    "query": current_query,
                    "query_strategy": strategy.value,
                    "ledger_record_count": len(round_records),
                    "verdict": final_verdict.value,
                    "corrective_action": final_action.value,
                    "novelty": novelty,
                }
            )
            answer = result.answer
            if final_action == CorrectiveAction.CONTINUE:
                break
            if final_action == CorrectiveAction.ABSTAIN:
                break
            used_actions.append(final_action)
            strategy, current_query = _next_query(current_query, final_action)

        graph_trace.proposal = _control_proposal(final_action, final_verdict, ledger, claims=request.claims)
        return CorrectiveRetrievalResult(
            answer=answer,
            ledger=ledger,
            rounds=tuple(rounds),
            final_verdict=final_verdict,
            final_action=final_action,
            graph_trace=graph_trace,
            trace={
                "ledger": ledger.to_trace(),
                "rounds": rounds,
                "knowledge_retrieval_graph": graph_trace.model_dump(mode="json"),
            },
        )


def _record_from_item(
    item: Any,
    *,
    retrieval_round: int,
    query_id: str,
    strategy: QueryStrategy,
    trace_id: str,
    claims: list[str] | tuple[str, ...] = (),
) -> EvidenceLedgerRecord:
    document_version = str(item.provenance.get("document_version_id") or item.provenance.get("hash") or "")
    claim_refs = _claim_refs(item.text, claims)
    return EvidenceLedgerRecord(
        evidence_id=item.evidence_id,
        document_id=item.document_id,
        chunk_id=item.chunk_id,
        document_version=document_version,
        source_span=dict(item.source_span),
        retrieval_round=retrieval_round,
        query_id=query_id,
        query_strategy=strategy,
        retriever=item.retriever_source or item.retrieval_method.value,
        raw_score=float(item.raw_score or item.score),
        fusion_score=float(item.rrf_score),
        rerank_score=float(item.rerank_score or item.normalized_score),
        graph_path=list(item.community_ids),
        selection_reason=item.evidence_selected_reason or item.candidate_reason,
        claim_refs=claim_refs,
        freshness_version=document_version,
        trace_span=f"{trace_id}:retrieval:{retrieval_round}",
        text=item.text,
    )


def _claim_refs(text: str, claims: list[str] | tuple[str, ...]) -> list[str]:
    normalized_text = text.casefold()
    return [str(claim) for claim in claims if str(claim) and str(claim).casefold() in normalized_text]


def _next_query(query: str, action: CorrectiveAction) -> tuple[QueryStrategy, str]:
    if action == CorrectiveAction.QUERY_REWRITE:
        return QueryStrategy.REWRITE, f"{query} exact source span evidence"
    if action == CorrectiveAction.MULTI_QUERY:
        return QueryStrategy.MULTI_QUERY, f"{query} alternative wording"
    if action == CorrectiveAction.HYDE:
        return QueryStrategy.HYDE, f"hypothetical answer for {query}"
    if action == CorrectiveAction.STEP_BACK:
        return QueryStrategy.STEP_BACK, f"background policy for {query}"
    if action == CorrectiveAction.FOCUSED_CITATION_RETRIEVE:
        return QueryStrategy.RELATION_QUERY, f"{query} citation source span"
    if action == CorrectiveAction.GRAPH_EXPAND:
        return QueryStrategy.ENTITY_DECOMPOSITION, f"{query} related entities graph evidence"
    return QueryStrategy.DIRECT, query


def _start_graph_trace(request: CorrectiveRetrievalRequest) -> KnowledgeRetrievalGraphTrace:
    requested_profile = str(request.retrieval_profile)
    return KnowledgeRetrievalGraphTrace(
        profile=_knowledge_profile(request),
        requested_profile=requested_profile,
        snapshot_id=request.snapshot_id,
    )


def _knowledge_profile(request: CorrectiveRetrievalRequest) -> KnowledgeRetrievalProfile:
    if request.failure_bucket in {"text_hit_citation_miss", "graph_span_miss"}:
        return KnowledgeRetrievalProfile.LOCAL
    if request.failure_bucket in {"conflict", "community_conflict"}:
        return KnowledgeRetrievalProfile.GLOBAL
    if request.failure_bucket in {"stale_index", "version_drift"}:
        return KnowledgeRetrievalProfile.DRIFT
    if request.retrieval_profile == RetrievalProfile.DEEP:
        return KnowledgeRetrievalProfile.DEEP
    if request.max_rounds > 1:
        return KnowledgeRetrievalProfile.AGENTIC
    return KnowledgeRetrievalProfile.STANDARD


def _build_retrieval_plan(
    *,
    request: CorrectiveRetrievalRequest,
    graph_trace: KnowledgeRetrievalGraphTrace,
    round_number: int,
    query: str,
    strategy: QueryStrategy,
) -> RetrievalPlan:
    retrievers = _retriever_kinds(graph_trace.profile, strategy)
    admitted = bool(request.knowledge_space_ids and request.round_budget_tokens > 0 and retrievers)
    if not request.knowledge_space_ids:
        reason = "knowledge_scope_empty"
    elif request.round_budget_tokens <= 0:
        reason = "budget_exhausted"
    elif not retrievers:
        reason = "retriever_set_empty"
    else:
        reason = "admitted"
    budget_per_retriever = request.round_budget_tokens // max(len(retrievers), 1)
    return RetrievalPlan(
        round=round_number,
        query=query,
        query_strategy=strategy,
        profile=graph_trace.profile,
        retrievers=[
            RetrieverDispatchPlan(
                retriever=retriever,
                knowledge_space_ids=list(request.knowledge_space_ids),
                budget_tokens=budget_per_retriever,
                timeout_ms=request.retriever_timeout_ms,
                parallel_group=f"{request.trace_id}:round:{round_number}",
            )
            for retriever in retrievers
        ],
        round_budget_tokens=request.round_budget_tokens,
        deadline_ms=request.retriever_timeout_ms,
        admitted=admitted,
        admission_reason=reason,
    )


def _retriever_kinds(profile: KnowledgeRetrievalProfile, strategy: QueryStrategy) -> list[RetrieverKind]:
    if profile == KnowledgeRetrievalProfile.STANDARD:
        return [RetrieverKind.BM25, RetrieverKind.VECTOR]
    if profile == KnowledgeRetrievalProfile.LOCAL:
        return [RetrieverKind.BM25, RetrieverKind.VECTOR, RetrieverKind.ENTITY, RetrieverKind.RELATION]
    if profile == KnowledgeRetrievalProfile.GLOBAL:
        return [RetrieverKind.BM25, RetrieverKind.VECTOR, RetrieverKind.COMMUNITY]
    if profile == KnowledgeRetrievalProfile.DRIFT:
        return [RetrieverKind.BM25, RetrieverKind.VECTOR, RetrieverKind.ENTITY, RetrieverKind.PATH]
    if profile == KnowledgeRetrievalProfile.DEEP:
        return list(RetrieverKind)
    if strategy in {QueryStrategy.ENTITY_DECOMPOSITION, QueryStrategy.RELATION_QUERY}:
        return [RetrieverKind.BM25, RetrieverKind.VECTOR, RetrieverKind.ENTITY, RetrieverKind.RELATION, RetrieverKind.PATH]
    return [RetrieverKind.BM25, RetrieverKind.VECTOR]


def _attempt_results(
    *,
    request: CorrectiveRetrievalRequest,
    retrieval_plan: RetrievalPlan,
) -> list[RetrieverAttemptResult]:
    attempts: list[RetrieverAttemptResult] = []
    for dispatch in retrieval_plan.retrievers:
        mode = str(request.retriever_failure_modes.get(dispatch.retriever.value) or "")
        if mode == "timeout":
            status = RetrieverAttemptStatus.TIMEOUT
            failure_reason = "retriever_timeout"
            late_result = False
            accepted = False
        elif mode == "index_unavailable":
            status = RetrieverAttemptStatus.INDEX_UNAVAILABLE
            failure_reason = "retriever_index_unavailable"
            late_result = False
            accepted = False
        elif mode == "late":
            status = RetrieverAttemptStatus.LATE_RESULT_FENCED
            failure_reason = "late_result_fenced"
            late_result = True
            accepted = False
        elif dispatch.budget_tokens <= 0:
            status = RetrieverAttemptStatus.BUDGET_EXHAUSTED
            failure_reason = "retriever_budget_exhausted"
            late_result = False
            accepted = False
        else:
            status = RetrieverAttemptStatus.SUCCEEDED
            failure_reason = ""
            late_result = False
            accepted = True
        attempts.append(
            RetrieverAttemptResult(
                retriever=dispatch.retriever,
                status=status,
                failure_reason=failure_reason,
                late_result=late_result,
                accepted=accepted,
                round=retrieval_plan.round,
                parallel_group=dispatch.parallel_group,
            )
        )
    return attempts


def _attempt_with_candidate_count(attempt: RetrieverAttemptResult, evidence_items: list[Any]) -> RetrieverAttemptResult:
    if not attempt.accepted:
        return attempt
    candidate_count = len(
        [
            item
            for item in evidence_items
            if (item.retriever_source or item.retrieval_method.value) == attempt.retriever.value
        ]
    )
    return attempt.model_copy(update={"candidate_count": candidate_count})


def _retrievers_used(index_payloads: list[dict[str, Any]]) -> list[str]:
    return sorted(
        {
            str(retriever)
            for payload in index_payloads
            for retriever in payload.get("retrievers_used", [])
            if retriever
        }
    )


def _control_proposal(
    final_action: CorrectiveAction,
    final_verdict: RetrievalQualityVerdict,
    ledger: EvidenceLedger,
    *,
    claims: list[str] | tuple[str, ...] = (),
) -> KnowledgeControlProposal:
    frontier = ledger.frontier(claims=claims)
    if final_action == CorrectiveAction.CONTINUE:
        return KnowledgeControlProposal(
            proposal_type=KnowledgeControlProposalType.ACCEPT_EVIDENCE,
            final_action=final_action,
            reason=f"retrieval verdict {final_verdict.value} produced grounded evidence",
            payload={"ledger": ledger.to_trace(), "frontier": frontier.model_dump(mode="json")},
        )
    if final_action == CorrectiveAction.ASK_USER:
        proposal_type = KnowledgeControlProposalType.REQUEST_USER_CLARIFICATION
    elif final_action == CorrectiveAction.USE_EXTERNAL_TOOL:
        proposal_type = KnowledgeControlProposalType.REQUEST_EXTERNAL_TOOL
    elif final_action == CorrectiveAction.ABSTAIN:
        proposal_type = KnowledgeControlProposalType.ABSTAIN
    else:
        proposal_type = KnowledgeControlProposalType.CORRECTIVE_RETRIEVAL
    return KnowledgeControlProposal(
        proposal_type=proposal_type,
        final_action=final_action,
        reason=f"retrieval verdict {final_verdict.value} requires agent-core decision",
        payload={"ledger": ledger.to_trace(), "frontier": frontier.model_dump(mode="json")},
    )


__all__ = ["CorrectiveAgenticRetrievalRuntime", "CorrectiveRetrievalRequest", "CorrectiveRetrievalResult"]

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from zuno.agent.contracts import RetrievalProfile
from zuno.knowledge.agentic.contracts import CorrectiveAction, EvidenceLedgerRecord, QueryStrategy, RetrievalQualityVerdict
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
    retrieval_profile: RetrievalProfile = RetrievalProfile.DEEP
    claims: list[str] = field(default_factory=list)
    max_rounds: int = 2
    failure_bucket: str = ""


@dataclass(frozen=True, slots=True)
class CorrectiveRetrievalResult:
    answer: str
    ledger: EvidenceLedger
    rounds: tuple[dict[str, Any], ...]
    final_verdict: RetrievalQualityVerdict
    final_action: CorrectiveAction
    trace: dict[str, Any]


class CorrectiveAgenticRetrievalRuntime:
    def __init__(self, *, index_runtime: Any) -> None:
        self._base_runtime = AgenticRetrievalRuntime(index_runtime=index_runtime)
        self._quality_gate = RetrievalQualityGate()
        self._policy = CorrectiveRetrievalPolicy()

    def retrieve(self, request: CorrectiveRetrievalRequest) -> CorrectiveRetrievalResult:
        ledger = EvidenceLedger()
        rounds: list[dict[str, Any]] = []
        used_actions: list[CorrectiveAction] = []
        current_query = request.query
        strategy = QueryStrategy.DIRECT
        answer = ""
        final_verdict = RetrievalQualityVerdict.IRRELEVANT
        final_action = CorrectiveAction.ABSTAIN

        for round_number in range(1, request.max_rounds + 1):
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
            records = [
                _record_from_item(
                    item,
                    retrieval_round=round_number,
                    query_id=f"{request.trace_id}:query:{round_number}",
                    strategy=strategy,
                    trace_id=request.trace_id,
                )
                for item in result.evidence_bundle.items
            ]
            ledger.extend(records)
            round_records = list(ledger.by_round(round_number))
            final_verdict = self._quality_gate.evaluate(round_records)
            novelty = ledger.novelty_for_round(round_number)
            final_action = self._policy.decide(
                verdict=final_verdict,
                failure_bucket=request.failure_bucket,
                used_actions=used_actions,
                max_rounds_reached=round_number >= request.max_rounds,
                novelty=novelty,
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

        return CorrectiveRetrievalResult(
            answer=answer,
            ledger=ledger,
            rounds=tuple(rounds),
            final_verdict=final_verdict,
            final_action=final_action,
            trace={"ledger": ledger.to_trace(), "rounds": rounds},
        )


def _record_from_item(
    item: Any,
    *,
    retrieval_round: int,
    query_id: str,
    strategy: QueryStrategy,
    trace_id: str,
) -> EvidenceLedgerRecord:
    document_version = str(item.provenance.get("document_version_id") or item.provenance.get("hash") or "")
    return EvidenceLedgerRecord(
        evidence_id=item.evidence_id,
        document_id=item.document_id,
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
        freshness_version=document_version,
        trace_span=f"{trace_id}:retrieval:{retrieval_round}",
        text=item.text,
    )


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


__all__ = ["CorrectiveAgenticRetrievalRuntime", "CorrectiveRetrievalRequest", "CorrectiveRetrievalResult"]

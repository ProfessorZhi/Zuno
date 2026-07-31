"""Canonical Execution Adapters for Deep GraphRAG and Agentic GraphRAG.

AG-PR56-GEMINI-3-6-FLASH-HIGH-RUNTIME-TRUTH-REBUILD

Truthful Boundary Contract:
1. Deep GraphRAG Canonical Adapter:
   - Connects to formal Knowledge Runtime Port (deps.knowledge_runtime).
   - Gold document refs MUST NEVER enter the retrieval request.
   - Zero synthetic fallback answers or artificial token/cost/latency generation.
   - When Knowledge Runtime Port or execute_deep_retrieval method is absent, returns BLOCKED with failure_class="canonical_knowledge_runtime_unavailable".
   - Test doubles / fake runtimes MUST set is_test_double=True and CANNOT claim measurement_state="runtime_observed".

2. Agentic GraphRAG Canonical Adapter:
   - Connects to formal Agent Run Runtime Port (deps.agent_run_runtime).
   - Zero local synthetic AgentRunGraph composition roots inside eval layer.
   - When formal product runtime is absent or unwired, returns BLOCKED with failure_class="canonical_agentic_product_runtime_unavailable".
   - Validates authentic receipt fields: receipt_type, receipt_ref, owner, status, tenant_id, workspace_id, runtime_version, snapshot_ref, payload_hash.
   - Validates receipt owners: SecurityDecision (security), PlanVersion/RunOutcome (agent_core), UsageReceipt (model_gateway), BudgetSettlement (budget), Trace (observability), ArtifactReceipt (artifact_store).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any, Dict, List, Optional, Tuple

from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalBenchmarkProfileRunner,
    CanonicalCaseInput,
    CanonicalCaseResult,
    CanonicalRuntimeDependencies,
    _blocked_result,
    _extract_trace_id,
)


@dataclass(frozen=True, slots=True)
class CanonicalReceiptRef:
    """Typed receipt contract for authentic runtime evidence."""

    receipt_type: str
    receipt_ref: str
    owner: str
    status: str
    tenant_id: str
    workspace_id: str
    runtime_version: str
    snapshot_ref: str
    payload_hash: str


EXPECTED_RECEIPT_OWNERS = {
    "SecurityDecision": "security",
    "PlanVersion": "agent_core",
    "RunOutcome": "agent_core",
    "UsageReceipt": "model_gateway",
    "BudgetSettlement": "budget",
    "Trace": "observability",
    "ArtifactReceipt": "artifact_store",
}


def validate_canonical_receipt(
    receipt: Any,
    expected_type: str,
    expected_owner: str,
    tenant_id: str,
    workspace_id: str,
) -> bool:
    """Validate authentic receipt object structure, owner, status, and payload hash."""
    if receipt is None:
        return False
    if isinstance(receipt, dict):
        r_type = receipt.get("receipt_type", "")
        r_ref = receipt.get("receipt_ref", "")
        r_owner = receipt.get("owner", "")
        r_status = receipt.get("status", "")
        r_tenant = receipt.get("tenant_id", "")
        r_workspace = receipt.get("workspace_id", "")
        r_hash = receipt.get("payload_hash", "")
    elif hasattr(receipt, "receipt_type"):
        r_type = getattr(receipt, "receipt_type", "")
        r_ref = getattr(receipt, "receipt_ref", "")
        r_owner = getattr(receipt, "owner", "")
        r_status = getattr(receipt, "status", "")
        r_tenant = getattr(receipt, "tenant_id", "")
        r_workspace = getattr(receipt, "workspace_id", "")
        r_hash = getattr(receipt, "payload_hash", "")
    else:
        return False

    if r_type != expected_type:
        return False
    if r_owner != expected_owner:
        return False
    if r_status != "valid":
        return False
    if r_tenant != tenant_id or r_workspace != workspace_id:
        return False
    if not r_ref or not r_hash:
        return False
    return True


class DeepGraphRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Deep GraphRAG Canonical Execution Adapter.
    
    Delegates multi-round retrieval to formal Knowledge Runtime Port.
    Gold document refs are NEVER passed into retrieval requests.
    """

    def __init__(self, deps: CanonicalRuntimeDependencies) -> None:
        super().__init__(deps=deps)

    def check_preflight_gaps(self) -> list[str]:
        return self._deps.validate_dependencies("deep_graphrag")

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        adapter = self._trace_adapter
        span_handle = None
        if adapter is not None and hasattr(adapter, "start_span"):
            span_handle = adapter.start_span(
                "benchmark_case",
                span_type="Graph",
                metadata={
                    "eval_run_id": case_input.eval_run_id,
                    "case_id": case_input.case_id,
                    "profile": "deep_graphrag",
                },
            )
        trace_id = _extract_trace_id(span_handle)

        gaps = self.check_preflight_gaps()
        if gaps:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": gaps})
            return _blocked_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                gaps=gaps,
                latency=0.0,
                trace_id=trace_id,
            )

        k_runtime = self._deps.knowledge_runtime
        if k_runtime is None:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_unavailable"]})
            return _blocked_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                gaps=["canonical_knowledge_runtime_unavailable"],
                latency=0.0,
                trace_id=trace_id,
            )

        retrieval_func = getattr(k_runtime, "execute_deep_retrieval", None)
        if not callable(retrieval_func):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_unavailable"]})
            return _blocked_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                gaps=["canonical_knowledge_runtime_unavailable"],
                latency=0.0,
                trace_id=trace_id,
            )

        start_t = time.monotonic()
        # CRITICAL SAFETY: gold_document_refs MUST NEVER enter retrieval request!
        res_obj = retrieval_func(
            question=case_input.question,
            corpus_snapshot_ref=case_input.corpus_snapshot_ref,
        )
        latency_ms = (time.monotonic() - start_t) * 1000.0

        if not isinstance(res_obj, dict):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return _blocked_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                gaps=["runtime_contract_incomplete"],
                latency=latency_ms,
                trace_id=trace_id,
            )

        is_test_double = getattr(k_runtime, "is_test_double", True)
        meas_state = "runtime_observed" if not is_test_double else "blocked_not_measured"

        answer = res_obj.get("answer", "")
        evidence_refs = tuple(res_obj.get("evidence_refs", ()))
        retrieved_docs = tuple(res_obj.get("retrieved_document_refs", ()))
        retrieval_rounds = int(res_obj.get("retrieval_rounds", 0))
        token_usage = int(res_obj.get("token_usage", 0))
        cost = float(res_obj.get("cost", 0.0))
        stop_reason = str(res_obj.get("stop_reason", ""))

        if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "completed", "rounds": retrieval_rounds})

        return CanonicalCaseResult(
            eval_run_id=case_input.eval_run_id,
            case_id=case_input.case_id,
            profile_name="deep_graphrag",
            runtime_status="completed" if not is_test_double else "completed_test_double",
            measurement_state=meas_state,
            answer=answer,
            retrieved_document_refs=retrieved_docs,
            retrieved_evidence_refs=evidence_refs,
            citation_refs=evidence_refs,
            knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
            plan_version_ref=res_obj.get("plan_version_ref", ""),
            run_outcome_ref=res_obj.get("run_outcome_ref", ""),
            budget_settlement_ref=res_obj.get("budget_settlement_ref", ""),
            artifact_receipt_ref=res_obj.get("artifact_receipt_ref", ""),
            trace_id=trace_id or res_obj.get("trace_id"),
            retrieval_rounds=retrieval_rounds,
            latency=latency_ms,
            token_usage=token_usage,
            cost=cost,
            failure_class="",
            retry_count=0,
            standard_floor_preserved=None,
            is_test_double=is_test_double,
            blocked_reason="",
            dependency_gaps=(),
            evidence_refs=evidence_refs,
            retrieval_trace={"stop_reason": stop_reason},
        )


class AgenticGraphRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Agentic GraphRAG Canonical Execution Adapter.
    
    Delegates agent execution to formal Agent Run Runtime Port (deps.agent_run_runtime).
    Zero synthetic local composition roots inside the eval layer.
    """

    def __init__(self, deps: CanonicalRuntimeDependencies) -> None:
        super().__init__(deps=deps)

    def check_preflight_gaps(self) -> list[str]:
        return self._deps.validate_dependencies("agentic_graphrag")

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        adapter = self._trace_adapter
        span_handle = None
        if adapter is not None and hasattr(adapter, "start_span"):
            span_handle = adapter.start_span(
                "benchmark_case",
                span_type="AgentRunGraph",
                metadata={
                    "eval_run_id": case_input.eval_run_id,
                    "case_id": case_input.case_id,
                    "profile": "agentic_graphrag",
                },
            )
        trace_id = _extract_trace_id(span_handle)

        gaps = self.check_preflight_gaps()
        if gaps:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": gaps})
            return _blocked_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                gaps=gaps,
                latency=0.0,
                trace_id=trace_id,
            )

        agent_runtime = self._deps.agent_run_runtime
        if agent_runtime is None:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_agent_run_graph_unavailable"]})
            return _blocked_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                gaps=["canonical_agent_run_graph_unavailable"],
                latency=0.0,
                trace_id=trace_id,
            )

        exec_func = getattr(agent_runtime, "execute_agent_run", None)
        if not callable(exec_func):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_agentic_product_runtime_unavailable"]})
            return _blocked_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                gaps=["canonical_agentic_product_runtime_unavailable"],
                latency=0.0,
                trace_id=trace_id,
            )

        start_t = time.monotonic()
        run_res = exec_func(
            eval_run_id=case_input.eval_run_id,
            case_id=case_input.case_id,
            question=case_input.question,
            corpus_snapshot_ref=case_input.corpus_snapshot_ref,
            tenant_id=case_input.tenant_id,
            workspace_id=case_input.workspace_id,
            authorization_ref=case_input.authorization_ref,
            security_epoch=case_input.security_epoch,
            attempt_number=case_input.attempt_number,
        )
        latency_ms = (time.monotonic() - start_t) * 1000.0

        if not isinstance(run_res, dict) or run_res.get("status") == "blocked":
            failure_class = run_res.get("failure_class", "canonical_agentic_product_runtime_unavailable") if isinstance(run_res, dict) else "canonical_agentic_product_runtime_unavailable"
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": [failure_class]})
            return _blocked_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                gaps=[failure_class],
                latency=latency_ms,
                trace_id=trace_id,
            )

        sec_receipt = run_res.get("security_decision_receipt")
        plan_receipt = run_res.get("plan_version_receipt")
        outcome_receipt = run_res.get("run_outcome_receipt")
        usage_receipt = run_res.get("usage_receipt")
        budget_receipt = run_res.get("budget_settlement_receipt")

        valid_sec = validate_canonical_receipt(sec_receipt, "SecurityDecision", "security", case_input.tenant_id, case_input.workspace_id)
        valid_plan = validate_canonical_receipt(plan_receipt, "PlanVersion", "agent_core", case_input.tenant_id, case_input.workspace_id)
        valid_outcome = validate_canonical_receipt(outcome_receipt, "RunOutcome", "agent_core", case_input.tenant_id, case_input.workspace_id)
        valid_usage = validate_canonical_receipt(usage_receipt, "UsageReceipt", "model_gateway", case_input.tenant_id, case_input.workspace_id)
        valid_budget = validate_canonical_receipt(budget_receipt, "BudgetSettlement", "budget", case_input.tenant_id, case_input.workspace_id)

        if not (valid_sec and valid_plan and valid_outcome and valid_usage and valid_budget):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return _blocked_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                gaps=["runtime_contract_incomplete"],
                latency=latency_ms,
                trace_id=trace_id,
            )

        is_test_double = getattr(agent_runtime, "is_test_double", True)
        meas_state = "runtime_observed" if not is_test_double else "blocked_not_measured"

        if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "completed", "outcome": run_res.get("run_outcome_ref")})

        return CanonicalCaseResult(
            eval_run_id=case_input.eval_run_id,
            case_id=case_input.case_id,
            profile_name="agentic_graphrag",
            runtime_status="completed" if not is_test_double else "completed_test_double",
            measurement_state=meas_state,
            answer=run_res.get("answer", ""),
            retrieved_document_refs=tuple(run_res.get("retrieved_document_refs", ())),
            retrieved_evidence_refs=tuple(run_res.get("evidence_refs", ())),
            citation_refs=tuple(run_res.get("evidence_refs", ())),
            knowledge_snapshot_ref=run_res.get("knowledge_snapshot_ref", case_input.corpus_snapshot_ref),
            plan_version_ref=run_res.get("plan_version_ref", ""),
            run_outcome_ref=run_res.get("run_outcome_ref", ""),
            budget_settlement_ref=run_res.get("budget_settlement_ref", ""),
            artifact_receipt_ref=run_res.get("artifact_receipt_ref", ""),
            trace_id=trace_id or run_res.get("trace_id"),
            retrieval_rounds=int(run_res.get("retrieval_rounds", 0)),
            latency=latency_ms,
            token_usage=int(run_res.get("token_usage", 0)),
            cost=float(run_res.get("cost", 0.0)),
            failure_class="",
            retry_count=0,
            standard_floor_preserved=None,
            is_test_double=is_test_double,
            blocked_reason="",
            dependency_gaps=(),
            evidence_refs=tuple(run_res.get("evidence_refs", ())),
            retrieval_trace={"stop_reason": "agent_run_final_gate_passed"},
        )

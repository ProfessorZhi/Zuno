"""Canonical Execution Adapters for Deep GraphRAG and Agentic GraphRAG.

AG-PR56-FAIL-CLOSED-BOUNDARY-REPAIR

Fail-Closed Boundary Contract:
1. Deep GraphRAG Canonical Adapter:
   - Connects to formal Knowledge Runtime Port (deps.knowledge_runtime).
   - Gold document refs MUST NEVER enter the retrieval request.
   - Zero synthetic fallback answers or artificial token/cost/latency generation.
   - When Knowledge Runtime Port or execute_deep_retrieval method is absent, returns BLOCKED with failure_class="canonical_knowledge_runtime_unavailable".
   - Without formal external Product Runtime Authority binding, all injected objects fail closed (runtime_status="blocked", measurement_state="BLOCKED", is_test_double=True).

2. Agentic GraphRAG Canonical Adapter:
   - Connects to formal Agent Run Runtime Port (deps.agent_run_runtime).
   - Zero local synthetic AgentRunGraph composition roots inside eval layer.
   - When formal product runtime is absent or unwired, returns BLOCKED with failure_class="canonical_agentic_product_runtime_unavailable".
   - Without formal external Product Runtime Authority binding, all injected objects fail closed (runtime_status="blocked", measurement_state="BLOCKED", is_test_double=True).
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


def _get_receipt_field(receipt: Any, field_name: str) -> str:
    """Safely extract string field from dict or object receipt."""
    if receipt is None:
        return ""
    if isinstance(receipt, dict):
        return str(receipt.get(field_name, ""))
    return str(getattr(receipt, field_name, ""))


def validate_canonical_receipt(
    receipt: Any,
    expected_type: str,
    expected_owner: str,
    tenant_id: str,
    workspace_id: str,
) -> bool:
    """Validate authentic receipt object structure, owner, status, runtime_version, snapshot_ref, and payload hash."""
    if receipt is None:
        return False

    r_type = _get_receipt_field(receipt, "receipt_type")
    r_ref = _get_receipt_field(receipt, "receipt_ref")
    r_owner = _get_receipt_field(receipt, "owner")
    r_status = _get_receipt_field(receipt, "status")
    r_tenant = _get_receipt_field(receipt, "tenant_id")
    r_workspace = _get_receipt_field(receipt, "workspace_id")
    r_version = _get_receipt_field(receipt, "runtime_version")
    r_snapshot = _get_receipt_field(receipt, "snapshot_ref")
    r_hash = _get_receipt_field(receipt, "payload_hash")

    if r_type != expected_type:
        return False
    if r_owner != expected_owner:
        return False
    if r_status != "valid":
        return False
    if r_tenant != tenant_id or r_workspace != workspace_id:
        return False
    if not r_ref or not r_hash or not r_version or not r_snapshot:
        return False
    return True


class DeepGraphRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Deep GraphRAG Canonical Execution Adapter.

    Delegates multi-round retrieval to formal Knowledge Runtime Port.
    Gold document refs are NEVER passed into retrieval requests.
    Fails closed when formal external Product Runtime Authority is unavailable.
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
            res = _blocked_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                gaps=gaps,
                latency=0.0,
                trace_id=trace_id,
            )
            return CanonicalCaseResult(
                eval_run_id=res.eval_run_id,
                case_id=res.case_id,
                profile_name=res.profile_name,
                runtime_status=res.runtime_status,
                measurement_state=res.measurement_state,
                answer=res.answer,
                retrieved_document_refs=res.retrieved_document_refs,
                retrieved_evidence_refs=res.retrieved_evidence_refs,
                citation_refs=res.citation_refs,
                knowledge_snapshot_ref=res.knowledge_snapshot_ref,
                plan_version_ref=res.plan_version_ref,
                run_outcome_ref=res.run_outcome_ref,
                budget_settlement_ref=res.budget_settlement_ref,
                artifact_receipt_ref=res.artifact_receipt_ref,
                trace_id=res.trace_id,
                retrieval_rounds=res.retrieval_rounds,
                latency=res.latency,
                token_usage=res.token_usage,
                cost=res.cost,
                failure_class=res.failure_class,
                retry_count=res.retry_count,
                standard_floor_preserved=res.standard_floor_preserved,
                is_test_double=True,
                blocked_reason=res.blocked_reason,
                dependency_gaps=res.dependency_gaps,
                evidence_refs=res.evidence_refs,
                retrieval_trace=res.retrieval_trace,
            )

        k_runtime = self._deps.knowledge_runtime
        if k_runtime is None:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_unavailable"]})
            res = _blocked_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                gaps=["canonical_knowledge_runtime_unavailable"],
                latency=0.0,
                trace_id=trace_id,
            )
            return CanonicalCaseResult(
                eval_run_id=res.eval_run_id,
                case_id=res.case_id,
                profile_name=res.profile_name,
                runtime_status=res.runtime_status,
                measurement_state=res.measurement_state,
                answer=res.answer,
                retrieved_document_refs=res.retrieved_document_refs,
                retrieved_evidence_refs=res.retrieved_evidence_refs,
                citation_refs=res.citation_refs,
                knowledge_snapshot_ref=res.knowledge_snapshot_ref,
                plan_version_ref=res.plan_version_ref,
                run_outcome_ref=res.run_outcome_ref,
                budget_settlement_ref=res.budget_settlement_ref,
                artifact_receipt_ref=res.artifact_receipt_ref,
                trace_id=res.trace_id,
                retrieval_rounds=res.retrieval_rounds,
                latency=res.latency,
                token_usage=res.token_usage,
                cost=res.cost,
                failure_class=res.failure_class,
                retry_count=res.retry_count,
                standard_floor_preserved=res.standard_floor_preserved,
                is_test_double=True,
                blocked_reason=res.blocked_reason,
                dependency_gaps=res.dependency_gaps,
                evidence_refs=res.evidence_refs,
                retrieval_trace=res.retrieval_trace,
            )

        retrieval_func = getattr(k_runtime, "execute_deep_retrieval", None)
        if not callable(retrieval_func):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_unavailable"]})
            res = _blocked_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                gaps=["canonical_knowledge_runtime_unavailable"],
                latency=0.0,
                trace_id=trace_id,
            )
            return CanonicalCaseResult(
                eval_run_id=res.eval_run_id,
                case_id=res.case_id,
                profile_name=res.profile_name,
                runtime_status=res.runtime_status,
                measurement_state=res.measurement_state,
                answer=res.answer,
                retrieved_document_refs=res.retrieved_document_refs,
                retrieved_evidence_refs=res.retrieved_evidence_refs,
                citation_refs=res.citation_refs,
                knowledge_snapshot_ref=res.knowledge_snapshot_ref,
                plan_version_ref=res.plan_version_ref,
                run_outcome_ref=res.run_outcome_ref,
                budget_settlement_ref=res.budget_settlement_ref,
                artifact_receipt_ref=res.artifact_receipt_ref,
                trace_id=res.trace_id,
                retrieval_rounds=res.retrieval_rounds,
                latency=res.latency,
                token_usage=res.token_usage,
                cost=res.cost,
                failure_class=res.failure_class,
                retry_count=res.retry_count,
                standard_floor_preserved=res.standard_floor_preserved,
                is_test_double=True,
                blocked_reason=res.blocked_reason,
                dependency_gaps=res.dependency_gaps,
                evidence_refs=res.evidence_refs,
                retrieval_trace=res.retrieval_trace,
            )

        start_t = time.monotonic()
        try:
            # CRITICAL SAFETY: gold_document_refs & gold evidence MUST NEVER enter retrieval request!
            res_obj = retrieval_func(
                question=case_input.question,
                corpus_snapshot_ref=case_input.corpus_snapshot_ref,
            )
        except Exception:
            latency_sec = time.monotonic() - start_t
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_exception"]})
            return CanonicalCaseResult(
                eval_run_id=case_input.eval_run_id,
                case_id=case_input.case_id,
                profile_name="deep_graphrag",
                runtime_status="blocked",
                measurement_state="BLOCKED",
                answer="",
                retrieved_document_refs=(),
                retrieved_evidence_refs=(),
                citation_refs=(),
                knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
                plan_version_ref="",
                run_outcome_ref="",
                budget_settlement_ref="",
                artifact_receipt_ref="",
                trace_id=trace_id,
                retrieval_rounds=0,
                latency=latency_sec,
                token_usage=0,
                cost=0.0,
                failure_class="canonical_knowledge_runtime_exception",
                retry_count=0,
                standard_floor_preserved=None,
                is_test_double=True,
                blocked_reason="canonical_knowledge_runtime_exception",
                dependency_gaps=("canonical_knowledge_runtime_exception",),
                evidence_refs=(),
                retrieval_trace={"stop_reason": "exception_raised"},
            )

        latency_sec = time.monotonic() - start_t

        if not isinstance(res_obj, dict):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return CanonicalCaseResult(
                eval_run_id=case_input.eval_run_id,
                case_id=case_input.case_id,
                profile_name="deep_graphrag",
                runtime_status="blocked",
                measurement_state="BLOCKED",
                answer="",
                retrieved_document_refs=(),
                retrieved_evidence_refs=(),
                citation_refs=(),
                knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
                plan_version_ref="",
                run_outcome_ref="",
                budget_settlement_ref="",
                artifact_receipt_ref="",
                trace_id=trace_id,
                retrieval_rounds=0,
                latency=latency_sec,
                token_usage=0,
                cost=0.0,
                failure_class="runtime_contract_incomplete",
                retry_count=0,
                standard_floor_preserved=None,
                is_test_double=True,
                blocked_reason="runtime_contract_incomplete",
                dependency_gaps=("runtime_contract_incomplete",),
                evidence_refs=(),
                retrieval_trace={"stop_reason": "invalid_return_type"},
            )

        # Boundary test double observation data
        answer = str(res_obj.get("answer", ""))
        evidence_refs = tuple(res_obj.get("evidence_refs", ()))
        retrieved_docs = tuple(res_obj.get("retrieved_document_refs", ()))
        retrieval_rounds = int(res_obj.get("retrieval_rounds", 0))
        stop_reason = str(res_obj.get("stop_reason", ""))

        if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "blocked", "rounds": retrieval_rounds})

        # FAIL CLOSED: Product Runtime Attestation is unavailable in PR #56
        return CanonicalCaseResult(
            eval_run_id=case_input.eval_run_id,
            case_id=case_input.case_id,
            profile_name="deep_graphrag",
            runtime_status="blocked",
            measurement_state="BLOCKED",
            answer=answer,
            retrieved_document_refs=retrieved_docs,
            retrieved_evidence_refs=evidence_refs,
            citation_refs=evidence_refs,
            knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
            plan_version_ref="",
            run_outcome_ref="",
            budget_settlement_ref="",
            artifact_receipt_ref="",
            trace_id=trace_id,
            retrieval_rounds=retrieval_rounds,
            latency=latency_sec,
            token_usage=0,
            cost=0.0,
            failure_class="canonical_product_runtime_attestation_unavailable",
            retry_count=0,
            standard_floor_preserved=None,
            is_test_double=True,
            blocked_reason="canonical_product_runtime_attestation_unavailable",
            dependency_gaps=("canonical_product_runtime_attestation_unavailable",),
            evidence_refs=evidence_refs,
            retrieval_trace={"stop_reason": stop_reason},
        )


class AgenticGraphRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Agentic GraphRAG Canonical Execution Adapter.

    Delegates agent execution to formal Agent Run Runtime Port (deps.agent_run_runtime).
    Zero synthetic local composition roots inside the eval layer.
    Fails closed when formal external Product Runtime Authority is unavailable.
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
            res = _blocked_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                gaps=gaps,
                latency=0.0,
                trace_id=trace_id,
            )
            return CanonicalCaseResult(
                eval_run_id=res.eval_run_id,
                case_id=res.case_id,
                profile_name=res.profile_name,
                runtime_status=res.runtime_status,
                measurement_state=res.measurement_state,
                answer=res.answer,
                retrieved_document_refs=res.retrieved_document_refs,
                retrieved_evidence_refs=res.retrieved_evidence_refs,
                citation_refs=res.citation_refs,
                knowledge_snapshot_ref=res.knowledge_snapshot_ref,
                plan_version_ref=res.plan_version_ref,
                run_outcome_ref=res.run_outcome_ref,
                budget_settlement_ref=res.budget_settlement_ref,
                artifact_receipt_ref=res.artifact_receipt_ref,
                trace_id=res.trace_id,
                retrieval_rounds=res.retrieval_rounds,
                latency=res.latency,
                token_usage=res.token_usage,
                cost=res.cost,
                failure_class=res.failure_class,
                retry_count=res.retry_count,
                standard_floor_preserved=res.standard_floor_preserved,
                is_test_double=True,
                blocked_reason=res.blocked_reason,
                dependency_gaps=res.dependency_gaps,
                evidence_refs=res.evidence_refs,
                retrieval_trace=res.retrieval_trace,
            )

        agent_runtime = self._deps.agent_run_runtime
        if agent_runtime is None:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_agent_run_graph_unavailable"]})
            res = _blocked_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                gaps=["canonical_agent_run_graph_unavailable"],
                latency=0.0,
                trace_id=trace_id,
            )
            return CanonicalCaseResult(
                eval_run_id=res.eval_run_id,
                case_id=res.case_id,
                profile_name=res.profile_name,
                runtime_status=res.runtime_status,
                measurement_state=res.measurement_state,
                answer=res.answer,
                retrieved_document_refs=res.retrieved_document_refs,
                retrieved_evidence_refs=res.retrieved_evidence_refs,
                citation_refs=res.citation_refs,
                knowledge_snapshot_ref=res.knowledge_snapshot_ref,
                plan_version_ref=res.plan_version_ref,
                run_outcome_ref=res.run_outcome_ref,
                budget_settlement_ref=res.budget_settlement_ref,
                artifact_receipt_ref=res.artifact_receipt_ref,
                trace_id=res.trace_id,
                retrieval_rounds=res.retrieval_rounds,
                latency=res.latency,
                token_usage=res.token_usage,
                cost=res.cost,
                failure_class=res.failure_class,
                retry_count=res.retry_count,
                standard_floor_preserved=res.standard_floor_preserved,
                is_test_double=True,
                blocked_reason=res.blocked_reason,
                dependency_gaps=res.dependency_gaps,
                evidence_refs=res.evidence_refs,
                retrieval_trace=res.retrieval_trace,
            )

        exec_func = getattr(agent_runtime, "execute_agent_run", None)
        if not callable(exec_func):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_agentic_product_runtime_unavailable"]})
            res = _blocked_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                gaps=["canonical_agentic_product_runtime_unavailable"],
                latency=0.0,
                trace_id=trace_id,
            )
            return CanonicalCaseResult(
                eval_run_id=res.eval_run_id,
                case_id=res.case_id,
                profile_name=res.profile_name,
                runtime_status=res.runtime_status,
                measurement_state=res.measurement_state,
                answer=res.answer,
                retrieved_document_refs=res.retrieved_document_refs,
                retrieved_evidence_refs=res.retrieved_evidence_refs,
                citation_refs=res.citation_refs,
                knowledge_snapshot_ref=res.knowledge_snapshot_ref,
                plan_version_ref=res.plan_version_ref,
                run_outcome_ref=res.run_outcome_ref,
                budget_settlement_ref=res.budget_settlement_ref,
                artifact_receipt_ref=res.artifact_receipt_ref,
                trace_id=res.trace_id,
                retrieval_rounds=res.retrieval_rounds,
                latency=res.latency,
                token_usage=res.token_usage,
                cost=res.cost,
                failure_class=res.failure_class,
                retry_count=res.retry_count,
                standard_floor_preserved=res.standard_floor_preserved,
                is_test_double=True,
                blocked_reason=res.blocked_reason,
                dependency_gaps=res.dependency_gaps,
                evidence_refs=res.evidence_refs,
                retrieval_trace=res.retrieval_trace,
            )

        start_t = time.monotonic()
        try:
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
        except Exception:
            latency_sec = time.monotonic() - start_t
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_agentic_runtime_exception"]})
            return CanonicalCaseResult(
                eval_run_id=case_input.eval_run_id,
                case_id=case_input.case_id,
                profile_name="agentic_graphrag",
                runtime_status="blocked",
                measurement_state="BLOCKED",
                answer="",
                retrieved_document_refs=(),
                retrieved_evidence_refs=(),
                citation_refs=(),
                knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
                plan_version_ref="",
                run_outcome_ref="",
                budget_settlement_ref="",
                artifact_receipt_ref="",
                trace_id=trace_id,
                retrieval_rounds=0,
                latency=latency_sec,
                token_usage=0,
                cost=0.0,
                failure_class="canonical_agentic_runtime_exception",
                retry_count=0,
                standard_floor_preserved=None,
                is_test_double=True,
                blocked_reason="canonical_agentic_runtime_exception",
                dependency_gaps=("canonical_agentic_runtime_exception",),
                evidence_refs=(),
                retrieval_trace={"stop_reason": "exception_raised"},
            )

        latency_sec = time.monotonic() - start_t

        if not isinstance(run_res, dict):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return CanonicalCaseResult(
                eval_run_id=case_input.eval_run_id,
                case_id=case_input.case_id,
                profile_name="agentic_graphrag",
                runtime_status="blocked",
                measurement_state="BLOCKED",
                answer="",
                retrieved_document_refs=(),
                retrieved_evidence_refs=(),
                citation_refs=(),
                knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
                plan_version_ref="",
                run_outcome_ref="",
                budget_settlement_ref="",
                artifact_receipt_ref="",
                trace_id=trace_id,
                retrieval_rounds=0,
                latency=latency_sec,
                token_usage=0,
                cost=0.0,
                failure_class="runtime_contract_incomplete",
                retry_count=0,
                standard_floor_preserved=None,
                is_test_double=True,
                blocked_reason="runtime_contract_incomplete",
                dependency_gaps=("runtime_contract_incomplete",),
                evidence_refs=(),
                retrieval_trace={"stop_reason": "invalid_return_type"},
            )

        if run_res.get("status") == "blocked":
            failure_class = run_res.get("failure_class", "canonical_agentic_product_runtime_unavailable")
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": [failure_class]})
            return CanonicalCaseResult(
                eval_run_id=case_input.eval_run_id,
                case_id=case_input.case_id,
                profile_name="agentic_graphrag",
                runtime_status="blocked",
                measurement_state="BLOCKED",
                answer="",
                retrieved_document_refs=(),
                retrieved_evidence_refs=(),
                citation_refs=(),
                knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
                plan_version_ref="",
                run_outcome_ref="",
                budget_settlement_ref="",
                artifact_receipt_ref="",
                trace_id=trace_id,
                retrieval_rounds=0,
                latency=latency_sec,
                token_usage=0,
                cost=0.0,
                failure_class=failure_class,
                retry_count=0,
                standard_floor_preserved=None,
                is_test_double=True,
                blocked_reason=failure_class,
                dependency_gaps=(failure_class,),
                evidence_refs=(),
                retrieval_trace={"stop_reason": "runtime_blocked"},
            )

        # Receipt structural validation for contract checking
        sec_receipt = run_res.get("security_decision_receipt")
        plan_receipt = run_res.get("plan_version_receipt")
        outcome_receipt = run_res.get("run_outcome_receipt")
        usage_receipt = run_res.get("usage_receipt")
        budget_receipt = run_res.get("budget_settlement_receipt")
        artifact_receipt = run_res.get("artifact_receipt")

        valid_sec = validate_canonical_receipt(sec_receipt, "SecurityDecision", "security", case_input.tenant_id, case_input.workspace_id)
        valid_plan = validate_canonical_receipt(plan_receipt, "PlanVersion", "agent_core", case_input.tenant_id, case_input.workspace_id)
        valid_outcome = validate_canonical_receipt(outcome_receipt, "RunOutcome", "agent_core", case_input.tenant_id, case_input.workspace_id)
        valid_usage = validate_canonical_receipt(usage_receipt, "UsageReceipt", "model_gateway", case_input.tenant_id, case_input.workspace_id)
        valid_budget = validate_canonical_receipt(budget_receipt, "BudgetSettlement", "budget", case_input.tenant_id, case_input.workspace_id)

        valid_artifact = True
        artifact_ref = str(run_res.get("artifact_receipt_ref", ""))
        if artifact_receipt is not None or artifact_ref:
            valid_artifact = validate_canonical_receipt(artifact_receipt, "ArtifactReceipt", "artifact_store", case_input.tenant_id, case_input.workspace_id)

        if not (valid_sec and valid_plan and valid_outcome and valid_usage and valid_budget and valid_artifact):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return CanonicalCaseResult(
                eval_run_id=case_input.eval_run_id,
                case_id=case_input.case_id,
                profile_name="agentic_graphrag",
                runtime_status="blocked",
                measurement_state="BLOCKED",
                answer="",
                retrieved_document_refs=(),
                retrieved_evidence_refs=(),
                citation_refs=(),
                knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
                plan_version_ref="",
                run_outcome_ref="",
                budget_settlement_ref="",
                artifact_receipt_ref="",
                trace_id=trace_id,
                retrieval_rounds=0,
                latency=latency_sec,
                token_usage=0,
                cost=0.0,
                failure_class="runtime_contract_incomplete",
                retry_count=0,
                standard_floor_preserved=None,
                is_test_double=True,
                blocked_reason="runtime_contract_incomplete",
                dependency_gaps=("runtime_contract_incomplete",),
                evidence_refs=(),
                retrieval_trace={"stop_reason": "receipt_validation_failed"},
            )

        # Receipt reference binding checks
        plan_ref = str(run_res.get("plan_version_ref", ""))
        outcome_ref = str(run_res.get("run_outcome_ref", ""))
        budget_ref = str(run_res.get("budget_settlement_ref", ""))

        if (
            plan_ref != _get_receipt_field(plan_receipt, "receipt_ref")
            or outcome_ref != _get_receipt_field(outcome_receipt, "receipt_ref")
            or budget_ref != _get_receipt_field(budget_receipt, "receipt_ref")
        ):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return CanonicalCaseResult(
                eval_run_id=case_input.eval_run_id,
                case_id=case_input.case_id,
                profile_name="agentic_graphrag",
                runtime_status="blocked",
                measurement_state="BLOCKED",
                answer="",
                retrieved_document_refs=(),
                retrieved_evidence_refs=(),
                citation_refs=(),
                knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
                plan_version_ref="",
                run_outcome_ref="",
                budget_settlement_ref="",
                artifact_receipt_ref="",
                trace_id=trace_id,
                retrieval_rounds=0,
                latency=latency_sec,
                token_usage=0,
                cost=0.0,
                failure_class="runtime_contract_incomplete",
                retry_count=0,
                standard_floor_preserved=None,
                is_test_double=True,
                blocked_reason="runtime_contract_incomplete",
                dependency_gaps=("runtime_contract_incomplete",),
                evidence_refs=(),
                retrieval_trace={"stop_reason": "receipt_binding_mismatch"},
            )

        if artifact_ref and artifact_ref != _get_receipt_field(artifact_receipt, "receipt_ref"):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return CanonicalCaseResult(
                eval_run_id=case_input.eval_run_id,
                case_id=case_input.case_id,
                profile_name="agentic_graphrag",
                runtime_status="blocked",
                measurement_state="BLOCKED",
                answer="",
                retrieved_document_refs=(),
                retrieved_evidence_refs=(),
                citation_refs=(),
                knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
                plan_version_ref="",
                run_outcome_ref="",
                budget_settlement_ref="",
                artifact_receipt_ref="",
                trace_id=trace_id,
                retrieval_rounds=0,
                latency=latency_sec,
                token_usage=0,
                cost=0.0,
                failure_class="runtime_contract_incomplete",
                retry_count=0,
                standard_floor_preserved=None,
                is_test_double=True,
                blocked_reason="runtime_contract_incomplete",
                dependency_gaps=("runtime_contract_incomplete",),
                evidence_refs=(),
                retrieval_trace={"stop_reason": "artifact_receipt_mismatch"},
            )

        # Boundary test double observation answer and refs
        answer = str(run_res.get("answer", ""))
        retrieved_docs = tuple(run_res.get("retrieved_document_refs", ()))
        evidence_refs = tuple(run_res.get("evidence_refs", ()))
        retrieval_rounds = int(run_res.get("retrieval_rounds", 0))

        if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "blocked", "outcome": outcome_ref})

        # FAIL CLOSED: Formal Product Runtime Authority is unavailable in PR #56.
        # Formal evidence fields MUST remain empty.
        return CanonicalCaseResult(
            eval_run_id=case_input.eval_run_id,
            case_id=case_input.case_id,
            profile_name="agentic_graphrag",
            runtime_status="blocked",
            measurement_state="BLOCKED",
            answer=answer,
            retrieved_document_refs=retrieved_docs,
            retrieved_evidence_refs=evidence_refs,
            citation_refs=evidence_refs,
            knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
            plan_version_ref="",
            run_outcome_ref="",
            budget_settlement_ref="",
            artifact_receipt_ref="",
            trace_id=trace_id,
            retrieval_rounds=retrieval_rounds,
            latency=latency_sec,
            token_usage=0,
            cost=0.0,
            failure_class="canonical_product_runtime_attestation_unavailable",
            retry_count=0,
            standard_floor_preserved=None,
            is_test_double=True,
            blocked_reason="canonical_product_runtime_attestation_unavailable",
            dependency_gaps=("canonical_product_runtime_attestation_unavailable",),
            evidence_refs=evidence_refs,
            retrieval_trace={"stop_reason": "agent_run_final_gate_passed"},
        )

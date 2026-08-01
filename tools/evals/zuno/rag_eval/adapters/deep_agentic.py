"""Canonical Execution Adapters for Deep GraphRAG and Agentic GraphRAG.

AG-PR56-FAIL-CLOSED-PAYLOAD-HARDENING

Fail-Closed Boundary Contract:
1. Deep GraphRAG Canonical Adapter:
   - Connects to formal Knowledge Runtime Port (deps.knowledge_runtime).
   - Gold document refs MUST NEVER enter the retrieval request.
   - Zero synthetic fallback answers or artificial token/cost/latency generation.
   - Strict payload normalization and fail-closed error code mapping.
   - All result trace_id values are None on blocked/test-double results.

2. Agentic GraphRAG Canonical Adapter:
   - Connects to formal Agent Run Runtime Port (deps.agent_run_runtime).
   - Zero local synthetic AgentRunGraph composition roots inside eval layer.
   - Strict payload normalization and structural receipt checking.
   - All result trace_id values are None on blocked/test-double results.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any, Mapping, Optional, Sequence

from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalBenchmarkProfileRunner,
    CanonicalCaseInput,
    CanonicalCaseResult,
    CanonicalRuntimeDependencies,
    _extract_trace_id,
)


ALLOWED_FAILURE_CLASSES = {
    "authorization_denied",
    "security_epoch_stale",
    "snapshot_unavailable",
    "retriever_timeout",
    "corrective_retrieval_failed",
    "evidence_frontier_empty",
    "budget_exhausted",
    "model_gateway_failed",
    "plan_validation_failed",
    "plan_activation_failed",
    "step_execution_failed",
    "action_evaluation_rejected",
    "step_acceptance_rejected",
    "final_gate_rejected",
    "agent_run_crashed",
    "trace_delivery_failed",
    "artifact_persist_failed",
    "result_store_failed",
    "canonical_knowledge_runtime_unavailable",
    "canonical_agent_run_graph_unavailable",
    "canonical_agentic_product_runtime_unavailable",
    "canonical_product_runtime_attestation_unavailable",
    "canonical_knowledge_runtime_exception",
    "canonical_agentic_runtime_exception",
    "runtime_contract_incomplete",
    "runtime_payload_invalid",
    "canonical_runtime_reported_blocked",
}


def _normalize_failure_class(raw_fc: Any) -> str:
    """Normalize raw failure_class to a safe, fixed, allowed repository error code."""
    if isinstance(raw_fc, str) and raw_fc in ALLOWED_FAILURE_CLASSES:
        return raw_fc
    return "canonical_runtime_reported_blocked"


@dataclass(frozen=True, slots=True)
class CanonicalReceiptRef:
    """Typed receipt contract for structural receipt checking."""

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


def validate_structural_canonical_receipt(
    receipt: Any,
    expected_type: str,
    expected_owner: str,
    tenant_id: str,
    workspace_id: str,
) -> bool:
    """Validate structural schema of receipt dicts.

    This is a pure structural format check, NOT an authentic runtime authority or evidence proof.
    """
    if not isinstance(receipt, dict):
        return False

    r_type = receipt.get("receipt_type")
    r_ref = receipt.get("receipt_ref")
    r_owner = receipt.get("owner")
    r_status = receipt.get("status")
    r_tenant = receipt.get("tenant_id")
    r_workspace = receipt.get("workspace_id")
    r_version = receipt.get("runtime_version")
    r_snapshot = receipt.get("snapshot_ref")
    r_hash = receipt.get("payload_hash")

    if not isinstance(r_type, str) or r_type != expected_type:
        return False
    if not isinstance(r_owner, str) or r_owner != expected_owner:
        return False
    if not isinstance(r_status, str) or r_status != "valid":
        return False
    if not isinstance(r_tenant, str) or r_tenant != tenant_id:
        return False
    if not isinstance(r_workspace, str) or r_workspace != workspace_id:
        return False
    if not isinstance(r_ref, str) or not r_ref:
        return False
    if not isinstance(r_hash, str) or not r_hash:
        return False
    if not isinstance(r_version, str) or not r_version:
        return False
    if not isinstance(r_snapshot, str) or not r_snapshot:
        return False

    return True


def _safe_str_tuple(val: Any) -> Optional[tuple[str, ...]]:
    """Safely parse sequence into tuple of strings. Returns None if invalid type."""
    if val is None:
        return ()
    if isinstance(val, (tuple, list)):
        for elem in val:
            if not isinstance(elem, str):
                return None
        return tuple(val)
    return None


def _safe_uint(val: Any) -> Optional[int]:
    """Safely parse unsigned int. Returns None if invalid type or negative."""
    if isinstance(val, bool):
        return None
    if isinstance(val, int) and val >= 0:
        return val
    return None


def _build_fail_closed_result(
    case_input: CanonicalCaseInput,
    profile_name: str,
    failure_class: str,
    latency: float = 0.0,
    answer: str = "",
    retrieved_document_refs: tuple[str, ...] = (),
    retrieved_evidence_refs: tuple[str, ...] = (),
    retrieval_rounds: int = 0,
    stop_reason: str = "",
    dependency_gaps: tuple[str, ...] = (),
) -> CanonicalCaseResult:
    """Build a fail-closed CanonicalCaseResult for blocked / test-double execution paths."""
    fc = _normalize_failure_class(failure_class)
    gaps = dependency_gaps if dependency_gaps else (fc,)
    return CanonicalCaseResult(
        eval_run_id=case_input.eval_run_id,
        case_id=case_input.case_id,
        profile_name=profile_name,
        runtime_status="blocked",
        measurement_state="BLOCKED",
        answer=answer,
        retrieved_document_refs=retrieved_document_refs,
        retrieved_evidence_refs=retrieved_evidence_refs,
        citation_refs=retrieved_evidence_refs,
        knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
        plan_version_ref="",
        run_outcome_ref="",
        budget_settlement_ref="",
        artifact_receipt_ref="",
        trace_id=None,  # MUST BE NONE on blocked/test-double results!
        retrieval_rounds=retrieval_rounds,
        latency=latency,
        token_usage=0,
        cost=0.0,
        failure_class=fc,
        retry_count=0,
        standard_floor_preserved=None,
        is_test_double=True,
        blocked_reason=fc,
        dependency_gaps=gaps,
        evidence_refs=retrieved_evidence_refs,
        retrieval_trace={"stop_reason": stop_reason} if stop_reason else {},
    )


class DeepGraphRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Deep GraphRAG Canonical Execution Adapter."""

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

        gaps = self.check_preflight_gaps()
        if gaps:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": gaps})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class=gaps[0],
                dependency_gaps=tuple(gaps),
            )

        k_runtime = self._deps.knowledge_runtime
        if k_runtime is None:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_unavailable"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="canonical_knowledge_runtime_unavailable",
            )

        retrieval_func = getattr(k_runtime, "execute_deep_retrieval", None)
        if not callable(retrieval_func):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_unavailable"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="canonical_knowledge_runtime_unavailable",
            )

        start_t = time.monotonic()
        try:
            res_obj = retrieval_func(
                question=case_input.question,
                corpus_snapshot_ref=case_input.corpus_snapshot_ref,
            )
        except Exception:
            latency_sec = time.monotonic() - start_t
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_exception"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="canonical_knowledge_runtime_exception",
                latency=latency_sec,
                stop_reason="exception_raised",
            )

        latency_sec = time.monotonic() - start_t

        if not isinstance(res_obj, dict):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_return_type",
            )

        # Payload Normalization & Safe Type Checks
        raw_answer = res_obj.get("answer", "")
        if not isinstance(raw_answer, str):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_answer_type",
            )

        evidence_refs_tuple = _safe_str_tuple(res_obj.get("evidence_refs", ()))
        retrieved_docs_tuple = _safe_str_tuple(res_obj.get("retrieved_document_refs", ()))
        rounds_val = _safe_uint(res_obj.get("retrieval_rounds", 0))

        if evidence_refs_tuple is None or retrieved_docs_tuple is None or rounds_val is None:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_payload_field_types",
            )

        raw_stop_reason = res_obj.get("stop_reason", "")
        stop_reason_str = str(raw_stop_reason) if isinstance(raw_stop_reason, str) else ""

        if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "blocked", "rounds": rounds_val})

        return _build_fail_closed_result(
            case_input=case_input,
            profile_name="deep_graphrag",
            failure_class="canonical_product_runtime_attestation_unavailable",
            latency=latency_sec,
            answer=raw_answer,
            retrieved_document_refs=retrieved_docs_tuple,
            retrieved_evidence_refs=evidence_refs_tuple,
            retrieval_rounds=rounds_val,
            stop_reason=stop_reason_str,
        )


class AgenticGraphRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Agentic GraphRAG Canonical Execution Adapter."""

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

        gaps = self.check_preflight_gaps()
        if gaps:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": gaps})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class=gaps[0],
                dependency_gaps=tuple(gaps),
            )

        agent_runtime = self._deps.agent_run_runtime
        if agent_runtime is None:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_agent_run_graph_unavailable"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="canonical_agent_run_graph_unavailable",
            )

        exec_func = getattr(agent_runtime, "execute_agent_run", None)
        if not callable(exec_func):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["canonical_agentic_product_runtime_unavailable"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="canonical_agentic_product_runtime_unavailable",
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
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="canonical_agentic_runtime_exception",
                latency=latency_sec,
                stop_reason="exception_raised",
            )

        latency_sec = time.monotonic() - start_t

        if not isinstance(run_res, dict):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_return_type",
            )

        raw_status = run_res.get("status")
        if not isinstance(raw_status, str):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_status_type",
            )

        if raw_status == "blocked":
            raw_fc = run_res.get("failure_class")
            norm_fc = _normalize_failure_class(raw_fc)
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": [norm_fc]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class=norm_fc,
                latency=latency_sec,
                stop_reason="runtime_blocked",
            )

        # Structural Receipt Check
        sec_receipt = run_res.get("security_decision_receipt")
        plan_receipt = run_res.get("plan_version_receipt")
        outcome_receipt = run_res.get("run_outcome_receipt")
        usage_receipt = run_res.get("usage_receipt")
        budget_receipt = run_res.get("budget_settlement_receipt")
        artifact_receipt = run_res.get("artifact_receipt")

        valid_sec = validate_structural_canonical_receipt(sec_receipt, "SecurityDecision", "security", case_input.tenant_id, case_input.workspace_id)
        valid_plan = validate_structural_canonical_receipt(plan_receipt, "PlanVersion", "agent_core", case_input.tenant_id, case_input.workspace_id)
        valid_outcome = validate_structural_canonical_receipt(outcome_receipt, "RunOutcome", "agent_core", case_input.tenant_id, case_input.workspace_id)
        valid_usage = validate_structural_canonical_receipt(usage_receipt, "UsageReceipt", "model_gateway", case_input.tenant_id, case_input.workspace_id)
        valid_budget = validate_structural_canonical_receipt(budget_receipt, "BudgetSettlement", "budget", case_input.tenant_id, case_input.workspace_id)

        valid_artifact = True
        artifact_ref_val = run_res.get("artifact_receipt_ref")
        if artifact_receipt is not None or artifact_ref_val is not None:
            valid_artifact = validate_structural_canonical_receipt(artifact_receipt, "ArtifactReceipt", "artifact_store", case_input.tenant_id, case_input.workspace_id)

        if not (valid_sec and valid_plan and valid_outcome and valid_usage and valid_budget and valid_artifact):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_contract_incomplete",
                latency=latency_sec,
                stop_reason="receipt_validation_failed",
            )

        # Receipt reference binding checks
        plan_ref = run_res.get("plan_version_ref")
        outcome_ref = run_res.get("run_outcome_ref")
        budget_ref = run_res.get("budget_settlement_ref")
        art_ref = run_res.get("artifact_receipt_ref", "")

        if (
            not isinstance(plan_ref, str)
            or not isinstance(outcome_ref, str)
            or not isinstance(budget_ref, str)
            or plan_ref != plan_receipt.get("receipt_ref")
            or outcome_ref != outcome_receipt.get("receipt_ref")
            or budget_ref != budget_receipt.get("receipt_ref")
        ):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_contract_incomplete",
                latency=latency_sec,
                stop_reason="receipt_binding_mismatch",
            )

        if art_ref and (not isinstance(art_ref, str) or art_ref != artifact_receipt.get("receipt_ref")):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_contract_incomplete"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_contract_incomplete",
                latency=latency_sec,
                stop_reason="artifact_receipt_mismatch",
            )

        # Safe Payload Parsing for Boundary Test Double Observation
        raw_answer = run_res.get("answer", "")
        if not isinstance(raw_answer, str):
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_answer_type",
            )

        evidence_refs_tuple = _safe_str_tuple(run_res.get("evidence_refs", ()))
        retrieved_docs_tuple = _safe_str_tuple(run_res.get("retrieved_document_refs", ()))
        rounds_val = _safe_uint(run_res.get("retrieval_rounds", 0))

        if evidence_refs_tuple is None or retrieved_docs_tuple is None or rounds_val is None:
            if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
                adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_payload_field_types",
            )

        if adapter is not None and hasattr(adapter, "end_span") and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "blocked", "outcome": outcome_ref})

        return _build_fail_closed_result(
            case_input=case_input,
            profile_name="agentic_graphrag",
            failure_class="canonical_product_runtime_attestation_unavailable",
            latency=latency_sec,
            answer=raw_answer,
            retrieved_document_refs=retrieved_docs_tuple,
            retrieved_evidence_refs=evidence_refs_tuple,
            retrieval_rounds=rounds_val,
            stop_reason="agent_run_final_gate_passed",
        )

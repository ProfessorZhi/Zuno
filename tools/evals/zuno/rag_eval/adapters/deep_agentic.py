"""Canonical Execution Adapters for Deep GraphRAG and Agentic GraphRAG.

AG-PR56-FINAL-BOUNDARY-HARDENING-AND-PERFORMANCE-RECORD

Fail-Closed Boundary Contract:
1. Deep GraphRAG Canonical Adapter:
   - Connects to formal Knowledge Runtime Port (deps.knowledge_runtime).
   - Gold document refs MUST NEVER enter the retrieval request.
   - Zero synthetic fallback answers or artificial token/cost/latency generation.
   - Strict payload normalization and fail-closed error code mapping.
   - Trace adapter exception safety (_safe_start_span, _safe_end_span).
   - All result trace_id values are None on blocked/test-double results.

2. Agentic GraphRAG Canonical Adapter:
   - Connects to formal Agent Run Runtime Port (deps.agent_run_runtime).
   - Status allowlist ("completed", "blocked", "failed").
   - Trace adapter exception safety (_safe_start_span, _safe_end_span).
   - Formal evidence validation deferred to dedicated Runtime Evidence Binding PR.
   - All result trace_id values are None on blocked/test-double results.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalBenchmarkProfileRunner,
    CanonicalCaseInput,
    CanonicalCaseResult,
    CanonicalRuntimeDependencies,
    build_product_runtime_attestation,
)
from tools.evals.zuno.rag_eval.measurement_gate import MeasurementState, MeasurementTruthGate
from tools.evals.zuno.rag_eval.runtime_evidence_binding import (
    BindingValidationState,
    RuntimeEvidenceBindingValidator,
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
    "runtime_evidence_binding_blocked",
    "canonical_runtime_reported_blocked",
    "trace_delivery_failed",
}

ALLOWED_STOP_REASONS = {
    "invalid_return_type",
    "invalid_answer_type",
    "invalid_payload_field_types",
    "runtime_blocked",
    "runtime_failed",
    "trace_delivery_failed",
    "product_runtime_attestation_unavailable",
    "exception_raised",
}


def _normalize_failure_class(raw_fc: Any) -> str:
    """Normalize raw failure_class to a safe, fixed, allowed repository error code."""
    if isinstance(raw_fc, str) and raw_fc in ALLOWED_FAILURE_CLASSES:
        return raw_fc
    return "canonical_runtime_reported_blocked"


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
    st_reason = stop_reason if stop_reason in ALLOWED_STOP_REASONS else "product_runtime_attestation_unavailable"
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
        trace_id=None,  # MUST BE NONE on all blocked/test-double results!
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
        retrieval_trace={"stop_reason": st_reason},
    )


def _safe_start_span(trace_adapter: Any, name: str, span_type: str, metadata: dict[str, Any]) -> tuple[Any, Optional[str]]:
    """Safe helper to invoke start_span on trace_adapter without letting exceptions escape.

    Returns (span_handle, error_code). If error_code is not None, start_span failed.
    """
    if trace_adapter is None:
        return (None, None)
    start_fn = getattr(trace_adapter, "start_span", None)
    if not callable(start_fn):
        return (None, None)
    try:
        before_failures = getattr(trace_adapter, "delivery_failures", None)
        handle = start_fn(name, span_type=span_type, metadata=metadata)
        after_failures = getattr(trace_adapter, "delivery_failures", None)
        if before_failures is not None and after_failures is not None and after_failures > before_failures:
            return (None, "trace_delivery_failed")
        return (handle, None)
    except Exception:
        return (None, "trace_delivery_failed")


def _safe_end_span(trace_adapter: Any, handle: Any, outputs: dict[str, Any]) -> Optional[str]:
    """Safe helper to invoke end_span on trace_adapter without letting exceptions escape.

    Returns error_code if end_span raises an exception, or None if successful.
    """
    if trace_adapter is None or handle is None:
        return None
    end_fn = getattr(trace_adapter, "end_span", None)
    if not callable(end_fn):
        return None
    try:
        before_failures = getattr(trace_adapter, "delivery_failures", None)
        end_fn(handle, outputs=outputs)
        after_failures = getattr(trace_adapter, "delivery_failures", None)
        if before_failures is not None and after_failures is not None and after_failures > before_failures:
            return "trace_delivery_failed"
        return None
    except Exception:
        return "trace_delivery_failed"


def _result_from_runtime_evidence_binding(
    *,
    case_input: CanonicalCaseInput,
    profile_name: str,
    payload: dict[str, Any],
    latency: float,
    answer: str,
    retrieved_document_refs: tuple[str, ...],
    retrieved_evidence_refs: tuple[str, ...],
    retrieval_rounds: int,
    end_span: Any,
) -> Optional[CanonicalCaseResult]:
    binding_payload = payload.get("runtime_evidence_binding")
    if binding_payload is None:
        return None

    binding_result = RuntimeEvidenceBindingValidator().validate(binding_payload)
    if binding_result.state is not BindingValidationState.VALID:
        end_span({"status": "blocked", "gaps": list(binding_result.gap_codes)})
        return _build_fail_closed_result(
            case_input=case_input,
            profile_name=profile_name,
            failure_class="runtime_evidence_binding_blocked",
            latency=latency,
            answer=answer,
            retrieved_document_refs=retrieved_document_refs,
            retrieved_evidence_refs=retrieved_evidence_refs,
            retrieval_rounds=retrieval_rounds,
            stop_reason="runtime_blocked",
            dependency_gaps=binding_result.gap_codes,
        )

    state, reason = MeasurementTruthGate().evaluate(
        is_test_double=False,
        runtime_status="completed",
        requested_profile=str(binding_payload.get("requested_profile") or profile_name),
        actual_profile=str(binding_payload.get("actual_profile") or profile_name),
        snapshot_ref=str(binding_payload.get("corpus_snapshot_ref") or ""),
        trace_id=str(binding_payload.get("trace_id") or ""),
        budget_settlement_ref=str(binding_payload.get("budget_settlement_ref") or ""),
        budget_settlement_valid=True,
        artifact_receipt_ref=str(binding_payload.get("artifact_receipt_ref") or ""),
        artifact_receipt_valid=True,
        run_outcome_ref=str(binding_payload.get("run_outcome_ref") or ""),
        run_outcome_valid=bool(binding_payload.get("run_outcome_ref")),
    )
    end_err = end_span({"status": state.value, "measurement_reason": reason})
    if end_err is not None:
        return _build_fail_closed_result(
            case_input=case_input,
            profile_name=profile_name,
            failure_class="trace_delivery_failed",
            latency=latency,
            stop_reason="trace_delivery_failed",
        )
    if state is MeasurementState.RUNTIME_OBSERVED:
        return CanonicalCaseResult(
            eval_run_id=case_input.eval_run_id,
            case_id=case_input.case_id,
            profile_name=profile_name,
            runtime_status="completed",
            measurement_state=state.value,
            answer=answer,
            retrieved_document_refs=retrieved_document_refs,
            retrieved_evidence_refs=retrieved_evidence_refs,
            citation_refs=retrieved_evidence_refs,
            knowledge_snapshot_ref=str(binding_payload.get("corpus_snapshot_ref") or case_input.corpus_snapshot_ref),
            plan_version_ref=str(binding_payload.get("plan_version_ref") or ""),
            run_outcome_ref=str(binding_payload.get("run_outcome_ref") or ""),
            budget_settlement_ref=str(binding_payload.get("budget_settlement_ref") or ""),
            artifact_receipt_ref=str(binding_payload.get("artifact_receipt_ref") or ""),
            trace_id=str(binding_payload.get("trace_id") or ""),
            retrieval_rounds=retrieval_rounds,
            latency=latency,
            token_usage=0,
            cost=0.0,
            failure_class="",
            retry_count=0,
            standard_floor_preserved=None,
            is_test_double=False,
            blocked_reason=reason,
            dependency_gaps=(),
            evidence_refs=retrieved_evidence_refs,
            retrieval_trace={"measurement_gate": reason},
            product_runtime_attestation=build_product_runtime_attestation(
                profile_name=profile_name,
                binding_payload=binding_payload,
                security_epoch=case_input.security_epoch,
            ),
        )
    return _build_fail_closed_result(
        case_input=case_input,
        profile_name=profile_name,
        failure_class="runtime_evidence_binding_blocked",
        latency=latency,
        answer=answer,
        retrieved_document_refs=retrieved_document_refs,
        retrieved_evidence_refs=retrieved_evidence_refs,
        retrieval_rounds=retrieval_rounds,
        stop_reason="runtime_blocked",
        dependency_gaps=(reason,),
    )


class DeepGraphRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Deep GraphRAG Canonical Execution Adapter."""

    def __init__(self, deps: CanonicalRuntimeDependencies) -> None:
        super().__init__(deps=deps)

    def check_preflight_gaps(self) -> list[str]:
        return self._deps.validate_dependencies("deep_graphrag")

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        span_handle, span_err = _safe_start_span(
            self._trace_adapter,
            "benchmark_case",
            span_type="Graph",
            metadata={
                "eval_run_id": case_input.eval_run_id,
                "case_id": case_input.case_id,
                "profile": "deep_graphrag",
            },
        )
        if span_err is not None:
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="trace_delivery_failed",
                stop_reason="trace_delivery_failed",
            )

        gaps = self.check_preflight_gaps()
        if gaps:
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": gaps})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class=gaps[0],
                dependency_gaps=tuple(gaps),
                stop_reason="runtime_blocked",
            )

        k_runtime = self._deps.knowledge_runtime
        if k_runtime is None:
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_unavailable"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="canonical_knowledge_runtime_unavailable",
                stop_reason="runtime_blocked",
            )

        retrieval_func = getattr(k_runtime, "execute_deep_retrieval", None)
        if not callable(retrieval_func):
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_unavailable"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="canonical_knowledge_runtime_unavailable",
                stop_reason="runtime_blocked",
            )

        start_t = time.monotonic()
        try:
            res_obj = retrieval_func(
                question=case_input.question,
                corpus_snapshot_ref=case_input.corpus_snapshot_ref,
            )
        except Exception:
            latency_sec = time.monotonic() - start_t
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_exception"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="canonical_knowledge_runtime_exception",
                latency=latency_sec,
                stop_reason="exception_raised",
            )

        latency_sec = time.monotonic() - start_t

        if not isinstance(res_obj, dict):
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
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
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
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
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_payload_field_types",
            )

        binding_result = _result_from_runtime_evidence_binding(
            case_input=case_input,
            profile_name="deep_graphrag",
            payload=res_obj,
            latency=latency_sec,
            answer=raw_answer,
            retrieved_document_refs=retrieved_docs_tuple,
            retrieved_evidence_refs=evidence_refs_tuple,
            retrieval_rounds=rounds_val,
            end_span=lambda outputs: _safe_end_span(self._trace_adapter, span_handle, outputs=outputs),
        )
        if binding_result is not None:
            return binding_result

        end_err = _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "rounds": rounds_val})
        if end_err is not None:
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="deep_graphrag",
                failure_class="trace_delivery_failed",
                latency=latency_sec,
                stop_reason="trace_delivery_failed",
            )

        return _build_fail_closed_result(
            case_input=case_input,
            profile_name="deep_graphrag",
            failure_class="canonical_product_runtime_attestation_unavailable",
            latency=latency_sec,
            answer=raw_answer,
            retrieved_document_refs=retrieved_docs_tuple,
            retrieved_evidence_refs=evidence_refs_tuple,
            retrieval_rounds=rounds_val,
            stop_reason="product_runtime_attestation_unavailable",
        )


class AgenticGraphRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Agentic GraphRAG Canonical Execution Adapter."""

    def __init__(self, deps: CanonicalRuntimeDependencies) -> None:
        super().__init__(deps=deps)

    def check_preflight_gaps(self) -> list[str]:
        return self._deps.validate_dependencies("agentic_graphrag")

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        span_handle, span_err = _safe_start_span(
            self._trace_adapter,
            "benchmark_case",
            span_type="AgentRunGraph",
            metadata={
                "eval_run_id": case_input.eval_run_id,
                "case_id": case_input.case_id,
                "profile": "agentic_graphrag",
            },
        )
        if span_err is not None:
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="trace_delivery_failed",
                stop_reason="trace_delivery_failed",
            )

        gaps = self.check_preflight_gaps()
        if gaps:
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": gaps})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class=gaps[0],
                dependency_gaps=tuple(gaps),
                stop_reason="runtime_blocked",
            )

        agent_runtime = self._deps.agent_run_runtime
        if agent_runtime is None:
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["canonical_agent_run_graph_unavailable"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="canonical_agent_run_graph_unavailable",
                stop_reason="runtime_blocked",
            )

        exec_func = getattr(agent_runtime, "execute_agent_run", None)
        if not callable(exec_func):
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["canonical_agentic_product_runtime_unavailable"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="canonical_agentic_product_runtime_unavailable",
                stop_reason="runtime_blocked",
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
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["canonical_agentic_runtime_exception"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="canonical_agentic_runtime_exception",
                latency=latency_sec,
                stop_reason="exception_raised",
            )

        latency_sec = time.monotonic() - start_t

        if not isinstance(run_res, dict):
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_return_type",
            )

        raw_status = run_res.get("status")

        # Status Allowlist Check: ("completed", "blocked", "failed")
        if raw_status == "blocked":
            raw_fc = run_res.get("failure_class")
            norm_fc = _normalize_failure_class(raw_fc)
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": [norm_fc]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class=norm_fc,
                latency=latency_sec,
                stop_reason="runtime_blocked",
            )
        elif raw_status == "failed":
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["canonical_runtime_reported_blocked"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="canonical_runtime_reported_blocked",
                latency=latency_sec,
                stop_reason="runtime_failed",
            )
        elif raw_status != "completed":
            # Any unknown, empty, or non-string status -> runtime_payload_invalid
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_payload_field_types",
            )

        # Safe Payload Parsing for Boundary Test Double Observation
        raw_answer = run_res.get("answer", "")
        if not isinstance(raw_answer, str):
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
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
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": ["runtime_payload_invalid"]})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="runtime_payload_invalid",
                latency=latency_sec,
                stop_reason="invalid_payload_field_types",
            )

        binding_result = _result_from_runtime_evidence_binding(
            case_input=case_input,
            profile_name="agentic_graphrag",
            payload=run_res,
            latency=latency_sec,
            answer=raw_answer,
            retrieved_document_refs=retrieved_docs_tuple,
            retrieved_evidence_refs=evidence_refs_tuple,
            retrieval_rounds=rounds_val,
            end_span=lambda outputs: _safe_end_span(self._trace_adapter, span_handle, outputs=outputs),
        )
        if binding_result is not None:
            return binding_result

        end_err = _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "rounds": rounds_val})
        if end_err is not None:
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="agentic_graphrag",
                failure_class="trace_delivery_failed",
                latency=latency_sec,
                stop_reason="trace_delivery_failed",
            )

        # Completed payload still returns BLOCKED because external Product Runtime Authority is unwired in PR #56
        return _build_fail_closed_result(
            case_input=case_input,
            profile_name="agentic_graphrag",
            failure_class="canonical_product_runtime_attestation_unavailable",
            latency=latency_sec,
            answer=raw_answer,
            retrieved_document_refs=retrieved_docs_tuple,
            retrieved_evidence_refs=evidence_refs_tuple,
            retrieval_rounds=rounds_val,
            stop_reason="product_runtime_attestation_unavailable",
        )

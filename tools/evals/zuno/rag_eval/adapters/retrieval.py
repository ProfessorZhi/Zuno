"""Canonical execution adapters for Standard RAG and Local GraphRAG.

These adapters put Standard / Local benchmark profiles on the canonical
factory path without converting injected runtime observations into measured
production evidence. Product Runtime attestation and formal receipts remain
mandatory before any result can become measured.
"""

from __future__ import annotations

import time
from typing import Any

from tools.evals.zuno.rag_eval.adapters.deep_agentic import (
    _build_fail_closed_result,
    _safe_end_span,
    _safe_start_span,
    _safe_str_tuple,
    _safe_uint,
)
from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalBenchmarkProfileRunner,
    CanonicalCaseInput,
    CanonicalCaseResult,
    CanonicalRuntimeDependencies,
)


class StandardRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Standard RAG canonical execution adapter."""

    def __init__(self, deps: CanonicalRuntimeDependencies) -> None:
        super().__init__(deps=deps)

    def check_preflight_gaps(self) -> list[str]:
        return self._deps.validate_dependencies("standard_rag")

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        span_handle, span_err = _safe_start_span(
            self._trace_adapter,
            "benchmark_case",
            span_type="RetrievalRound",
            metadata={
                "eval_run_id": case_input.eval_run_id,
                "case_id": case_input.case_id,
                "profile": "standard_rag",
            },
        )
        if span_err is not None:
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="standard_rag",
                failure_class="trace_delivery_failed",
                stop_reason="trace_delivery_failed",
            )

        gaps = self.check_preflight_gaps()
        if gaps:
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": gaps})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="standard_rag",
                failure_class=gaps[0],
                dependency_gaps=tuple(gaps),
                stop_reason="runtime_blocked",
            )

        knowledge_runtime = self._deps.knowledge_runtime
        execute_retrieval = getattr(knowledge_runtime, "execute_standard_retrieval", None)
        if not callable(execute_retrieval):
            _safe_end_span(
                self._trace_adapter,
                span_handle,
                outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_unavailable"]},
            )
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="standard_rag",
                failure_class="canonical_knowledge_runtime_unavailable",
                stop_reason="runtime_blocked",
            )

        start_t = time.monotonic()
        try:
            payload = execute_retrieval(
                question=case_input.question,
                corpus_snapshot_ref=case_input.corpus_snapshot_ref,
            )
        except Exception:
            latency_sec = time.monotonic() - start_t
            _safe_end_span(
                self._trace_adapter,
                span_handle,
                outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_exception"]},
            )
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="standard_rag",
                failure_class="canonical_knowledge_runtime_exception",
                latency=latency_sec,
                stop_reason="exception_raised",
            )

        latency_sec = time.monotonic() - start_t
        return _normalize_retrieval_payload(
            case_input=case_input,
            profile_name="standard_rag",
            payload=payload,
            latency=latency_sec,
            end_span=lambda outputs: _safe_end_span(self._trace_adapter, span_handle, outputs=outputs),
        )


class LocalGraphRAGCanonicalAdapter(CanonicalBenchmarkProfileRunner):
    """Local GraphRAG canonical execution adapter."""

    def __init__(self, deps: CanonicalRuntimeDependencies) -> None:
        super().__init__(deps=deps)

    def check_preflight_gaps(self) -> list[str]:
        return self._deps.validate_dependencies("local_graphrag")

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        span_handle, span_err = _safe_start_span(
            self._trace_adapter,
            "benchmark_case",
            span_type="Graph",
            metadata={
                "eval_run_id": case_input.eval_run_id,
                "case_id": case_input.case_id,
                "profile": "local_graphrag",
            },
        )
        if span_err is not None:
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="local_graphrag",
                failure_class="trace_delivery_failed",
                stop_reason="trace_delivery_failed",
            )

        gaps = self.check_preflight_gaps()
        if gaps:
            _safe_end_span(self._trace_adapter, span_handle, outputs={"status": "blocked", "gaps": gaps})
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="local_graphrag",
                failure_class=gaps[0],
                dependency_gaps=tuple(gaps),
                stop_reason="runtime_blocked",
            )

        index_runtime = self._deps.index_runtime
        execute_retrieval = getattr(index_runtime, "execute_local_graph_retrieval", None)
        if not callable(execute_retrieval):
            _safe_end_span(
                self._trace_adapter,
                span_handle,
                outputs={"status": "blocked", "gaps": ["canonical_index_runtime_unavailable"]},
            )
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="local_graphrag",
                failure_class="canonical_index_runtime_unavailable",
                stop_reason="runtime_blocked",
            )

        start_t = time.monotonic()
        try:
            payload = execute_retrieval(
                question=case_input.question,
                corpus_snapshot_ref=case_input.corpus_snapshot_ref,
            )
        except Exception:
            latency_sec = time.monotonic() - start_t
            _safe_end_span(
                self._trace_adapter,
                span_handle,
                outputs={"status": "blocked", "gaps": ["canonical_knowledge_runtime_exception"]},
            )
            return _build_fail_closed_result(
                case_input=case_input,
                profile_name="local_graphrag",
                failure_class="canonical_knowledge_runtime_exception",
                latency=latency_sec,
                stop_reason="exception_raised",
            )

        latency_sec = time.monotonic() - start_t
        return _normalize_retrieval_payload(
            case_input=case_input,
            profile_name="local_graphrag",
            payload=payload,
            latency=latency_sec,
            end_span=lambda outputs: _safe_end_span(self._trace_adapter, span_handle, outputs=outputs),
        )


def _normalize_retrieval_payload(
    *,
    case_input: CanonicalCaseInput,
    profile_name: str,
    payload: Any,
    latency: float,
    end_span: Any,
) -> CanonicalCaseResult:
    if not isinstance(payload, dict):
        end_span({"status": "blocked", "gaps": ["runtime_payload_invalid"]})
        return _build_fail_closed_result(
            case_input=case_input,
            profile_name=profile_name,
            failure_class="runtime_payload_invalid",
            latency=latency,
            stop_reason="invalid_return_type",
        )

    raw_answer = payload.get("answer", "")
    if not isinstance(raw_answer, str):
        end_span({"status": "blocked", "gaps": ["runtime_payload_invalid"]})
        return _build_fail_closed_result(
            case_input=case_input,
            profile_name=profile_name,
            failure_class="runtime_payload_invalid",
            latency=latency,
            stop_reason="invalid_answer_type",
        )

    evidence_refs = _safe_str_tuple(payload.get("evidence_refs", ()))
    retrieved_docs = _safe_str_tuple(payload.get("retrieved_document_refs", ()))
    rounds = _safe_uint(payload.get("retrieval_rounds", 0))
    if evidence_refs is None or retrieved_docs is None or rounds is None:
        end_span({"status": "blocked", "gaps": ["runtime_payload_invalid"]})
        return _build_fail_closed_result(
            case_input=case_input,
            profile_name=profile_name,
            failure_class="runtime_payload_invalid",
            latency=latency,
            stop_reason="invalid_payload_field_types",
        )

    end_err = end_span({"status": "blocked", "rounds": rounds})
    if end_err is not None:
        return _build_fail_closed_result(
            case_input=case_input,
            profile_name=profile_name,
            failure_class="trace_delivery_failed",
            latency=latency,
            stop_reason="trace_delivery_failed",
        )

    return _build_fail_closed_result(
        case_input=case_input,
        profile_name=profile_name,
        failure_class="canonical_product_runtime_attestation_unavailable",
        latency=latency,
        answer=raw_answer,
        retrieved_document_refs=retrieved_docs,
        retrieved_evidence_refs=evidence_refs,
        retrieval_rounds=rounds,
        stop_reason="product_runtime_attestation_unavailable",
    )

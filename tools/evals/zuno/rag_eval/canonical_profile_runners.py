"""Zuno PHASE22 Canonical Four-Profile Benchmark Runtime.

This module provides canonical, non-double profile runners for Zuno benchmark
evaluation. Each runner connects directly to Zuno's production Knowledge Runtime
and Index Runtime.

Truth Contract (AG-PR55-CANONICAL-RUNTIME-TRUTH-REPAIR):
- No synthetic receipt refs. Fields only populated from real Runtime receipts.
- No template answers. Empty answer -> BLOCKED.
- No hardcoded token_usage / cost. Set to 0 until ModelUsageReceipt exists.
- No hardcoded security gate checks. Security wiring is BLOCKED pending
  a formal Canonical Security Composition Root in the Eval layer.
- trace_id comes from TraceSpanHandle.trace_id. No span -> trace_id = None.
- Agentic profile requires full AgentRunGraph. Currently BLOCKED.
- plan_version_ref, run_outcome_ref, budget_settlement_ref: empty.
  Receipt types do not yet exist in the repository.

BLOCKED reasons use deterministic enum strings:
  canonical_security_gate_unavailable
  canonical_agent_run_graph_unavailable
  canonical_result_store_unavailable
  answer_receipt_missing
  trace_not_sampled
  retriever_failed
  index_unavailable
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from zuno.agent.contracts import RetrievalProfile
from zuno.knowledge.agentic import (
    CorrectiveAgenticRetrievalRuntime,
    CorrectiveRetrievalRequest,
    CorrectiveRetrievalResult,
)
from zuno.knowledge.indexing import KnowledgeIndexRuntime
from zuno.platform.observability.trace_adapter import (
    ObservabilityTracePort,
    TraceSpanHandle,
    get_observability_adapter,
)


# ---------------------------------------------------------------------------
# Dependency Bundle
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class CanonicalRuntimeDependencies:
    """Explicit dependency bundle for canonical benchmark profile runners.

    In canonical mode ALL profile runners must receive this bundle from an
    external Composition Root. Runners must NOT create their own instances
    of knowledge_runtime or index_runtime. If a required dependency is absent
    the factory returns BLOCKED; runners never auto-downgrade.

    Fields:
        knowledge_runtime:  CorrectiveAgenticRetrievalRuntime (required for all profiles).
        index_runtime:      KnowledgeIndexRuntime (required for local_graphrag).
        trace_adapter:      ObservabilityTracePort (optional; None -> trace_not_sampled).
    """
    knowledge_runtime: Optional[CorrectiveAgenticRetrievalRuntime] = None
    index_runtime: Optional[KnowledgeIndexRuntime] = None
    trace_adapter: Optional[ObservabilityTracePort] = None


# ---------------------------------------------------------------------------
# Data contracts
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class CanonicalCaseInput:
    eval_run_id: str
    case_id: str
    profile_name: str
    question: str
    question_type: str = "factoid"
    tenant_id: str = "tenant_default"
    workspace_id: str = "workspace_default"
    knowledge_space_ids: tuple[str, ...] = ("ks_default",)
    corpus_snapshot_ref: str = "snapshot_v1"
    gold_document_refs: tuple[str, ...] = ()
    gold_evidence_refs: tuple[str, ...] = ()
    authorization_ref: str = "auth_valid_default"
    security_epoch: str = "epoch_2026"
    budget: dict[str, Any] = field(default_factory=dict)
    deadline: str = ""
    trace_parent: str = ""
    model_policy_ref: str = "policy_standard"
    attempt_number: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CanonicalCaseResult:
    eval_run_id: str
    case_id: str
    profile_name: str
    runtime_status: str
    # measurement_state: deterministic enum string from MeasurementTruthGate
    measurement_state: str
    answer: str
    retrieved_document_refs: tuple[str, ...]
    retrieved_evidence_refs: tuple[str, ...]
    citation_refs: tuple[str, ...]
    knowledge_snapshot_ref: str
    # Receipts: empty until formal Receipt types exist in the repository.
    plan_version_ref: str
    run_outcome_ref: str
    budget_settlement_ref: str
    # trace_id: None if trace adapter did not sample this span.
    trace_id: Optional[str]
    retrieval_rounds: int
    # latency: real wall-clock seconds from monotonic timer.
    latency: float
    # token_usage / cost: 0 until ModelUsageReceipt is wired.
    token_usage: int
    cost: float
    # failure_class: deterministic enum string.
    failure_class: str
    retry_count: int
    standard_floor_preserved: bool
    is_test_double: bool = False
    blocked_reason: str = ""
    evidence_refs: tuple[str, ...] = ()
    standard_candidate_refs: tuple[str, ...] = ()
    graph_added_refs: tuple[str, ...] = ()
    graph_added_gold_refs: tuple[str, ...] = ()
    graph_added_non_gold_refs: tuple[str, ...] = ()
    final_candidate_refs: tuple[str, ...] = ()
    retrieval_trace: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helper: extract trace_id from span handle
# ---------------------------------------------------------------------------

def _extract_trace_id(handle: Optional[TraceSpanHandle]) -> Optional[str]:
    """Extract the trace_id from a TraceSpanHandle.

    Returns None if handle is None (trace not sampled or Noop adapter).
    Never constructs a synthetic trace ID.
    """
    if handle is None:
        return None
    return handle.trace_id


def _blocked_result(
    case_input: CanonicalCaseInput,
    profile_name: str,
    blocked_reason: str,
    failure_class: str,
    latency: float,
    trace_id: Optional[str] = None,
    runtime_status: str = "blocked",
) -> CanonicalCaseResult:
    return CanonicalCaseResult(
        eval_run_id=case_input.eval_run_id,
        case_id=case_input.case_id,
        profile_name=profile_name,
        runtime_status=runtime_status,
        measurement_state="BLOCKED",
        answer="",
        retrieved_document_refs=(),
        retrieved_evidence_refs=(),
        citation_refs=(),
        knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
        plan_version_ref="",
        run_outcome_ref="",
        budget_settlement_ref="",
        trace_id=trace_id,
        retrieval_rounds=0,
        latency=latency,
        token_usage=0,
        cost=0.0,
        failure_class=failure_class,
        retry_count=0,
        standard_floor_preserved=True,
        is_test_double=False,
        blocked_reason=blocked_reason,
    )


def _failed_result(
    case_input: CanonicalCaseInput,
    profile_name: str,
    failure_class: str,
    blocked_reason: str,
    latency: float,
    trace_id: Optional[str] = None,
) -> CanonicalCaseResult:
    return CanonicalCaseResult(
        eval_run_id=case_input.eval_run_id,
        case_id=case_input.case_id,
        profile_name=profile_name,
        runtime_status="failed",
        measurement_state="FAILED",
        answer="",
        retrieved_document_refs=(),
        retrieved_evidence_refs=(),
        citation_refs=(),
        knowledge_snapshot_ref=case_input.corpus_snapshot_ref,
        plan_version_ref="",
        run_outcome_ref="",
        budget_settlement_ref="",
        trace_id=trace_id,
        retrieval_rounds=0,
        latency=latency,
        token_usage=0,
        cost=0.0,
        failure_class=failure_class,
        retry_count=0,
        standard_floor_preserved=False,
        is_test_double=False,
        blocked_reason=blocked_reason,
    )


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class CanonicalBenchmarkProfileRunner(ABC):
    """Abstract base for canonical benchmark profile runners.

    Subclasses receive a CanonicalRuntimeDependencies bundle from the factory.
    They must NOT create their own KnowledgeIndexRuntime or other infrastructure.
    """

    def __init__(self, deps: CanonicalRuntimeDependencies) -> None:
        self._deps = deps

    @property
    def is_test_double(self) -> bool:
        return False

    @property
    def _trace_adapter(self) -> ObservabilityTracePort:
        return self._deps.trace_adapter or get_observability_adapter()

    @abstractmethod
    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        pass


# ---------------------------------------------------------------------------
# Standard RAG Runner
# ---------------------------------------------------------------------------

class CanonicalStandardRAGRunner(CanonicalBenchmarkProfileRunner):
    """Canonical Standard RAG Profile (BM25 + Vector + Fusion + EvidenceLedger).

    Requires: deps.knowledge_runtime (CorrectiveAgenticRetrievalRuntime).
    Security wiring: BLOCKED (canonical_security_gate_unavailable).
    Budget settlement: not available -> budget_settlement_ref = "".
    Token/cost: 0 (ModelUsageReceipt not wired).
    """

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        start_time = time.monotonic()
        adapter = self._trace_adapter
        span_handle = adapter.start_span(
            "benchmark_case",
            span_type="RetrievalRound",
            metadata={
                "eval_run_id": case_input.eval_run_id,
                "case_id": case_input.case_id,
                "profile": "standard_rag",
                "tenant_id": case_input.tenant_id,
                "workspace_id": case_input.workspace_id,
                "snapshot_ref": case_input.corpus_snapshot_ref,
                "attempt_number": case_input.attempt_number,
            },
        )
        trace_id = _extract_trace_id(span_handle)

        # Security gate: BLOCKED — no formal security gate available in eval layer
        # Never check authorization_ref string content; that is not a security check.
        adapter.end_span(span_handle, outputs={"status": "blocked", "reason": "canonical_security_gate_unavailable"})
        return _blocked_result(
            case_input,
            "standard_rag",
            blocked_reason="canonical_security_gate_unavailable",
            failure_class="canonical_security_gate_unavailable",
            latency=time.monotonic() - start_time,
            trace_id=trace_id,
        )


# ---------------------------------------------------------------------------
# Local GraphRAG Runner
# ---------------------------------------------------------------------------

class CanonicalLocalGraphRAGRunner(CanonicalBenchmarkProfileRunner):
    """Canonical Local GraphRAG Profile (entity/relation + neighborhood).

    Requires: deps.knowledge_runtime + deps.index_runtime.
    Security wiring: BLOCKED (canonical_security_gate_unavailable).
    """

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        start_time = time.monotonic()
        adapter = self._trace_adapter
        span_handle = adapter.start_span(
            "benchmark_case",
            span_type="Graph",
            metadata={
                "eval_run_id": case_input.eval_run_id,
                "case_id": case_input.case_id,
                "profile": "local_graphrag",
                "tenant_id": case_input.tenant_id,
                "workspace_id": case_input.workspace_id,
                "snapshot_ref": case_input.corpus_snapshot_ref,
            },
        )
        trace_id = _extract_trace_id(span_handle)

        adapter.end_span(span_handle, outputs={"status": "blocked", "reason": "canonical_security_gate_unavailable"})
        return _blocked_result(
            case_input,
            "local_graphrag",
            blocked_reason="canonical_security_gate_unavailable",
            failure_class="canonical_security_gate_unavailable",
            latency=time.monotonic() - start_time,
            trace_id=trace_id,
        )


# ---------------------------------------------------------------------------
# Deep GraphRAG Runner
# ---------------------------------------------------------------------------

class CanonicalDeepGraphRAGRunner(CanonicalBenchmarkProfileRunner):
    """Canonical Deep GraphRAG Profile (multi-round corrective retrieval).

    Requires: deps.knowledge_runtime.
    Security wiring: BLOCKED (canonical_security_gate_unavailable).
    """

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        start_time = time.monotonic()
        adapter = self._trace_adapter
        span_handle = adapter.start_span(
            "benchmark_case",
            span_type="Replan",
            metadata={
                "eval_run_id": case_input.eval_run_id,
                "case_id": case_input.case_id,
                "profile": "deep_graphrag",
                "tenant_id": case_input.tenant_id,
                "workspace_id": case_input.workspace_id,
                "snapshot_ref": case_input.corpus_snapshot_ref,
            },
        )
        trace_id = _extract_trace_id(span_handle)

        adapter.end_span(span_handle, outputs={"status": "blocked", "reason": "canonical_security_gate_unavailable"})
        return _blocked_result(
            case_input,
            "deep_graphrag",
            blocked_reason="canonical_security_gate_unavailable",
            failure_class="canonical_security_gate_unavailable",
            latency=time.monotonic() - start_time,
            trace_id=trace_id,
        )


# ---------------------------------------------------------------------------
# Agentic GraphRAG Runner
# ---------------------------------------------------------------------------

class CanonicalAgenticGraphRAGRunner(CanonicalBenchmarkProfileRunner):
    """Canonical Agentic GraphRAG Profile.

    Requires: full AgentRunGraph Composition Root.
    Current status: BLOCKED (canonical_agent_run_graph_unavailable).

    The formal AgentRunGraph (build_agent_graph in zuno.agent.runtime.graph)
    exists in the repository but requires a complete RuntimeDependencies
    injection from a Composition Root that is not available in the eval layer.
    This runner returns BLOCKED rather than simulate the run with manual
    Retrieval -> RuntimeObservation -> AgentControlRuntime.run() assembly,
    which would constitute a false claim of Agentic Graph wiring.

    When the Composition Root is available, this runner will:
    - Call build_agent_graph(dependencies=...) with injected deps
    - Read plan_version_ref from plan_state.plan_id
    - Read run_outcome_ref from AgentRuntimeResult.finalized
    - Read answer from AgentRuntimeResult.final_answer
    """

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        start_time = time.monotonic()
        adapter = self._trace_adapter
        span_handle = adapter.start_span(
            "benchmark_case",
            span_type="AgentRun",
            metadata={
                "eval_run_id": case_input.eval_run_id,
                "case_id": case_input.case_id,
                "profile": "agentic_graphrag",
                "tenant_id": case_input.tenant_id,
                "workspace_id": case_input.workspace_id,
                "snapshot_ref": case_input.corpus_snapshot_ref,
            },
        )
        trace_id = _extract_trace_id(span_handle)

        adapter.end_span(span_handle, outputs={"status": "blocked", "reason": "canonical_agent_run_graph_unavailable"})
        return _blocked_result(
            case_input,
            "agentic_graphrag",
            blocked_reason="canonical_agent_run_graph_unavailable",
            failure_class="canonical_agent_run_graph_unavailable",
            latency=time.monotonic() - start_time,
            trace_id=trace_id,
        )

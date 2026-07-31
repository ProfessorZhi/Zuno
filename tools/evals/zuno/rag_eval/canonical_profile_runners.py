"""Zuno PHASE22 Canonical Four-Profile Benchmark Runtime.

These runners define fail-closed canonical benchmark adapter boundaries.
Formal execution adapters are not yet implemented.

Truth Contract (AG-PR55-GEMINI-3-6-FLASH-PREMERGE-HARDENING):
- Explicit CanonicalRuntimeDependencies bundle required.
- Preflight gap validation returns precise dependency gap codes when ports are missing.
- When all dependency ports are present but formal execution adapter is not yet wired,
  runners return canonical_<profile>_execution_adapter_unavailable.
- blocked_reason is ALWAYS non-empty. No generic fallback when dependency_gaps is empty.
- Standard floor preserved: None when retrieval is not executed (blocked result).
- Receipt fields are empty strings pending formal Receipt types in repository.
- token_usage / cost set to 0.0 until ModelUsageReceipt is wired.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from zuno.agent.contracts import RetrievalProfile
from zuno.platform.observability.trace_adapter import (
    ObservabilityTracePort,
    TraceSpanHandle,
)


# ---------------------------------------------------------------------------
# Dependency Bundle & Preflight
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class CanonicalRuntimeDependencies:
    """Explicit dependency bundle for canonical benchmark profile runners.

    In canonical mode ALL profile runners receive this bundle from an
    external Composition Root. Runners must NOT create their own instances
    of knowledge_runtime, index_runtime, or trace_adapter. If a required
    dependency is absent, preflight returns deterministic gap codes.
    """
    knowledge_runtime: Optional[Any] = None
    index_runtime: Optional[Any] = None
    security_gate: Optional[Any] = None
    agent_run_runtime: Optional[Any] = None
    trace_adapter: Optional[ObservabilityTracePort] = None
    result_store: Optional[Any] = None
    artifact_store: Optional[Any] = None
    usage_receipt_provider: Optional[Any] = None
    budget_settlement_provider: Optional[Any] = None

    def validate_dependencies(self, profile_name: str) -> list[str]:
        """Validate dependencies for the requested profile and return gap codes."""
        gaps: list[str] = []
        if self.security_gate is None:
            gaps.append("canonical_security_gate_unavailable")
        if self.knowledge_runtime is None:
            gaps.append("canonical_knowledge_runtime_unavailable")
        if profile_name == "local_graphrag" and self.index_runtime is None:
            gaps.append("canonical_index_runtime_unavailable")
        if profile_name == "agentic_graphrag" and self.agent_run_runtime is None:
            gaps.append("canonical_agent_run_graph_unavailable")
        if self.trace_adapter is None:
            gaps.append("canonical_trace_adapter_unavailable")
        if self.result_store is None:
            gaps.append("canonical_result_store_unavailable")
        if self.artifact_store is None:
            gaps.append("canonical_artifact_store_unavailable")
        if self.usage_receipt_provider is None:
            gaps.append("canonical_usage_receipt_provider_unavailable")
        if self.budget_settlement_provider is None:
            gaps.append("canonical_budget_settlement_provider_unavailable")
        return gaps

    def is_empty(self) -> bool:
        return all(
            v is None for v in (
                self.knowledge_runtime,
                self.index_runtime,
                self.security_gate,
                self.agent_run_runtime,
                self.trace_adapter,
                self.result_store,
                self.artifact_store,
                self.usage_receipt_provider,
                self.budget_settlement_provider,
            )
        )


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
    measurement_state: str
    answer: str
    retrieved_document_refs: tuple[str, ...]
    retrieved_evidence_refs: tuple[str, ...]
    citation_refs: tuple[str, ...]
    knowledge_snapshot_ref: str
    # Receipts: empty until formal Receipt types exist in repository.
    plan_version_ref: str
    run_outcome_ref: str
    budget_settlement_ref: str
    artifact_receipt_ref: str = ""
    # trace_id: None if trace_adapter is missing or span not sampled.
    trace_id: Optional[str] = None
    retrieval_rounds: int = 0
    latency: float = 0.0
    token_usage: int = 0
    cost: float = 0.0
    failure_class: str = ""
    retry_count: int = 0
    # standard_floor_preserved: None when floor was not evaluated (e.g. blocked)
    standard_floor_preserved: Optional[bool] = None
    is_test_double: bool = False
    blocked_reason: str = ""
    dependency_gaps: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    standard_candidate_refs: tuple[str, ...] = ()
    graph_added_refs: tuple[str, ...] = ()
    graph_added_gold_refs: tuple[str, ...] = ()
    graph_added_non_gold_refs: tuple[str, ...] = ()
    final_candidate_refs: tuple[str, ...] = ()
    retrieval_trace: dict[str, Any] = field(default_factory=dict)


def _extract_trace_id(handle: Optional[TraceSpanHandle]) -> Optional[str]:
    if handle is None:
        return None
    return handle.trace_id


def _blocked_result(
    case_input: CanonicalCaseInput,
    profile_name: str,
    gaps: list[str],
    latency: float,
    trace_id: Optional[str] = None,
) -> CanonicalCaseResult:
    if gaps:
        primary_blocker = gaps[0]
        blocked_reason = ",".join(gaps)
        dep_gaps = tuple(gaps)
    else:
        execution_adapter_blockers = {
            "standard_rag": "canonical_standard_execution_adapter_unavailable",
            "local_graphrag": "canonical_local_execution_adapter_unavailable",
            "deep_graphrag": "canonical_deep_execution_adapter_unavailable",
            "agentic_graphrag": "canonical_agentic_execution_adapter_unavailable",
        }
        primary_blocker = execution_adapter_blockers.get(
            profile_name, f"canonical_{profile_name}_execution_adapter_unavailable"
        )
        blocked_reason = primary_blocker
        dep_gaps = ()

    return CanonicalCaseResult(
        eval_run_id=case_input.eval_run_id,
        case_id=case_input.case_id,
        profile_name=profile_name,
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
        latency=latency,
        token_usage=0,
        cost=0.0,
        failure_class=primary_blocker,
        retry_count=0,
        standard_floor_preserved=None,
        is_test_double=False,
        blocked_reason=blocked_reason,
        dependency_gaps=dep_gaps,
    )


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class CanonicalBenchmarkProfileRunner(ABC):
    """Abstract base for canonical benchmark profile runners."""

    def __init__(self, deps: CanonicalRuntimeDependencies) -> None:
        self._deps = deps

    @property
    def is_test_double(self) -> bool:
        return False

    @property
    def _trace_adapter(self) -> Optional[ObservabilityTracePort]:
        # MUST NOT fall back to global get_observability_adapter()
        return self._deps.trace_adapter

    @abstractmethod
    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        pass


# ---------------------------------------------------------------------------
# Standard RAG Runner
# ---------------------------------------------------------------------------

class CanonicalStandardRAGRunner(CanonicalBenchmarkProfileRunner):
    """Canonical Standard RAG Profile Runner."""

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        start_time = time.monotonic()
        gaps = self._deps.validate_dependencies("standard_rag")
        adapter = self._trace_adapter

        span_handle = None
        if adapter is not None:
            span_handle = adapter.start_span(
                "benchmark_case",
                span_type="RetrievalRound",
                metadata={
                    "eval_run_id": case_input.eval_run_id,
                    "case_id": case_input.case_id,
                    "profile": "standard_rag",
                    "tenant_id": case_input.tenant_id,
                    "workspace_id": case_input.workspace_id,
                },
            )
        trace_id = _extract_trace_id(span_handle)
        if adapter is not None and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": gaps})

        return _blocked_result(
            case_input,
            "standard_rag",
            gaps=gaps,
            latency=time.monotonic() - start_time,
            trace_id=trace_id,
        )


# ---------------------------------------------------------------------------
# Local GraphRAG Runner
# ---------------------------------------------------------------------------

class CanonicalLocalGraphRAGRunner(CanonicalBenchmarkProfileRunner):
    """Canonical Local GraphRAG Profile Runner."""

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        start_time = time.monotonic()
        gaps = self._deps.validate_dependencies("local_graphrag")
        adapter = self._trace_adapter

        span_handle = None
        if adapter is not None:
            span_handle = adapter.start_span(
                "benchmark_case",
                span_type="Graph",
                metadata={
                    "eval_run_id": case_input.eval_run_id,
                    "case_id": case_input.case_id,
                    "profile": "local_graphrag",
                },
            )
        trace_id = _extract_trace_id(span_handle)
        if adapter is not None and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": gaps})

        return _blocked_result(
            case_input,
            "local_graphrag",
            gaps=gaps,
            latency=time.monotonic() - start_time,
            trace_id=trace_id,
        )


# ---------------------------------------------------------------------------
# Deep GraphRAG Runner
# ---------------------------------------------------------------------------

class CanonicalDeepGraphRAGRunner(CanonicalBenchmarkProfileRunner):
    """Canonical Deep GraphRAG Profile Runner."""

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        start_time = time.monotonic()
        gaps = self._deps.validate_dependencies("deep_graphrag")
        adapter = self._trace_adapter

        span_handle = None
        if adapter is not None:
            span_handle = adapter.start_span(
                "benchmark_case",
                span_type="Replan",
                metadata={
                    "eval_run_id": case_input.eval_run_id,
                    "case_id": case_input.case_id,
                    "profile": "deep_graphrag",
                },
            )
        trace_id = _extract_trace_id(span_handle)
        if adapter is not None and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": gaps})

        return _blocked_result(
            case_input,
            "deep_graphrag",
            gaps=gaps,
            latency=time.monotonic() - start_time,
            trace_id=trace_id,
        )


# ---------------------------------------------------------------------------
# Agentic GraphRAG Runner
# ---------------------------------------------------------------------------

class CanonicalAgenticGraphRAGRunner(CanonicalBenchmarkProfileRunner):
    """Canonical Agentic GraphRAG Profile Runner."""

    def run_canonical_case(self, case_input: CanonicalCaseInput) -> CanonicalCaseResult:
        start_time = time.monotonic()
        gaps = self._deps.validate_dependencies("agentic_graphrag")
        adapter = self._trace_adapter

        span_handle = None
        if adapter is not None:
            span_handle = adapter.start_span(
                "benchmark_case",
                span_type="AgentRun",
                metadata={
                    "eval_run_id": case_input.eval_run_id,
                    "case_id": case_input.case_id,
                    "profile": "agentic_graphrag",
                },
            )
        trace_id = _extract_trace_id(span_handle)
        if adapter is not None and span_handle is not None:
            adapter.end_span(span_handle, outputs={"status": "blocked", "gaps": gaps})

        return _blocked_result(
            case_input,
            "agentic_graphrag",
            gaps=gaps,
            latency=time.monotonic() - start_time,
            trace_id=trace_id,
        )

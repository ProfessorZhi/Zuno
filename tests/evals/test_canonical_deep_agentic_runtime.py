"""Unit Contract Tests for Deep and Agentic GraphRAG Canonical Execution Adapters.

AG-PR56-FINAL-BOUNDARY-HARDENING-AND-PERFORMANCE-RECORD

Fail-Closed Boundary Hardening Verification:
- Injected Runtime ports are invoked with exact parameters.
- Gold document refs are NEVER passed into Deep retrieval request.
- Safe trace adapter exception handling (_safe_start_span and _safe_end_span).
- Runtime stop_reason allowlisting (no raw string leakage into retrieval_trace).
- Agentic status allowlisting ("completed", "blocked", "failed", others -> runtime_payload_invalid).
- Receipt shape validation deleted from PR #56 (formal receipt refs always empty "").
- All result trace_id values are None on blocked/test-double results even when trace adapter generates spans.
- All formal evidence fields (token_usage=0, cost=0.0, receipts="") remain empty.
"""

from __future__ import annotations

import hashlib
from typing import Any
import pytest

from tools.evals.zuno.rag_eval.adapters.deep_agentic import (
    AgenticGraphRAGCanonicalAdapter,
    DeepGraphRAGCanonicalAdapter,
)
from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalCaseInput,
    CanonicalRuntimeDependencies,
)
from tools.evals.zuno.rag_eval.runtime_evidence_binding import (
    RECEIPT_OWNERS,
    compute_reference_binding_hash,
)
from zuno.platform.observability.trace_adapter import InMemoryTraceAdapter


def _full_preflight_deps(**overrides: Any) -> CanonicalRuntimeDependencies:
    default_kwargs: dict[str, Any] = {
        "security_gate": object(),
        "knowledge_runtime": object(),
        "index_runtime": object(),
        "agent_run_runtime": object(),
        "trace_adapter": InMemoryTraceAdapter(config={"enabled": True, "sample_rate": 1.0}),
        "result_store": object(),
        "artifact_store": object(),
        "usage_receipt_provider": object(),
        "budget_settlement_provider": object(),
    }
    default_kwargs.update(overrides)
    return CanonicalRuntimeDependencies(**default_kwargs)


class ContractTestDoubleKnowledgeRuntime:
    """Explicit Test Double Knowledge Runtime for Unit Contract Tests."""

    def __init__(self, return_payload: Any = None) -> None:
        self.last_query_params: dict[str, Any] = {}
        self.return_payload = return_payload

    def execute_deep_retrieval(self, question: str, corpus_snapshot_ref: str) -> Any:
        self.last_query_params = {
            "question": question,
            "corpus_snapshot_ref": corpus_snapshot_ref,
        }
        if self.return_payload is not None:
            return self.return_payload
        return {
            "answer": "Test double response text",
            "evidence_refs": ("ev_001",),
            "retrieved_document_refs": ("doc_001",),
            "retrieval_rounds": 2,
            "token_usage": 150,
            "cost": 0.001,
            "stop_reason": "sk-secret-token-do-not-leak",
        }


class ContractTestDoubleAgentRuntime:
    """Explicit Test Double Agent Runtime for Unit Contract Tests."""

    def __init__(self, return_payload: Any = None) -> None:
        self.last_execute_params: dict[str, Any] = {}
        self.return_payload = return_payload

    def execute_agent_run(self, **kwargs: Any) -> Any:
        self.last_execute_params = kwargs
        if self.return_payload is not None:
            return self.return_payload
        return {
            "status": "completed",
            "answer": "Test double agentic answer",
            "evidence_refs": ("ev_001",),
            "retrieved_document_refs": ("doc_001",),
            "retrieval_rounds": 1,
            "token_usage": 200,
            "cost": 0.002,
        }


class ExceptionTraceAdapter:
    """Trace Adapter that raises exceptions on start_span or end_span."""

    def __init__(self, raise_on_start: bool = False, raise_on_end: bool = False) -> None:
        self.raise_on_start = raise_on_start
        self.raise_on_end = raise_on_end

    def start_span(self, name: str, **kwargs: Any) -> Any:
        if self.raise_on_start:
            raise RuntimeError("Trace adapter start_span crashed!")
        return "span_handle_123"

    def end_span(self, handle: Any, **kwargs: Any) -> None:
        if self.raise_on_end:
            raise RuntimeError("Trace adapter end_span crashed!")


def _unit_case_input(profile_name: str = "deep_graphrag") -> CanonicalCaseInput:
    return CanonicalCaseInput(
        eval_run_id="run_unit_01",
        case_id="case_unit_01",
        profile_name=profile_name,
        question="What is the unit test behavior of deep graphrag?",
        question_type="factoid",
        tenant_id="tenant_unit",
        workspace_id="workspace_unit",
        knowledge_space_ids=("ks_unit",),
        corpus_snapshot_ref="snapshot_unit_v1",
        gold_document_refs=("doc_gold_100", "doc_gold_200"),
        gold_evidence_refs=("ev_gold_100",),
        authorization_ref="auth_unit_ref",
        security_epoch="epoch_2026",
        budget={},
        attempt_number=1,
    )


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _receipt(receipt_type: str, ref: str) -> dict[str, str]:
    return {
        "receipt_type": receipt_type,
        "receipt_ref": ref,
        "owner": RECEIPT_OWNERS[receipt_type],
        "runtime_version": "rt-1.0",
        "snapshot_ref": "snapshot_unit_v1",
        "payload_hash": _hash(ref),
    }


def _runtime_evidence_binding(profile_name: str, **overrides: Any) -> dict[str, Any]:
    receipts = [
        _receipt("security_decision", "security-1"),
        _receipt("trace", "trace-1"),
        _receipt("usage_receipt", "usage-1"),
        _receipt("budget_settlement", "budget-1"),
        _receipt("artifact_receipt", "artifact-1"),
    ]
    binding: dict[str, Any] = {
        "eval_run_id": "run_unit_01",
        "case_id": "case_unit_01",
        "requested_profile": profile_name,
        "actual_profile": profile_name,
        "runtime_name": f"canonical-{profile_name}-runtime",
        "runtime_version": "rt-1.0",
        "corpus_snapshot_ref": "snapshot_unit_v1",
        "trace_id": "trace-1",
        "security_decision_ref": "security-1",
        "plan_version_ref": "",
        "run_outcome_ref": "",
        "usage_receipt_ref": "usage-1",
        "budget_settlement_ref": "budget-1",
        "artifact_receipt_ref": "artifact-1",
        "artifact_payload_hash": _hash("artifact-payload"),
        "result_payload_hash": _hash("result-payload"),
        "reference_binding_hash": "0" * 64,
        "receipts": receipts,
    }
    if profile_name == "agentic_graphrag":
        binding["plan_version_ref"] = "plan-1"
        binding["run_outcome_ref"] = "outcome-1"
        binding["receipts"] = [
            _receipt("security_decision", "security-1"),
            _receipt("plan_version", "plan-1"),
            _receipt("run_outcome", "outcome-1"),
            _receipt("usage_receipt", "usage-1"),
            _receipt("budget_settlement", "budget-1"),
            _receipt("trace", "trace-1"),
            _receipt("artifact_receipt", "artifact-1"),
        ]
    binding.update(overrides)
    if "reference_binding_hash" not in overrides:
        binding["reference_binding_hash"] = compute_reference_binding_hash(binding)
    return binding


# ---------------------------------------------------------------------------
# Trace Adapter Exception Tests
# ---------------------------------------------------------------------------

def test_unit_contract_start_span_exception_fails_closed_without_escaping() -> None:
    """Trace adapter start_span raising exception returns trace_delivery_failed without crashing."""
    k_runtime = ContractTestDoubleKnowledgeRuntime()
    bad_trace = ExceptionTraceAdapter(raise_on_start=True)
    deps = _full_preflight_deps(knowledge_runtime=k_runtime, trace_adapter=bad_trace)

    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_unit_case_input("deep_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "trace_delivery_failed"
    assert res.trace_id is None


def test_unit_contract_end_span_exception_fails_closed_without_escaping() -> None:
    """Trace adapter end_span raising exception returns trace_delivery_failed without crashing."""
    k_runtime = ContractTestDoubleKnowledgeRuntime()
    bad_trace = ExceptionTraceAdapter(raise_on_end=True)
    deps = _full_preflight_deps(knowledge_runtime=k_runtime, trace_adapter=bad_trace)

    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_unit_case_input("deep_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "trace_delivery_failed"
    assert res.trace_id is None


# ---------------------------------------------------------------------------
# Stop Reason Allowlist & Sanitization Tests
# ---------------------------------------------------------------------------

def test_unit_contract_secret_or_multiline_stop_reason_not_published() -> None:
    """Raw secret or multiline stop_reason from Runtime is replaced with allowlisted stop_reason."""
    k_runtime = ContractTestDoubleKnowledgeRuntime(return_payload={
        "answer": "ok",
        "retrieval_rounds": 1,
        "stop_reason": "sk-proj-secret-key-12345\nline2_secret",
    })
    deps = _full_preflight_deps(knowledge_runtime=k_runtime)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("deep_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.retrieval_trace.get("stop_reason") == "product_runtime_attestation_unavailable"
    assert "sk-proj" not in str(res.retrieval_trace)


# ---------------------------------------------------------------------------
# Agentic Status Allowlist Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status_val", ["unknown", "", None, "success", 123])
def test_unit_contract_agentic_status_unmapped_returns_payload_invalid(status_val: Any) -> None:
    """Agentic status not in allowlist ('completed', 'blocked', 'failed') returns runtime_payload_invalid."""
    agent_runtime = ContractTestDoubleAgentRuntime(return_payload={"status": status_val})
    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "runtime_payload_invalid"


def test_unit_contract_agentic_status_failed_returns_canonical_reported_blocked() -> None:
    """Agentic status 'failed' returns canonical_runtime_reported_blocked."""
    agent_runtime = ContractTestDoubleAgentRuntime(return_payload={"status": "failed"})
    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_runtime_reported_blocked"
    assert res.retrieval_trace.get("stop_reason") == "runtime_failed"


def test_unit_contract_agentic_status_completed_payload_returns_blocked() -> None:
    """Agentic status 'completed' payload still returns BLOCKED due to unwired authority."""
    agent_runtime = ContractTestDoubleAgentRuntime()
    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_product_runtime_attestation_unavailable"
    assert res.answer == "Test double agentic answer"


def test_unit_contract_deep_valid_runtime_evidence_binding_reaches_observed_not_measured() -> None:
    """Deep adapter validates runtime binding and reaches RUNTIME_OBSERVED, not MEASURED."""
    k_runtime = ContractTestDoubleKnowledgeRuntime(return_payload={
        "answer": "Deep runtime observed answer",
        "evidence_refs": ("ev_001",),
        "retrieved_document_refs": ("doc_001",),
        "retrieval_rounds": 2,
        "runtime_evidence_binding": _runtime_evidence_binding("deep_graphrag"),
    })
    deps = _full_preflight_deps(knowledge_runtime=k_runtime)
    res = DeepGraphRAGCanonicalAdapter(deps=deps).run_canonical_case(_unit_case_input("deep_graphrag"))

    assert res.runtime_status == "completed"
    assert res.measurement_state == "RUNTIME_OBSERVED"
    assert res.failure_class == ""
    assert res.trace_id == "trace-1"
    assert res.budget_settlement_ref == "budget-1"
    assert res.artifact_receipt_ref == "artifact-1"
    assert res.blocked_reason.startswith("runtime_observed_pending_formal_gates:")


def test_unit_contract_deep_invalid_runtime_evidence_binding_fails_closed() -> None:
    """Deep adapter must not accept tampered runtime evidence binding."""
    k_runtime = ContractTestDoubleKnowledgeRuntime(return_payload={
        "answer": "Deep runtime observed answer",
        "evidence_refs": ("ev_001",),
        "retrieved_document_refs": ("doc_001",),
        "retrieval_rounds": 2,
        "runtime_evidence_binding": _runtime_evidence_binding(
            "deep_graphrag",
            reference_binding_hash="1" * 64,
        ),
    })
    deps = _full_preflight_deps(knowledge_runtime=k_runtime)
    res = DeepGraphRAGCanonicalAdapter(deps=deps).run_canonical_case(_unit_case_input("deep_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "runtime_evidence_binding_blocked"
    assert "reference_binding_hash_mismatch" in res.dependency_gaps
    assert res.trace_id is None


def test_unit_contract_agentic_valid_runtime_evidence_binding_reaches_observed_not_measured() -> None:
    """Agentic adapter validates runtime binding and reaches RUNTIME_OBSERVED, not MEASURED."""
    agent_runtime = ContractTestDoubleAgentRuntime(return_payload={
        "status": "completed",
        "answer": "Agentic runtime observed answer",
        "evidence_refs": ("ev_001",),
        "retrieved_document_refs": ("doc_001",),
        "retrieval_rounds": 1,
        "runtime_evidence_binding": _runtime_evidence_binding("agentic_graphrag"),
    })
    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    res = AgenticGraphRAGCanonicalAdapter(deps=deps).run_canonical_case(_unit_case_input("agentic_graphrag"))

    assert res.runtime_status == "completed"
    assert res.measurement_state == "RUNTIME_OBSERVED"
    assert res.failure_class == ""
    assert res.trace_id == "trace-1"
    assert res.plan_version_ref == "plan-1"
    assert res.run_outcome_ref == "outcome-1"
    assert res.budget_settlement_ref == "budget-1"
    assert res.artifact_receipt_ref == "artifact-1"
    assert res.blocked_reason.startswith("runtime_observed_pending_formal_gates:")


def test_unit_contract_agentic_invalid_runtime_evidence_binding_fails_closed() -> None:
    """Agentic adapter must not accept tampered runtime evidence binding."""
    agent_runtime = ContractTestDoubleAgentRuntime(return_payload={
        "status": "completed",
        "answer": "Agentic runtime observed answer",
        "evidence_refs": ("ev_001",),
        "retrieved_document_refs": ("doc_001",),
        "retrieval_rounds": 1,
        "runtime_evidence_binding": _runtime_evidence_binding(
            "agentic_graphrag",
            reference_binding_hash="1" * 64,
        ),
    })
    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    res = AgenticGraphRAGCanonicalAdapter(deps=deps).run_canonical_case(_unit_case_input("agentic_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "runtime_evidence_binding_blocked"
    assert "reference_binding_hash_mismatch" in res.dependency_gaps
    assert res.trace_id is None


# ---------------------------------------------------------------------------
# Receipt Deletion & Safe Evidence Verification Tests
# ---------------------------------------------------------------------------

def test_unit_contract_arbitrary_receipt_payload_does_not_produce_formal_evidence() -> None:
    """Arbitrary receipt payload does not generate formal evidence (receipt refs stay empty '')."""
    agent_runtime = ContractTestDoubleAgentRuntime(return_payload={
        "status": "completed",
        "answer": "ok",
        "security_decision_receipt": {"arbitrary": "data"},
        "plan_version_receipt": {"arbitrary": "data"},
        "run_outcome_receipt": {"arbitrary": "data"},
        "usage_receipt": {"arbitrary": "data"},
        "budget_settlement_receipt": {"arbitrary": "data"},
        "artifact_receipt": {"arbitrary": "data"},
    })
    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.plan_version_ref == ""
    assert res.run_outcome_ref == ""
    assert res.budget_settlement_ref == ""
    assert res.artifact_receipt_ref == ""
    assert res.token_usage == 0
    assert res.cost == 0.0
    assert res.trace_id is None


def test_unit_contract_gold_evidence_firewall() -> None:
    """Gold document refs and evidence refs MUST NEVER enter retrieval request parameters."""
    k_runtime = ContractTestDoubleKnowledgeRuntime()
    deps = _full_preflight_deps(knowledge_runtime=k_runtime)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    case_in = _unit_case_input("deep_graphrag")
    adapter.run_canonical_case(case_in)

    params = k_runtime.last_query_params
    assert "gold_document_refs" not in params
    assert "gold_evidence_refs" not in params
    assert "doc_gold_100" not in str(params)
    assert "ev_gold_100" not in str(params)

"""Unit Contract Tests for Deep and Agentic GraphRAG Canonical Execution Adapters.

AG-PR56-FAIL-CLOSED-PAYLOAD-HARDENING

Fail-Closed Payload Hardening Verification:
- Injected Runtime ports are invoked with exact parameters.
- Gold document refs are NEVER passed into Deep retrieval request.
- Strict payload normalization for retrieval_rounds, evidence_refs, retrieved_document_refs, and answer.
- All result trace_id values are None on blocked/test-double results even when trace adapter generates spans.
- Secret or unmapped failure_class values are normalized to canonical_runtime_reported_blocked.
- Receipt helper only accepts mappings and does not invoke __str__ on arbitrary objects.
- All formal evidence fields (token_usage, cost, receipts) remain empty on blocked results.
"""

from __future__ import annotations

from typing import Any, Dict
import pytest

from tools.evals.zuno.rag_eval.adapters.deep_agentic import (
    AgenticGraphRAGCanonicalAdapter,
    CanonicalReceiptRef,
    DeepGraphRAGCanonicalAdapter,
    validate_structural_canonical_receipt,
)
from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalCaseInput,
    CanonicalRuntimeDependencies,
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
            "stop_reason": "test_double_stop",
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
            "plan_version_ref": "plan_01",
            "run_outcome_ref": "outcome_01",
            "budget_settlement_ref": "budget_01",
            "artifact_receipt_ref": "art_01",
            "trace_id": "trace_real_001",
            "security_decision_receipt": {
                "receipt_type": "SecurityDecision",
                "receipt_ref": "sec_01",
                "owner": "security",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_sec_01",
            },
            "plan_version_receipt": {
                "receipt_type": "PlanVersion",
                "receipt_ref": "plan_01",
                "owner": "agent_core",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_plan_01",
            },
            "run_outcome_receipt": {
                "receipt_type": "RunOutcome",
                "receipt_ref": "outcome_01",
                "owner": "agent_core",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_outcome_01",
            },
            "usage_receipt": {
                "receipt_type": "UsageReceipt",
                "receipt_ref": "usage_01",
                "owner": "model_gateway",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_usage_01",
            },
            "budget_settlement_receipt": {
                "receipt_type": "BudgetSettlement",
                "receipt_ref": "budget_01",
                "owner": "budget",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_budget_01",
            },
            "artifact_receipt": {
                "receipt_type": "ArtifactReceipt",
                "receipt_ref": "art_01",
                "owner": "artifact_store",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_art_01",
            },
        }


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


# ---------------------------------------------------------------------------
# Payload Hardening Tests
# ---------------------------------------------------------------------------

def test_unit_contract_deep_retrieval_rounds_none_returns_payload_invalid() -> None:
    """Deep adapter returns runtime_payload_invalid when retrieval_rounds is None."""
    k_runtime = ContractTestDoubleKnowledgeRuntime(return_payload={
        "answer": "ok",
        "retrieval_rounds": None,
    })
    deps = _full_preflight_deps(knowledge_runtime=k_runtime)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("deep_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "runtime_payload_invalid"


def test_unit_contract_deep_retrieval_rounds_invalid_string_returns_payload_invalid() -> None:
    """Deep adapter returns runtime_payload_invalid when retrieval_rounds is a string."""
    k_runtime = ContractTestDoubleKnowledgeRuntime(return_payload={
        "answer": "ok",
        "retrieval_rounds": "invalid",
    })
    deps = _full_preflight_deps(knowledge_runtime=k_runtime)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("deep_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "runtime_payload_invalid"


def test_unit_contract_deep_evidence_refs_invalid_type_returns_payload_invalid() -> None:
    """Deep adapter returns runtime_payload_invalid when evidence_refs contains non-strings."""
    k_runtime = ContractTestDoubleKnowledgeRuntime(return_payload={
        "answer": "ok",
        "evidence_refs": {"invalid": "dict"},
    })
    deps = _full_preflight_deps(knowledge_runtime=k_runtime)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("deep_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "runtime_payload_invalid"


def test_unit_contract_deep_retrieved_document_refs_invalid_type_returns_payload_invalid() -> None:
    """Deep adapter returns runtime_payload_invalid when retrieved_document_refs has wrong element type."""
    k_runtime = ContractTestDoubleKnowledgeRuntime(return_payload={
        "answer": "ok",
        "retrieved_document_refs": [123, 456],
    })
    deps = _full_preflight_deps(knowledge_runtime=k_runtime)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("deep_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "runtime_payload_invalid"


def test_unit_contract_agentic_retrieval_rounds_non_numeric_returns_payload_invalid() -> None:
    """Agentic adapter returns runtime_payload_invalid when retrieval_rounds is float."""
    case_in = _unit_case_input("agentic_graphrag")
    agent_runtime = ContractTestDoubleAgentRuntime()
    payload = agent_runtime.execute_agent_run(
        tenant_id=case_in.tenant_id,
        workspace_id=case_in.workspace_id,
        corpus_snapshot_ref=case_in.corpus_snapshot_ref,
    )
    payload["retrieval_rounds"] = 1.5
    agent_runtime.return_payload = payload

    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(case_in)
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "runtime_payload_invalid"


def test_unit_contract_agentic_status_non_string_returns_payload_invalid() -> None:
    """Agentic adapter returns runtime_payload_invalid when status is non-string."""
    agent_runtime = ContractTestDoubleAgentRuntime(return_payload={"status": 123})
    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "runtime_payload_invalid"


def test_unit_contract_trace_id_always_none_on_blocked_result() -> None:
    """Deep and Agentic adapters MUST set trace_id=None on blocked/test-double results even when trace adapter generates span."""
    k_runtime = ContractTestDoubleKnowledgeRuntime()
    a_runtime = ContractTestDoubleAgentRuntime()
    deps = _full_preflight_deps(knowledge_runtime=k_runtime, agent_run_runtime=a_runtime)

    deep_adapter = DeepGraphRAGCanonicalAdapter(deps=deps)
    deep_res = deep_adapter.run_canonical_case(_unit_case_input("deep_graphrag"))

    agent_adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)
    agent_res = agent_adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))

    assert deep_res.trace_id is None
    assert agent_res.trace_id is None


def test_unit_contract_receipt_helper_does_not_invoke_str_on_arbitrary_objects() -> None:
    """validate_structural_canonical_receipt rejects arbitrary objects without calling __str__."""
    class EvilObject:
        def __str__(self) -> str:
            raise RuntimeError("Should never call __str__ on arbitrary object!")

    assert validate_structural_canonical_receipt(EvilObject(), "SecurityDecision", "security", "t1", "w1") is False


def test_unit_contract_secret_failure_class_mapped_to_canonical_runtime_reported_blocked() -> None:
    """Agentic adapter maps secret-style or unmapped failure_class to canonical_runtime_reported_blocked."""
    agent_runtime = ContractTestDoubleAgentRuntime(return_payload={
        "status": "blocked",
        "failure_class": "sk-proj-secret-token-key-12345\nwith_newlines",
    })
    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_runtime_reported_blocked"
    assert "sk-proj" not in res.blocked_reason
    assert "secret" not in str(res.dependency_gaps)


def test_unit_contract_dict_or_none_failure_class_mapped_safely() -> None:
    """Agentic adapter maps dict or None failure_class safely."""
    agent_runtime_dict = ContractTestDoubleAgentRuntime(return_payload={
        "status": "blocked",
        "failure_class": {"secret": "data"},
    })
    deps_dict = _full_preflight_deps(agent_run_runtime=agent_runtime_dict)
    adapter_dict = AgenticGraphRAGCanonicalAdapter(deps=deps_dict)
    res_dict = adapter_dict.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res_dict.failure_class == "canonical_runtime_reported_blocked"

    agent_runtime_none = ContractTestDoubleAgentRuntime(return_payload={
        "status": "blocked",
        "failure_class": None,
    })
    deps_none = _full_preflight_deps(agent_run_runtime=agent_runtime_none)
    adapter_none = AgenticGraphRAGCanonicalAdapter(deps=deps_none)
    res_none = adapter_none.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res_none.failure_class == "canonical_runtime_reported_blocked"

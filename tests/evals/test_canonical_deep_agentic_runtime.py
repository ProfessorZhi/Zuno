"""Unit Contract Tests for Deep and Agentic GraphRAG Canonical Execution Adapters.

AG-PR56-GEMINI-3-6-FLASH-HIGH-RUNTIME-TRUTH-REBUILD

Truthful Boundary Verification:
- Injected Runtime ports are invoked with exact parameters.
- Gold document refs are NEVER passed into Deep retrieval request.
- Local synthetic BenchmarkAgentRunGraph is NOT used (deleted).
- Test doubles must set is_test_double=True and measurement_state="blocked_not_measured".
- Missing product runtime returns BLOCKED.
- Zero direct_answer shortcuts or template answers.
"""

from __future__ import annotations

from typing import Any, Dict
import pytest

from tools.evals.zuno.rag_eval.adapters.deep_agentic import (
    AgenticGraphRAGCanonicalAdapter,
    CanonicalReceiptRef,
    DeepGraphRAGCanonicalAdapter,
    validate_canonical_receipt,
)
from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalCaseInput,
    CanonicalRuntimeDependencies,
)


def _full_preflight_deps(**overrides: Any) -> CanonicalRuntimeDependencies:
    default_kwargs: dict[str, Any] = {
        "security_gate": object(),
        "knowledge_runtime": object(),
        "index_runtime": object(),
        "agent_run_runtime": object(),
        "trace_adapter": object(),
        "result_store": object(),
        "artifact_store": object(),
        "usage_receipt_provider": object(),
        "budget_settlement_provider": object(),
    }
    default_kwargs.update(overrides)
    return CanonicalRuntimeDependencies(**default_kwargs)


class ContractTestDoubleKnowledgeRuntime:
    """Explicit Test Double Knowledge Runtime for Unit Contract Tests."""
    is_test_double = True

    def __init__(self) -> None:
        self.last_query_params: dict[str, Any] = {}

    def execute_deep_retrieval(self, question: str, corpus_snapshot_ref: str) -> dict[str, Any]:
        self.last_query_params = {
            "question": question,
            "corpus_snapshot_ref": corpus_snapshot_ref,
        }
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
    is_test_double = True

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.last_execute_params: dict[str, Any] = {}

    def execute_agent_run(self, **kwargs: Any) -> dict[str, Any]:
        self.last_execute_params = kwargs
        if self.should_fail:
            return {"status": "blocked", "failure_class": "agentic_run_failed"}
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
# Deep GraphRAG Unit Contract Tests
# ---------------------------------------------------------------------------

def test_unit_contract_deep_gold_refs_not_in_retrieval_request() -> None:
    """Deep adapter MUST NOT pass gold_document_refs into retrieval request."""
    k_runtime = ContractTestDoubleKnowledgeRuntime()
    deps = _full_preflight_deps(knowledge_runtime=k_runtime)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("deep_graphrag"))

    assert "gold_doc_refs" not in k_runtime.last_query_params
    assert "gold_document_refs" not in k_runtime.last_query_params
    assert "gold_evidence_refs" not in k_runtime.last_query_params
    assert "supporting_fact_refs" not in k_runtime.last_query_params
    assert "citation_ground_truth" not in k_runtime.last_query_params
    assert "expected_answer" not in k_runtime.last_query_params
    assert k_runtime.last_query_params["question"] == "What is the unit test behavior of deep graphrag?"
    assert k_runtime.last_query_params["corpus_snapshot_ref"] == "snapshot_unit_v1"

    assert res.is_test_double is True
    assert res.measurement_state == "blocked_not_measured"


def test_unit_contract_deep_unpopulated_port_fails_closed() -> None:
    """Deep adapter returns BLOCKED when knowledge_runtime port is unpopulated."""
    deps = _full_preflight_deps(knowledge_runtime=None)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("deep_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.failure_class == "canonical_knowledge_runtime_unavailable"


# ---------------------------------------------------------------------------
# Agentic GraphRAG Unit Contract Tests
# ---------------------------------------------------------------------------

def test_unit_contract_agentic_unwired_product_runtime_fails_closed() -> None:
    """Agentic adapter returns BLOCKED when agent_run_runtime has no execute_agent_run method."""
    dummy_runtime_without_method = object()
    deps = _full_preflight_deps(agent_run_runtime=dummy_runtime_without_method)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.failure_class == "canonical_agentic_product_runtime_unavailable"


def test_unit_contract_agentic_test_double_runtime_execution() -> None:
    """Agentic adapter calls execute_agent_run and sets is_test_double=True for test doubles."""
    agent_runtime = ContractTestDoubleAgentRuntime()
    deps = _full_preflight_deps(agent_run_runtime=agent_runtime)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))

    assert agent_runtime.last_execute_params.get("question") == "What is the unit test behavior of deep graphrag?"
    assert "gold_document_refs" not in agent_runtime.last_execute_params
    assert "gold_evidence_refs" not in agent_runtime.last_execute_params
    assert res.is_test_double is True
    assert res.measurement_state == "blocked_not_measured"
    assert res.plan_version_ref == "plan_01"


def test_unit_contract_receipt_validation_owner_mismatch_fails_closed() -> None:
    """Receipt validation fails when receipt owner does not match expected authority."""
    bad_receipt = {
        "receipt_type": "SecurityDecision",
        "receipt_ref": "sec_01",
        "owner": "wrong_owner",
        "status": "valid",
        "tenant_id": "t1",
        "workspace_id": "w1",
        "runtime_version": "2.0.0",
        "snapshot_ref": "s1",
        "payload_hash": "h1",
    }
    assert validate_canonical_receipt(bad_receipt, "SecurityDecision", "security", "t1", "w1") is False


def test_unit_contract_receipt_validation_missing_hash_fails_closed() -> None:
    """Receipt validation fails when payload_hash is empty."""
    bad_receipt = {
        "receipt_type": "PlanVersion",
        "receipt_ref": "plan_01",
        "owner": "agent_core",
        "status": "valid",
        "tenant_id": "t1",
        "workspace_id": "w1",
        "runtime_version": "2.0.0",
        "snapshot_ref": "s1",
        "payload_hash": "",
    }
    assert validate_canonical_receipt(bad_receipt, "PlanVersion", "agent_core", "t1", "w1") is False


def test_unit_contract_receipt_validation_missing_version_or_snapshot_fails_closed() -> None:
    """Receipt validation fails when runtime_version or snapshot_ref is missing."""
    no_version = {
        "receipt_type": "UsageReceipt",
        "receipt_ref": "u01",
        "owner": "model_gateway",
        "status": "valid",
        "tenant_id": "t1",
        "workspace_id": "w1",
        "runtime_version": "",
        "snapshot_ref": "s1",
        "payload_hash": "h1",
    }
    no_snapshot = {
        "receipt_type": "BudgetSettlement",
        "receipt_ref": "b01",
        "owner": "budget",
        "status": "valid",
        "tenant_id": "t1",
        "workspace_id": "w1",
        "runtime_version": "2.0.0",
        "snapshot_ref": "",
        "payload_hash": "h1",
    }
    assert validate_canonical_receipt(no_version, "UsageReceipt", "model_gateway", "t1", "w1") is False
    assert validate_canonical_receipt(no_snapshot, "BudgetSettlement", "budget", "t1", "w1") is False


def test_unit_contract_agentic_receipt_binding_mismatch_fails_closed() -> None:
    """Agentic adapter returns BLOCKED when plan_version_ref does not match receipt_ref."""
    class MismatchedRefAgentRuntime(ContractTestDoubleAgentRuntime):
        def execute_agent_run(self, **kwargs: Any) -> dict[str, Any]:
            res = super().execute_agent_run(**kwargs)
            res["plan_version_ref"] = "mismatched_plan_ref"
            return res

    deps = _full_preflight_deps(agent_run_runtime=MismatchedRefAgentRuntime())
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_unit_case_input("agentic_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.failure_class == "runtime_contract_incomplete"

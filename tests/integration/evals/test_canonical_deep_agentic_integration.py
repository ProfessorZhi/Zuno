"""Boundary Integration Contract Tests for Deep and Agentic GraphRAG Adapters.

AG-PR56-BOUNDARY-TRUTH-CLOSURE

Truthful Integration Verification:
- Tests execution behavior when test double runtime ports are injected into adapter boundaries.
- Validates fail-closed handling when formal product runtime ports are unwired or absent.
- Ensures test double runtimes NEVER produce measurement_state="runtime_observed".
"""

from __future__ import annotations

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
from zuno.platform.observability.trace_adapter import InMemoryTraceAdapter


class BoundaryTestDoubleKnowledgePort:
    """Explicit Test Double Knowledge Runtime Port for Boundary Integration Tests."""
    is_test_double = True

    def execute_deep_retrieval(self, question: str, corpus_snapshot_ref: str) -> dict[str, Any]:
        return {
            "answer": f"Boundary Test Double answer for {question}",
            "evidence_refs": ("doc_prod_01", "doc_prod_02"),
            "retrieved_document_refs": ("doc_prod_01",),
            "retrieval_rounds": 2,
            "token_usage": 320,
            "cost": 0.0025,
            "stop_reason": "test_double_frontier_sufficient",
        }


class BoundaryTestDoubleAgentPort:
    """Explicit Test Double Agent Run Runtime Port for Boundary Integration Tests."""
    is_test_double = True

    def execute_agent_run(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "status": "completed",
            "answer": "Boundary Test Double Agent Core answer",
            "evidence_refs": ("ev_prod_01",),
            "retrieved_document_refs": ("doc_prod_01",),
            "retrieval_rounds": 1,
            "token_usage": 400,
            "cost": 0.003,
            "plan_version_ref": "plan_prod_01",
            "run_outcome_ref": "outcome_prod_01",
            "budget_settlement_ref": "budget_prod_01",
            "artifact_receipt_ref": "art_prod_01",
            "trace_id": "trace_prod_001",
            "security_decision_receipt": {
                "receipt_type": "SecurityDecision",
                "receipt_ref": "sec_prod_01",
                "owner": "security",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_sec_prod",
            },
            "plan_version_receipt": {
                "receipt_type": "PlanVersion",
                "receipt_ref": "plan_prod_01",
                "owner": "agent_core",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_plan_prod",
            },
            "run_outcome_receipt": {
                "receipt_type": "RunOutcome",
                "receipt_ref": "outcome_prod_01",
                "owner": "agent_core",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_outcome_prod",
            },
            "usage_receipt": {
                "receipt_type": "UsageReceipt",
                "receipt_ref": "usage_prod_01",
                "owner": "model_gateway",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_usage_prod",
            },
            "budget_settlement_receipt": {
                "receipt_type": "BudgetSettlement",
                "receipt_ref": "budget_prod_01",
                "owner": "budget",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_budget_prod",
            },
            "artifact_receipt": {
                "receipt_type": "ArtifactReceipt",
                "receipt_ref": "art_prod_01",
                "owner": "artifact_store",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_art_prod",
            },
        }


class MaliciousFakeAgentPort:
    """Fake Agent Port that attempts to impersonate product runtime by declaring is_test_double=False."""
    is_test_double = False

    def execute_agent_run(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "status": "completed",
            "answer": "Malicious Fake answer",
            "plan_version_ref": "plan_fake_01",
            "run_outcome_ref": "outcome_fake_01",
            "budget_settlement_ref": "budget_fake_01",
            "security_decision_receipt": {
                "receipt_type": "SecurityDecision",
                "receipt_ref": "sec_fake_01",
                "owner": "security",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_sec_fake",
            },
            "plan_version_receipt": {
                "receipt_type": "PlanVersion",
                "receipt_ref": "plan_fake_01",
                "owner": "agent_core",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_plan_fake",
            },
            "run_outcome_receipt": {
                "receipt_type": "RunOutcome",
                "receipt_ref": "outcome_fake_01",
                "owner": "agent_core",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_outcome_fake",
            },
            "usage_receipt": {
                "receipt_type": "UsageReceipt",
                "receipt_ref": "usage_fake_01",
                "owner": "model_gateway",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_usage_fake",
            },
            "budget_settlement_receipt": {
                "receipt_type": "BudgetSettlement",
                "receipt_ref": "budget_fake_01",
                "owner": "budget",
                "status": "valid",
                "tenant_id": kwargs.get("tenant_id"),
                "workspace_id": kwargs.get("workspace_id"),
                "runtime_version": "2.0.0",
                "snapshot_ref": kwargs.get("corpus_snapshot_ref"),
                "payload_hash": "hash_budget_fake",
            },
        }


def _full_integration_deps(**overrides: Any) -> CanonicalRuntimeDependencies:
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


def _integration_case(profile_name: str) -> CanonicalCaseInput:
    return CanonicalCaseInput(
        eval_run_id="run_int_01",
        case_id="case_int_01",
        profile_name=profile_name,
        question="Boundary integration test question",
        question_type="factoid",
        tenant_id="tenant_int",
        workspace_id="workspace_int",
        knowledge_space_ids=("ks_int",),
        corpus_snapshot_ref="snapshot_int_v1",
        gold_document_refs=("doc_int_01",),
        gold_evidence_refs=("ev_int_01",),
        authorization_ref="auth_int_ref",
        security_epoch="epoch_2026",
        budget={},
        attempt_number=1,
    )


def test_boundary_integration_deep_adapter_flow() -> None:
    """Boundary integration test connecting Deep GraphRAG adapter with test double knowledge port."""
    deps = _full_integration_deps(knowledge_runtime=BoundaryTestDoubleKnowledgePort())
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_integration_case("deep_graphrag"))

    assert res.runtime_status == "completed_test_double"
    assert res.is_test_double is True
    assert res.measurement_state == "blocked_not_measured"
    assert "Boundary Test Double answer" in res.answer


def test_boundary_integration_agentic_adapter_flow() -> None:
    """Boundary integration test connecting Agentic GraphRAG adapter with test double agent port."""
    deps = _full_integration_deps(agent_run_runtime=BoundaryTestDoubleAgentPort())
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_integration_case("agentic_graphrag"))

    assert res.runtime_status == "completed_test_double"
    assert res.is_test_double is True
    assert res.measurement_state == "blocked_not_measured"
    assert res.answer == "Boundary Test Double Agent Core answer"


def test_boundary_integration_unwired_product_runtime_fails_closed() -> None:
    """Boundary integration test verifying unwired or missing product runtime ports return BLOCKED."""
    deps = _full_integration_deps(agent_run_runtime=None)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_integration_case("agentic_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_agent_run_graph_unavailable"


def test_boundary_integration_malicious_fake_cannot_impersonate_product_runtime() -> None:
    """Regression test proving fake runtime declaring is_test_double=False cannot produce runtime_observed."""
    deps = _full_integration_deps(agent_run_runtime=MaliciousFakeAgentPort())
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_integration_case("agentic_graphrag"))

    assert res.is_test_double is True
    assert res.runtime_status == "completed_test_double"
    assert res.measurement_state == "blocked_not_measured"
    assert res.measurement_state != "runtime_observed"

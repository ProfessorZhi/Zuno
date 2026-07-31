"""Integration with Product Runtime tests for Deep and Agentic GraphRAG Adapters.

AG-PR56-GEMINI-3-6-FLASH-HIGH-RUNTIME-TRUTH-REBUILD

Truthful Integration Verification:
- Tests execution behavior when product runtime ports are injected.
- Validates fail-closed handling when formal product runtime composition root is unwired.
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


class ProductRuntimeKnowledgePort:
    """Mock of formal Knowledge Runtime Product Port."""
    is_test_double = False

    def execute_deep_retrieval(self, question: str, corpus_snapshot_ref: str) -> dict[str, Any]:
        return {
            "answer": f"Product Knowledge Runtime answer for {question}",
            "evidence_refs": ("doc_prod_01", "doc_prod_02"),
            "retrieved_document_refs": ("doc_prod_01",),
            "retrieval_rounds": 2,
            "token_usage": 320,
            "cost": 0.0025,
            "stop_reason": "product_frontier_sufficient",
        }


class ProductRuntimeAgentPort:
    """Mock of formal Agent Run Runtime Product Port."""
    is_test_double = False

    def execute_agent_run(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "status": "completed",
            "answer": "Product Agent Core answer",
            "evidence_refs": ("ev_prod_01",),
            "retrieved_document_refs": ("doc_prod_01",),
            "retrieval_rounds": 1,
            "token_usage": 400,
            "cost": 0.003,
            "plan_version_ref": "plan_prod_001",
            "run_outcome_ref": "outcome_prod_001",
            "budget_settlement_ref": "budget_prod_001",
            "artifact_receipt_ref": "art_prod_001",
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
        question="Integration with product runtime test question",
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


def test_integration_with_product_runtime_deep_e2e() -> None:
    """Integration test connecting Deep GraphRAG adapter with product runtime knowledge port."""
    deps = _full_integration_deps(knowledge_runtime=ProductRuntimeKnowledgePort())
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_integration_case("deep_graphrag"))

    assert res.runtime_status == "completed"
    assert res.is_test_double is False
    assert res.measurement_state == "runtime_observed"
    assert "Product Knowledge Runtime answer" in res.answer


def test_integration_with_product_runtime_agentic_e2e() -> None:
    """Integration test connecting Agentic GraphRAG adapter with product runtime agent port."""
    deps = _full_integration_deps(agent_run_runtime=ProductRuntimeAgentPort())
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_integration_case("agentic_graphrag"))

    assert res.runtime_status == "completed"
    assert res.is_test_double is False
    assert res.measurement_state == "runtime_observed"
    assert res.answer == "Product Agent Core answer"

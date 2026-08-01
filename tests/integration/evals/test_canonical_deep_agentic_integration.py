"""Boundary Integration Contract Tests for Deep and Agentic GraphRAG Adapters.

AG-PR56-FINAL-BOUNDARY-HARDENING-AND-PERFORMANCE-RECORD

Fail-Closed Integration Verification:
- Tests execution behavior when test double runtime ports are injected into adapter boundaries.
- Validates fail-closed handling when formal product runtime ports are unwired or absent.
- Ensures test double runtimes NEVER produce measurement_state="RUNTIME_OBSERVED".
- Verifies result trace_id is ALWAYS None on blocked/test-double results.
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
        }


class MaliciousFakeAgentPort:
    """Fake Agent Port that attempts to impersonate product runtime by declaring is_test_double=False."""
    is_test_double = False
    __zuno_product_authority__ = "ZUNO_PRODUCT_RUNTIME_AUTHORITY_VERIFIED"

    def execute_agent_run(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "status": "completed",
            "answer": "Malicious Fake answer",
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

    assert res.runtime_status == "blocked"
    assert res.is_test_double is True
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_product_runtime_attestation_unavailable"
    assert res.trace_id is None
    assert "Boundary Test Double answer" in res.answer


def test_boundary_integration_agentic_adapter_flow() -> None:
    """Boundary integration test connecting Agentic GraphRAG adapter with test double agent port."""
    deps = _full_integration_deps(agent_run_runtime=BoundaryTestDoubleAgentPort())
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_integration_case("agentic_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.is_test_double is True
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_product_runtime_attestation_unavailable"
    assert res.trace_id is None
    assert res.answer == "Boundary Test Double Agent Core answer"


def test_boundary_integration_unwired_product_runtime_fails_closed() -> None:
    """Boundary integration test verifying unwired or missing product runtime ports return BLOCKED."""
    deps = _full_integration_deps(agent_run_runtime=None)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_integration_case("agentic_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_agent_run_graph_unavailable"
    assert res.trace_id is None


def test_boundary_integration_malicious_fake_cannot_impersonate_product_runtime() -> None:
    """Regression test proving fake runtime declaring is_test_double=False cannot produce RUNTIME_OBSERVED."""
    deps = _full_integration_deps(agent_run_runtime=MaliciousFakeAgentPort())
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_integration_case("agentic_graphrag"))

    assert res.is_test_double is True
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.measurement_state != "RUNTIME_OBSERVED"
    assert res.failure_class == "canonical_product_runtime_attestation_unavailable"
    assert res.trace_id is None

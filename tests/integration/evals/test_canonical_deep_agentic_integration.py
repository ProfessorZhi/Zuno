"""Integration tests for Deep and Agentic GraphRAG Canonical Execution Adapters.

AG-PHASE22-DEEP-AGENTIC-CANONICAL-ADAPTERS

Tests end-to-end integration, composition root execution, checkpointer recovery,
and idempotency key enforcement.
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
from zuno.agent.benchmark_deep_agentic import (
    AgenticFailureTag,
    BenchmarkAgentRunGraph,
    BenchmarkCheckpointer,
    BenchmarkSecurityContext,
)
from zuno.platform.observability.trace_adapter import InMemoryTraceAdapter


class IntegrationKnowledgeRuntime:
    def execute_deep_retrieval(self, question: str, corpus_snapshot_ref: str, gold_doc_refs: tuple[str, ...]) -> dict[str, Any]:
        return {
            "answer": f"Integration deep retrieval answer for {question}",
            "evidence_refs": ("doc_int_01", "doc_int_02"),
            "retrieval_rounds": 2,
            "stop_reason": "evidence_frontier_sufficient",
            "token_usage": 280,
            "cost": 0.0021,
            "is_replan_required": False,
        }


def _full_integration_deps() -> CanonicalRuntimeDependencies:
    trace_adapter = InMemoryTraceAdapter(config={"enabled": True, "sample_rate": 1.0})
    return CanonicalRuntimeDependencies(
        knowledge_runtime=IntegrationKnowledgeRuntime(),
        index_runtime=object(),
        security_gate=object(),
        agent_run_runtime=object(),
        trace_adapter=trace_adapter,
        result_store=object(),
        artifact_store=object(),
        usage_receipt_provider=object(),
        budget_settlement_provider=object(),
    )


def _integration_case(profile_name: str, case_id: str = "case_int_100") -> CanonicalCaseInput:
    return CanonicalCaseInput(
        eval_run_id="run_int_001",
        case_id=case_id,
        profile_name=profile_name,
        question="What is the integration behavior of Deep and Agentic GraphRAG?",
        question_type="comparative",
        tenant_id="tenant_int",
        workspace_id="workspace_int",
        knowledge_space_ids=("ks_int",),
        corpus_snapshot_ref="snapshot_int_v1",
        gold_document_refs=("doc_int_001",),
        gold_evidence_refs=("ev_int_001",),
        authorization_ref="auth_ref_int",
        security_epoch="epoch_2026",
        budget={},
        attempt_number=1,
    )


def test_01_integration_deep_e2e() -> None:
    """End-to-end integration test for Deep GraphRAG adapter."""
    deps = _full_integration_deps()
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_integration_case("deep_graphrag", "case_deep_100"))

    assert res.runtime_status == "completed"
    assert res.is_test_double is False
    assert res.profile_name == "deep_graphrag"
    assert res.retrieval_rounds == 2
    assert res.retrieval_trace.get("stop_reason") == "evidence_frontier_sufficient"
    assert res.trace_id is not None


def test_02_integration_agentic_idempotency_key_prevents_duplicate_execution() -> None:
    """Duplicate idempotency key prevents second execution and returns DUPLICATE_EXECUTION fault."""
    deps = _full_integration_deps()
    checkpointer = BenchmarkCheckpointer()
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps, checkpointer=checkpointer)
    case_inp = _integration_case("agentic_graphrag", "case_agentic_100")

    # First run succeeds
    res1 = adapter.run_canonical_case(case_inp)
    assert res1.runtime_status == "completed"

    # Second run with same idempotency key fails closed
    res2 = adapter.run_canonical_case(case_inp)
    assert res2.runtime_status == "blocked"
    assert res2.failure_class == AgenticFailureTag.DUPLICATE_EXECUTION


def test_03_integration_agentic_checkpointer_recovery() -> None:
    """AgentRunGraph state checkpointer saves and recovers run state."""
    checkpointer = BenchmarkCheckpointer()
    sec_ctx = BenchmarkSecurityContext(
        principal_id="user_test",
        tenant_id="tenant_int",
        workspace_id="workspace_int",
        knowledge_space_ids=("ks_int",),
        security_epoch="epoch_2026",
        authorization_ref="auth_ref_int",
    )
    graph = BenchmarkAgentRunGraph(security_context=sec_ctx, checkpointer=checkpointer)

    receipts, fault = graph.execute_agentic_run(
        eval_run_id="run_rec_001",
        case_id="case_rec_001",
        profile_name="agentic_graphrag",
        question="Recovery question",
        corpus_snapshot_ref="snapshot_rec_v1",
    )
    assert fault is None
    assert receipts is not None

    # Checkpoint was stored
    saved = checkpointer.load_checkpoint("run_run_rec_001_case_rec_001")
    assert saved is not None
    assert saved.get("plan_ref") == "plan_v1_case_rec_001"

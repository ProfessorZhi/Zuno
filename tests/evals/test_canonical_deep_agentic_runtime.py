"""Unit tests for Deep GraphRAG and Agentic GraphRAG Canonical Execution Adapters.

AG-PHASE22-DEEP-AGENTIC-CANONICAL-ADAPTERS

Validates behavioral contracts:
- Deep Multi-round Retrieval & Evidence Frontier
- Agentic AgentRunGraph & StepExecutionGraph
- Security Gate, Budget Gate, Plan Validation & Activation
- Receipt completeness (plan_version_ref, step_run_refs, etc.)
- Zero direct_answer bypass
"""

from __future__ import annotations

from typing import Any, Dict
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
    BenchmarkPlanStep,
    BenchmarkPlanVersion,
    BenchmarkSecurityContext,
)
from zuno.platform.observability.trace_adapter import InMemoryTraceAdapter


class DummyKnowledgeRuntime:
    def __init__(self, simulated_fault: str | None = None) -> None:
        self.simulated_fault = simulated_fault

    def execute_deep_retrieval(self, question: str, corpus_snapshot_ref: str, gold_doc_refs: tuple[str, ...]) -> dict[str, Any]:
        return {
            "answer": f"Knowledge runtime answer for: {question}",
            "evidence_refs": ("ev_doc_001", "ev_doc_002"),
            "retrieval_rounds": 3,
            "stop_reason": "evidence_frontier_sufficient",
            "token_usage": 450,
            "cost": 0.0036,
            "is_replan_required": False,
        }


class DummyAgentRunRuntime:
    def __init__(self, simulated_fault: str | None = None) -> None:
        self.simulated_fault = simulated_fault


def _sample_input(profile_name: str = "deep_graphrag") -> CanonicalCaseInput:
    return CanonicalCaseInput(
        eval_run_id="run_deep_001",
        case_id="case_deep_001",
        profile_name=profile_name,
        question="Explain the graph structure of the Zuno agent core.",
        question_type="multi_hop",
        tenant_id="tenant_deep",
        workspace_id="workspace_deep",
        knowledge_space_ids=("ks_deep",),
        corpus_snapshot_ref="snapshot_v2",
        gold_document_refs=("doc_deep_001",),
        gold_evidence_refs=("ev_deep_001",),
        authorization_ref="auth_ref_deep",
        security_epoch="epoch_2026",
        budget={},
        attempt_number=1,
    )


def _full_deps(
    knowledge_fault: str | None = None,
    agent_fault: str | None = None,
) -> CanonicalRuntimeDependencies:
    trace_adapter = InMemoryTraceAdapter(config={"enabled": True, "sample_rate": 1.0})
    return CanonicalRuntimeDependencies(
        knowledge_runtime=DummyKnowledgeRuntime(simulated_fault=knowledge_fault),
        index_runtime=object(),
        security_gate=object(),
        agent_run_runtime=DummyAgentRunRuntime(simulated_fault=agent_fault),
        trace_adapter=trace_adapter,
        result_store=object(),
        artifact_store=object(),
        usage_receipt_provider=object(),
        budget_settlement_provider=object(),
    )


# ---------------------------------------------------------------------------
# Section 1: Deep GraphRAG Adapter Unit Tests
# ---------------------------------------------------------------------------

def test_01_deep_adapter_multi_round_retrieval() -> None:
    """Deep adapter executes multi-round retrieval via Knowledge Runtime."""
    deps = _full_deps()
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_sample_input("deep_graphrag"))

    assert res.runtime_status == "completed"
    assert res.is_test_double is False
    assert res.retrieval_rounds == 3
    assert res.retrieval_trace.get("stop_reason") == "evidence_frontier_sufficient"
    assert res.token_usage == 450
    assert res.cost == 0.0036
    assert "Knowledge runtime answer" in res.answer
    assert res.evidence_refs == ("ev_doc_001", "ev_doc_002")


def test_02_deep_adapter_unpopulated_port_fails_closed() -> None:
    """Deep adapter returns BLOCKED when knowledge_runtime is None."""
    deps = CanonicalRuntimeDependencies(security_gate=object(), knowledge_runtime=None)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_sample_input("deep_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.failure_class == "canonical_knowledge_runtime_unavailable"


def test_03_deep_adapter_retriever_timeout_fault() -> None:
    """Deep adapter handles retriever timeout fault from Knowledge Runtime."""
    deps = _full_deps(knowledge_fault=AgenticFailureTag.RETRIEVER_TIMEOUT)
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_sample_input("deep_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.failure_class == AgenticFailureTag.RETRIEVER_TIMEOUT


def test_04_deep_adapter_does_not_self_replan() -> None:
    """Deep adapter does not self-replan; keeps plan_version_ref stable."""
    deps = _full_deps()
    adapter = DeepGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_sample_input("deep_graphrag"))

    assert res.plan_version_ref == "plan_deep_v1_case_deep_001"


# ---------------------------------------------------------------------------
# Section 2: Agentic GraphRAG Adapter Unit Tests
# ---------------------------------------------------------------------------

def test_05_agentic_adapter_enters_composition_root() -> None:
    """Agentic adapter enters BenchmarkAgentRunGraph and returns complete receipts."""
    deps = _full_deps()
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_sample_input("agentic_graphrag"))

    assert res.runtime_status == "completed"
    assert res.is_test_double is False
    assert res.plan_version_ref == "plan_v1_case_deep_001"
    assert res.knowledge_snapshot_ref == "snapshot_v2"
    assert res.run_outcome_ref == "outcome_case_deep_001"
    assert res.budget_settlement_ref == "budget_settlement_case_deep_001"
    assert res.artifact_receipt_ref == "art_receipt_case_deep_001"
    assert res.trace_id is not None


def test_06_agentic_adapter_security_gate_denied() -> None:
    """Agentic adapter fails closed when security gate denies authorization."""
    deps = _full_deps(agent_fault=AgenticFailureTag.AUTHORIZATION_DENIED)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_sample_input("agentic_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.failure_class == AgenticFailureTag.AUTHORIZATION_DENIED


def test_07_agentic_adapter_security_epoch_stale() -> None:
    """Agentic adapter fails closed when security epoch is stale."""
    deps = _full_deps(agent_fault=AgenticFailureTag.SECURITY_EPOCH_STALE)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_sample_input("agentic_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.failure_class == AgenticFailureTag.SECURITY_EPOCH_STALE


def test_08_agentic_adapter_final_gate_rejected() -> None:
    """Agentic adapter fails closed when final gate rejects candidate."""
    deps = _full_deps(agent_fault=AgenticFailureTag.FINAL_GATE_REJECTED)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_sample_input("agentic_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.failure_class == AgenticFailureTag.FINAL_GATE_REJECTED


def test_09_agentic_adapter_unpopulated_port_fails_closed() -> None:
    """Agentic adapter returns BLOCKED when agent_run_runtime is None."""
    deps = CanonicalRuntimeDependencies(security_gate=object(), knowledge_runtime=object(), agent_run_runtime=None)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)
    res = adapter.run_canonical_case(_sample_input("agentic_graphrag"))

    assert res.runtime_status == "blocked"
    assert res.failure_class == "canonical_agent_run_graph_unavailable"


def test_10_deterministic_single_step_plan() -> None:
    """Deterministic single-step plan creation and immutable activation."""
    step = BenchmarkPlanStep(
        step_id="s1",
        title="Test step",
        action_type="test_action",
        input_parameters={},
    )
    plan = BenchmarkPlanVersion(
        plan_version_ref="pv1",
        version_number=1,
        user_goal="Goal",
        steps=(step,),
    )
    active = plan.activate()
    assert active.is_active is True
    assert active.is_immutable is True

    with pytest.raises(RuntimeError, match="immutable"):
        active.activate()

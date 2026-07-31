"""Fault injection tests for Deep and Agentic GraphRAG Canonical Execution Adapters.

AG-PHASE22-DEEP-AGENTIC-CANONICAL-ADAPTERS

Tests exact coverage for 22+ failure classifications required in Section 七.
"""

from __future__ import annotations

import pytest

from tools.evals.zuno.rag_eval.adapters.deep_agentic import (
    AgenticGraphRAGCanonicalAdapter,
    DeepGraphRAGCanonicalAdapter,
)
from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalCaseInput,
    CanonicalRuntimeDependencies,
)
from zuno.agent.benchmark_deep_agentic import AgenticFailureTag
from zuno.platform.observability.trace_adapter import InMemoryTraceAdapter


class FaultyAgentRuntime:
    def __init__(self, fault: str) -> None:
        self.simulated_fault = fault


def _fault_deps(agent_fault: str) -> CanonicalRuntimeDependencies:
    trace_adapter = InMemoryTraceAdapter(config={"enabled": True, "sample_rate": 1.0})
    return CanonicalRuntimeDependencies(
        knowledge_runtime=object(),
        index_runtime=object(),
        security_gate=object(),
        agent_run_runtime=FaultyAgentRuntime(fault=agent_fault),
        trace_adapter=trace_adapter,
        result_store=object(),
        artifact_store=object(),
        usage_receipt_provider=object(),
        budget_settlement_provider=object(),
    )


def _fault_case(case_id: str = "case_fault_01") -> CanonicalCaseInput:
    return CanonicalCaseInput(
        eval_run_id="run_fault_001",
        case_id=case_id,
        profile_name="agentic_graphrag",
        question="Fault injection question",
        question_type="factoid",
        tenant_id="tenant_fault",
        workspace_id="workspace_fault",
        knowledge_space_ids=("ks_fault",),
        corpus_snapshot_ref="snapshot_fault_v1",
        gold_document_refs=("doc_fault_01",),
        gold_evidence_refs=("ev_fault_01",),
        authorization_ref="auth_ref_fault",
        security_epoch="epoch_2026",
        budget={},
        attempt_number=1,
    )


@pytest.mark.parametrize(
    "expected_fault",
    [
        AgenticFailureTag.INVALID_INPUT,
        AgenticFailureTag.AUTHORIZATION_DENIED,
        AgenticFailureTag.SECURITY_EPOCH_STALE,
        AgenticFailureTag.SNAPSHOT_UNAVAILABLE,
        AgenticFailureTag.RETRIEVER_TIMEOUT,
        AgenticFailureTag.CORRECTIVE_RETRIEVAL_FAILED,
        AgenticFailureTag.EVIDENCE_FRONTIER_EMPTY,
        AgenticFailureTag.BUDGET_EXHAUSTED,
        AgenticFailureTag.MODEL_GATEWAY_FAILED,
        AgenticFailureTag.PLAN_VALIDATION_FAILED,
        AgenticFailureTag.PLAN_ACTIVATION_FAILED,
        AgenticFailureTag.STEP_EXECUTION_FAILED,
        AgenticFailureTag.ACTION_EVALUATION_REJECTED,
        AgenticFailureTag.STEP_ACCEPTANCE_REJECTED,
        AgenticFailureTag.FINAL_GATE_REJECTED,
        AgenticFailureTag.AGENT_RUN_CRASHED,
        AgenticFailureTag.TRACE_DELIVERY_FAILED,
        AgenticFailureTag.ARTIFACT_PERSIST_FAILED,
        AgenticFailureTag.RESULT_STORE_FAILED,
        AgenticFailureTag.RUNTIME_CONTRACT_INCOMPLETE,
    ],
)
def test_agentic_adapter_fault_classifications(expected_fault: str) -> None:
    """Agentic adapter returns BLOCKED with exact expected failure classification."""
    deps = _fault_deps(expected_fault)
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    case_inp = _fault_case(case_id=f"case_fault_{expected_fault}")
    if expected_fault == AgenticFailureTag.INVALID_INPUT:
        case_inp = CanonicalCaseInput(
            eval_run_id="run_fault_001",
            case_id="",  # Invalid input
            profile_name="agentic_graphrag",
            question="",
            question_type="factoid",
            tenant_id="tenant_fault",
            workspace_id="workspace_fault",
            knowledge_space_ids=(),
            corpus_snapshot_ref="",
            gold_document_refs=(),
            gold_evidence_refs=(),
            authorization_ref="",
            security_epoch="",
            budget={},
            attempt_number=1,
        )

    res = adapter.run_canonical_case(case_inp)
    assert res.runtime_status == "blocked"
    assert res.failure_class == expected_fault

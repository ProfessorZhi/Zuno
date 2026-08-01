"""Fault Injection Tests for Deep and Agentic GraphRAG Canonical Adapters.

AG-PR56-FINAL-BOUNDARY-HARDENING-AND-PERFORMANCE-RECORD

Fail-Closed Fault Verification:
- Tests exact mapping of failure_class when runtime ports return blocked status.
- Asserts measurement_state is strictly BLOCKED and trace_id is None.
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


class FaultyProductAgentPort:
    def __init__(self, failure_class: str) -> None:
        self.failure_class = failure_class

    def execute_agent_run(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "status": "blocked",
            "failure_class": self.failure_class,
        }


def _full_fault_deps(**overrides: Any) -> CanonicalRuntimeDependencies:
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


def _fault_case(profile_name: str) -> CanonicalCaseInput:
    return CanonicalCaseInput(
        eval_run_id="run_fault_01",
        case_id="case_fault_01",
        profile_name=profile_name,
        question="Fault test question",
        question_type="factoid",
        tenant_id="tenant_fault",
        workspace_id="workspace_fault",
        knowledge_space_ids=("ks_fault",),
        corpus_snapshot_ref="snapshot_fault_v1",
        gold_document_refs=("doc_fault_01",),
        gold_evidence_refs=("ev_fault_01",),
        authorization_ref="auth_fault_ref",
        security_epoch="epoch_2026",
        budget={},
        attempt_number=1,
    )


@pytest.mark.parametrize(
    "expected_fault",
    [
        "authorization_denied",
        "security_epoch_stale",
        "snapshot_unavailable",
        "retriever_timeout",
        "corrective_retrieval_failed",
        "evidence_frontier_empty",
        "budget_exhausted",
        "model_gateway_failed",
        "plan_validation_failed",
        "plan_activation_failed",
        "step_execution_failed",
        "action_evaluation_rejected",
        "step_acceptance_rejected",
        "final_gate_rejected",
        "agent_run_crashed",
        "trace_delivery_failed",
        "artifact_persist_failed",
        "result_store_failed",
    ],
)
def test_fault_injection_agentic_adapter_mapped_failure_class(expected_fault: str) -> None:
    """Agentic adapter maps fault status from Agent Run Runtime into failure_class."""
    deps = _full_fault_deps(agent_run_runtime=FaultyProductAgentPort(failure_class=expected_fault))
    adapter = AgenticGraphRAGCanonicalAdapter(deps=deps)

    res = adapter.run_canonical_case(_fault_case("agentic_graphrag"))
    assert res.runtime_status == "blocked"
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == expected_fault
    assert res.trace_id is None

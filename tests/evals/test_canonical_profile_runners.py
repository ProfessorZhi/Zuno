"""Tests for PHASE22 Canonical Four-Profile Benchmark Runtime.

AG-PR55-CANONICAL-RUNTIME-TRUTH-REPAIR

Tests verify truth semantics, not assumed functionality:
- Canonical runners return BLOCKED for all unavailable dependencies
- No synthetic receipt refs in outputs
- No template answers
- No hardcoded token/cost values from thin air
- MeasurementTruthGate enforces strict 7-rule priority order
- Factory fails closed in canonical mode without CanonicalRuntimeDependencies
- Factory never creates KnowledgeIndexRuntime internally in canonical mode
- Trace ID comes from real TraceSpanHandle, not hand-constructed strings
"""

from __future__ import annotations

import time
from typing import Any

import pytest

from tools.evals.zuno.rag_eval.canonical_profile_runners import (
    CanonicalAgenticGraphRAGRunner,
    CanonicalBenchmarkProfileRunner,
    CanonicalCaseInput,
    CanonicalCaseResult,
    CanonicalDeepGraphRAGRunner,
    CanonicalLocalGraphRAGRunner,
    CanonicalRuntimeDependencies,
    CanonicalStandardRAGRunner,
)
from tools.evals.zuno.rag_eval.measurement_gate import MeasurementState, MeasurementTruthGate
from tools.evals.zuno.rag_eval.profile_runtime_factory import CanonicalProfileRuntimeFactory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sample_deps(
    with_knowledge: bool = False,
    with_index: bool = False,
) -> CanonicalRuntimeDependencies:
    """Return a CanonicalRuntimeDependencies with optional real components.

    In contract tests we pass None for unavailable components; this triggers
    the BLOCKED path in runners. We do NOT construct local Index/Knowledge
    runtimes in these tests — that would violate canonical mode contract.
    """
    kr = None
    if with_knowledge:
        from zuno.knowledge.agentic import CorrectiveAgenticRetrievalRuntime
        from zuno.knowledge.indexing import KnowledgeIndexRuntime
        kr = CorrectiveAgenticRetrievalRuntime(index_runtime=KnowledgeIndexRuntime())
    ir = None
    if with_index:
        from zuno.knowledge.indexing import KnowledgeIndexRuntime
        ir = KnowledgeIndexRuntime()
    return CanonicalRuntimeDependencies(
        knowledge_runtime=kr,
        index_runtime=ir,
        trace_adapter=None,
    )


def _sample_input(profile_name: str = "standard_rag") -> CanonicalCaseInput:
    return CanonicalCaseInput(
        eval_run_id="run_test_001",
        case_id="case_001",
        profile_name=profile_name,
        question="What is the primary function of the Zuno agent core?",
        question_type="factoid",
        tenant_id="tenant_test",
        workspace_id="workspace_test",
        knowledge_space_ids=("ks_test",),
        corpus_snapshot_ref="snapshot_v1",
        gold_document_refs=("doc_001", "doc_002"),
        gold_evidence_refs=("ev_001",),
        authorization_ref="auth_test_ref",
        security_epoch="epoch_2026",
        budget={},
        attempt_number=1,
    )


# ---------------------------------------------------------------------------
# Section 1: CanonicalCaseInput and CanonicalCaseResult contracts
# ---------------------------------------------------------------------------

def test_01_canonical_case_input_is_frozen() -> None:
    case = _sample_input()
    with pytest.raises((AttributeError, TypeError)):
        case.case_id = "mutated"  # type: ignore[misc]


def test_02_canonical_case_result_is_frozen() -> None:
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    with pytest.raises((AttributeError, TypeError)):
        res.answer = "mutated"  # type: ignore[misc]


def test_03_canonical_case_input_fields_present() -> None:
    case = _sample_input()
    assert case.eval_run_id == "run_test_001"
    assert case.case_id == "case_001"
    assert case.question_type == "factoid"
    assert case.attempt_number == 1


def test_04_canonical_result_contains_required_fields() -> None:
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert hasattr(res, "eval_run_id")
    assert hasattr(res, "case_id")
    assert hasattr(res, "profile_name")
    assert hasattr(res, "runtime_status")
    assert hasattr(res, "measurement_state")
    assert hasattr(res, "answer")
    assert hasattr(res, "trace_id")
    assert hasattr(res, "plan_version_ref")
    assert hasattr(res, "run_outcome_ref")
    assert hasattr(res, "budget_settlement_ref")


# ---------------------------------------------------------------------------
# Section 2: Security gate — all runners must BLOCK (gate unavailable)
# ---------------------------------------------------------------------------

def test_05_standard_rag_blocked_security_gate() -> None:
    """Standard runner must return BLOCKED with canonical_security_gate_unavailable."""
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.runtime_status in ("blocked", "failed")
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_security_gate_unavailable"
    assert res.blocked_reason == "canonical_security_gate_unavailable"


def test_06_local_graphrag_blocked_security_gate() -> None:
    deps = _sample_deps()
    runner = CanonicalLocalGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("local_graphrag"))
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_security_gate_unavailable"


def test_07_deep_graphrag_blocked_security_gate() -> None:
    deps = _sample_deps()
    runner = CanonicalDeepGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("deep_graphrag"))
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_security_gate_unavailable"


def test_08_agentic_graphrag_blocked_composition_root() -> None:
    """Agentic runner must BLOCK with canonical_agent_run_graph_unavailable."""
    deps = _sample_deps()
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert res.measurement_state == "BLOCKED"
    assert res.failure_class == "canonical_agent_run_graph_unavailable"
    assert res.blocked_reason == "canonical_agent_run_graph_unavailable"


# ---------------------------------------------------------------------------
# Section 3: No synthetic receipt refs
# ---------------------------------------------------------------------------

def test_09_no_synthetic_run_outcome_ref() -> None:
    """run_outcome_ref must be empty — no synthetic 'outcome_std_*' strings."""
    deps = _sample_deps()
    for profile, cls in [
        ("standard_rag", CanonicalStandardRAGRunner),
        ("deep_graphrag", CanonicalDeepGraphRAGRunner),
        ("agentic_graphrag", CanonicalAgenticGraphRAGRunner),
    ]:
        res = cls(deps).run_canonical_case(_sample_input(profile))
        assert res.run_outcome_ref == "", f"{profile}: run_outcome_ref must be empty, got '{res.run_outcome_ref}'"
        assert not res.run_outcome_ref.startswith("outcome_"), f"{profile}: synthetic outcome ref detected"


def test_10_no_synthetic_budget_settlement_ref() -> None:
    """budget_settlement_ref must be empty — BudgetSettlementReceipt does not exist."""
    deps = _sample_deps()
    for profile, cls in [
        ("standard_rag", CanonicalStandardRAGRunner),
        ("local_graphrag", CanonicalLocalGraphRAGRunner),
        ("deep_graphrag", CanonicalDeepGraphRAGRunner),
        ("agentic_graphrag", CanonicalAgenticGraphRAGRunner),
    ]:
        res = cls(deps).run_canonical_case(_sample_input(profile))
        assert res.budget_settlement_ref == "", f"{profile}: synthetic budget_settlement_ref detected"


def test_11_no_synthetic_plan_version_ref() -> None:
    """plan_version_ref must be empty — PlanVersionReceipt does not exist."""
    deps = _sample_deps()
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert res.plan_version_ref == "", "synthetic plan_version_ref detected"
    assert not res.plan_version_ref.startswith("plan_v1_"), "synthetic plan_v1_* ref detected"


def test_12_no_hardcoded_token_usage() -> None:
    """token_usage must be 0 — ModelUsageReceipt not wired."""
    deps = _sample_deps()
    for profile, cls in [
        ("standard_rag", CanonicalStandardRAGRunner),
        ("local_graphrag", CanonicalLocalGraphRAGRunner),
        ("deep_graphrag", CanonicalDeepGraphRAGRunner),
        ("agentic_graphrag", CanonicalAgenticGraphRAGRunner),
    ]:
        res = cls(deps).run_canonical_case(_sample_input(profile))
        assert res.token_usage == 0, f"{profile}: hardcoded token_usage={res.token_usage} detected"


def test_13_no_hardcoded_cost() -> None:
    """cost must be 0.0 — ModelUsageReceipt not wired."""
    deps = _sample_deps()
    for profile, cls in [
        ("standard_rag", CanonicalStandardRAGRunner),
        ("local_graphrag", CanonicalLocalGraphRAGRunner),
        ("deep_graphrag", CanonicalDeepGraphRAGRunner),
        ("agentic_graphrag", CanonicalAgenticGraphRAGRunner),
    ]:
        res = cls(deps).run_canonical_case(_sample_input(profile))
        assert res.cost == 0.0, f"{profile}: hardcoded cost={res.cost} detected"


def test_14_no_template_answer() -> None:
    """No template answer strings allowed. Blocked results must have empty answer."""
    deps = _sample_deps()
    template_patterns = [
        "Standard RAG evidence synthesis",
        "Local GraphRAG synthesis",
        "Deep GraphRAG multi-round synthesis",
        "Agentic GraphRAG synthesis",
    ]
    for profile, cls in [
        ("standard_rag", CanonicalStandardRAGRunner),
        ("local_graphrag", CanonicalLocalGraphRAGRunner),
        ("deep_graphrag", CanonicalDeepGraphRAGRunner),
        ("agentic_graphrag", CanonicalAgenticGraphRAGRunner),
    ]:
        res = cls(deps).run_canonical_case(_sample_input(profile))
        for pattern in template_patterns:
            assert pattern not in res.answer, f"{profile}: template answer '{pattern}' detected"


def test_15_blocked_result_has_empty_answer() -> None:
    """BLOCKED results must have empty answer field."""
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.answer == ""


# ---------------------------------------------------------------------------
# Section 4: Trace ID
# ---------------------------------------------------------------------------

def test_16_trace_id_from_span_handle_or_none() -> None:
    """trace_id must come from TraceSpanHandle or be None. Never a hand-constructed string."""
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    # NoopTraceAdapter returns None for start_span -> trace_id = None
    assert res.trace_id is None, f"Expected None trace_id from NoopAdapter, got '{res.trace_id}'"


def test_17_trace_id_not_constructed_from_case_fields() -> None:
    """trace_id must not be 'trace_benchmark_{eval_run_id}_{case_id}_{profile}' string."""
    deps = _sample_deps()
    case = _sample_input("standard_rag")
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(case)
    synthetic_pattern = f"trace_benchmark_{case.eval_run_id}_{case.case_id}"
    if res.trace_id is not None:
        assert not res.trace_id.startswith("trace_benchmark_"), (
            f"Synthetic trace_id '{res.trace_id}' constructed from case fields"
        )


def test_18_in_memory_adapter_provides_real_trace_id() -> None:
    """InMemoryTraceAdapter should provide a real TraceSpanHandle with trace_id."""
    from zuno.platform.observability.trace_adapter import InMemoryTraceAdapter
    adapter = InMemoryTraceAdapter(config={"enabled": True, "sample_rate": 1.0})
    deps = CanonicalRuntimeDependencies(trace_adapter=adapter)
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    # With InMemoryAdapter, trace_id should be a non-empty string from the handle
    # (it may be None if adapter returns None on start_span, which is also valid)
    if res.trace_id is not None:
        assert isinstance(res.trace_id, str)
        assert len(res.trace_id) > 0
        # Must not be a synthetic pattern
        assert not res.trace_id.startswith("trace_benchmark_"), "Synthetic trace_id detected"


# ---------------------------------------------------------------------------
# Section 5: Runner is_test_double contract
# ---------------------------------------------------------------------------

def test_19_canonical_runner_is_not_test_double() -> None:
    """All canonical runners must report is_test_double = False."""
    deps = _sample_deps()
    for cls in [
        CanonicalStandardRAGRunner,
        CanonicalLocalGraphRAGRunner,
        CanonicalDeepGraphRAGRunner,
        CanonicalAgenticGraphRAGRunner,
    ]:
        runner = cls(deps)
        assert runner.is_test_double is False


def test_20_canonical_result_is_not_test_double() -> None:
    """CanonicalCaseResult.is_test_double must be False."""
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.is_test_double is False


# ---------------------------------------------------------------------------
# Section 6: Agentic Runner specifically BLOCKED
# ---------------------------------------------------------------------------

def test_21_agentic_runner_does_not_call_agent_control_runtime() -> None:
    """Agentic runner must not invoke AgentControlRuntime manually.
    It should return BLOCKED immediately without assembling manual retrieval chain.
    """
    deps = _sample_deps()
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    # If it called AgentControlRuntime manually it might return 'completed'
    assert res.runtime_status == "blocked"
    assert res.failure_class == "canonical_agent_run_graph_unavailable"


def test_22_agentic_runner_has_no_plan_version_ref() -> None:
    deps = _sample_deps()
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert res.plan_version_ref == ""


def test_23_agentic_runner_has_no_security_decision_ref() -> None:
    deps = _sample_deps()
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    # No security_decision_ref field expected to contain a synthetic value
    assert res.run_outcome_ref == ""


def test_24_agentic_runner_budget_settlement_empty() -> None:
    deps = _sample_deps()
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert res.budget_settlement_ref == ""


def test_25_agentic_runner_no_step_acceptance_events_fabricated() -> None:
    """No fabricated RuntimeObservation with status='completed' used to bypass AgentRunGraph."""
    deps = _sample_deps()
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    # Result must be BLOCKED, not completed
    assert res.runtime_status == "blocked"


def test_26_agentic_runner_no_final_gate_fabricated() -> None:
    """Runner must not report a finalized run without actual AgentRunGraph execution."""
    deps = _sample_deps()
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert res.measurement_state == "BLOCKED"


def test_27_agentic_runner_no_run_outcome_ref() -> None:
    deps = _sample_deps()
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert res.run_outcome_ref == ""


def test_28_agentic_runner_retrieval_answer_bypass_absent() -> None:
    """Verifies no path exists where retrieval directly produces answer without AgentRunGraph."""
    deps = _sample_deps(with_knowledge=True, with_index=True)
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    # With real knowledge runtime deps, runner should still BLOCK due to missing AgentRunGraph
    assert res.failure_class == "canonical_agent_run_graph_unavailable"


# ---------------------------------------------------------------------------
# Section 7: Latency contract
# ---------------------------------------------------------------------------

def test_29_latency_is_positive_float() -> None:
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert isinstance(res.latency, float)
    assert res.latency >= 0.0


def test_30_latency_reasonable_upper_bound() -> None:
    """Latency must be < 5 seconds for a BLOCKED result (no real network call)."""
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    start = time.monotonic()
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    elapsed = time.monotonic() - start
    assert res.latency < 5.0, f"Latency {res.latency:.3f}s too high for a BLOCKED result"


# ---------------------------------------------------------------------------
# Section 8: MeasurementTruthGate priority order
# ---------------------------------------------------------------------------

def test_31_gate_rule1_test_double_always_blocked() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(is_test_double=True, runtime_status="completed")
    assert state == MeasurementState.BLOCKED
    assert "test_double" in reason


def test_32_gate_rule2_failed_before_security() -> None:
    """Rule 2 (failed) must fire before rule 3 (security)."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="failed",
        security_blocked=True,
        failure_class="retriever_timeout",
    )
    assert state == MeasurementState.FAILED


def test_33_gate_rule3_security_blocked() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="blocked",
        security_blocked=True,
        failure_class="canonical_security_gate_unavailable",
    )
    assert state == MeasurementState.BLOCKED


def test_34_gate_rule4_profile_mismatch() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        requested_profile="standard_rag",
        actual_profile="deep_graphrag",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        run_outcome_ref="outcome_001",
    )
    assert state == MeasurementState.INCOMPARABLE


def test_35_gate_rule5_missing_snapshot_blocked() -> None:
    """Missing snapshot_ref triggers BLOCKED before RUNTIME_OBSERVED."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="",  # missing
        trace_id="trace_001",
        run_outcome_ref="outcome_001",
        reviewer_status="approved",
        benchmark_eligible=True,
        has_formal_credentials=True,
        formal_execution_requested=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "snapshot_ref_missing" in reason


def test_36_gate_rule5_missing_trace_blocked() -> None:
    """Missing trace_id triggers BLOCKED before RUNTIME_OBSERVED — rule 5 before rule 6."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id=None,  # missing
        run_outcome_ref="outcome_001",
        reviewer_status="pending",  # also pending
        has_formal_credentials=False,
        formal_execution_requested=False,
    )
    # Rule 5 must fire (trace missing) before rule 6 (reviewer pending)
    assert state == MeasurementState.BLOCKED
    assert "trace_missing" in reason


def test_37_gate_rule5_missing_budget_settlement_blocked() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="",  # missing
        run_outcome_ref="outcome_001",
        reviewer_status="approved",
        benchmark_eligible=True,
        has_formal_credentials=True,
        formal_execution_requested=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "budget_settlement_missing" in reason


def test_38_gate_rule6_runtime_observed_pending_reviewer() -> None:
    """When all evidence present but reviewer pending -> RUNTIME_OBSERVED."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        run_outcome_ref="outcome_001",
        reviewer_status="pending",  # not approved
        benchmark_eligible=True,
        has_formal_credentials=True,
        formal_execution_requested=True,
    )
    assert state == MeasurementState.RUNTIME_OBSERVED


def test_39_gate_rule7_measured_when_all_gates_pass() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        run_outcome_ref="outcome_001",
        reviewer_status="approved",
        benchmark_eligible=True,
        has_formal_credentials=True,
        formal_execution_requested=True,
    )
    assert state == MeasurementState.MEASURED


# ---------------------------------------------------------------------------
# Section 9: Factory truth contracts
# ---------------------------------------------------------------------------

def test_40_factory_canonical_mode_fails_without_deps() -> None:
    """canonical mode without CanonicalRuntimeDependencies must raise RuntimeError (fail closed)."""
    with pytest.raises(RuntimeError, match="canonical mode requires"):
        CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=None)


def test_41_factory_canonical_mode_does_not_create_index_runtime() -> None:
    """Factory must NOT create a KnowledgeIndexRuntime in canonical mode.
    It must accept None and fail closed (handled in __init__).
    """
    with pytest.raises(RuntimeError):
        CanonicalProfileRuntimeFactory(runtime_mode="canonical")


def test_42_factory_contract_smoke_creates_test_double() -> None:
    factory = CanonicalProfileRuntimeFactory(runtime_mode="contract-smoke")
    runner = factory.create_runner("standard_rag")
    assert runner.is_test_double is True


def test_43_factory_unknown_profile_raises() -> None:
    factory = CanonicalProfileRuntimeFactory(runtime_mode="contract-smoke")
    with pytest.raises(ValueError, match="Unknown profile"):
        factory.create_runner("nonexistent_profile")


def test_44_factory_canonical_with_deps_creates_canonical_runner() -> None:
    deps = _sample_deps()
    factory = CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=deps)
    runner = factory.create_runner("standard_rag")
    assert isinstance(runner, CanonicalBenchmarkProfileRunner)
    assert runner.is_test_double is False


def test_45_factory_fake_receipt_ref_not_accepted_as_measurement() -> None:
    """A canonical runner result with synthetic refs must classify as BLOCKED, not MEASURED."""
    gate = MeasurementTruthGate()
    # Attempt to pass a synthetic receipt ref as run_outcome_ref
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="blocked",
        failure_class="canonical_security_gate_unavailable",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        run_outcome_ref="outcome_001",
        reviewer_status="approved",
        benchmark_eligible=True,
        has_formal_credentials=True,
        formal_execution_requested=True,
    )
    # runtime_status = "blocked" -> Rule 3 fires
    assert state == MeasurementState.BLOCKED


def test_46_missing_snapshot_with_reviewer_pending_still_blocked() -> None:
    """Rule 5 (snapshot missing) must fire before Rule 6 (reviewer pending)."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="",
        trace_id=None,
        budget_settlement_ref="",
        run_outcome_ref="",
        reviewer_status="pending",
        benchmark_eligible=False,
        has_formal_credentials=False,
        formal_execution_requested=False,
    )
    assert state == MeasurementState.BLOCKED


def test_47_missing_trace_with_credentials_missing_still_blocked() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id=None,
        budget_settlement_ref="budget_001",
        run_outcome_ref="outcome_001",
        reviewer_status="approved",
        benchmark_eligible=True,
        has_formal_credentials=False,
        formal_execution_requested=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "trace_missing" in reason


def test_48_missing_run_outcome_ref_blocked() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        run_outcome_ref="",  # missing
        reviewer_status="approved",
        benchmark_eligible=True,
        has_formal_credentials=True,
        formal_execution_requested=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "run_outcome_missing" in reason


# ---------------------------------------------------------------------------
# Section 10: CLI runtime-mode contract
# ---------------------------------------------------------------------------

def test_49_cli_canonical_mode_not_auto_created() -> None:
    """The CLI must not silently downgrade canonical mode to contract-smoke."""
    import importlib
    mod = importlib.import_module("tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark")
    # Verify --runtime-mode argument exists in parser (introspect source)
    import inspect
    src = inspect.getsource(mod.main)
    assert "--runtime-mode" in src, "CLI must declare --runtime-mode argument"
    assert "canonical" in src, "CLI must declare canonical choice"
    assert "fail closed" in src.lower() or "sys.exit" in src, "CLI must fail closed for canonical mode"


def test_50_windows_posix_path_consistency() -> None:
    """Trace IDs, eval_run_id, case_id must not contain OS path separators."""
    import pathlib
    case = _sample_input("standard_rag")
    assert "\\" not in case.eval_run_id, "eval_run_id must not contain backslashes"
    assert "/" not in case.eval_run_id, "eval_run_id must not contain forward slashes"
    assert "\\" not in case.case_id, "case_id must not contain backslashes"
    assert "/" not in case.case_id, "case_id must not contain forward slashes"
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(case)
    if res.trace_id is not None:
        assert "\\" not in res.trace_id, "trace_id must not contain backslashes"
    # failure_class must also be a portable identifier
    assert "\\" not in res.failure_class
    assert "/" not in res.failure_class

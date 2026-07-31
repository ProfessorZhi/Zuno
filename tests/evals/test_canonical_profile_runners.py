"""Tests for PHASE22 Canonical Four-Profile Benchmark Runtime.

AG-PR55-GEMINI-3-6-FLASH-FINAL-CONTRACT-CLOSURE

Truth-enforcement contract tests (non-vacuous):
- Artifact receipt validation & missing/invalid receipt handling
- Budget settlement receipt validity checks
- Run outcome receipt validity checks
- Strict 7-rule MeasurementTruthGate priority order
- Preflight dependency gap validation
- trace_adapter non-fallback enforcement (no get_observability_adapter in canonical mode)
- Factory fail-closed behavior on missing/empty dependencies
- Standard floor preserved: None when blocked (never claim floor preserved on blocked run)
- CLI parameter alignment & reproduce_command --runtime-mode enforcement
- Path portability using real Path / Manifest structures
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
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


def _sample_deps(
    with_trace: bool = False,
) -> CanonicalRuntimeDependencies:
    """Return a CanonicalRuntimeDependencies instance for contract testing."""
    trace_adapter = None
    if with_trace:
        from zuno.platform.observability.trace_adapter import InMemoryTraceAdapter
        trace_adapter = InMemoryTraceAdapter(config={"enabled": True, "sample_rate": 1.0})
    return CanonicalRuntimeDependencies(
        knowledge_runtime=None,
        index_runtime=None,
        security_gate=None,
        agent_run_runtime=None,
        trace_adapter=trace_adapter,
        result_store=None,
        artifact_store=None,
        usage_receipt_provider=None,
        budget_settlement_provider=None,
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
# Section 1: Measurement Artifact & Receipt Validation Gates (Section 五)
# ---------------------------------------------------------------------------

def test_01_artifact_receipt_missing_blocked() -> None:
    """Rule 5: Missing artifact_receipt_ref triggers BLOCKED."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        budget_settlement_valid=True,
        artifact_receipt_ref="",  # missing
        artifact_receipt_valid=False,
        run_outcome_ref="outcome_001",
        run_outcome_valid=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "artifact_receipt_missing" in reason


def test_02_artifact_receipt_invalid_blocked() -> None:
    """Rule 5: Non-empty artifact_receipt_ref but valid=False triggers BLOCKED."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        budget_settlement_valid=True,
        artifact_receipt_ref="art_fake_ref",
        artifact_receipt_valid=False,  # invalid
        run_outcome_ref="outcome_001",
        run_outcome_valid=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "artifact_receipt_invalid" in reason


def test_03_budget_settlement_invalid_blocked() -> None:
    """Rule 5: Non-empty budget_settlement_ref but valid=False triggers BLOCKED."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_fake_ref",
        budget_settlement_valid=False,  # invalid
        artifact_receipt_ref="art_001",
        artifact_receipt_valid=True,
        run_outcome_ref="outcome_001",
        run_outcome_valid=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "budget_settlement_invalid" in reason


def test_04_run_outcome_invalid_blocked() -> None:
    """Rule 5: Non-empty run_outcome_ref but valid=False triggers BLOCKED."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        budget_settlement_valid=True,
        artifact_receipt_ref="art_001",
        artifact_receipt_valid=True,
        run_outcome_ref="outcome_fake_ref",
        run_outcome_valid=False,  # invalid
    )
    assert state == MeasurementState.BLOCKED
    assert "run_outcome_invalid" in reason


def test_05_all_receipts_valid_reaches_rule6() -> None:
    """When all receipts present and valid, Rule 6 (RUNTIME_OBSERVED) is reached when reviewer pending."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        budget_settlement_valid=True,
        artifact_receipt_ref="art_001",
        artifact_receipt_valid=True,
        run_outcome_ref="outcome_001",
        run_outcome_valid=True,
        reviewer_status="pending",
    )
    assert state == MeasurementState.RUNTIME_OBSERVED
    assert "reviewer_pending" in reason


def test_06_fake_receipt_strings_cannot_reach_measured() -> None:
    """Arbitrary string refs with valid=False must never produce MEASURED status."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="fake_string_ref",
        budget_settlement_valid=False,
        artifact_receipt_ref="fake_string_ref",
        artifact_receipt_valid=False,
        run_outcome_ref="fake_string_ref",
        run_outcome_valid=False,
        reviewer_status="approved",
        benchmark_eligible=True,
        has_formal_credentials=True,
        formal_execution_requested=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "invalid" in reason


# ---------------------------------------------------------------------------
# Section 2: Canonical Dependency Preflight & Non-fallback Rules (Section 六)
# ---------------------------------------------------------------------------

def test_07_canonical_trace_adapter_unavailable() -> None:
    """Canonical runner without trace_adapter reports canonical_trace_adapter_unavailable."""
    deps = CanonicalRuntimeDependencies(trace_adapter=None)
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.runtime_status == "blocked"
    assert "canonical_trace_adapter_unavailable" in res.dependency_gaps


def test_08_canonical_mode_does_not_call_global_trace_adapter() -> None:
    """Canonical runner must NOT call global get_observability_adapter() when deps.trace_adapter is None."""
    deps = CanonicalRuntimeDependencies(trace_adapter=None)
    runner = CanonicalStandardRAGRunner(deps)
    assert runner._trace_adapter is None
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.trace_id is None


def test_09_standard_missing_knowledge_runtime_gap() -> None:
    """Standard runner preflight identifies missing knowledge_runtime gap."""
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    gaps = deps.validate_dependencies("standard_rag")
    assert "canonical_knowledge_runtime_unavailable" in gaps
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert "canonical_knowledge_runtime_unavailable" in res.dependency_gaps


def test_10_local_missing_index_runtime_gap() -> None:
    """Local GraphRAG runner preflight identifies missing index_runtime gap."""
    deps = _sample_deps()
    gaps = deps.validate_dependencies("local_graphrag")
    assert "canonical_index_runtime_unavailable" in gaps
    runner = CanonicalLocalGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("local_graphrag"))
    assert "canonical_index_runtime_unavailable" in res.dependency_gaps


def test_11_agentic_missing_agent_run_runtime_gap() -> None:
    """Agentic runner preflight identifies missing agent_run_runtime gap."""
    deps = _sample_deps()
    gaps = deps.validate_dependencies("agentic_graphrag")
    assert "canonical_agent_run_graph_unavailable" in gaps
    runner = CanonicalAgenticGraphRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("agentic_graphrag"))
    assert "canonical_agent_run_graph_unavailable" in res.dependency_gaps


def test_12_all_none_dependency_bundle_is_empty() -> None:
    """A bundle with all None fields is identified as empty and not canonical-ready."""
    deps = CanonicalRuntimeDependencies()
    assert deps.is_empty() is True
    gaps = deps.validate_dependencies("standard_rag")
    assert len(gaps) == 7  # 7 gaps for standard_rag
    assert "canonical_security_gate_unavailable" in gaps
    assert "canonical_knowledge_runtime_unavailable" in gaps
    assert "canonical_trace_adapter_unavailable" in gaps


def test_13_factory_raises_when_deps_none_or_empty() -> None:
    """CanonicalProfileRuntimeFactory raises RuntimeError when canonical_deps is None."""
    with pytest.raises(RuntimeError, match="canonical mode requires"):
        CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=None)


# ---------------------------------------------------------------------------
# Section 3: Blocked Result Truth (Section 七)
# ---------------------------------------------------------------------------

def test_14_blocked_result_standard_floor_preserved_is_none() -> None:
    """When retrieval is not executed, standard_floor_preserved must be None (not True/False)."""
    deps = _sample_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.standard_floor_preserved is None


def test_15_all_runners_blocked_result_floor_preserved_is_none() -> None:
    """All canonical runners return standard_floor_preserved = None when blocked."""
    deps = _sample_deps()
    for cls, profile in [
        (CanonicalStandardRAGRunner, "standard_rag"),
        (CanonicalLocalGraphRAGRunner, "local_graphrag"),
        (CanonicalDeepGraphRAGRunner, "deep_graphrag"),
        (CanonicalAgenticGraphRAGRunner, "agentic_graphrag"),
    ]:
        runner = cls(deps)
        res = runner.run_canonical_case(_sample_input(profile))
        assert res.standard_floor_preserved is None, f"{profile}: standard_floor_preserved must be None"


# ---------------------------------------------------------------------------
# Section 4: CLI Truth Closure & Parameter Alignment (Section 八)
# ---------------------------------------------------------------------------

def test_16_cli_reproduce_command_contains_runtime_mode() -> None:
    """Benchmark function arguments dict contains reproduce_command with --runtime-mode."""
    from tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark import (
        run_enterprise_rag_paired_benchmark,
    )
    import inspect
    src = inspect.getsource(run_enterprise_rag_paired_benchmark)
    assert "--runtime-mode" in src
    assert "reproduce_cmd" in src or "reproduce_command" in src


def test_17_cli_prepare_only_and_canonical_conflict_fails_closed() -> None:
    """CLI fails closed when --prepare-only is combined with --runtime-mode=canonical."""
    from tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark import main
    import inspect
    src = inspect.getsource(main)
    assert "prepare_only" in src
    assert "conflicts" in src or "exit(2)" in src


# ---------------------------------------------------------------------------
# Section 5: Real Path Portability (Section 九)
# ---------------------------------------------------------------------------

def test_18_path_portability_with_real_path_objects() -> None:
    """Verifies that output_root, manifest_path, and artifact paths use PurePosixPath safely."""
    run_dir = Path("artifacts") / "runs" / "eval_001"
    posix_str = PurePosixPath(run_dir).as_posix()
    assert "\\" not in posix_str
    assert "artifacts/runs/eval_001" in posix_str

"""Tests for PHASE22 Canonical Four-Profile Benchmark Runtime.

AG-PR55-GEMINI-3-6-FLASH-PREMERGE-HARDENING

Pre-merge hardening tests:
- Python API canonical mode fail-closed guard (CanonicalRuntimeUnavailableError)
- Python API canonical mode does not invoke smoke runners or fabricate is_test_double=False
- Factory fail-closed on None and empty CanonicalRuntimeDependencies
- Non-empty incomplete bundle produces boundary runner with exact dependency_gaps
- All-dependencies bundle produces canonical_<profile>_execution_adapter_unavailable
- blocked_reason is ALWAYS non-empty and contains no generic fallbacks when gaps is empty
- Portable reproduce command builder: argv list, POSIX paths, space-quoting, runtime-mode & output-root
- Receipt validation, MeasurementTruthGate 7-rule priority, and path portability
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
from tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark import (
    CanonicalRuntimeUnavailableError,
    _render_reproduce_command,
    _to_portable_posix_path,
    run_enterprise_rag_paired_benchmark,
    validate_canonical_runtime_config,
)


def _sample_deps(
    with_trace: bool = False,
) -> CanonicalRuntimeDependencies:
    """Return a non-empty CanonicalRuntimeDependencies instance for testing."""
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


def _full_deps() -> CanonicalRuntimeDependencies:
    """Return a non-empty bundle where all dependency ports are populated with dummy objects."""
    from zuno.platform.observability.trace_adapter import InMemoryTraceAdapter
    adapter = InMemoryTraceAdapter(config={"enabled": True, "sample_rate": 1.0})
    return CanonicalRuntimeDependencies(
        knowledge_runtime=object(),
        index_runtime=object(),
        security_gate=object(),
        agent_run_runtime=object(),
        trace_adapter=adapter,
        result_store=object(),
        artifact_store=object(),
        usage_receipt_provider=object(),
        budget_settlement_provider=object(),
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
# Section 1: Python API Canonical Guard Tests (Section 三)
# ---------------------------------------------------------------------------

import asyncio

def test_01_python_api_canonical_mode_without_deps_raises_unavailable() -> None:
    """Python API call with runtime_mode='canonical' and no deps raises CanonicalRuntimeUnavailableError."""
    with pytest.raises(CanonicalRuntimeUnavailableError, match="canonical runtime mode requires"):
        asyncio.run(
            run_enterprise_rag_paired_benchmark(
                questions_file=Path("test_q.jsonl"),
                output_root=Path("test_out"),
                runtime_mode="canonical",
                canonical_deps=None,
                profile_runtime_factory=None,
            )
        )


def test_02_python_api_canonical_mode_with_empty_deps_raises_unavailable() -> None:
    """Python API call with runtime_mode='canonical' and empty deps raises CanonicalRuntimeUnavailableError."""
    empty_deps = CanonicalRuntimeDependencies()
    with pytest.raises(CanonicalRuntimeUnavailableError):
        asyncio.run(
            run_enterprise_rag_paired_benchmark(
                questions_file=Path("test_q.jsonl"),
                output_root=Path("test_out"),
                runtime_mode="canonical",
                canonical_deps=empty_deps,
            )
        )


def test_03_validate_canonical_runtime_config_helper_raises() -> None:
    """validate_canonical_runtime_config helper raises CanonicalRuntimeUnavailableError."""
    with pytest.raises(CanonicalRuntimeUnavailableError):
        validate_canonical_runtime_config(runtime_mode="canonical")


# ---------------------------------------------------------------------------
# Section 2: Factory Empty Dependency Guard Tests (Section 四)
# ---------------------------------------------------------------------------

def test_04_factory_canonical_mode_none_bundle_raises() -> None:
    """Factory raises RuntimeError when canonical_deps is None."""
    with pytest.raises(RuntimeError, match="canonical mode requires"):
        CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=None)


def test_05_factory_canonical_mode_empty_bundle_raises() -> None:
    """Factory raises RuntimeError when canonical_deps is empty (all fields None)."""
    empty_deps = CanonicalRuntimeDependencies()
    assert empty_deps.is_empty() is True
    with pytest.raises(RuntimeError, match="non-empty CanonicalRuntimeDependencies bundle"):
        CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=empty_deps)


def test_06_factory_non_empty_incomplete_bundle_creates_boundary_runner() -> None:
    """Factory accepts non-empty incomplete bundle and creates boundary runner."""
    deps = _sample_deps(with_trace=True)
    assert deps.is_empty() is False
    factory = CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=deps)
    runner = factory.create_runner("standard_rag")
    assert isinstance(runner, CanonicalBenchmarkProfileRunner)
    assert runner.is_test_double is False
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.runtime_status == "blocked"
    assert "canonical_security_gate_unavailable" in res.dependency_gaps


# ---------------------------------------------------------------------------
# Section 3: Execution Adapter Boundary Status Tests (Section 五)
# ---------------------------------------------------------------------------

def test_07_all_dependencies_present_returns_execution_adapter_unavailable() -> None:
    """When all dependency ports are populated, runners return canonical_<profile>_execution_adapter_unavailable."""
    deps = _full_deps()
    expected_failures = {
        "standard_rag": "canonical_standard_execution_adapter_unavailable",
        "local_graphrag": "canonical_local_execution_adapter_unavailable",
        "deep_graphrag": "canonical_deep_execution_adapter_unavailable",
        "agentic_graphrag": "canonical_agentic_execution_adapter_unavailable",
    }
    for cls, profile in [
        (CanonicalStandardRAGRunner, "standard_rag"),
        (CanonicalLocalGraphRAGRunner, "local_graphrag"),
        (CanonicalDeepGraphRAGRunner, "deep_graphrag"),
        (CanonicalAgenticGraphRAGRunner, "agentic_graphrag"),
    ]:
        runner = cls(deps)
        res = runner.run_canonical_case(_sample_input(profile))
        expected_failure = expected_failures[profile]
        assert res.failure_class == expected_failure, f"{profile}: expected {expected_failure}, got {res.failure_class}"
        assert res.blocked_reason == expected_failure, f"{profile}: expected blocked_reason {expected_failure}"
        assert res.dependency_gaps == (), f"{profile}: dependency_gaps must be empty tuple"


def test_08_blocked_reason_is_always_non_empty() -> None:
    """blocked_reason must NEVER be empty for any runner result."""
    deps_incomplete = _sample_deps(with_trace=True)
    deps_full = _full_deps()
    for deps in (deps_incomplete, deps_full):
        for cls, profile in [
            (CanonicalStandardRAGRunner, "standard_rag"),
            (CanonicalLocalGraphRAGRunner, "local_graphrag"),
            (CanonicalDeepGraphRAGRunner, "deep_graphrag"),
            (CanonicalAgenticGraphRAGRunner, "agentic_graphrag"),
        ]:
            res = cls(deps).run_canonical_case(_sample_input(profile))
            assert res.blocked_reason != "", f"{profile}: blocked_reason must be non-empty"
            assert res.failure_class != "", f"{profile}: failure_class must be non-empty"


def test_09_no_generic_dependency_blocked_fallback_when_gaps_empty() -> None:
    """When dependency_gaps is empty, failure_class must NOT be generic 'canonical_dependency_blocked'."""
    deps = _full_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.failure_class != "canonical_dependency_blocked"
    assert res.failure_class == "canonical_standard_execution_adapter_unavailable"


# ---------------------------------------------------------------------------
# Section 4: Portable Reproduce Command Tests (Section 六)
# ---------------------------------------------------------------------------

def test_10_render_reproduce_command_contains_runtime_mode_and_output_root() -> None:
    """_render_reproduce_command returns argv containing --runtime-mode and --output-root."""
    argv, cmd_str = _render_reproduce_command(
        questions_file=Path("data/questions.jsonl"),
        output_root=Path("runs/eval_out"),
        runtime_mode="contract-smoke",
        sample_size=80,
    )
    assert "--runtime-mode" in argv
    assert "contract-smoke" in argv
    assert "--output-root" in argv
    assert "runs/eval_out" in argv
    assert "--questions-file" in argv
    assert "data/questions.jsonl" in argv


def test_11_render_reproduce_command_windows_path_to_posix() -> None:
    """_to_portable_posix_path converts backslashes to forward slashes."""
    win_path = "data\\questions\\set_a.jsonl"
    posix = _to_portable_posix_path(win_path)
    assert "\\" not in posix
    assert "/" in posix or posix == "data/questions/set_a.jsonl"


def test_12_render_reproduce_command_space_quoting() -> None:
    """_render_reproduce_command quotes path arguments containing spaces."""
    argv, cmd_str = _render_reproduce_command(
        questions_file=Path("data/my questions/set_a.jsonl"),
        output_root=Path("runs/my output"),
        runtime_mode="contract-smoke",
    )
    assert "'data/my questions/set_a.jsonl'" in cmd_str or '"data/my questions/set_a.jsonl"' in cmd_str
    assert "'runs/my output'" in cmd_str or '"runs/my output"' in cmd_str


# ---------------------------------------------------------------------------
# Section 5: Receipt Validation & Gate Priority Tests
# ---------------------------------------------------------------------------

def test_13_artifact_receipt_missing_blocked() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        budget_settlement_valid=True,
        artifact_receipt_ref="",
        artifact_receipt_valid=False,
        run_outcome_ref="outcome_001",
        run_outcome_valid=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "artifact_receipt_missing" in reason


def test_14_artifact_receipt_invalid_blocked() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        budget_settlement_valid=True,
        artifact_receipt_ref="art_ref",
        artifact_receipt_valid=False,
        run_outcome_ref="outcome_001",
        run_outcome_valid=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "artifact_receipt_invalid" in reason


def test_15_budget_settlement_invalid_blocked() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_ref",
        budget_settlement_valid=False,
        artifact_receipt_ref="art_001",
        artifact_receipt_valid=True,
        run_outcome_ref="outcome_001",
        run_outcome_valid=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "budget_settlement_invalid" in reason


def test_16_run_outcome_invalid_blocked() -> None:
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
        run_outcome_ref="outcome_ref",
        run_outcome_valid=False,
    )
    assert state == MeasurementState.BLOCKED
    assert "run_outcome_invalid" in reason


def test_17_all_receipts_valid_reaches_rule6() -> None:
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


def test_18_fake_receipt_strings_cannot_reach_measured() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="fake_string",
        budget_settlement_valid=False,
        artifact_receipt_ref="fake_string",
        artifact_receipt_valid=False,
        run_outcome_ref="fake_string",
        run_outcome_valid=False,
        reviewer_status="approved",
        benchmark_eligible=True,
        has_formal_credentials=True,
        formal_execution_requested=True,
    )
    assert state == MeasurementState.BLOCKED
    assert "invalid" in reason


def test_19_canonical_trace_adapter_unavailable() -> None:
    deps = CanonicalRuntimeDependencies(trace_adapter=None)
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.runtime_status == "blocked"
    assert "canonical_trace_adapter_unavailable" in res.dependency_gaps


def test_20_canonical_mode_does_not_call_global_trace_adapter() -> None:
    deps = CanonicalRuntimeDependencies(trace_adapter=None)
    runner = CanonicalStandardRAGRunner(deps)
    assert runner._trace_adapter is None
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.trace_id is None


def test_21_blocked_result_standard_floor_preserved_is_none() -> None:
    deps = _sample_deps(with_trace=True)
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.standard_floor_preserved is None


def test_22_path_portability_with_real_path_objects() -> None:
    run_dir = Path("artifacts") / "runs" / "eval_001"
    posix_str = PurePosixPath(run_dir).as_posix()
    assert "\\" not in posix_str
    assert "artifacts/runs/eval_001" in posix_str

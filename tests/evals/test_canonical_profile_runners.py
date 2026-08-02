"""Tests for PHASE22 Canonical Four-Profile Benchmark Runtime.

AG-PR55-GEMINI-3-6-FLASH-TRUE-PREMERGE-CLOSURE

True pre-merge closure tests:
- Canonical mode without an explicit dependency bundle or profile factory fails closed.
- Canonical mode with a valid bundle/factory enters canonical profile preflight.
- Canonical mode must not dispatch to stackless contract-smoke test doubles.
- Generated canonical output remains BLOCKED / not measured until formal execution adapters and receipts exist.
- AST test: _render_reproduce_command has exactly 1 FunctionDef in run_enterprise_rag_paired_benchmark.py
- Contract-smoke and prepare-only modes preserve their existing behavior
"""

from __future__ import annotations

import ast
import asyncio
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
# Section 1: Canonical Mode Configuration Gate Tests (Section 三)
# ---------------------------------------------------------------------------

def test_01_canonical_mode_without_deps_fails_closed(tmp_path: Path) -> None:
    """canonical mode + canonical_deps=None fails closed with CanonicalRuntimeUnavailableError."""
    out_dir = tmp_path / "canonical_out_01"
    q_file = tmp_path / "non_existent_q.jsonl"
    with pytest.raises(CanonicalRuntimeUnavailableError, match="canonical benchmark execution adapters are not implemented"):
        asyncio.run(
            run_enterprise_rag_paired_benchmark(
                questions_file=q_file,
                output_root=out_dir,
                runtime_mode="canonical",
                canonical_deps=None,
                profile_runtime_factory=None,
            )
        )
    assert out_dir.exists() is False


def test_02_canonical_mode_with_empty_deps_fails_closed(tmp_path: Path) -> None:
    """canonical mode + empty CanonicalRuntimeDependencies fails closed."""
    out_dir = tmp_path / "canonical_out_02"
    q_file = tmp_path / "non_existent_q.jsonl"
    empty_deps = CanonicalRuntimeDependencies()
    with pytest.raises(CanonicalRuntimeUnavailableError, match="canonical benchmark execution adapters are not implemented"):
        asyncio.run(
            run_enterprise_rag_paired_benchmark(
                questions_file=q_file,
                output_root=out_dir,
                runtime_mode="canonical",
                canonical_deps=empty_deps,
            )
        )
    assert out_dir.exists() is False


def test_03_canonical_config_with_full_deps_is_admitted_to_profile_preflight() -> None:
    """canonical mode + full dependency bundle may enter profile preflight."""
    validate_canonical_runtime_config(
        runtime_mode="canonical",
        canonical_deps=_full_deps(),
    )


def test_04_canonical_mode_with_dummy_factory_fails_closed(tmp_path: Path) -> None:
    """canonical mode + profile_runtime_factory=object() fails closed."""
    out_dir = tmp_path / "canonical_out_04"
    q_file = tmp_path / "non_existent_q.jsonl"
    with pytest.raises(CanonicalRuntimeUnavailableError, match="canonical benchmark execution adapters are not implemented"):
        asyncio.run(
            run_enterprise_rag_paired_benchmark(
                questions_file=q_file,
                output_root=out_dir,
                runtime_mode="canonical",
                profile_runtime_factory=object(),
            )
        )
    assert out_dir.exists() is False


def test_05_canonical_config_with_valid_factory_is_admitted_to_profile_preflight() -> None:
    """canonical mode + valid CanonicalProfileRuntimeFactory may enter profile preflight."""
    factory = CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=_full_deps())
    validate_canonical_runtime_config(
        runtime_mode="canonical",
        profile_runtime_factory=factory,
    )


def test_06_canonical_with_deps_writes_blocked_manifest_without_stackless_runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """canonical mode with deps may prepare evidence but must not call stackless test-double runners."""
    out_dir = tmp_path / "canonical_out_06"
    q_file = tmp_path / "questions_06.jsonl"
    q_file.write_text(
        '{"id":"q1","question":"test","expected_answer":"answer","expected_doc_ids":["doc_1"],'
        '"question_type":"simple_retrieval","complexity":"low","reviewer_status":"approved",'
        '"provenance":{"dataset":"unit"}}\n',
        encoding="utf-8",
    )

    stackless_calls = 0
    async def mock_stackless(*args: Any, **kwargs: Any) -> dict[str, Any]:
        nonlocal stackless_calls
        stackless_calls += 1
        return {}

    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark.run_stackless_local_eval",
        mock_stackless,
    )

    result = asyncio.run(
        run_enterprise_rag_paired_benchmark(
            questions_file=q_file,
            output_root=out_dir,
            runtime_mode="canonical",
            canonical_deps=_full_deps(),
            sample_size=1,
            allow_blocked=True,
        )
    )

    assert stackless_calls == 0
    assert result["status"] == "blocked"
    assert (out_dir / "benchmark_manifest.json").exists() is True
    assert (out_dir / "metrics.json").exists() is True


def test_06b_canonical_ready_dataset_uses_profile_factory_not_stackless(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """canonical execution dispatch must use the canonical profile factory, not stackless test doubles."""
    out_dir = tmp_path / "canonical_out_06b"
    q_file = tmp_path / "questions_06b.jsonl"
    q_file.write_text(
        '{"id":"q1","question":"test","expected_answer":"answer","expected_doc_ids":["doc_1"],'
        '"question_type":"simple_retrieval","complexity":"low","reviewer_status":"approved",'
        '"provenance":{"dataset":"unit"}}\n',
        encoding="utf-8",
    )

    def fake_prepare_public_enterprise_eval(**kwargs: Any) -> dict[str, Any]:
        output_dir = Path(kwargs["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        dataset_path = output_dir / "enterprise_eval.jsonl"
        dataset_path.write_text(
            '{"id":"q1","question":"test","expected_answer":"answer","expected_doc_ids":["doc_1"],'
            '"question_type":"simple_retrieval","complexity":"low"}\n',
            encoding="utf-8",
        )
        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(
            '{"case_count":1,"external_documents_required":false,"documents":[]}',
            encoding="utf-8",
        )
        return {
            "dataset_path": str(dataset_path),
            "manifest_path": str(manifest_path),
            "case_count": 1,
            "external_documents_required": False,
        }

    async def fail_if_stackless(*args: Any, **kwargs: Any) -> dict[str, Any]:
        raise AssertionError("canonical mode must not call stackless local eval")

    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark.prepare_public_enterprise_eval",
        fake_prepare_public_enterprise_eval,
    )
    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark.run_stackless_local_eval",
        fail_if_stackless,
    )

    result = asyncio.run(
        run_enterprise_rag_paired_benchmark(
            questions_file=q_file,
            output_root=out_dir,
            runtime_mode="canonical",
            canonical_deps=_full_deps(),
            sample_size=1,
            allow_blocked=True,
        )
    )

    assert result["status"] == "blocked"
    manifest = (out_dir / "benchmark_manifest.json").read_text(encoding="utf-8")
    assert "canonical_standard_execution_adapter_unavailable" in manifest


# ---------------------------------------------------------------------------
# Section 2: Factory Empty Dependency Guard Tests (Section 四)
# ---------------------------------------------------------------------------

def test_07_factory_canonical_mode_none_bundle_raises() -> None:
    """Factory raises RuntimeError when canonical_deps is None."""
    with pytest.raises(RuntimeError, match="canonical mode requires"):
        CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=None)


def test_08_factory_canonical_mode_empty_bundle_raises() -> None:
    """Factory raises RuntimeError when canonical_deps is empty (all fields None)."""
    empty_deps = CanonicalRuntimeDependencies()
    assert empty_deps.is_empty() is True
    with pytest.raises(RuntimeError, match="non-empty CanonicalRuntimeDependencies bundle"):
        CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=empty_deps)


def test_09_factory_non_empty_incomplete_bundle_creates_boundary_runner() -> None:
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
# Section 3: Execution Adapter Boundary Status Tests
# ---------------------------------------------------------------------------

def test_10_all_dependencies_present_returns_execution_adapter_unavailable() -> None:
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


def test_11_blocked_reason_is_always_non_empty() -> None:
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


def test_12_no_generic_dependency_blocked_fallback_when_gaps_empty() -> None:
    """When dependency_gaps is empty, failure_class must NOT be generic 'canonical_dependency_blocked'."""
    deps = _full_deps()
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.failure_class != "canonical_dependency_blocked"
    assert res.failure_class == "canonical_standard_execution_adapter_unavailable"


# ---------------------------------------------------------------------------
# Section 4: Portable Reproduce Command & AST Single Definition Tests
# ---------------------------------------------------------------------------

def test_13_render_reproduce_command_contains_runtime_mode_and_output_root() -> None:
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


def test_14_render_reproduce_command_windows_path_to_posix() -> None:
    """_to_portable_posix_path converts backslashes to forward slashes."""
    win_path = "data\\questions\\set_a.jsonl"
    posix = _to_portable_posix_path(win_path)
    assert "\\" not in posix
    assert "/" in posix or posix == "data/questions/set_a.jsonl"


def test_15_render_reproduce_command_space_quoting() -> None:
    """_render_reproduce_command quotes path arguments containing spaces."""
    argv, cmd_str = _render_reproduce_command(
        questions_file=Path("data/my questions/set_a.jsonl"),
        output_root=Path("runs/my output"),
        runtime_mode="contract-smoke",
    )
    assert "'data/my questions/set_a.jsonl'" in cmd_str or '"data/my questions/set_a.jsonl"' in cmd_str
    assert "'runs/my output'" in cmd_str or '"runs/my output"' in cmd_str


def test_16_single_definition_of_render_reproduce_command_in_ast() -> None:
    """AST check: run_enterprise_rag_paired_benchmark.py contains EXACTLY ONE FunctionDef named _render_reproduce_command."""
    script_path = Path("tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py")
    tree = ast.parse(script_path.read_text(encoding="utf-8"))
    functions = [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_render_reproduce_command"
    ]
    assert len(functions) == 1, f"Expected exactly 1 definition of _render_reproduce_command, found {len(functions)}"


# ---------------------------------------------------------------------------
# Section 5: Receipt Validation & Gate Priority Tests
# ---------------------------------------------------------------------------

def test_17_artifact_receipt_missing_blocked() -> None:
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


def test_18_artifact_receipt_invalid_blocked() -> None:
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


def test_19_budget_settlement_invalid_blocked() -> None:
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


def test_20_run_outcome_invalid_blocked() -> None:
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


def test_21_all_receipts_valid_reaches_rule6() -> None:
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


def test_22_fake_receipt_strings_cannot_reach_measured() -> None:
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


def test_23_canonical_trace_adapter_unavailable() -> None:
    deps = CanonicalRuntimeDependencies(trace_adapter=None)
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.runtime_status == "blocked"
    assert "canonical_trace_adapter_unavailable" in res.dependency_gaps


def test_24_canonical_mode_does_not_call_global_trace_adapter() -> None:
    deps = CanonicalRuntimeDependencies(trace_adapter=None)
    runner = CanonicalStandardRAGRunner(deps)
    assert runner._trace_adapter is None
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.trace_id is None


def test_25_blocked_result_standard_floor_preserved_is_none() -> None:
    deps = _sample_deps(with_trace=True)
    runner = CanonicalStandardRAGRunner(deps)
    res = runner.run_canonical_case(_sample_input("standard_rag"))
    assert res.standard_floor_preserved is None


def test_26_path_portability_with_real_path_objects() -> None:
    run_dir = Path("artifacts") / "runs" / "eval_001"
    posix_str = PurePosixPath(run_dir).as_posix()
    assert "\\" not in posix_str
    assert "artifacts/runs/eval_001" in posix_str

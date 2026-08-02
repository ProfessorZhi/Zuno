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
import hashlib
import json
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
from tools.evals.zuno.rag_eval.adapters.deep_agentic import (
    AgenticGraphRAGCanonicalAdapter,
    DeepGraphRAGCanonicalAdapter,
)
from tools.evals.zuno.rag_eval.adapters.retrieval import StandardRAGCanonicalAdapter
from tools.evals.zuno.rag_eval.measurement_gate import MeasurementState, MeasurementTruthGate
from tools.evals.zuno.rag_eval.benchmark_preflight import (
    BenchmarkPreflightEvaluator,
    compute_product_runtime_attestation_hash,
)
from tools.evals.zuno.rag_eval.profile_runtime_factory import CanonicalProfileRuntimeFactory
from tools.evals.zuno.rag_eval.runtime_evidence_binding import (
    RECEIPT_OWNERS,
    compute_reference_binding_hash,
)
from tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark import (
    CanonicalRuntimeUnavailableError,
    REQUIRED_MEASURED_PROFILES,
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


class FactoryPathKnowledgePort:
    def execute_standard_retrieval(self, question: str, corpus_snapshot_ref: str) -> dict[str, Any]:
        return {
            "answer": f"Standard adapter observed {question} at {corpus_snapshot_ref}",
            "evidence_refs": ("ev_standard_factory",),
            "retrieved_document_refs": ("doc_standard_factory",),
            "retrieval_rounds": 1,
        }

    def execute_deep_retrieval(self, question: str, corpus_snapshot_ref: str) -> dict[str, Any]:
        return {
            "answer": f"Deep adapter observed {question} at {corpus_snapshot_ref}",
            "evidence_refs": ("ev_deep_factory",),
            "retrieved_document_refs": ("doc_deep_factory",),
            "retrieval_rounds": 2,
        }


class FactoryPathIndexPort:
    def execute_local_graph_retrieval(self, question: str, corpus_snapshot_ref: str) -> dict[str, Any]:
        return {
            "answer": f"Local adapter observed {question} at {corpus_snapshot_ref}",
            "evidence_refs": ("ev_local_factory",),
            "retrieved_document_refs": ("doc_local_factory",),
            "retrieval_rounds": 1,
            "graph_added_refs": ("doc_local_graph_added",),
        }


class FactoryPathAgentPort:
    def execute_agent_run(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "status": "completed",
            "answer": f"Agentic adapter observed {kwargs['case_id']}",
            "evidence_refs": ("ev_agentic_factory",),
            "retrieved_document_refs": ("doc_agentic_factory",),
            "retrieval_rounds": 1,
        }


def _factory_path_deps() -> CanonicalRuntimeDependencies:
    """Return deps that let Deep and Agentic factory adapters reach their runtime ports."""
    from zuno.platform.observability.trace_adapter import InMemoryTraceAdapter
    return CanonicalRuntimeDependencies(
        knowledge_runtime=FactoryPathKnowledgePort(),
        index_runtime=FactoryPathIndexPort(),
        security_gate=object(),
        agent_run_runtime=FactoryPathAgentPort(),
        trace_adapter=InMemoryTraceAdapter(config={"enabled": True, "sample_rate": 1.0}),
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


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _receipt(receipt_type: str, ref: str) -> dict[str, str]:
    return {
        "receipt_type": receipt_type,
        "receipt_ref": ref,
        "owner": RECEIPT_OWNERS[receipt_type],
        "runtime_version": "rt-1.0",
        "snapshot_ref": "snapshot_v1",
        "payload_hash": _hash(ref),
    }


def _standard_runtime_evidence_binding(**overrides: Any) -> dict[str, Any]:
    binding: dict[str, Any] = {
        "eval_run_id": "run_test_001",
        "case_id": "case_001",
        "requested_profile": "standard_rag",
        "actual_profile": "standard_rag",
        "runtime_name": "canonical-standard-runtime",
        "runtime_version": "rt-1.0",
        "corpus_snapshot_ref": "snapshot_v1",
        "trace_id": "trace-1",
        "security_decision_ref": "security-1",
        "plan_version_ref": "",
        "run_outcome_ref": "",
        "usage_receipt_ref": "usage-1",
        "budget_settlement_ref": "budget-1",
        "artifact_receipt_ref": "artifact-1",
        "artifact_payload_hash": _hash("artifact-payload"),
        "result_payload_hash": _hash("result-payload"),
        "reference_binding_hash": "0" * 64,
        "receipts": [
            _receipt("security_decision", "security-1"),
            _receipt("trace", "trace-1"),
            _receipt("usage_receipt", "usage-1"),
            _receipt("budget_settlement", "budget-1"),
            _receipt("artifact_receipt", "artifact-1"),
        ],
    }
    binding.update(overrides)
    if "reference_binding_hash" not in overrides:
        binding["reference_binding_hash"] = compute_reference_binding_hash(binding)
    return binding


class EvidenceBindingKnowledgePort:
    def __init__(self, binding: dict[str, Any]) -> None:
        self.binding = binding

    def execute_standard_retrieval(self, question: str, corpus_snapshot_ref: str) -> dict[str, Any]:
        return {
            "answer": f"Runtime answer for {question}",
            "evidence_refs": ("ev_runtime",),
            "retrieved_document_refs": ("doc_runtime",),
            "retrieval_rounds": 1,
            "runtime_evidence_binding": self.binding,
        }


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
            canonical_deps=_factory_path_deps(),
            sample_size=1,
            allow_blocked=True,
        )
    )

    assert result["status"] == "blocked"
    manifest = (out_dir / "benchmark_manifest.json").read_text(encoding="utf-8")
    metrics = (out_dir / "metrics.json").read_text(encoding="utf-8")
    assert "canonical_standard_execution_adapter_unavailable" not in manifest
    assert "Standard adapter observed test at snapshot_v1" in metrics
    assert "Local adapter observed test at snapshot_v1" in metrics
    assert "Deep adapter observed test at snapshot_v1" in metrics
    assert "Agentic adapter observed q1" in metrics
    assert "canonical_product_runtime_attestation_unavailable" in metrics


def test_06c_canonical_benchmark_preserves_runtime_observed_profile_state(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Canonical aggregation must not flatten RUNTIME_OBSERVED profile evidence to BLOCKED."""
    out_dir = tmp_path / "canonical_out_06c"
    q_file = tmp_path / "questions.jsonl"
    q_file.write_text(
        '{"id":"case_001","question":"What did runtime observe?","expected_answer":"answer",'
        '"expected_doc_ids":["doc_runtime"],"question_type":"simple_retrieval",'
        '"complexity":"low","reviewer_status":"approved","provenance":{"dataset":"unit"}}\n',
        encoding="utf-8",
    )

    def fake_prepare_public_enterprise_eval(**kwargs: Any) -> dict[str, Any]:
        output_dir = Path(kwargs["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        dataset_path = output_dir / "enterprise_eval.jsonl"
        dataset_path.write_text(
            '{"id":"case_001","question":"What did runtime observe?","expected_answer":"answer",'
            '"expected_doc_ids":["doc_runtime"],"question_type":"simple_retrieval","complexity":"low"}\n',
            encoding="utf-8",
        )
        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(
            '{"case_count":1,"external_documents_required":false,"documents":[],"corpus_snapshot_ref":"snapshot_v1"}',
            encoding="utf-8",
        )
        return {
            "dataset_path": str(dataset_path),
            "manifest_path": str(manifest_path),
            "case_count": 1,
            "external_documents_required": False,
        }

    monkeypatch.setattr(
        "tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark.prepare_public_enterprise_eval",
        fake_prepare_public_enterprise_eval,
    )

    deps = _full_deps()
    deps = CanonicalRuntimeDependencies(
        knowledge_runtime=EvidenceBindingKnowledgePort(_standard_runtime_evidence_binding(case_id="case_001")),
        index_runtime=deps.index_runtime,
        security_gate=deps.security_gate,
        agent_run_runtime=deps.agent_run_runtime,
        trace_adapter=deps.trace_adapter,
        result_store=deps.result_store,
        artifact_store=deps.artifact_store,
        usage_receipt_provider=deps.usage_receipt_provider,
        budget_settlement_provider=deps.budget_settlement_provider,
    )

    result = asyncio.run(
        run_enterprise_rag_paired_benchmark(
            questions_file=q_file,
            output_root=out_dir,
            runtime_mode="canonical",
            canonical_deps=deps,
            sample_size=1,
            allow_blocked=True,
        )
    )

    metrics = json.loads((out_dir / "metrics.json").read_text(encoding="utf-8"))
    assert result["status"] == "blocked"
    assert metrics["measurement_status"] == "blocked_not_measured"
    assert metrics["profiles"]["standard_rag"]["measurement_state"] == "RUNTIME_OBSERVED"
    assert metrics["profiles"]["standard_rag"]["runtime_status"] == "completed"
    assert metrics["profiles"]["standard_rag"]["measured"] is False
    attestation = metrics["profiles"]["standard_rag"]["product_runtime_attestation"]
    assert attestation["profile_name"] == "standard_rag"
    assert attestation["runtime_name"] == "canonical-standard-runtime"
    assert attestation["runtime_version"] == "rt-1.0"
    assert attestation["corpus_snapshot_ref"] == "snapshot_v1"
    assert attestation["security_epoch"] == "epoch_2026"
    assert attestation["attestation_hash"] == compute_product_runtime_attestation_hash(attestation)

    preflight_payload = {
        "eval_run_id": "canonical_preflight",
        "case_set_ref": "case-set-runtime-observed",
        "dataset_version": "dataset-v1",
        "dataset_hash": "0" * 64,
        "candidate_count": 1,
        "reviewer_status": "approved",
        "benchmark_eligible": True,
        "license_status": "verified",
        "integrity_status": "verified",
        "runtime_request_schema_gold_free": True,
        "authorization_ref": "auth-ref-001",
        "security_epoch": "epoch_2026",
        "security_epoch_stale": False,
        "formal_execution_approved": True,
        "human_budget_approved": True,
        "budget_policy_ref": "budget-policy-standard",
        "provider_cost_limit": 100.0,
        "token_limit": 1_000_000,
        "deadline": "2026-12-31T23:59:59Z",
        "credential_ref": "vault://preflight/credentials",
        "has_formal_credentials": True,
        "formal_execution_requested": True,
        "output_artifact_ref": "s3://zuno-preflight/eval-run-2026-08-01.json",
        "profiles": [
            {
                "profile_name": name,
                "case_set_ref": "case-set-runtime-observed",
                "dataset_version": "dataset-v1",
                "corpus_snapshot_ref": "snapshot_v1",
                "security_epoch": "epoch_2026",
                "budget_policy_ref": "budget-policy-standard",
                "runtime_name": (
                    "canonical-standard-runtime"
                    if name == "standard_rag"
                    else f"{name}-runtime"
                ),
                "runtime_version": "rt-1.0" if name == "standard_rag" else "1.0.0",
                "product_runtime_attested": name == "standard_rag",
                "product_runtime_attestation": (
                    attestation if name == "standard_rag" else None
                ),
                "formal_adapter_wired": True,
                "knowledge_runtime_available": True,
                "index_runtime_available": True,
                "agent_run_runtime_available": True,
                "trace_adapter_available": True,
                "result_store_available": True,
                "artifact_store_available": True,
                "usage_receipt_provider_available": True,
                "budget_settlement_provider_available": True,
            }
            for name in REQUIRED_MEASURED_PROFILES
        ],
    }
    report = BenchmarkPreflightEvaluator().evaluate(preflight_payload)
    standard_profile = next(
        profile for profile in report.profile_results if profile.profile_name == "standard_rag"
    )
    assert "product_runtime_attestation_hash_mismatch" not in standard_profile.gap_codes


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


def test_09b_factory_uses_formal_deep_and_agentic_adapters_for_canonical_mode() -> None:
    """Deep and Agentic adapters must be on the default canonical factory path."""
    deps = _full_deps()
    factory = CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=deps)

    deep_runner = factory.create_runner("deep_graphrag")
    agentic_runner = factory.create_runner("agentic_graphrag")

    assert isinstance(deep_runner, DeepGraphRAGCanonicalAdapter)
    assert not isinstance(deep_runner, CanonicalDeepGraphRAGRunner)
    assert isinstance(agentic_runner, AgenticGraphRAGCanonicalAdapter)
    assert not isinstance(agentic_runner, CanonicalAgenticGraphRAGRunner)


def test_09c_factory_uses_formal_standard_and_local_adapters_for_canonical_mode() -> None:
    """Standard and Local adapters must be on the default canonical factory path."""
    deps = _full_deps()
    factory = CanonicalProfileRuntimeFactory(runtime_mode="canonical", canonical_deps=deps)

    standard_runner = factory.create_runner("standard_rag")
    local_runner = factory.create_runner("local_graphrag")

    assert standard_runner.__class__.__name__ == "StandardRAGCanonicalAdapter"
    assert not isinstance(standard_runner, CanonicalStandardRAGRunner)
    assert local_runner.__class__.__name__ == "LocalGraphRAGCanonicalAdapter"
    assert not isinstance(local_runner, CanonicalLocalGraphRAGRunner)


def test_09d_standard_adapter_validates_runtime_evidence_binding_to_observed_not_measured() -> None:
    """A VALID binding may become RUNTIME_OBSERVED but must not become MEASURED."""
    deps = _full_deps()
    deps = CanonicalRuntimeDependencies(
        knowledge_runtime=EvidenceBindingKnowledgePort(_standard_runtime_evidence_binding()),
        index_runtime=deps.index_runtime,
        security_gate=deps.security_gate,
        agent_run_runtime=deps.agent_run_runtime,
        trace_adapter=deps.trace_adapter,
        result_store=deps.result_store,
        artifact_store=deps.artifact_store,
        usage_receipt_provider=deps.usage_receipt_provider,
        budget_settlement_provider=deps.budget_settlement_provider,
    )
    result = StandardRAGCanonicalAdapter(deps).run_canonical_case(_sample_input("standard_rag"))

    assert result.runtime_status == "completed"
    assert result.measurement_state == MeasurementState.RUNTIME_OBSERVED
    assert result.failure_class == ""
    assert result.blocked_reason.startswith("runtime_observed_pending_formal_gates:")
    assert result.trace_id == "trace-1"
    assert result.budget_settlement_ref == "budget-1"
    assert result.artifact_receipt_ref == "artifact-1"
    assert result.run_outcome_ref == ""
    assert result.is_test_double is False


def test_09e_standard_adapter_invalid_runtime_evidence_binding_fails_closed() -> None:
    """A tampered binding must stay BLOCKED and expose fixed validation gap codes."""
    binding = _standard_runtime_evidence_binding(reference_binding_hash="1" * 64)
    deps = _full_deps()
    deps = CanonicalRuntimeDependencies(
        knowledge_runtime=EvidenceBindingKnowledgePort(binding),
        index_runtime=deps.index_runtime,
        security_gate=deps.security_gate,
        agent_run_runtime=deps.agent_run_runtime,
        trace_adapter=deps.trace_adapter,
        result_store=deps.result_store,
        artifact_store=deps.artifact_store,
        usage_receipt_provider=deps.usage_receipt_provider,
        budget_settlement_provider=deps.budget_settlement_provider,
    )
    result = StandardRAGCanonicalAdapter(deps).run_canonical_case(_sample_input("standard_rag"))

    assert result.runtime_status == "blocked"
    assert result.measurement_state == MeasurementState.BLOCKED
    assert result.failure_class == "runtime_evidence_binding_blocked"
    assert "reference_binding_hash_mismatch" in result.dependency_gaps
    assert result.trace_id is None


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
        actual_profile="agentic_graphrag",
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
        actual_profile="agentic_graphrag",
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
        actual_profile="agentic_graphrag",
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
        actual_profile="agentic_graphrag",
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


def test_21b_standard_rag_does_not_require_agent_run_outcome_for_rule6() -> None:
    """Standard RAG follows runtime_evidence_binding: run_outcome is agentic-only."""
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        requested_profile="standard_rag",
        actual_profile="standard_rag",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        budget_settlement_valid=True,
        artifact_receipt_ref="art_001",
        artifact_receipt_valid=True,
        run_outcome_ref="",
        run_outcome_valid=False,
        reviewer_status="pending",
        benchmark_eligible=False,
        has_formal_credentials=False,
        formal_execution_requested=False,
    )
    assert state == MeasurementState.RUNTIME_OBSERVED
    assert "runtime_evidence_incomplete" not in reason
    assert "reviewer_pending" in reason


def test_21c_formal_credential_bools_without_attestation_cannot_reach_measured() -> None:
    gate = MeasurementTruthGate()
    state, reason = gate.evaluate(
        is_test_double=False,
        runtime_status="completed",
        requested_profile="standard_rag",
        actual_profile="standard_rag",
        snapshot_ref="snap_v1",
        trace_id="trace_001",
        budget_settlement_ref="budget_001",
        budget_settlement_valid=True,
        artifact_receipt_ref="art_001",
        artifact_receipt_valid=True,
        reviewer_status="approved",
        benchmark_eligible=True,
        has_formal_credentials=True,
        formal_execution_requested=True,
    )
    assert state == MeasurementState.RUNTIME_OBSERVED
    assert "formal_credential_attestation_missing" in reason


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

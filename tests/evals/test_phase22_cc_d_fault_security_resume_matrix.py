"""Dependency-free tests for PHASE22 CC-D fault / security / resume matrix.

These tests never depend on DeepSeek CC-B snapshot_id or CC-C profile_run_ids.
They assert the structural contract documented in the CC-D task card:

* All required fields are present for every matrix row.
* All rows are ``NOT_RUN_DEPENDENCY_BLOCKED`` while the dependency hand-off
  has not landed.
* No row carries a forged ``receipt_ref`` or ``trace_ref``.
* Secret / credential redaction works.
* Environment probe never claims write/read verified.
* Evidence bundle matches the matrix structurally.
* Verifier rejects attempts to flip BLOCKED to PASSED or to fake receipts.

These tests fail loudly if anyone tries to ship a fake PASSED row before
the DeepSeek runtime delivers the receipts.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evals.zuno.synthetic_benchmark.phase22_cc_d_fault_matrix import (  # noqa: E402
    REQUIRED_CASE_FIELDS,
    cases,
    iter_problems,
    load_matrix,
    matrix_sha256,
    matrix_status,
    summarise,
)


MATRIX_PATH = (
    REPO_ROOT
    / "tools"
    / "evals"
    / "zuno"
    / "synthetic_benchmark"
    / "phase22_cc_d_fault_matrix.yaml"
)
EVIDENCE_DIR = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "goal05-phase22-machine-attested-synthetic-regression"
    / "minimax2-cc-d"
)


REQUIRED_CASE_FIELDS = REQUIRED_CASE_FIELDS


def _matrix():
    return load_matrix(MATRIX_PATH)


def test_matrix_status_is_honest_dependency_blocked() -> None:
    matrix = _matrix()
    assert matrix_status(matrix) == "NOT_RUN_DEPENDENCY_BLOCKED", (
        "matrix_status must stay NOT_RUN_DEPENDENCY_BLOCKED while DeepSeek "
        "CC-B snapshot_id and CC-C profile_run_ids are absent"
    )


def test_matrix_dependency_placeholders_are_placeholders() -> None:
    matrix = _matrix()
    assert matrix.get("snapshot_id") is None
    assert matrix.get("profile_run_ids") in (None, [], ())
    assert matrix.get("dependency_head_sha") == "NOT_RUN_DEPENDENCY_BLOCKED"


def test_matrix_has_all_required_case_fields() -> None:
    matrix = _matrix()
    problems = list(iter_problems(matrix))
    assert problems == [], f"matrix has structural problems: {problems}"


def test_matrix_has_unique_case_ids() -> None:
    matrix = _matrix()
    ids = [str(c.get("case_id")) for c in cases(matrix)]
    assert len(ids) == len(set(ids)), f"duplicate case_ids: {ids}"


def test_matrix_covers_minimum_required_cases() -> None:
    matrix = _matrix()
    expected = {
        "D-MINIO-UNREACHABLE",
        "D-POSTGRES-UNREACHABLE",
        "D-RABBITMQ-DUPLICATE-MESSAGE",
        "D-ELASTICSEARCH-PARTIAL-SUCCESS",
        "D-MILVUS-WRITE-FAILURE",
        "D-NEO4J-READBACK-MISMATCH",
        "D-EMBEDDING-CREDENTIAL-MISSING",
        "D-INDEX-WORKER-CRASH",
        "D-SNAPSHOT-EXIT-BEFORE-ACTIVATION",
        "D-DUPLICATE-INGEST",
        "D-TENANT-CROSS-VIOLATION",
        "D-WORKSPACE-CROSS-VIOLATION",
        "D-SECURITY-EPOCH-EXPIRED",
        "D-CANCEL",
        "D-DEADLINE",
        "D-RESUME",
        "D-UNKNOWN-SIDE-EFFECT",
        "D-RETRY-EXHAUSTED",
        "D-REPLAN-BARRIER",
        "D-PARALLEL-PARTIAL-FAILURE",
        "D-CITATION-CONFLICT",
        "D-EVIDENCE-INSUFFICIENT-ABSTAIN",
    }
    actual = {str(c.get("case_id")) for c in cases(matrix)}
    missing = expected - actual
    assert not missing, f"matrix missing required cases: {sorted(missing)}"


def test_matrix_rows_carry_no_receipts_or_traces() -> None:
    matrix = _matrix()
    for case in cases(matrix):
        assert case.get("receipt_ref") is None, (
            f"{case.get('case_id')} must not carry receipt_ref while matrix is blocked"
        )
        assert case.get("trace_ref") is None, (
            f"{case.get('case_id')} must not carry trace_ref while matrix is blocked"
        )


def test_required_case_fields_set_matches_task_card() -> None:
    matrix = _matrix()
    declared = set(matrix.get("required_fields", []))
    expected = {
        "case_id",
        "trigger",
        "state_before",
        "state_after",
        "owner",
        "failure_class",
        "propagation",
        "retryability",
        "recovery",
        "idempotency_key",
        "receipt_ref",
        "trace_ref",
        "test_command",
        "exit_code",
        "cleanup",
        "status",
        "not_run_reason",
    }
    assert declared == expected, f"required_fields mismatch: {declared ^ expected}"


def test_matrix_summary_reports_all_rows_blocked() -> None:
    matrix = _matrix()
    summary = summarise(matrix)
    assert summary["case_count"] == 22
    assert summary["status_counts"].get("PASSED", 0) == 0
    assert summary["status_counts"].get("NOT_RUN_DEPENDENCY_BLOCKED", 0) == 22


def test_matrix_sha256_is_stable() -> None:
    matrix = _matrix()
    first = matrix_sha256(matrix)
    second = matrix_sha256(matrix)
    assert first == second
    assert re.fullmatch(r"[0-9a-f]{64}", first)


@pytest.mark.parametrize(
    "forbidden_owner",
    [
        "knowledge_ingestion",
        "object_store",
        "postgres_domain",
        "knowledge_index",
        "snapshot_activation",
        "observability",
        "gold_isolation",
        "release_decision",
        "fault_recovery",
        "security_isolation",
        "runtime_resume",
        "evidence_reproducibility",
    ],
)
def test_matrix_declares_owner_namespace(forbidden_owner: str) -> None:
    matrix = _matrix()
    owners = matrix.get("owners", {})
    assert forbidden_owner in owners, f"owners namespace missing {forbidden_owner}"


def test_environment_probe_artifact_does_not_claim_write_read() -> None:
    probe_path = EVIDENCE_DIR / "environment_probe.json"
    if not probe_path.exists():
        pytest.skip("environment_probe.json has not been generated yet")
    payload = json.loads(probe_path.read_text(encoding="utf-8"))
    for service in payload.get("services", []):
        assert service.get("service_write_read_verified") is False, (
            f"probe must not claim write/read verified for {service.get('id')}"
        )


def test_environment_probe_artifact_has_no_secrets() -> None:
    probe_path = EVIDENCE_DIR / "environment_probe.json"
    if not probe_path.exists():
        pytest.skip("environment_probe.json has not been generated yet")
    text = probe_path.read_text(encoding="utf-8")
    for pattern in (
        r"(?i)postgres:postgres@",
        r"(?i)neo4j/neo4j12345",
        r"(?i)minioadmin:minioadmin",
        r"(?i)guest:guest@",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    ):
        assert not re.search(pattern, text), f"secret pattern leaked: {pattern}"


def test_evidence_bundle_artifact_matches_matrix() -> None:
    bundle_path = EVIDENCE_DIR / "evidence_bundle.json"
    if not bundle_path.exists():
        pytest.skip("evidence_bundle.json has not been generated yet")
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    matrix = _matrix()
    assert bundle["matrix_status"] == matrix.get("matrix_status")
    assert bundle["case_count"] == len(cases(matrix))
    assert bundle["snapshot_id"] is None
    assert bundle["profile_run_ids"] in (None, [], ())
    for run in bundle.get("case_runs", []):
        assert run["status"] != "PASSED", (
            f"case {run['case_id']} marked PASSED while matrix is blocked"
        )


def test_evidence_bundle_records_no_secrets() -> None:
    bundle_path = EVIDENCE_DIR / "evidence_bundle.json"
    if not bundle_path.exists():
        pytest.skip("evidence_bundle.json has not been generated yet")
    text = bundle_path.read_text(encoding="utf-8")
    for pattern in (
        r"(?i)postgres:postgres@",
        r"(?i)neo4j/neo4j12345",
        r"(?i)minioadmin:minioadmin",
        r"(?i)guest:guest@",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"(?i)api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]{16,}",
        r"(?i)bearer\s+[A-Za-z0-9_\-\.]{16,}",
    ):
        assert not re.search(pattern, text), f"secret pattern leaked: {pattern}"


def test_evidence_builder_refuses_secret_like_inputs(tmp_path: Path) -> None:
    """The builder must abort if anyone tries to feed it a fake-secret payload."""

    from tools.scripts.phase22_evidence_builder import SECRET_PATTERNS, write_bundle

    bad = {
        "schema_version": "1.0.0",
        "case_count": 0,
        "case_runs": [],
        "service_url": "postgres:postgres@localhost:5432/zuno",
    }
    payload = json.dumps(bad, ensure_ascii=False)
    leaks = [p.pattern for p in SECRET_PATTERNS if p.search(payload)]
    assert leaks, "expected the synthetic secret to be detected"
    with pytest.raises(RuntimeError):
        write_bundle(bad, tmp_path / "leak.json")


def test_fault_matrix_runner_records_without_subprocess(tmp_path: Path) -> None:
    """The runner must record per-case state without invoking subprocesses
    while matrix_status is NOT_RUN_DEPENDENCY_BLOCKED (no fan-out, no live
    runtime attempts)."""

    from tools.scripts.phase22_fault_matrix_runner import run_case

    matrix = _matrix()
    first_case = cases(matrix)[0]
    record = run_case(first_case)
    assert record["status"] == "NOT_RUN_DEPENDENCY_BLOCKED"
    assert record["execution"]["launched"] is False
    assert record["execution"]["would_run"] == first_case["test_command"]
    assert record["execution"]["exit_code"] is None


def test_fault_matrix_record_helper_does_not_execute() -> None:
    """Internal helper used by the evidence builder must not launch anything."""

    from tools.scripts.phase22_evidence_builder import _record_matrix_case

    matrix = _matrix()
    record = _record_matrix_case(cases(matrix)[0])
    assert record["execution"]["launched"] is False
    assert record["execution"]["exit_code"] is None
    assert record["execution"]["status"] == "NOT_RUN_DEPENDENCY_BLOCKED"
    assert record["execution"]["not_run_reason"].startswith(
        "test_command recorded but not executed"
    )


def test_required_case_fields_constant_is_complete() -> None:
    expected = {
        "case_id",
        "trigger",
        "state_before",
        "state_after",
        "owner",
        "failure_class",
        "propagation",
        "retryability",
        "recovery",
        "idempotency_key",
        "receipt_ref",
        "trace_ref",
        "test_command",
        "exit_code",
        "cleanup",
        "status",
        "not_run_reason",
    }
    assert set(REQUIRED_CASE_FIELDS) == expected


def test_unrun_record_carries_null_exit_code_and_reason() -> None:
    """Every unrun record must carry exit_code=null, status=NOT_RUN_DEPENDENCY_BLOCKED,
    and an explicit not_run_reason."""

    from tools.scripts.phase22_evidence_builder import _record_matrix_case

    matrix = _matrix()
    for case in cases(matrix):
        record = _record_matrix_case(case)
        execution = record["execution"]
        assert execution["launched"] is False
        assert execution["exit_code"] is None
        assert execution["status"] == "NOT_RUN_DEPENDENCY_BLOCKED"
        assert execution["not_run_reason"], (
            f"case {case.get('case_id')} missing not_run_reason"
        )
        assert execution["started_at"] is None
        assert execution["ended_at"] is None
        assert execution["elapsed_seconds"] is None
        assert execution["stdout"] is None
        assert execution["stderr"] is None
        assert execution["would_run"] == case["test_command"]


def test_matrix_loader_returns_expected_keys() -> None:
    matrix = _matrix()
    for key in (
        "schema_version",
        "goal_id",
        "worker_task_id",
        "matrix_owner",
        "matrix_status",
        "dependency_pr",
        "dependency_head_sha",
        "snapshot_id",
        "profile_run_ids",
        "required_fields",
        "owners",
        "cases",
    ):
        assert key in matrix, f"missing top-level matrix key: {key}"
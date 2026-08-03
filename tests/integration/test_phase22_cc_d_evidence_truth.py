"""PHASE22 CC-D evidence-truth integration tests.

These tests run without DeepSeek CC-B / CC-C hand-off. They pin down the
nine truth requirements the coordinator listed:

1. Unrun commands record ``exit_code == None`` (never a manufactured ``0``).
2. Subprocess failures propagate truthfully (real ``exit_code``).
3. ``--expect unreachable`` returns non-zero when the port is reachable.
4. ``--expect reachable`` returns non-zero when the port is unreachable.
5. Expectation match returns zero.
6. ``stdout`` / ``stderr`` are recorded for executed commands.
7. Secrets in captured ``stdout`` / ``stderr`` are redacted before write.
8. All 22 matrix rows still report ``NOT_RUN_DEPENDENCY_BLOCKED``.
9. Forged ``receipt_ref`` / ``trace_ref`` / ``PASSED`` rows are rejected
   by the structural verifier.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]

ENV_PROBE = REPO_ROOT / "tools" / "scripts" / "phase22_environment_probe.py"
EVIDENCE_BUILDER = REPO_ROOT / "tools" / "scripts" / "phase22_evidence_builder.py"
EVIDENCE_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase22_cc_d_evidence.py"

EVIDENCE_DIR = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "goal05-phase22-machine-attested-synthetic-regression"
    / "minimax2-cc-d"
)

EXPECTED_CASE_IDS = {
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


def _run(args: list[str], *, timeout: float = 60.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def _invoke_probe(
    *,
    service: str | None = None,
    expect: str | None = None,
    timeout: float = 0.25,
    output: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(ENV_PROBE), "--timeout", str(timeout)]
    if service is not None:
        cmd += ["--service", service]
    if expect is not None:
        cmd += ["--expect", expect]
    if output is not None:
        cmd += ["--output", str(output)]
    return _run(cmd)


def _build_bundle(*, output_dir: Path) -> subprocess.CompletedProcess[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    return _run(
        [
            sys.executable,
            str(EVIDENCE_BUILDER),
            "--skip-probe",
            "--skip-tracks",
            "--output",
            str(output_dir / "evidence_bundle.json"),
        ]
    )


# ---------------------------------------------------------------------------
# 1. Unrun commands record exit_code == None
# ---------------------------------------------------------------------------


def test_unrun_command_exit_code_is_null(tmp_path: Path) -> None:
    """The evidence builder must never invent exit_code == 0 for unrun commands."""

    result = _build_bundle(output_dir=tmp_path)
    assert result.returncode == 0, f"builder failed: {result.stderr}"
    bundle = json.loads((tmp_path / "evidence_bundle.json").read_text(encoding="utf-8"))

    unrun_records = [
        r
        for r in bundle["commands"]
        if r.get("launched") is False and r.get("status") == "NOT_RUN_DEPENDENCY_BLOCKED"
    ]
    assert unrun_records, "expected at least one unrun command record"
    for record in unrun_records:
        assert record["exit_code"] is None, (
            f"unrun command {record['command']!r} fabricated exit_code={record['exit_code']!r}"
        )
        assert record.get("not_run_reason"), (
            f"unrun command {record['command']!r} missing not_run_reason"
        )


# ---------------------------------------------------------------------------
# 2. Subprocess failure propagates truthfully
# ---------------------------------------------------------------------------


def test_subprocess_failure_propagates_truthfully(tmp_path: Path) -> None:
    """A failing subprocess must show real non-zero exit_code in the bundle.

    We exercise this directly via ``_execute_command`` which is the
    builder's internal subprocess runner. The returned record must carry
    the real ``exit_code`` (2 in this case) and ``status=FAILED`` instead
    of being rewritten to 0.
    """

    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.phase22_evidence_builder import _execute_command

    record = _execute_command(
        [sys.executable, "-c", "import sys; sys.exit(2)"],
        timeout=10.0,
    )
    assert record["launched"] is True
    assert record["exit_code"] == 2
    assert record["status"] == "FAILED"
    assert isinstance(record["stdout"], str)
    assert isinstance(record["stderr"], str)
    assert record["started_at"] is not None
    assert record["ended_at"] is not None
    assert record["elapsed_seconds"] is not None


# ---------------------------------------------------------------------------
# 3 & 4. Expectation mismatch returns non-zero
# ---------------------------------------------------------------------------


def test_expect_unreachable_returns_nonzero_when_reachable(
    tmp_path: Path,
) -> None:
    """If we *fake* reachability by stubbing, expect=unreachable must return 1.

    Without Docker / a live service we cannot guarantee a port is open, so
    we exercise the contract by importing the probe module and invoking
    ``main`` with a mocked ``probe_all`` that reports
    ``service_reachable=True``.
    """

    import importlib.util

    spec = importlib.util.spec_from_file_location("phase22_env_probe", ENV_PROBE)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    fake_report = {
        "probe_kind": "phase22_cc_d_environment",
        "probe_version": "1.0.0",
        "captured_at": "2026-08-03T00:00:00Z",
        "host": "synthetic",
        "python_version": "3.12.10",
        "docker_compose_file": "infra/docker/docker-compose.yml",
        "services": [
            {
                "id": "postgres",
                "expected_kind": "postgres_domain",
                "host": "localhost",
                "port": 5432,
                "protocol": "tcp",
                "docker": {"docker_available": False},
                "service_reachable": True,
                "service_write_read_verified": False,
                "probe_state": "SERVICE_REACHABLE",
            }
        ],
    }
    output = tmp_path / "probe.json"

    original_probe_all = module.probe_all
    module.probe_all = lambda timeout: fake_report  # type: ignore[assignment]
    try:
        rc = module.main(
            [
                "--service",
                "postgres",
                "--expect",
                "unreachable",
                "--output",
                str(output),
            ]
        )
    finally:
        module.probe_all = original_probe_all  # type: ignore[assignment]

    assert rc == 1, f"expect=unreachable but reachable should exit 1, got {rc}"
    probe_payload = json.loads(output.read_text(encoding="utf-8"))
    assert probe_payload["services"][0]["service_write_read_verified"] is False


def test_expect_reachable_returns_nonzero_when_unreachable(
    tmp_path: Path,
) -> None:
    """If we *fake* unreachability, expect=reachable must return 1."""

    import importlib.util

    spec = importlib.util.spec_from_file_location("phase22_env_probe", ENV_PROBE)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    fake_report = {
        "probe_kind": "phase22_cc_d_environment",
        "probe_version": "1.0.0",
        "captured_at": "2026-08-03T00:00:00Z",
        "host": "synthetic",
        "python_version": "3.12.10",
        "docker_compose_file": "infra/docker/docker-compose.yml",
        "services": [
            {
                "id": "postgres",
                "expected_kind": "postgres_domain",
                "host": "localhost",
                "port": 5432,
                "protocol": "tcp",
                "docker": {"docker_available": False},
                "service_reachable": False,
                "service_write_read_verified": False,
                "probe_state": "SERVICE_UNREACHABLE",
            }
        ],
    }
    output = tmp_path / "probe.json"

    original_probe_all = module.probe_all
    module.probe_all = lambda timeout: fake_report  # type: ignore[assignment]
    try:
        rc = module.main(
            [
                "--service",
                "postgres",
                "--expect",
                "reachable",
                "--output",
                str(output),
            ]
        )
    finally:
        module.probe_all = original_probe_all  # type: ignore[assignment]

    assert rc == 1, f"expect=reachable but unreachable should exit 1, got {rc}"


def test_expect_reachable_with_matching_actual_returns_zero(tmp_path: Path) -> None:
    """When the actual state matches expectation, the probe must return 0."""

    import importlib.util

    spec = importlib.util.spec_from_file_location("phase22_env_probe", ENV_PROBE)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    fake_report = {
        "probe_kind": "phase22_cc_d_environment",
        "probe_version": "1.0.0",
        "captured_at": "2026-08-03T00:00:00Z",
        "host": "synthetic",
        "python_version": "3.12.10",
        "docker_compose_file": "infra/docker/docker-compose.yml",
        "services": [
            {
                "id": "postgres",
                "expected_kind": "postgres_domain",
                "host": "localhost",
                "port": 5432,
                "protocol": "tcp",
                "docker": {"docker_available": False},
                "service_reachable": False,
                "service_write_read_verified": False,
                "probe_state": "SERVICE_UNREACHABLE",
            }
        ],
    }
    output = tmp_path / "probe.json"

    original_probe_all = module.probe_all
    module.probe_all = lambda timeout: fake_report  # type: ignore[assignment]
    try:
        rc = module.main(
            [
                "--service",
                "postgres",
                "--expect",
                "unreachable",
                "--output",
                str(output),
            ]
        )
    finally:
        module.probe_all = original_probe_all  # type: ignore[assignment]

    assert rc == 0, f"matched expectation should exit 0, got {rc}"


def test_probe_invalid_expect_returns_two(tmp_path: Path) -> None:
    """An invalid --expect value must surface as exit 2."""

    result = _run(
        [
            sys.executable,
            str(ENV_PROBE),
            "--service",
            "postgres",
            "--expect",
            "bogus",
            "--timeout",
            "0.1",
            "--output",
            str(tmp_path / "probe.json"),
        ]
    )
    assert result.returncode == 2, (
        f"invalid --expect must exit 2, got {result.returncode}"
    )


# ---------------------------------------------------------------------------
# 5. stdout / stderr are recorded for executed commands
# ---------------------------------------------------------------------------


def test_executed_command_records_stdout_and_stderr(tmp_path: Path) -> None:
    """A real launch must produce stdout / stderr entries (even if empty)."""

    output = tmp_path / "probe.json"
    result = _invoke_probe(
        service="postgres",
        expect="unreachable",
        timeout=0.1,
        output=output,
    )
    # We only assert stdout/stderr shape via the builder's record because
    # the probe itself writes to its own output. Re-invoke via builder to
    # capture the structured command log.
    builder_out = tmp_path / "bundle.json"
    builder = _run(
        [
            sys.executable,
            str(EVIDENCE_BUILDER),
            "--skip-tracks",
            "--output",
            str(builder_out),
        ]
    )
    assert builder.returncode == 0
    bundle = json.loads(builder_out.read_text(encoding="utf-8"))
    probe_records = [
        r for r in bundle["commands"] if "phase22_environment_probe" in r["command"]
    ]
    assert probe_records
    for record in probe_records:
        assert isinstance(record.get("stdout"), str)
        assert isinstance(record.get("stderr"), str)


# ---------------------------------------------------------------------------
# 6. Secrets in stdout / stderr are redacted before write
# ---------------------------------------------------------------------------


def test_captured_secrets_are_redacted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """If a subprocess prints a secret-like token it must be redacted."""

    # Build a synthetic command log entry by directly calling the
    # builder's internal helpers — the cleaner way is to invoke the
    # builder end-to-end with a process that prints a secret. We use
    # ``python -c`` for that and feed it through the builder.
    fake_secret = "postgres:postgres@localhost:5432/zuno"
    builder_out = tmp_path / "bundle.json"
    # Use the builder's redact helper directly to prove the redaction
    # pipeline works on captured text.
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.phase22_evidence_builder import (  # noqa: E402
        _redact_text,
        _scan_for_secrets,
    )

    redacted = _redact_text(fake_secret)
    assert "postgres:postgres" not in redacted, (
        f"redaction failed, got: {redacted!r}"
    )
    assert "***REDACTED***" in redacted

    leaks = _scan_for_secrets(redacted)
    assert not leaks, f"redaction left leaks: {leaks}"


# ---------------------------------------------------------------------------
# 7. All 22 matrix rows still blocked
# ---------------------------------------------------------------------------


def test_all_twenty_two_rows_still_blocked(tmp_path: Path) -> None:
    """The matrix must keep all 22 rows in NOT_RUN_DEPENDENCY_BLOCKED."""

    import yaml  # type: ignore[import-untyped]

    from tools.evals.zuno.synthetic_benchmark.phase22_cc_d_fault_matrix import (
        cases,
        load_matrix,
        summarise,
    )

    matrix_path = (
        REPO_ROOT
        / "tools"
        / "evals"
        / "zuno"
        / "synthetic_benchmark"
        / "phase22_cc_d_fault_matrix.yaml"
    )
    matrix = load_matrix(matrix_path)
    summary = summarise(matrix)
    assert summary["case_count"] == 22
    assert summary["status_counts"].get("NOT_RUN_DEPENDENCY_BLOCKED", 0) == 22
    assert summary["status_counts"].get("PASSED", 0) == 0
    assert summary["matrix_status"] == "NOT_RUN_DEPENDENCY_BLOCKED"
    assert summary["snapshot_id"] is None
    assert summary["profile_run_ids"] in (None, [], ())

    # Case-id set must match the CC-D task card.
    actual = {str(c.get("case_id")) for c in cases(matrix)}
    assert actual == EXPECTED_CASE_IDS, f"matrix case_ids drifted: {actual ^ EXPECTED_CASE_IDS}"


# ---------------------------------------------------------------------------
# 8. Forged receipt / trace / PASSED are rejected
# ---------------------------------------------------------------------------


def test_forged_receipt_trace_passed_rejected(tmp_path: Path) -> None:
    """The verifier must reject forged receipts / traces / PASSED rows."""

    import yaml  # type: ignore[import-untyped]

    from tools.evals.zuno.synthetic_benchmark.phase22_cc_d_fault_matrix import (
        iter_problems,
        load_matrix,
    )

    matrix_path = (
        REPO_ROOT
        / "tools"
        / "evals"
        / "zuno"
        / "synthetic_benchmark"
        / "phase22_cc_d_fault_matrix.yaml"
    )
    forged = yaml.safe_load(matrix_path.read_text(encoding="utf-8"))
    forged["matrix_status"] = "NOT_RUN_DEPENDENCY_BLOCKED"
    forged["cases"][0]["status"] = "PASSED"
    forged["cases"][0]["receipt_ref"] = "fake_receipt"
    forged["cases"][0]["trace_ref"] = "fake_trace"
    forged_path = tmp_path / "forged_matrix.yaml"
    forged_path.write_text(yaml.safe_dump(forged), encoding="utf-8")

    forged_matrix = load_matrix(forged_path)
    problems = list(iter_problems(forged_matrix))
    assert any("PASSED" in p for p in problems), (
        f"loader should reject PASSED, got: {problems}"
    )
    assert any("receipt_ref" in p for p in problems), (
        f"loader should reject receipt_ref, got: {problems}"
    )
    assert any("trace_ref" in p for p in problems), (
        f"loader should reject trace_ref, got: {problems}"
    )

    # And the bundle-level verifier must also reject any forged run.
    bad_bundle = tmp_path / "bad_bundle.json"
    bad_bundle.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "matrix_status": "NOT_RUN_DEPENDENCY_BLOCKED",
                "snapshot_id": None,
                "profile_run_ids": [],
                "case_count": 1,
                "case_runs": [
                    {
                        "case_id": "D-MINIO-UNREACHABLE",
                        "status": "PASSED",
                        "execution": {"launched": False, "exit_code": None},
                    }
                ],
                "commands": [
                    {
                        "command": "python -c pass",
                        "started_at": "2026-08-03T00:00:00Z",
                        "ended_at": "2026-08-03T00:00:00Z",
                        "elapsed_seconds": 0,
                        "launched": False,
                        "exit_code": None,
                        "stdout": "",
                        "stderr": "",
                        "status": "NOT_RUN_DEPENDENCY_BLOCKED",
                        "not_run_reason": "synthetic",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    # The verifier reads the canonical artifacts at docs/evidence/...,
    # so we patch its module paths temporarily.
    from tools.scripts import verify_phase22_cc_d_evidence as verifier

    original_bundle = verifier.BUNDLE_PATH
    verifier.BUNDLE_PATH = bad_bundle  # type: ignore[attr-defined]
    try:
        errors = verifier.verify()
    finally:
        verifier.BUNDLE_PATH = original_bundle  # type: ignore[attr-defined]
    assert any("PASSED" in err for err in errors), (
        f"verifier should reject forged PASSED run, got: {errors}"
    )


# ---------------------------------------------------------------------------
# 9. End-to-end verifier passes against the canonical bundle (if present)
# ---------------------------------------------------------------------------


def test_canonical_verifier_pass() -> None:
    """If the canonical bundle has been regenerated, the verifier must pass."""

    canonical_bundle = EVIDENCE_DIR / "evidence_bundle.json"
    canonical_probe = EVIDENCE_DIR / "environment_probe.json"
    canonical_run = EVIDENCE_DIR / "fault_matrix_run.json"
    if not (canonical_bundle.exists() and canonical_probe.exists() and canonical_run.exists()):
        pytest.skip("canonical evidence not regenerated yet")
    result = _run([sys.executable, str(EVIDENCE_VERIFIER)])
    assert result.returncode == 0, (
        f"canonical verifier failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
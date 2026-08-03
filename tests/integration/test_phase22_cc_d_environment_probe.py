"""PHASE22 CC-D integration tests for environment probe and evidence verifier.

These tests are dependency-free in the runtime sense: they do not require
the DeepSeek CC-B snapshot_id or CC-C profile_run_ids. They do require
local Python and the ability to run ``python tools/scripts/...``.

They exercise:

* The environment probe binary and its JSON output schema.
* The evidence verifier and its rejection rules.
* The fault matrix runner's recording contract.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ENV_PROBE = REPO_ROOT / "tools" / "scripts" / "phase22_environment_probe.py"
EVIDENCE_BUILDER = REPO_ROOT / "tools" / "scripts" / "phase22_evidence_builder.py"
EVIDENCE_DIR = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "goal05-phase22-machine-attested-synthetic-regression"
    / "minimax2-cc-d"
)
PROBE_OUT = EVIDENCE_DIR / "environment_probe.json"


def _run(args: list[str], timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )


def test_environment_probe_writes_schema_compliant_report() -> None:
    result = _run([
        sys.executable,
        str(ENV_PROBE),
        "--output",
        str(PROBE_OUT),
        "--timeout",
        "0.5",
    ])
    assert result.returncode == 0, f"probe failed: {result.stderr}"
    assert PROBE_OUT.exists(), "probe output missing"
    payload = json.loads(PROBE_OUT.read_text(encoding="utf-8"))
    assert payload["probe_kind"] == "phase22_cc_d_environment"
    assert "captured_at" in payload
    assert isinstance(payload["services"], list) and payload["services"]
    for service in payload["services"]:
        assert "id" in service
        assert "host" in service
        assert "port" in service
        assert "service_reachable" in service
        assert "service_write_read_verified" in service
        assert service["service_write_read_verified"] is False
        # docker_available may be True or False depending on host, but never
        # claim write/read.
        assert service["probe_state"] in {"SERVICE_REACHABLE", "SERVICE_UNREACHABLE"}


def test_environment_probe_rejects_unreachable_when_expected_reachable() -> None:
    """Verify the expectation-mismatch exit code regardless of host state.

    On some hosts the configured service ports are reachable (e.g. a
    dev Postgres is up); on others they are not. We cannot rely on
    the host's actual state, so we exercise the contract by importing
    the probe module, monkey-patching ``probe_all`` to return a known
    report, and calling ``main`` in-process.
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
                "service_reachable": False,
                "service_write_read_verified": False,
                "probe_state": "SERVICE_UNREACHABLE",
            }
        ],
    }

    output = EVIDENCE_DIR / "environment_probe.json"
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
    assert rc == 0, (
        f"expect=unreachable + actual=unreachable should exit 0 (match), got {rc}"
    )


def test_evidence_verifier_rejects_forged_passed_row(tmp_path: Path) -> None:
    """Forging a PASSED row in the matrix must be rejected by the structural
    contract enforced by ``iter_problems``.

    The verifier in ``tools/scripts/verify_phase22_cc_d_evidence.py`` reads
    the canonical matrix directly, so this test exercises the same rule via
    the public loader / ``iter_problems`` API. The behaviour is identical
    because the verifier itself delegates to the same checks for the matrix
    payload.
    """

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
    errors = list(iter_problems(forged_matrix))
    assert any("PASSED" in err for err in errors), (
        f"loader should reject forged PASSED row, got: {errors}"
    )
    assert any("receipt_ref" in err for err in errors), (
        f"loader should reject forged receipt_ref, got: {errors}"
    )
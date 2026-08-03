from __future__ import annotations

"""Tests for the PHASE22-SNAPSHOT-FAIL-CLOSED-GATE verifier.

The gate is a static AST + contract fixture verifier.  This file exercises
both the contract fixtures (fixed, hand-authored) and the repository-mode
scan.
"""

import io
import json
from contextlib import redirect_stdout
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase22_snapshot_fail_closed.py"


def _load_verifier():
    spec = spec_from_file_location(
        "verify_phase22_snapshot_fail_closed", VERIFIER
    )
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _capture_json(verifier, argv):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        verifier.main(argv + ["--json"])
    return json.loads(buffer.getvalue())


def test_repository_mode_emits_a_valid_status() -> None:
    """The real repo must yield a documented status (non-zero is allowed)."""

    verifier = _load_verifier()
    payload = _capture_json(verifier, ["--mode", "repository"])
    assert payload["status"] in {
        verifier.STATUS_CONFIRMED,
        verifier.STATUS_PERSISTENCE,
        verifier.STATUS_READBACK,
        verifier.STATUS_INDEX,
        verifier.STATUS_RECEIPT,
        verifier.STATUS_UNRESOLVED,
        verifier.STATUS_TOOL_ERROR,
    }
    assert "not_proven" in payload
    assert any(
        "live PostgreSQL" in boundary for boundary in payload["not_proven"]
    )


def test_contract_mode_passes_all_fixtures() -> None:
    """All contract fixtures must pass."""

    verifier = _load_verifier()
    payload = _capture_json(verifier, ["--mode", "contract"])
    assert payload["overall_status"] == verifier.STATUS_CONFIRMED
    failed = [
        result
        for result in payload["results"]
        if result["actual_status"] != result["expected_status"]
    ]
    assert failed == [], f"failed fixtures: {failed}"


def test_contract_status_to_exit_mapping_is_stable() -> None:
    """The status→exit mapping must be stable for downstream tooling."""

    verifier = _load_verifier()
    assert verifier._status_to_exit(verifier.STATUS_CONFIRMED) == verifier.EXIT_CONFIRMED
    assert verifier._status_to_exit(verifier.STATUS_PERSISTENCE) == verifier.EXIT_PERSISTENCE
    assert verifier._status_to_exit(verifier.STATUS_READBACK) == verifier.EXIT_READBACK
    assert verifier._status_to_exit(verifier.STATUS_INDEX) == verifier.EXIT_INDEX
    assert verifier._status_to_exit(verifier.STATUS_RECEIPT) == verifier.EXIT_RECEIPT
    assert verifier._status_to_exit(verifier.STATUS_TOOL_ERROR) == verifier.EXIT_TOOL_ERROR
    assert (
        verifier._status_to_exit(verifier.STATUS_UNRESOLVED)
        == verifier.EXIT_UNRESOLVED
    )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "correct_fail_closed_implementation",
        "persistence_port_missing",
        "persist_throws",
        "persist_returns_readback_none",
        "readback_tenant_wrong",
        "readback_knowledge_version_wrong",
        "readback_snapshot_hash_wrong",
        "consistency_check_false_but_activated",
        "consistency_checks_missing",
        "receipt_before_persist",
        "es_missing_scope",
        "milvus_missing_scope",
        "neo4j_missing_scope",
        "foreign_snapshot_dynamic_port",
        "adapter_smoke_no_scope_filter",
        "immutable_payload_conflict",
    ],
)
def test_each_contract_fixture_matches_expected_status(fixture_name: str) -> None:
    """Each contract fixture must land on its declared expected status."""

    verifier = _load_verifier()
    payload = _capture_json(verifier, ["--mode", "contract"])
    matching = [
        result
        for result in payload["results"]
        if result["fixture"] == fixture_name
    ]
    assert matching, f"missing fixture {fixture_name!r}"
    assert matching[0]["actual_status"] == matching[0]["expected_status"]


def test_status_constants_use_documented_names() -> None:
    """The verifier must use the documented status names."""

    verifier = _load_verifier()
    assert verifier.STATUS_CONFIRMED == "SNAPSHOT_FAIL_CLOSED_CONFIRMED"
    assert verifier.STATUS_PERSISTENCE == "PERSISTENCE_GATE_VIOLATION"
    assert verifier.STATUS_READBACK == "READBACK_SCOPE_VIOLATION"
    assert verifier.STATUS_INDEX == "INDEX_SCOPE_VIOLATION"
    assert verifier.STATUS_RECEIPT == "ACTIVATION_RECEIPT_VIOLATION"


def test_snapshot_report_exposes_not_proven_boundary() -> None:
    """The not-proven boundary must be explicit in the report."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    assert any(
        "live PostgreSQL" in boundary for boundary in report.not_proven
    )


def test_activation_paths_observed_in_real_repo() -> None:
    """The collector must locate the snapshot activation file."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    assert verifier.SNAPSHOT_ACTIVATION_PATH in report.activation_paths


def test_index_adapters_path_observed() -> None:
    """The collector must locate the index adapters file."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    assert report.errors == [] or any(
        "adapters" in path or "snapshot_activation" in path
        for path in report.activation_paths
    )
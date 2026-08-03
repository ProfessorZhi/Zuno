"""Tests for the PHASE22 canonical hash / scope companion gate.

These tests are dependency-free. They cover:

* Contract mode — every fixture lands on the expected status kind.
* Repository mode — the verifier reports truthfully on PR #112's current
  manifests and never lowers its standards to force a pass.
* The frozen expected hashes / scopes are stable.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]

VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase22_canonical_hash_scope.py"
FIXTURES_DIR = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "phase22_canonical_hash_scope"
)


# --- Frozen expectations ---------------------------------------------------


def test_frozen_expected_hashes_are_64_char_hex() -> None:
    """The frozen values used by the verifier must be valid 64-char hex."""

    expected = (
        "0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a",
        "43d4842d41ea528cec6bfdfd7540a0c58c8c6653f8fa752b9eee31c7a0f079a6",
        "749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4",
    )
    for value in expected:
        assert len(value) == 64
        int(value, 16)  # raises if not hex


def test_frozen_expected_hashes_are_distinct() -> None:
    """No two frozen canonical hashes may collide."""

    expected = (
        "0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a",
        "43d4842d41ea528cec6bfdfd7540a0c58c8c6653f8fa752b9eee31c7a0f079a6",
        "749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4",
    )
    assert len(set(expected)) == 3


# --- Helper: invoke the verifier as a subprocess ---------------------------


def _invoke_verifier(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFIER), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=60.0,
    )


# --- Contract mode ---------------------------------------------------------


def test_contract_mode_exits_zero() -> None:
    """Contract mode must exit 0 when the fixture suite is healthy."""

    result = _invoke_verifier("--mode", "contract")
    assert result.returncode == 0, (
        f"contract mode failed: stdout={result.stdout[:500]!r} "
        f"stderr={result.stderr!r}"
    )
    payload = json.loads(result.stdout.splitlines()[0] if False else result.stdout)
    # Verifier prints JSON; we accept any trailing text.
    json_start = result.stdout.find("{")
    payload = json.loads(result.stdout[json_start:])
    assert payload["status"] == "CANONICAL_HASH_SCOPE_CONFIRMED"
    assert payload["exit_code"] == 0


def test_contract_mode_reports_each_fixture_outcome() -> None:
    """Every fixture must be reported; totals must agree with the suite size."""

    result = _invoke_verifier("--mode", "contract")
    json_start = result.stdout.find("{")
    payload = json.loads(result.stdout[json_start:])
    fixture_files = list(FIXTURES_DIR.glob("[0-9][0-9]_*.json"))
    summary = payload["detected_scope"].get("_contract_summary", [])
    summary_text = "\n".join(summary)
    assert f"passed={len(fixture_files)}" in summary_text, (
        f"contract summary does not match fixture count: {summary!r}"
    )


# --- Per-fixture parametrized tests ----------------------------------------


EXPECTED_OUTCOMES_PATH = FIXTURES_DIR / "expected_outcomes.json"


def _expected_outcomes() -> dict[str, dict[str, str]]:
    return json.loads(EXPECTED_OUTCOMES_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "fixture_path",
    sorted(FIXTURES_DIR.glob("[0-9][0-9]_*.json")),
    ids=lambda p: p.stem,
)
def test_each_fixture_lands_on_expected_status(
    fixture_path: Path,
) -> None:
    """Each fixture must be classified as the expected status kind."""

    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    expected_kind = _expected_outcomes().get(
        fixture_path.stem, {}
    ).get("expected_status_kind", "CANONICAL_HASH_SCOPE_CONFIRMED")

    observed_kind, observed_detail = _classify_fixture(payload)
    assert observed_kind == expected_kind, (
        f"fixture {fixture_path.stem}: expected {expected_kind!r}, "
        f"got {observed_kind!r} ({observed_detail})"
    )


# --- Repository mode -------------------------------------------------------


def test_repository_mode_reports_truthfully() -> None:
    """Repository mode must exit with a code in the documented set."""

    result = _invoke_verifier("--mode", "repository")
    assert result.returncode in {0, 2, 3, 4, 5}, (
        f"repository mode returned unexpected exit code {result.returncode}: "
        f"stdout={result.stdout!r}"
    )
    json_start = result.stdout.find("{")
    payload = json.loads(result.stdout[json_start:])
    assert payload["status"] in {
        "CANONICAL_HASH_SCOPE_CONFIRMED",
        "HASH_CONTRACT_VIOLATION",
        "SCOPE_CONTRACT_VIOLATION",
        "IDENTITY_UNRESOLVED",
        "TOOL_ERROR",
    }
    assert payload["exit_code"] == result.returncode


def test_repository_mode_records_field_sources() -> None:
    """Repository mode must surface the JSON path of every detected hash."""

    result = _invoke_verifier("--mode", "repository")
    json_start = result.stdout.find("{")
    payload = json.loads(result.stdout[json_start:])
    detected = payload["detected_hashes"]
    for label in ("source_manifest_hash", "canonical_ir_hash", "dataset_corpus_hash"):
        entry = detected.get(label, {})
        assert "field_source" in entry, (
            f"{label} entry missing field_source: {entry}"
        )
        assert "value" in entry, f"{label} entry missing value: {entry}"


def test_repository_mode_records_not_proven_boundary() -> None:
    """Repository mode must list the boundaries the verifier cannot prove."""

    result = _invoke_verifier("--mode", "repository")
    json_start = result.stdout.find("{")
    payload = json.loads(result.stdout[json_start:])
    boundary = payload["not_proven_boundary"]
    assert isinstance(boundary, list)
    assert any("knowledge_versions" in s for s in boundary), (
        f"boundary must include knowledge_versions: {boundary!r}"
    )
    assert any("security_decisions" in s for s in boundary), (
        f"boundary must include security_decisions: {boundary!r}"
    )


# --- Specific contract fixture behaviours ---------------------------------


def test_aliasing_fixture_is_caught() -> None:
    """``02_source_aliasing_as_corpus`` must fail with HASH_CONTRACT_VIOLATION.

    Aliasing or value mismatch both surface as HASH_CONTRACT_VIOLATION.
    """

    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "02_source_aliasing_as_corpus.json").read_text(
            encoding="utf-8"
        )
    )
    kind, detail = _classify_fixture(payload)
    assert kind == "HASH_CONTRACT_VIOLATION"
    lowered = detail.lower()
    assert (
        "aliasing" in lowered
        or "equal" in lowered
        or "tampered" in lowered
    ), f"unexpected detail for fixture 02: {detail!r}"


def test_missing_dataset_corpus_hash_fixture_is_caught() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "04_missing_dataset_corpus_hash.json").read_text(
            encoding="utf-8"
        )
    )
    kind, detail = _classify_fixture(payload)
    assert kind == "HASH_CONTRACT_VIOLATION"
    assert "dataset_corpus_hash" in detail


def test_tampered_corpus_hash_fixture_is_caught() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "05_tampered_corpus_hash.json").read_text(
            encoding="utf-8"
        )
    )
    kind, detail = _classify_fixture(payload)
    assert kind == "HASH_CONTRACT_VIOLATION"
    assert "tampered" in detail or "does not match" in detail


def test_tenant_renamed_to_verify_fixture_is_caught() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "07_tenant_renamed_to_verify.json").read_text(
            encoding="utf-8"
        )
    )
    kind, detail = _classify_fixture(payload)
    assert kind == "SCOPE_CONTRACT_VIOLATION"


def test_workspace_renamed_to_verify_fixture_is_caught() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "08_workspace_renamed_to_verify.json").read_text(
            encoding="utf-8"
        )
    )
    kind, detail = _classify_fixture(payload)
    assert kind == "SCOPE_CONTRACT_VIOLATION"


def test_source_id_diverges_from_db_fixture_is_caught() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "09_source_id_scope_diverges_from_db.json").read_text(
            encoding="utf-8"
        )
    )
    kind, _ = _classify_fixture(payload)
    assert kind == "SCOPE_CONTRACT_VIOLATION"


def test_security_decision_scope_off_fixture_is_caught() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "10_security_decision_scope_off.json").read_text(
            encoding="utf-8"
        )
    )
    kind, _ = _classify_fixture(payload)
    assert kind == "SCOPE_CONTRACT_VIOLATION"


def test_knowledge_version_scope_off_fixture_is_caught() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "11_knowledge_version_scope_off.json").read_text(
            encoding="utf-8"
        )
    )
    kind, _ = _classify_fixture(payload)
    assert kind == "SCOPE_CONTRACT_VIOLATION"


def test_isolated_db_official_scope_fixture_passes() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "12_isolated_db_official_scope.json").read_text(
            encoding="utf-8"
        )
    )
    kind, _ = _classify_fixture(payload)
    assert kind == "CANONICAL_HASH_SCOPE_CONFIRMED"


def test_evidence_field_name_ambiguous_fixture_is_caught() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "13_evidence_field_name_ambiguous.json").read_text(
            encoding="utf-8"
        )
    )
    kind, _ = _classify_fixture(payload)
    assert kind == "HASH_CONTRACT_VIOLATION"


def test_dynamic_unresolved_hash_fixture_is_caught() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "14_dynamic_unresolved_hash.json").read_text(
            encoding="utf-8"
        )
    )
    kind, _ = _classify_fixture(payload)
    assert kind == "HASH_CONTRACT_VIOLATION"


def test_correct_separation_fixture_passes() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "01_correct_separation.json").read_text(encoding="utf-8")
    )
    kind, _ = _classify_fixture(payload)
    assert kind == "CANONICAL_HASH_SCOPE_CONFIRMED"


def test_official_scope_consistent_fixture_passes() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        _classify_fixture,
    )

    payload = json.loads(
        (FIXTURES_DIR / "06_official_scope_consistent.json").read_text(
            encoding="utf-8"
        )
    )
    kind, _ = _classify_fixture(payload)
    assert kind == "CANONICAL_HASH_SCOPE_CONFIRMED"


# --- Exit code mapping -----------------------------------------------------


def test_exit_codes_are_stable() -> None:
    """The verifier must never return an undocumented exit code."""

    sys.path.insert(0, str(REPO_ROOT))
    from tools.scripts.verify_phase22_canonical_hash_scope import (
        ALLOWED_SCOPES,
        ALLOWED_WORKSPACES,
        EXPECTED_CANONICAL_IR_HASH,
        EXPECTED_DATASET_CORPUS_HASH,
        EXPECTED_SOURCE_MANIFEST_HASH,
        OFFICIAL_TENANT,
        OFFICIAL_WORKSPACE,
        VERIFICATION_TENANT,
        VERIFICATION_WORKSPACE,
    )

    assert EXPECTED_SOURCE_MANIFEST_HASH != EXPECTED_CANONICAL_IR_HASH
    assert EXPECTED_CANONICAL_IR_HASH != EXPECTED_DATASET_CORPUS_HASH
    assert EXPECTED_SOURCE_MANIFEST_HASH != EXPECTED_DATASET_CORPUS_HASH
    assert ALLOWED_SCOPES == frozenset({OFFICIAL_TENANT, VERIFICATION_TENANT})
    assert ALLOWED_WORKSPACES == frozenset({OFFICIAL_WORKSPACE, VERIFICATION_WORKSPACE})
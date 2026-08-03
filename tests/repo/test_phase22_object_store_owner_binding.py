from __future__ import annotations

"""Tests for the PHASE22-OBJECT-STORE-OWNER-GATE AST verifier.

The verifier is a static AST + data-flow gate; this file exercises both the
contract fixtures (fixed, hand-authored) and the repository-mode scan.
"""

import io
import json
from contextlib import redirect_stdout
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase22_object_store_owner_binding.py"


def _load_verifier():
    spec = spec_from_file_location(
        "verify_phase22_object_store_owner_binding", VERIFIER
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


def test_repository_mode_reports_unique_production_binding() -> None:
    """The real repository must bind exactly one production adapter."""

    verifier = _load_verifier()
    payload = _capture_json(verifier, ["--mode", "repository"])
    assert payload["status"] == verifier.STATUS_UNIQUE
    assert payload["not_proven"], "not_proven boundary must be reported"
    assert any(
        "live MinIO" in boundary for boundary in payload["not_proven"]
    )


def test_contract_mode_passes_all_fixtures() -> None:
    """All twelve contract fixtures must pass."""

    verifier = _load_verifier()
    payload = _capture_json(verifier, ["--mode", "contract"])
    assert payload["overall_status"] == verifier.STATUS_UNIQUE
    failed = [
        result
        for result in payload["results"]
        if result["actual_status"] != result["expected_status"]
    ]
    assert failed == [], f"failed fixtures: {failed}"


@pytest.mark.parametrize(
    "fixture_name",
    [
        "single_canonical_adapter_and_wrapper",
        "two_production_bindings",
        "no_production_binding",
        "local_only_adapter",
        "wrapper_does_not_wrap_adapter",
        "runtime_does_not_receive_wrapper",
        "explicit_local_override_at_call_site",
        "dynamic_override_lambda",
        "kwargs_unresolved",
        "many_classes_unique_production_binding",
        "test_double_excluded",
        "caller_does_not_handle_none",
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


def test_collect_observations_finds_repository_call_sites() -> None:
    """The collector must enumerate real-repository call sites via AST."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    paths = {cs.file_path for cs in report.call_sites}
    assert "src/backend/zuno/main.py" in paths
    assert "src/backend/zuno/platform/services/queue/runner.py" in paths


def test_data_flow_proves_wrapper_wraps_adapter() -> None:
    """The composition root data-flow must show wrapper.store=adapter."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    flow = report.composition_root_data_flow
    assert flow["adapter_variable"] == "object_store"
    assert flow["wrapper_variable"] == "durable_object_store"
    assert flow["wrapper_wraps_adapter"] is True
    assert flow["runtime_uses_wrapper"] is True
    assert flow["multi_adapter"] is False
    assert flow["multi_wrapper"] is False


def test_repository_signature_binds_canonical_defaults() -> None:
    """The composition root signature must bind canonical defaults."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    signature = report.composition_root_signature
    assert signature["object_store_factory"] == verifier.PRODUCTION_ADAPTER_CLASS
    assert signature["durable_object_store_factory"] == verifier.DURABLE_WRAPPER_CLASS
    assert signature["runtime_factory"] == verifier.CANONICAL_RUNTIME_CLASS


def test_fail_closed_branches_present_in_composition_root() -> None:
    """The composition root must fail closed on storage.mode and credentials."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    fc = report.composition_root_fail_closed
    assert fc["present"] is True
    assert fc["auto_fallback_to_local"] is False
    assert len(fc["branches"]) >= 2


def test_status_to_exit_mapping_is_stable() -> None:
    """Status-to-exit mapping must be stable for downstream tooling."""

    verifier = _load_verifier()
    assert verifier._status_to_exit(verifier.STATUS_UNIQUE) == verifier.EXIT_UNIQUE
    assert (
        verifier._status_to_exit(verifier.STATUS_MULTIPLE)
        == verifier.EXIT_MULTIPLE
    )
    assert verifier._status_to_exit(verifier.STATUS_NONE) == verifier.EXIT_NONE
    assert (
        verifier._status_to_exit(verifier.STATUS_UNRESOLVED)
        == verifier.EXIT_UNRESOLVED
    )
    assert (
        verifier._status_to_exit(verifier.STATUS_TOOL_ERROR)
        == verifier.EXIT_TOOL_ERROR
    )


def test_call_site_resolution_reports_known_callers() -> None:
    """Real call sites must be statically resolved, not dynamic."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    assert report.call_sites, "expected call sites in the real repo"
    for site in report.call_sites:
        assert site.resolution_status == "resolved"
        assert site.qualified_target.startswith("zuno.")


def test_status_constants_do_not_use_obsolete_name() -> None:
    """The old UNIQUE_PRODUCTION_BINDING_CONFIRMED must not exist."""

    verifier = _load_verifier()
    assert hasattr(verifier, "STATUS_UNIQUE")
    assert verifier.STATUS_UNIQUE == "UNIQUE_PRODUCTION_BINDING_STATICALLY_CONFIRMED"
    assert not hasattr(verifier, "UNIQUE_PRODUCTION_BINDING_CONFIRMED") or not hasattr(
        verifier, "STATUS_UNIQUE_LEGACY"
    )
    # The legacy name string must not appear in the module.
    source = VERIFIER.read_text(encoding="utf-8")
    assert "UNIQUE_PRODUCTION_BINDING_CONFIRMED" not in source
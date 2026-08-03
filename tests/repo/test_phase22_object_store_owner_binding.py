from __future__ import annotations

"""Tests for the PHASE22-OBJECT-STORE-OWNER-GATE verifier.

These tests exercise the Fail-closed Object Store Owner Binding Gate against
the live repository and against in-memory fixtures that represent the
fail-closed contract.  They refuse to rely on class-name suffix counting
and explicitly assert that the old DeepSeek algorithm is rejected.
"""

import json
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


def test_repository_mode_reports_unique_production_binding() -> None:
    """The real repository must bind exactly one production adapter."""

    verifier = _load_verifier()
    exit_code = verifier.main(["--mode", "repository", "--json"])
    assert exit_code == verifier.EXIT_UNIQUE

    payload = json.loads(_run_and_capture(verifier, ["--mode", "repository"]))
    assert payload["status"] == verifier.STATUS_UNIQUE
    assert any(
        "exactly one MinIO adapter" in reason for reason in payload["reasons"]
    )


def test_contract_mode_self_test_passes_all_fixtures() -> None:
    """All contract fixtures must pass and the contract mode must exit 0."""

    verifier = _load_verifier()
    payload = json.loads(_run_and_capture(verifier, ["--mode", "contract"]))
    assert payload["overall_status"] == verifier.STATUS_UNIQUE
    failed = [
        result
        for result in payload["results"]
        if result["actual_status"] != result["expected_status"]
    ]
    assert failed == []


def test_multiple_production_bindings_are_rejected() -> None:
    """Two simultaneous production adapters must yield MULTIPLE_PRODUCTION_BINDINGS."""

    verifier = _load_verifier()
    report = verifier._fixture_base_report()
    body_refs = dict(report.composition_root_body_references)
    body_refs[verifier.PRODUCTION_ADAPTER_CLASS] = 2
    report.composition_root_body_references = body_refs
    status, reasons = verifier.evaluate(report)
    assert status == verifier.STATUS_MULTIPLE
    assert any("exactly one" in reason.lower() for reason in reasons)


def test_only_local_adapter_is_rejected_as_no_production_binding() -> None:
    """A composition root with no production call sites is NO_PRODUCTION_BINDING."""

    verifier = _load_verifier()
    report = verifier._fixture_base_report()
    report.composition_root_call_sites = []
    status, reasons = verifier.evaluate(report)
    assert status == verifier.STATUS_NONE
    assert any("call sites" in reason for reason in reasons)


def test_missing_binding_is_unresolved() -> None:
    """Without a production adapter or wrapper reference, status is UNRESOLVED."""

    verifier = _load_verifier()
    report = verifier._fixture_base_report()
    body_refs = dict(report.composition_root_body_references)
    body_refs[verifier.PRODUCTION_ADAPTER_CLASS] = 0
    body_refs[verifier.DURABLE_WRAPPER_CLASS] = 0
    report.composition_root_body_references = body_refs
    status, _ = verifier.evaluate(report)
    assert status == verifier.STATUS_UNRESOLVED


def test_durable_wrapper_wrapping_production_adapter_is_one_owner() -> None:
    """The wrapper around the production adapter counts as a single owner."""

    verifier = _load_verifier()
    report = verifier._fixture_base_report()
    status, _ = verifier.evaluate(report)
    assert status == verifier.STATUS_UNIQUE


def test_test_double_does_not_count_as_production_owner() -> None:
    """Test doubles must not change the binding verdict."""

    verifier = _load_verifier()
    report = verifier._fixture_base_report()
    report.observations.append(
        verifier.ClassObservation(
            role=verifier.ROLE_TEST_DOUBLE,
            qualified_name="FakeObjectStore",
            file_path="tests/fixtures/phase22_object_store_owner_binding/fake.py",
            line_number=1,
            notes=("test double; excluded from production owner count",),
        )
    )
    status, _ = verifier.evaluate(report)
    assert status == verifier.STATUS_UNIQUE


def test_class_name_counting_is_rejected() -> None:
    """The old DeepSeek class-name-count algorithm must yield BINDING_UNRESOLVED."""

    verifier = _load_verifier()
    report = verifier._fixture_base_report()
    report.error_messages.append(
        "class-name suffix counting is not a binding proof"
    )
    status, _ = verifier.evaluate(report)
    assert status == verifier.STATUS_UNRESOLVED


def test_collect_observations_classifies_all_roles() -> None:
    """The collector must assign a role to every recognised class."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    roles = {obs.role for obs in report.observations}
    assert verifier.ROLE_PROTOCOL_PORT in roles
    assert verifier.ROLE_LOCAL_ADAPTER in roles
    assert verifier.ROLE_PRODUCTION_ADAPTER in roles
    assert verifier.ROLE_DURABLE_WRAPPER in roles
    assert verifier.ROLE_RUNTIME_OWNER in roles
    assert verifier.ROLE_COMPOSITION_ROOT in roles


def test_collect_observations_records_production_call_sites() -> None:
    """The composition root call sites must be enumerated for the live repo."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    assert report.composition_root_call_sites, (
        "expected at least one composition-root call site in the real repo"
    )
    assert any(
        "main.py" in site["file_path"] for site in report.composition_root_call_sites
    )


def test_repository_failure_paths_use_distinct_exit_codes() -> None:
    """Status-to-exit-code mapping must be stable for downstream tooling."""

    verifier = _load_verifier()
    assert verifier._status_to_exit(verifier.STATUS_UNIQUE) == verifier.EXIT_UNIQUE
    assert verifier._status_to_exit(verifier.STATUS_MULTIPLE) == verifier.EXIT_MULTIPLE
    assert verifier._status_to_exit(verifier.STATUS_NONE) == verifier.EXIT_NONE
    assert (
        verifier._status_to_exit(verifier.STATUS_UNRESOLVED)
        == verifier.EXIT_UNRESOLVED
    )


def test_fail_closed_branch_is_required_for_production_verdict() -> None:
    """Composition root without fail-closed branches must not be UNIQUE."""

    verifier = _load_verifier()
    report = verifier._fixture_base_report()
    report.fail_closed_branches = ()
    status, reasons = verifier.evaluate(report)
    assert status == verifier.STATUS_UNRESOLVED
    assert any("fail closed" in reason for reason in reasons)


def test_tenant_workspace_namespace_is_required() -> None:
    """Receipt must be tenant/workspace scoped for a production verdict."""

    verifier = _load_verifier()
    report = verifier._fixture_base_report()
    report.tenant_workspace_bindings = ()
    status, reasons = verifier.evaluate(report)
    assert status == verifier.STATUS_UNRESOLVED
    assert any("tenant/workspace" in reason for reason in reasons)


def test_local_object_store_in_production_body_is_unresolved() -> None:
    """The local adapter must not appear in the production composition root body."""

    verifier = _load_verifier()
    report = verifier._fixture_base_report()
    body_refs = dict(report.composition_root_body_references)
    body_refs[verifier.LOCAL_ADAPTER_CLASS] = 1
    report.composition_root_body_references = body_refs
    status, reasons = verifier.evaluate(report)
    assert status == verifier.STATUS_UNRESOLVED
    assert any("local" in reason.lower() for reason in reasons)


def test_real_repository_attested_by_contract_mode() -> None:
    """The real repository attestation must match the repository-mode verdict."""

    verifier = _load_verifier()
    payload = json.loads(_run_and_capture(verifier, ["--mode", "contract"]))
    real_results = [
        result
        for result in payload["results"]
        if result["fixture"] == "real_repository_attested"
    ]
    assert real_results, "contract mode must include the real_repository fixture"
    assert real_results[0]["expected_status"] == real_results[0]["actual_status"]


def test_runtime_owner_depends_on_durable_wrapper() -> None:
    """The canonical runtime must depend on the durable wrapper, not the adapter."""

    verifier = _load_verifier()
    report = verifier.collect_observations(REPO_ROOT)
    dependencies = {
        field: type_
        for field, type_ in report.runtime_owner_dependencies
    }
    assert dependencies.get("object_store") == verifier.DURABLE_WRAPPER_CLASS


@pytest.mark.parametrize(
    "fixture_name",
    [
        "unique_production_binding",
        "multiple_production_bindings",
        "no_production_binding",
        "missing_binding",
        "wrapper_wraps_production_adapter",
        "test_double_excluded",
        "name_count_algorithm_rejected",
    ],
)
def test_each_contract_fixture_lands_on_its_expected_status(fixture_name: str) -> None:
    """Each contract fixture must produce its declared expected status."""

    verifier = _load_verifier()
    payload = json.loads(_run_and_capture(verifier, ["--mode", "contract"]))
    matching = [
        result
        for result in payload["results"]
        if result["fixture"] == fixture_name
    ]
    assert matching, f"missing fixture {fixture_name!r} in contract mode output"
    assert matching[0]["actual_status"] == matching[0]["expected_status"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_and_capture(verifier, argv: list[str]) -> str:
    """Run verifier.main with the given argv and capture stdout JSON."""

    import io
    from contextlib import redirect_stdout

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        verifier.main(argv + ["--json"])
    return buffer.getvalue()
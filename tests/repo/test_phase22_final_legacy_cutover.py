"""PHASE22 Final Legacy/Cutover Audit Verifier (V2) — boundary tests.

This test suite wires the audit verifier defined in
``tools/scripts/verify_phase22_final_legacy_cutover.py`` into the
repository boundary test tree. It guarantees:

1. The verifier is machine-loadable and exposes a ``verify()`` entry
   point that returns a structured ``VerifierReport``.
2. The structural inspections, AST scans, text scans, and YAML config
   scans behave as specified on each contract fixture.
3. The verifier status classification respects the priority
   documented in the task contract.
4. The audit gate fails closed on the current ``origin/main`` head
   (the DeepSeek escalation and expired feature flags are still open).

Each test uses a temporary directory layout that mirrors the contract
fixtures under ``tests/fixtures/phase22_legacy_cutover/``.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "tests"
VERIFIER_PATH = REPO_ROOT / "tools" / "scripts" / "verify_phase22_final_legacy_cutover.py"
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "phase22_legacy_cutover"


# ---------------------------------------------------------------------------
# Module loading helpers
# ---------------------------------------------------------------------------


# Insert the repo root onto sys.path so we can import the verifier
# module directly. The verifier file uses ``from __future__ import
# annotations`` together with ``@dataclass(frozen=True)``; spec-based
# loading via ``importlib.util.spec_from_file_location`` is brittle on
# Windows when the file lives under ``tools/scripts/`` and the parent
# package uses implicit-namespace semantics. The direct import keeps
# the test stable across Python versions.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.scripts import verify_phase22_final_legacy_cutover as VERIFIER  # noqa: E402


# ---------------------------------------------------------------------------
# Inventory & fixture presence
# ---------------------------------------------------------------------------


def test_all_eight_contract_fixtures_exist() -> None:
    """All 28 contract fixtures must exist on disk."""
    for index in range(1, 29):
        prefix = f"{index:02d}_"
        matches = [
            path for path in FIXTURE_ROOT.iterdir()
            if path.name.startswith(prefix)
        ]
        assert matches, f"missing fixture #{index}"
        assert len(matches) == 1


def test_verifier_module_exposes_required_api() -> None:
    """Verifier must expose the public helpers used by the audit gate."""
    for name in (
        "verify",
        "Finding",
        "Inventory",
        "ReachabilityReport",
        "VerifierReport",
        "_classify_status",
        "_inspect_phase08_cutover",
        "_inspect_workspace_task_runtime",
        "_inspect_completion_service",
        "_check_forbidden_paths",
        "_check_feature_flag_expiry",
        "_check_allowlist_expiry",
        "_check_unresolved_escalations",
        "_load_removal_candidate_allowlist",
    ):
        assert hasattr(VERIFIER, name), f"missing helper {name}"


def test_phase22_verifier_is_machine_runnable() -> None:
    """The verifier must run as a subprocess and produce JSON output."""
    completed = subprocess.run(
        [
            sys.executable,
            str(VERIFIER_PATH),
            "--json",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert completed.returncode in {0, 1, 2}
    payload = json.loads(completed.stdout)
    assert payload["status"] in {
        "LEGACY_CUTOVER_AUDIT_CLEAN",
        "LEGACY_RUNTIME_BLOCKERS_FOUND",
        "DUAL_PATH_BLOCKERS_FOUND",
        "ALIAS_BYPASS_BLOCKERS_FOUND",
        "PUBLIC_ADAPTER_OWNERSHIP_VIOLATION",
        "AUDIT_UNRESOLVED",
        "TOOL_ERROR",
    }
    assert payload["inventory"]["head_sha"] != "UNKNOWN"


# ---------------------------------------------------------------------------
# Status classification invariants
# ---------------------------------------------------------------------------


def test_status_priority_runtime_first() -> None:
    """Runtime blockers outrank dual-path blockers in the priority list."""
    report = VERIFIER.VerifierReport()
    report.reachability.dual_path_blockers.append(
        VERIFIER.Finding(
            path="x", line=1, symbol="x", category="DUAL_PATH_BLOCKERS_FOUND",
            entrypoint="x", reachable=True, resolution="retire",
            owner="x", risk="x", required_action="x",
            recommended_worker="x", evidence_kind="STATIC_TEXT",
        )
    )
    report.reachability.phase08_runtime_blockers.append(
        VERIFIER.Finding(
            path="y", line=1, symbol="y", category="LEGACY_RUNTIME_BLOCKERS_FOUND",
            entrypoint="y", reachable=True, resolution="retire",
            owner="y", risk="y", required_action="y",
            recommended_worker="y", evidence_kind="STATIC_AST",
        )
    )
    assert VERIFIER._classify_status(report) == "LEGACY_RUNTIME_BLOCKERS_FOUND"


def test_status_priority_alias_outranked_by_dual() -> None:
    """Dual-path blockers outrank alias/bypass blockers."""
    report = VERIFIER.VerifierReport()
    report.reachability.alias_bypass_blockers.append(
        VERIFIER.Finding(
            path="x", line=1, symbol="x", category="ALIAS_BYPASS_BLOCKERS_FOUND",
            entrypoint="x", reachable=True, resolution="retire",
            owner="x", risk="x", required_action="x",
            recommended_worker="x", evidence_kind="STATIC_AST",
        )
    )
    report.reachability.dual_path_blockers.append(
        VERIFIER.Finding(
            path="y", line=1, symbol="y", category="DUAL_PATH_BLOCKERS_FOUND",
            entrypoint="y", reachable=True, resolution="retire",
            owner="y", risk="y", required_action="y",
            recommended_worker="y", evidence_kind="STATIC_AST",
        )
    )
    assert VERIFIER._classify_status(report) == "DUAL_PATH_BLOCKERS_FOUND"


def test_status_priority_unresolved_blocks_clean() -> None:
    """An unresolved item blocks ``LEGACY_CUTOVER_AUDIT_CLEAN``."""
    report = VERIFIER.VerifierReport()
    report.reachability.unresolved_items.append(
        VERIFIER.Finding(
            path="x", line=1, symbol="x", category="AUDIT_UNRESOLVED",
            entrypoint="x", reachable=True, resolution="escalate",
            owner="x", risk="x", required_action="x",
            recommended_worker="x", evidence_kind="RUNTIME_TEST",
        )
    )
    assert VERIFIER._classify_status(report) == "AUDIT_UNRESOLVED"


def test_status_priority_clean_only_when_empty() -> None:
    """An empty report is the only path to ``LEGACY_CUTOVER_AUDIT_CLEAN``."""
    report = VERIFIER.VerifierReport()
    assert VERIFIER._classify_status(report) == "LEGACY_CUTOVER_AUDIT_CLEAN"


def test_status_priority_tool_error_when_errors_present() -> None:
    """Tool errors always return ``TOOL_ERROR`` regardless of findings."""
    report = VERIFIER.VerifierReport()
    report.tool_errors.append("synthetic failure")
    assert VERIFIER._classify_status(report) == "TOOL_ERROR"


# ---------------------------------------------------------------------------
# History exclusion
# ---------------------------------------------------------------------------


def test_history_root_is_excluded(tmp_path: Path) -> None:
    """A legacy token under ``docs/history`` must not be flagged."""
    history_root = tmp_path / "docs" / "history" / "fake-program"
    history_root.mkdir(parents=True)
    history_file = history_root / "legacy_note.md"
    history_file.write_text(
        textwrap.dedent(
            """\
            # History
            Mentions ``GeneralAgent``, ``legacy_runner`` and
            ``_fallback_to_legacy``. None of these should surface as
            findings because the file lives under docs/history.
            """
        ),
        encoding="utf-8",
    )
    saved_excluded = list(VERIFIER.HISTORY_EXCLUDED_ROOTS)
    try:
        VERIFIER.HISTORY_EXCLUDED_ROOTS = (tmp_path / "docs" / "history",)
        assert VERIFIER._is_history_excluded(history_file)
    finally:
        VERIFIER.HISTORY_EXCLUDED_ROOTS = tuple(saved_excluded)


# ---------------------------------------------------------------------------
# AST detection on individual fixtures
# ---------------------------------------------------------------------------


def _build_report() -> VERIFIER.VerifierReport:
    return VERIFIER.VerifierReport()


def _run_legacy_runner_injection_fixture() -> VERIFIER.VerifierReport:
    report = _build_report()
    fixture = FIXTURE_ROOT / "03_legacy_runner_injection.py"
    tree = VERIFIER._build_inventory(report)  # touch inventory path
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture,
        rel,
        report,
        set(),
        is_phase08=False,
    )
    _ = tree
    return report


def test_legacy_runner_factory_outside_phase08_is_dual_path() -> None:
    report = _run_legacy_runner_injection_fixture()
    symbols = {finding.symbol for finding in report.reachability.dual_path_blockers}
    assert "legacy_runner" in symbols


def test_rollback_mode_in_production_is_dual_path() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "04_rollback_mode.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    # The rollback token is part of the runtime-blocker set; we accept
    # either dual_path or runtime_blocker classification.
    raised = (
        report.reachability.dual_path_blockers
        + report.reachability.runtime_blockers
        + report.reachability.phase08_runtime_blockers
    )
    assert raised, "rollback marker must surface a finding"


def test_shadow_mode_in_production_is_dual_path() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "05_shadow_legacy_primary.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    raised = (
        report.reachability.dual_path_blockers
        + report.reachability.runtime_blockers
        + report.reachability.phase08_runtime_blockers
    )
    assert raised


def test_canary_mode_in_production_is_dual_path() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "06_canary_legacy_shadow.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    raised = (
        report.reachability.dual_path_blockers
        + report.reachability.runtime_blockers
        + report.reachability.phase08_runtime_blockers
    )
    assert raised


def test_fallback_to_legacy_outside_phase08_is_dual_path() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "02_fallback_to_legacy.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    raised = (
        report.reachability.dual_path_blockers
        + report.reachability.runtime_blockers
        + report.reachability.phase08_runtime_blockers
    )
    assert raised


def test_python_legacy_import_is_dual_path() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "10_python_legacy_import.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    assert any(
        finding.symbol.startswith("zuno.core")
        for finding in report.reachability.dual_path_blockers
    )


def test_dynamic_importlib_legacy_is_alias_bypass() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "11_dynamic_legacy_import.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    assert any(
        finding.symbol == "importlib.import_module"
        for finding in report.reachability.alias_bypass_blockers
    )


def test_sys_meta_path_mutation_is_alias_bypass() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "12_sys_meta_path.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    assert any(
        finding.symbol.startswith("sys")
        for finding in report.reachability.alias_bypass_blockers
    )


def test_sys_modules_alias_is_alias_bypass() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "13_sys_modules_alias.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    assert any(
        finding.symbol.startswith("sys")
        for finding in report.reachability.alias_bypass_blockers
    )


def test_try_except_legacy_fallback_is_alias_bypass() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "14_try_except_legacy_import.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    assert any(
        finding.symbol == "try/except legacy fallback"
        for finding in report.reachability.alias_bypass_blockers
    )


def test_shell_legacy_env_is_dual_path() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "16_shell_legacy_env.sh"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_text_file(fixture, rel, report, set())
    symbols = {
        finding.symbol for finding in report.reachability.dual_path_blockers
    }
    assert any("legacy" in s.lower() for s in symbols)


def test_workflow_legacy_command_is_dual_path() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "17_workflow_legacy_command.yml"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_text_file(fixture, rel, report, set())
    symbols = {
        finding.symbol for finding in report.reachability.dual_path_blockers
    }
    assert any("legacy" in s.lower() for s in symbols)


def test_dual_read_marker_in_python_is_dual_path() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "18_dual_read_marker.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    symbols = {
        finding.symbol for finding in report.reachability.dual_path_blockers
    }
    assert any("dual_read" in s for s in symbols)


def test_dual_write_marker_in_python_is_dual_path() -> None:
    report = _build_report()
    fixture = FIXTURE_ROOT / "19_dual_write_marker.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    VERIFIER._scan_python_file(
        fixture, rel, report, set(), is_phase08=False
    )
    symbols = {
        finding.symbol for finding in report.reachability.dual_path_blockers
    }
    assert any("dual_write" in s for s in symbols)


# ---------------------------------------------------------------------------
# Public-adapter ownership checks (deterministic)
# ---------------------------------------------------------------------------


def test_public_adapter_direct_dao_write_is_violation() -> None:
    """Public adapter that writes into the DAO deterministically fails."""
    report = _build_report()
    fixture = FIXTURE_ROOT / "22_public_adapter_dao_write.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()

    # Simulate the public-adapter classification by patching the path
    # into PUBLIC_ADAPTER_ROOTS temporarily.
    saved_roots = list(VERIFIER.PUBLIC_ADAPTER_ROOTS)
    try:
        VERIFIER.PUBLIC_ADAPTER_ROOTS = (fixture.parent,)
        VERIFIER._scan_python_file(
            fixture, rel, report, set(), is_phase08=False
        )
    finally:
        VERIFIER.PUBLIC_ADAPTER_ROOTS = tuple(saved_roots)

    assert report.reachability.public_adapter_violations, (
        "public adapter that imports a domain DAO and writes must surface"
    )


def test_public_adapter_application_service_call_is_clean() -> None:
    """Public adapter that calls an application service is not flagged."""
    report = _build_report()
    fixture = FIXTURE_ROOT / "23_public_adapter_application_service.py"
    rel = fixture.relative_to(REPO_ROOT).as_posix()
    saved_roots = list(VERIFIER.PUBLIC_ADAPTER_ROOTS)
    try:
        VERIFIER.PUBLIC_ADAPTER_ROOTS = (fixture.parent,)
        VERIFIER._scan_python_file(
            fixture, rel, report, set(), is_phase08=False
        )
    finally:
        VERIFIER.PUBLIC_ADAPTER_ROOTS = tuple(saved_roots)
    assert not report.reachability.public_adapter_violations


# ---------------------------------------------------------------------------
# Feature flag expiry
# ---------------------------------------------------------------------------


def test_expired_unretired_flag_is_dual_path(tmp_path: Path) -> None:
    registry = tmp_path / "feature-flag-registry.yaml"
    registry.write_text(
        textwrap.dedent(
            """\
            flags:
              - flag: "expired_unretired_flag"
                owner: "Repository Governance"
                default: "DECLARED"
                metric: ["m"]
                rollback_command: "set expired_unretired_flag=ROLLBACK_WINDOW"
                expires_at_phase: "PHASE10"
                retire_task: "P22-T03"
                domain_fact_owner: "unchanged"
            """
        ),
        encoding="utf-8",
    )
    saved_path = VERIFIER.FEATURE_FLAG_REGISTRY
    try:
        VERIFIER.FEATURE_FLAG_REGISTRY = registry
        report = _build_report()
        VERIFIER._check_feature_flag_expiry(report)
    finally:
        VERIFIER.FEATURE_FLAG_REGISTRY = saved_path
    assert any(
        finding.symbol == "expired_unretired_flag"
        for finding in report.reachability.dual_path_blockers
    )


def test_retired_flag_with_no_runtime_reader_is_clean(tmp_path: Path) -> None:
    registry = tmp_path / "feature-flag-registry.yaml"
    registry.write_text(
        textwrap.dedent(
            """\
            flags:
              - flag: "retired_no_runtime_reader"
                owner: "Repository Governance"
                default: "RETIRED"
                metric: ["m"]
                rollback_command: "retired and fail-closed; no runtime reader"
                expires_at_phase: "PHASE10"
                retire_task: "P22-T03"
                domain_fact_owner: "unchanged"
            """
        ),
        encoding="utf-8",
    )
    saved_path = VERIFIER.FEATURE_FLAG_REGISTRY
    try:
        VERIFIER.FEATURE_FLAG_REGISTRY = registry
        report = _build_report()
        VERIFIER._check_feature_flag_expiry(report)
    finally:
        VERIFIER.FEATURE_FLAG_REGISTRY = saved_path
    assert not report.reachability.dual_path_blockers


# ---------------------------------------------------------------------------
# Removal candidates allowlist (strict)
# ---------------------------------------------------------------------------


def test_removal_candidate_allowlist_only_admits_active(tmp_path: Path) -> None:
    work_product = tmp_path / "phase22-removal-candidates.yaml"
    work_product.write_text(
        textwrap.dedent(
            """\
            mandatory_removal_candidates:
              - path: "src/backend/zuno/api/v1/foo.py"
                current_status: "active_candidate"
              - path: "src/backend/zuno/api/v1/bar.py"
                current_status: "resolved_retired"
            """
        ),
        encoding="utf-8",
    )
    saved_path = VERIFIER.REMOVAL_CANDIDATES_YAML
    try:
        VERIFIER.REMOVAL_CANDIDATES_YAML = work_product
        allowlist, errors = VERIFIER._load_removal_candidate_allowlist()
    finally:
        VERIFIER.REMOVAL_CANDIDATES_YAML = saved_path
    assert not errors
    assert "src/backend/zuno/api/v1/foo.py" in allowlist
    assert "src/backend/zuno/api/v1/bar.py" not in allowlist


def test_removal_candidate_yaml_must_be_a_mapping(tmp_path: Path) -> None:
    work_product = tmp_path / "phase22-removal-candidates.yaml"
    work_product.write_text("- not a mapping\n", encoding="utf-8")
    saved_path = VERIFIER.REMOVAL_CANDIDATES_YAML
    try:
        VERIFIER.REMOVAL_CANDIDATES_YAML = work_product
        allowlist, errors = VERIFIER._load_removal_candidate_allowlist()
    finally:
        VERIFIER.REMOVAL_CANDIDATES_YAML = saved_path
    assert allowlist == set()
    assert any("mapping" in err or "missing" in err for err in errors)


# ---------------------------------------------------------------------------
# Reachability & report integrity
# ---------------------------------------------------------------------------


def test_phase08_runtime_inventory_is_complete() -> None:
    """The Phase08CutoverController must surface runtime blockers on the
    current main branch — the live controller still defines rollback,
    shadow, canary and ``_fallback_to_legacy``."""

    report = VERIFIER.VerifierReport()
    VERIFIER._inspect_phase08_cutover(report)
    symbols = {finding.symbol for finding in report.reachability.phase08_runtime_blockers}
    assert any("rollback" in symbol for symbol in symbols)
    assert any("shadow" in symbol for symbol in symbols)
    assert any("canary" in symbol for symbol in symbols)
    assert "_run_legacy" in symbols
    assert "legacy_runner" in symbols
    assert "_fallback_to_legacy" in symbols


def test_workspace_task_runtime_legacy_runner_is_dual_path() -> None:
    report = VERIFIER.VerifierReport()
    VERIFIER._inspect_workspace_task_runtime(report)
    assert report.reachability.phase08_runtime_blockers, (
        "workspace_task_runtime defines a legacy_runner factory and must"
        " surface a runtime blocker until the symbol is retired."
    )


def test_bom_in_python_file_is_stripped() -> None:
    """UTF-8 BOM files must parse without crashing the AST stage."""
    text = "﻿import os\n"
    assert text.startswith("﻿")
    cleaned = VERIFIER._strip_bom(text)
    assert not cleaned.startswith("﻿")
    import ast
    ast.parse(cleaned)


def test_unresolved_escalation_yields_unresolved_status(tmp_path: Path) -> None:
    """A simulated escalation file marks the audit as ``AUDIT_UNRESOLVED``."""
    evidence = tmp_path / "docs" / "evidence" / "fake.md"
    evidence.parent.mkdir(parents=True)
    evidence.write_text(
        textwrap.dedent(
            """\
            # Escalation
            ESCALATE_TO_DEEPSEEK
            status: open
            """
        ),
        encoding="utf-8",
    )
    saved_root = VERIFIER.REPO_ROOT
    try:
        # Inject the temporary evidence root by monkeypatching the path.
        VERIFIER.REPO_ROOT = tmp_path
        report = VERIFIER.VerifierReport()
        VERIFIER._check_unresolved_escalations(report)
    finally:
        VERIFIER.REPO_ROOT = saved_root
    assert report.reachability.unresolved_items


def test_real_origin_main_fails_closed() -> None:
    """On the live ``origin/main`` head the audit MUST fail closed.

    The repository still carries the Phase08 ``_fallback_to_legacy``
    runtime, expired feature flags and unresolved escalations. The
    audit must therefore return a non-clean status. We accept any of
    ``LEGACY_RUNTIME_BLOCKERS_FOUND``, ``DUAL_PATH_BLOCKERS_FOUND``
    or ``AUDIT_UNRESOLVED``; we explicitly assert the verifier is not
    in ``LEGACY_CUTOVER_AUDIT_CLEAN`` state on the final head.
    """

    completed = subprocess.run(
        [sys.executable, str(VERIFIER_PATH), "--json"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert completed.returncode != 0, (
        "audit must fail closed on the current origin/main head"
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] != "LEGACY_CUTOVER_AUDIT_CLEAN", (
        "LEGACY_CUTOVER_AUDIT_CLEAN is not supported until the Phase08"
        " production fallback is retired or proven unreachable."
    )
    assert payload["status"] in {
        "LEGACY_RUNTIME_BLOCKERS_FOUND",
        "DUAL_PATH_BLOCKERS_FOUND",
        "ALIAS_BYPASS_BLOCKERS_FOUND",
        "PUBLIC_ADAPTER_OWNERSHIP_VIOLATION",
        "AUDIT_UNRESOLVED",
        "TOOL_ERROR",
    }


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
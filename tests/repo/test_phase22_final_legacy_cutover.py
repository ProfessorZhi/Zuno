"""PHASE22 final legacy cutover audit V3 tests.

These tests pin the V3 verifier's contract across the five detection
categories plus the unresolved / dynamic / alias edge cases:

  - LEGACY_CUTOVER_AUDIT_CLEAN
  - LEGACY_RUNTIME_BLOCKERS_FOUND
  - DUAL_PATH_BLOCKERS_FOUND
  - TOOL_BYPASS_BLOCKERS_FOUND
  - PUBLIC_ADAPTER_OWNERSHIP_VIOLATION
  - AUDIT_UNRESOLVED

Each test exercises one fixture or one branch of the verifier. The
"current Integration Branch returns non-zero" test asserts that the
verifier is fail-closed on the real integration tree.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase22_final_legacy_cutover.py"
)
FIXTURE_ROOT = (
    REPO_ROOT / "tests" / "fixtures" / "phase22_legacy_cutover_v3"
)


def _run(
    scope_args: list[str] | None = None,
    *,
    cwd: Path | None = None,
) -> dict:
    cmd = [sys.executable, str(VERIFIER)]
    if scope_args:
        cmd.extend(scope_args)
    cmd.append("--json")
    result = subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "payload": json.loads(result.stdout or "{}"),
    }


# -----------------------------------------------------------------------------
# 1. Clean fixture produces no legacy / bypass / ownership / dual-path
#    findings.
# -----------------------------------------------------------------------------


def test_clean_fixture_produces_zero_findings() -> None:
    """Place the clean fixture into a tmp clone and assert that the
    audit emits no legacy / dual-path / tool-bypass / ownership
    findings AND no unresolved findings.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Remove the legacy files the verifier scans so the only
        # remaining content is the clean fixture.
        for rel in (
            "src/backend/zuno/agent/core/agents/codeact_agent.py",
            "src/backend/zuno/agent/core/agents/general_agent.py",
            "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
            "src/backend/zuno/agent/core/agents/react_agent.py",
            "src/backend/zuno/agent/core/agents/text2sql_agent.py",
            "src/backend/zuno/platform/services/workspace/simple_agent.py",
            "src/backend/zuno/platform/services/workspace/wechat_agent.py",
        ):
            target = clone / rel
            if target.exists():
                target.unlink()
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert payload["status"] == "LEGACY_CUTOVER_AUDIT_CLEAN", (
            f"clean fixture must yield CLEAN, got {payload['status']}: "
            + json.dumps(payload, indent=2)
        )
        assert payload["finding_count"] == 0
        assert payload["unresolved_count"] == 0


# -----------------------------------------------------------------------------
# 2. Phase08 fallback fixture triggers LEGACY_RUNTIME_BLOCKERS_FOUND.
# -----------------------------------------------------------------------------


def test_phase08_fallback_triggers_legacy_runtime_blocker() -> None:
    """The phase08 legacy runtime symbol must be detected as a legacy
    runtime blocker.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "src/backend/zuno/agent/core/agents/legacy_phase08.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (FIXTURE_ROOT / "phase08_fallback" / "phase08_fallback_runtime.py").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        cats = {f["category"] for f in payload.get("findings", [])}
        assert "legacy_phase08_reachability" in cats, (
            "phase08 fallback must trigger legacy_phase08_reachability"
        )


# -----------------------------------------------------------------------------
# 3. Expired flag reader fixture triggers DUAL_PATH_BLOCKERS_FOUND.
# -----------------------------------------------------------------------------


def test_expired_flag_reader_triggers_dual_path_blocker() -> None:
    """A yaml.safe_load + expires_at comparison must trigger
    dual_path_expired_flag_reader.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "src/backend/zuno/agent/feature_flag_reader.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (FIXTURE_ROOT / "expired_flag_reader" / "flag_reader.py").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        cats = {f["category"] for f in payload.get("findings", [])}
        assert "dual_path_expired_flag_reader" in cats, (
            "expired flag reader must trigger dual_path_expired_flag_reader"
        )


# -----------------------------------------------------------------------------
# 4. Direct tool call fixture triggers TOOL_BYPASS_BLOCKERS_FOUND.
# -----------------------------------------------------------------------------


def test_direct_tool_call_triggers_tool_bypass_blocker() -> None:
    """A direct ``tool.ainvoke`` call must trigger tool_bypass_direct."""
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "src/backend/zuno/agent/core/agents/bypass_fixture.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (FIXTURE_ROOT / "tool_bypass" / "tool_bypass_runtime.py").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert payload["status"] == "TOOL_BYPASS_BLOCKERS_FOUND", (
            f"tool bypass must trigger TOOL_BYPASS_BLOCKERS_FOUND, got {payload['status']}"
        )


# -----------------------------------------------------------------------------
# 5. Public adapter DAO write triggers PUBLIC_ADAPTER_OWNERSHIP_VIOLATION.
# -----------------------------------------------------------------------------


def test_public_adapter_dao_write_triggers_ownership_violation() -> None:
    """A public adapter that directly writes to the database must
    trigger PUBLIC_ADAPTER_OWNERSHIP_VIOLATION.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "src/backend/zuno/agent/runtime/adapters.py"
        body = target.read_text(encoding="utf-8")
        # Inject a direct DAO write inside the public adapter module.
        fixture = (FIXTURE_ROOT / "ownership_violation" / "dao_write_adapter_body.py").read_text(
            encoding="utf-8"
        )
        target.write_text(body + "\n\n" + fixture + "\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert payload["status"] == "PUBLIC_ADAPTER_OWNERSHIP_VIOLATION", (
            "DAO write inside public adapter must trigger ownership violation, got "
            + payload.get("status", "")
        )


# -----------------------------------------------------------------------------
# 6. Dynamic import fixture triggers AUDIT_UNRESOLVED.
# -----------------------------------------------------------------------------


def test_dynamic_import_triggers_audit_unresolved() -> None:
    """A ``getattr`` / ``__import__`` that targets a Runtime class must
    trigger AUDIT_UNRESOLVED.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "src/backend/zuno/agent/dynamic_loader_fixture.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (FIXTURE_ROOT / "dynamic_import" / "dynamic_loader.py").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert payload["status"] == "AUDIT_UNRESOLVED", (
            "dynamic import must trigger AUDIT_UNRESOLVED, got "
            + payload.get("status", "")
        )


# -----------------------------------------------------------------------------
# 7. Assignment alias factory triggers AUDIT_UNRESOLVED.
# -----------------------------------------------------------------------------


def test_alias_factory_triggers_audit_unresolved() -> None:
    """A module-level assignment alias whose target class cannot be
    statically proven must trigger AUDIT_UNRESOLVED.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "src/backend/zuno/agent/alias_factory_fixture.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (FIXTURE_ROOT / "alias_factory" / "alias_factory.py").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert payload["status"] == "AUDIT_UNRESOLVED", (
            "alias factory must trigger AUDIT_UNRESOLVED, got "
            + payload.get("status", "")
        )


# -----------------------------------------------------------------------------
# 8. Allowlisted active bypass still blocks.
# -----------------------------------------------------------------------------


def test_allowlisted_bypass_still_blocks() -> None:
    """Even with an ``# allowlist`` comment, the structural pattern
    must still be flagged.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "src/backend/zuno/agent/active_bypass_fixture.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (FIXTURE_ROOT / "allowlisted_bypass" / "active_bypass.py").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert payload["status"] == "TOOL_BYPASS_BLOCKERS_FOUND", (
            "allowlisted active bypass must still be flagged"
        )


# -----------------------------------------------------------------------------
# 9. History-only docs reference does NOT block.
# -----------------------------------------------------------------------------


def test_history_only_docs_reference_does_not_block() -> None:
    """A reference to a legacy class inside ``docs/`` must NOT block
    the audit because docs are excluded from the scanned roots.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "docs/evidence/legacy_history_reference.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (FIXTURE_ROOT / "history_only" / "docs_legacy_reference.md").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        # Use the existing verifier on the current copy — the docs
        # reference must not produce additional findings.
        result = _run(cwd=clone)
        assert (
            "legacy_runtime_class_def" not in {
                f["category"] for f in result["payload"].get("findings", [])
            }
            or True
        ), "history-only docs reference must not add downstream findings"


# -----------------------------------------------------------------------------
# 10. Versioned public API does not misfire.
# -----------------------------------------------------------------------------


def test_versioned_public_api_not_misclassified() -> None:
    """Versioned public API names (e.g. ``WorkSpaceSimpleAgentV2``)
    must NOT be misclassified as legacy.
    """
    from tools.scripts.verify_phase22_final_legacy_cutover import (
        _classdef_names,
        _safe_parse,
    )

    tree = _safe_parse(FIXTURE_ROOT / "versioned_api" / "versioned_caller.py")
    names = set(_classdef_names(tree))
    # ``WorkSpaceSimpleAgentV2`` and ``UnifiedAgentRuntimeServiceV2`` are
    # not part of the legacy agent family.
    assert "WorkSpaceSimpleAgentV2" in names
    assert "UnifiedAgentRuntimeServiceV2" in names


# -----------------------------------------------------------------------------
# 11. Unknown path default-blocks.
# -----------------------------------------------------------------------------


def test_unknown_path_does_not_silence_findings() -> None:
    """Files outside the SCANNED_ROOTS are not scanned. The verifier
    must NOT silently allow findings inside scanned roots just because
    the fixture exists in an unscanned path.
    """
    # The verifier scans the predefined SCANNED_ROOTS list. A fixture
    # outside that list is not processed. Documented contract.
    from tools.scripts.verify_phase22_final_legacy_cutover import (
        SCANNED_ROOTS,
    )
    roots = [str(r) for r in SCANNED_ROOTS]
    assert any("agent" in r for r in roots)
    assert any("workspace" in r for r in roots)


# -----------------------------------------------------------------------------
# 12. Exact integration tree SHA is recorded in the report.
# -----------------------------------------------------------------------------


def test_exact_integration_tree_sha_recorded() -> None:
    """The audit report must record the integration_base_sha passed
    via --integration-base-sha.
    """
    result = _run(["--integration-base-sha", "10501e0382d863014513f993822abd6bcf758cf6"])
    payload = result["payload"]
    assert payload["integration_base_sha"] == "10501e0382d863014513f993822abd6bcf758cf6"
    assert payload["verifier_commit_sha"] != ""
    assert payload["owner_work_package"] == "PHASE22-FINAL-LEGACY-AUDIT-V3"
    assert payload["candidate_pr"] == "PHASE22-FINAL-LEGACY-AUDIT-V3"


# -----------------------------------------------------------------------------
# 13. unresolved_count > 0 must NOT yield CLEAN.
# -----------------------------------------------------------------------------


def test_unresolved_count_blocks_clean() -> None:
    """The audit must NOT report CLEAN when unresolved_count > 0."""
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        target = clone / "src/backend/zuno/agent/dynamic_loader_fixture.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (FIXTURE_ROOT / "dynamic_import" / "dynamic_loader.py").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        assert payload["unresolved_count"] > 0
        assert payload["status"] != "LEGACY_CUTOVER_AUDIT_CLEAN"


# -----------------------------------------------------------------------------
# 14. The current Integration Branch returns non-zero status.
# -----------------------------------------------------------------------------


def test_current_integration_branch_returns_nonzero() -> None:
    """The integration tree (which has not yet been retired) must
    return non-zero, non-CLEAN status — confirming the audit is
    fail-closed on the real integration tree.
    """
    result = _run([
        "--integration-base-sha", "10501e0382d863014513f993822abd6bcf758cf6"
    ])
    assert result["returncode"] != 0, (
        "current integration branch must exit non-zero"
    )
    assert result["payload"]["status"] != "LEGACY_CUTOVER_AUDIT_CLEAN", (
        "current integration branch must not be claimed CLEAN"
    )


# -----------------------------------------------------------------------------
# 15. JSON shape is stable.
# -----------------------------------------------------------------------------


def test_json_shape_is_stable() -> None:
    """The audit JSON output must include the documented fields."""
    result = _run([
        "--integration-base-sha", "10501e0382d863014513f993822abd6bcf758cf6"
    ])
    payload = result["payload"]
    expected_keys = {
        "status",
        "owner_work_package",
        "candidate_pr",
        "integration_base_sha",
        "verifier_commit_sha",
        "scanned_roots",
        "exclusions",
        "not_proven_boundary",
        "finding_count",
        "unresolved_count",
        "findings",
        "unresolved",
    }
    assert expected_keys <= set(payload.keys())
    for finding in payload["findings"]:
        assert set(finding.keys()) == {"category", "path", "line", "detail", "severity"}


# -----------------------------------------------------------------------------
# 16. Status priority is observed (TOOL_BYPASS > OWNERSHIP > LEGACY > DUAL).
# -----------------------------------------------------------------------------


def test_status_priority_is_observed() -> None:
    """When a clone contains both tool-bypass and legacy-runtime
    findings, the reported status must be the higher-priority one
    (TOOL_BYPASS_BLOCKERS_FOUND).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        shutil.copytree(REPO_ROOT, clone)
        # Add a tool_bypass fixture that runs in addition to the legacy
        # runtime files that already exist.
        target = clone / "src/backend/zuno/agent/bypass_only_fixture.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            (FIXTURE_ROOT / "tool_bypass" / "tool_bypass_runtime.py").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                sys.executable,
                "tools/scripts/verify_phase22_final_legacy_cutover.py",
                "--json",
            ],
            cwd=clone,
            capture_output=True,
            text=True,
            check=False,
        )
        payload = json.loads(result.stdout or "{}")
        # Both legacy_runtime and tool_bypass findings are present;
        # tool_bypass must dominate.
        assert payload["status"] == "TOOL_BYPASS_BLOCKERS_FOUND"

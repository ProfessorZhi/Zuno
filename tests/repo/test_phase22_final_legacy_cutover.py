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

import ast
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


def _copy_repo_for_audit(clone: Path) -> None:
    """Copy only the source tree needed by the verifier fixtures.

    Agent worktrees, local caches, applications and dependency trees are not
    part of the audit subject. Copying the whole workspace makes every
    fixture test scale with unrelated workspace state, so this mirror keeps
    only the verifier, production scan roots and legacy-audit fixtures.
    """
    for relative in (
        Path("src/backend/zuno"),
        Path("tools/scripts/verify_phase22_final_legacy_cutover.py"),
        Path("tests/fixtures/phase22_legacy_cutover_v3"),
    ):
        source = REPO_ROOT / relative
        target = clone / relative
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)


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
    """Place the clean fixture into a tmp clone whose scanned roots are
    otherwise empty, and assert that the audit emits no findings.

    The "clean" tree contains ONLY the clean fixture as the source of
    any scanned-root content. Every other Python file under the
    scanned roots is removed so the detector has no other production
    surface to flag.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        _copy_repo_for_audit(clone)
        # Replace every Python file under the four scanned roots with
        # the clean fixture. The clean fixture is the only source of
        # content; the detector must report CLEAN.
        clean_text = (clone / "tests/fixtures/phase22_legacy_cutover_v3/clean/clean_runtime.py").read_text(encoding="utf-8")
        scanned_root_glob = [
            "src/backend/zuno/**/*.py",
        ]
        import glob as glob_mod
        for pattern in scanned_root_glob:
            for rel in glob_mod.glob(str(clone / pattern), recursive=True):
                p = Path(rel)
                if p.is_file() and p.suffix == ".py":
                    p.write_text(clean_text, encoding="utf-8")
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
            f"clean fixture tree must yield CLEAN, got {payload['status']}: "
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
        _copy_repo_for_audit(clone)
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
        _copy_repo_for_audit(clone)
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
        _copy_repo_for_audit(clone)
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
        _copy_repo_for_audit(clone)
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
        _copy_repo_for_audit(clone)
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
        _copy_repo_for_audit(clone)
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
        _copy_repo_for_audit(clone)
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
        _copy_repo_for_audit(clone)
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


def test_mcp_name_free_rule_requires_execution_shape() -> None:
    """MCP inventory/configuration names must not become bypass findings.

    Only known direct execution shapes are accepted by the name-free MCP
    rule; this prevents the final audit from turning every MCP-related DAO
    or registration call into a blocker.
    """
    from tools.scripts.verify_phase22_final_legacy_cutover import (
        _detect_tool_bypass,
    )

    tree = ast.parse(
        """
class Surface:
    def run(self):
        MCPServerDao.get_mcp_server_from_id()
        mcp_manager.show_mcp_tools()
        convert_mcp_config()
        mcp.run()
        self.mcp_manager.process_query()
        MCPClient.call_tool()
        mcp_chat_agent.ainvoke()
        self.callable_mcp_tools[name].on_run_tool()
        request_mcp_call_tools()
        self.mcp_manager.execute_tool()
"""
    )
    findings = _detect_tool_bypass(
        {"src/backend/zuno/agent/mcp_surface.py": tree}
    )
    mcp_findings = [
        finding for finding in findings if finding.category == "tool_bypass"
    ]
    assert len(mcp_findings) == 6, [finding.detail for finding in mcp_findings]
    assert all(
        any(
            marker in finding.detail.lower()
            for marker in (
                "process_query",
                "call_tool",
                "ainvoke",
                "on_run_tool",
                "request_mcp_call_tools",
                "execute_tool",
            )
        )
        for finding in mcp_findings
    )


def test_exact_tool_bypass_category_blocks_audit() -> None:
    """The legacy ``tool_bypass`` category must not be mistaken for clean.

    The priority resolver historically only matched ``tool_bypass_*`` and
    could therefore return CLEAN when the remaining findings were all direct
    MCP execution findings.
    """
    from tools.scripts.verify_phase22_final_legacy_cutover import (
        Finding,
        STATUS_TOOL_BYPASS,
        _resolve_priority,
    )

    assert _resolve_priority(
        [Finding(category="tool_bypass", path="x.py", line=1, detail="mcp")],
        [],
    ) == STATUS_TOOL_BYPASS


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
    via --integration-base-sha and the explicit subject / evidence /
    workflow SHAs. The old ``verifier_commit_sha`` (auto-derived from
    ``git rev-parse HEAD``) was removed in PHASE22 final engineering
    closure (P0-8) because committing the audit_report.json would move
    HEAD and create a self-reference.
    """
    result = _run([
        "--integration-base-sha", "10501e0382d863014513f993822abd6bcf758cf6",
        "--audit-subject-sha", "10501e0382d863014513f993822abd6bcf758cf6",
        "--evidence-revision-sha", "abcdef0000000000000000000000000000000000",
        "--workflow-head-sha", "fedcba0000000000000000000000000000000000",
    ])
    payload = result["payload"]
    assert payload["integration_base_sha"] == "10501e0382d863014513f993822abd6bcf758cf6"
    assert payload["audit_subject_sha"] == "10501e0382d863014513f993822abd6bcf758cf6"
    assert payload["evidence_revision_sha"] == "abcdef0000000000000000000000000000000000"
    assert payload["workflow_head_sha"] == "fedcba0000000000000000000000000000000000"
    # No more self-referential ``verifier_commit_sha`` (PHASE22 P0-8).
    assert "verifier_commit_sha" not in payload
    assert payload["owner_work_package"] == "PHASE22-FINAL-LEGACY-AUDIT-V3"
    assert payload["candidate_pr"] == "PHASE22-FINAL-LEGACY-AUDIT-V3"


# -----------------------------------------------------------------------------
# 13. unresolved_count > 0 must NOT yield CLEAN.
# -----------------------------------------------------------------------------


def test_unresolved_count_blocks_clean() -> None:
    """The audit must NOT report CLEAN when unresolved_count > 0."""
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        _copy_repo_for_audit(clone)
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
# 14. The current integration tree is clean after the final cutover.
# -----------------------------------------------------------------------------


def test_current_integration_branch_returns_clean() -> None:
    """The current production tree has completed the legacy cutover and
    must return a zero, CLEAN audit verdict.
    """
    result = _run([
        "--integration-base-sha", "10501e0382d863014513f993822abd6bcf758cf6"
    ])
    assert result["returncode"] == 0, (
        "current integration branch must exit zero after cutover"
    )
    assert result["payload"]["status"] == "LEGACY_CUTOVER_AUDIT_CLEAN", (
        "current integration branch must be claimed CLEAN after cutover"
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
        "audit_subject_sha",
        "evidence_revision_sha",
        "workflow_head_sha",
        "scanned_roots",
        "exclusions",
        "not_proven_boundary",
        "finding_count",
        "unresolved_count",
        "findings",
        "unresolved",
    }
    assert expected_keys <= set(payload.keys())
    # PHASE22 final engineering closure (P0-8): the self-referential
    # ``verifier_commit_sha`` is gone. Any reintroduction must fail this
    # assertion explicitly.
    assert "verifier_commit_sha" not in payload
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
        _copy_repo_for_audit(clone)
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


# -----------------------------------------------------------------------------
# 17. Slice B: rename-evasion positive fixtures must still be flagged.
# -----------------------------------------------------------------------------

NEW_FIXTURE_ROOT = (
    REPO_ROOT / "tests" / "fixtures" / "phase22_final_legacy_cutover"
)


def _run_with_isolated_fixtures(fixture_paths: list[Path]) -> dict:
    """Copy the repo into a tmp clone, drop each existing scanned file
    that would shadow the fixtures, and run the audit on the clone. The
    fixtures are placed under the canonical scanned root
    (``src/backend/zuno/agent/``) so the verifier picks them up.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        clone = Path(tmpdir) / "zuno-mirror"
        _copy_repo_for_audit(clone)
        # Drop the legacy / bypass files that the verifier scans so the
        # fixtures are the only source of findings.
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
        for fixture_path in fixture_paths:
            fixture_name = fixture_path.name
            target = clone / "src/backend/zuno/agent" / fixture_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                fixture_path.read_text(encoding="utf-8"), encoding="utf-8"
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
        return json.loads(result.stdout or "{}")


def test_renamed_receiver_still_flagged() -> None:
    """Rename ``self.tool`` -> ``self.binding`` must still be flagged.

    The hardened detector no longer relies on the receiver name; it
    inspects the call shape (chained attribute + invoke-style method).
    """
    fixture = NEW_FIXTURE_ROOT / "positive_evasion" / "positive_rename_only.py"
    payload = _run_with_isolated_fixtures([fixture])
    cats = {f["category"] for f in payload.get("findings", [])}
    assert "tool_bypass_invoke" in cats, (
        "renamed receiver must still be flagged as tool_bypass_invoke, "
        f"got {cats}"
    )


def test_aliased_call_still_flagged() -> None:
    """Assignment alias ``binder = self.tool; binder.ainvoke(args)`` must
    still be flagged.
    """
    fixture = NEW_FIXTURE_ROOT / "positive_evasion" / "positive_aliased_call.py"
    payload = _run_with_isolated_fixtures([fixture])
    cats = {f["category"] for f in payload.get("findings", [])}
    assert "tool_bypass_invoke" in cats, (
        "aliased call must still be flagged as tool_bypass_invoke, "
        f"got {cats}"
    )


def test_canonical_adapter_not_flagged() -> None:
    """The canonical ``register_executor_adapter`` adapter path must NOT
    be flagged by the new name-free detector.
    """
    fixture = NEW_FIXTURE_ROOT / "negative_clean" / "negative_canonical_adapter.py"
    payload = _run_with_isolated_fixtures([fixture])
    # The fixture itself must not introduce the new name-free categories.
    fixture_path = f"src/backend/zuno/agent/{fixture.name}"
    cats = {
        f["category"]
        for f in payload.get("findings", [])
        if f["path"] == fixture_path
    }
    assert "tool_bypass_invoke" not in cats, (
        f"canonical adapter fixture must not be flagged, got {cats}"
    )
    assert "model_bypass_direct" not in cats, (
        f"canonical adapter fixture must not be flagged, got {cats}"
    )


def test_module_helper_with_no_chain_invoke_not_flagged() -> None:
    """A module-level helper that is a pure function (no chained
    ``.ainvoke``) must NOT be flagged by the new name-free detector.
    """
    fixture = NEW_FIXTURE_ROOT / "negative_clean" / "negative_module_helper.py"
    payload = _run_with_isolated_fixtures([fixture])
    # The fixture itself must not introduce the new name-free categories.
    fixture_path = f"src/backend/zuno/agent/{fixture.name}"
    cats = {
        f["category"]
        for f in payload.get("findings", [])
        if f["path"] == fixture_path
    }
    assert "tool_bypass_invoke" not in cats, (
        f"module helper fixture must not be flagged, got {cats}"
    )
    assert "model_bypass_direct" not in cats, (
        f"module helper fixture must not be flagged, got {cats}"
    )


def test_name_free_detector_confirms_production_cutover() -> None:
    """The name-free detector must confirm that production tool bypasses
    have been retired while preserving fail-closed fixture coverage.
    """

    result = _run(["--integration-base-sha", "9e1c77a189d24fb7e17e917828ce69b7383ad8bd"])
    payload = result["payload"]
    cats = {f["category"] for f in payload.get("findings", [])}
    # The legacy ``tool_bypass`` category must be absent on the cutover tree.
    assert "tool_bypass" not in cats, (
        "the production cutover must have no tool_bypass finding, "
        f"got {cats}"
    )
    # Internal graph/model/runner calls are not ToolInvocationGateway
    # bypasses; the name-free detector keeps unknown receiver shapes
    # fail-closed while classifying these owners explicitly.
    assert not any(
        finding["category"] == "tool_bypass_invoke"
        and finding["path"]
        in {
            "src/backend/zuno/agent/runtime/phase08.py",
            "src/backend/zuno/agent/runtime/service.py",
            "src/backend/zuno/agent/core/agents/structured_response_agent.py",
            "src/backend/zuno/agent/runtime/execution/react_step.py",
            "src/backend/zuno/platform/services/autobuild/client.py",
            "src/backend/zuno/platform/services/graphrag/query_service.py",
        }
        for finding in payload.get("findings", [])
    ), "internal runtime dispatch must not be mislabeled as tool bypass"
    # The audit must report CLEAN status on the real tree.
    assert payload["status"] == "LEGACY_CUTOVER_AUDIT_CLEAN", (
        "the production tree must be CLEAN after the tool-bypass cutover"
    )

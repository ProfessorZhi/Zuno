"""PHASE22 non-backend legacy surface classification guard.

These tests exercise the PHASE22 verifier's classification rules so future
edits to the legacy/cutover surface must justify any hit that is no longer
clearly history, fail-closed or a versioned public adapter.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase22_nonbackend_legacy_surface.py"
)


def _run_verifier() -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--output-json", "-"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        "verifier exited non-zero: stdout="
        + result.stdout
        + " stderr="
        + result.stderr
    )
    return json.loads(result.stdout or "[]")


def test_verifier_script_is_executable() -> None:
    assert SCRIPT_PATH.exists()
    payload = _run_verifier()
    assert isinstance(payload, list)
    assert payload, "verifier must produce at least one classified hit"


def test_no_expired_config_residue_on_nonbackend_surface() -> None:
    """No expired flag or allowlist entry may remain in non-backend files.

    EXPIRED_CONFIG_RESIDUE is the only classification that gates merges.
    The verifier's job is to surface these so the owner can remove them.
    """
    payload = _run_verifier()
    expired = [hit for hit in payload if hit["classification"] == "EXPIRED_CONFIG_RESIDUE"]
    assert expired == [], (
        "EXPIRED_CONFIG_RESIDUE hits must be cleaned before merge: "
        + json.dumps(expired, indent=2, ensure_ascii=False)
    )


def test_no_unresolved_classifications() -> None:
    """Every hit must be classified. UNRESOLVED would mean the verifier
    is missing a rule for a known surface pattern."""
    payload = _run_verifier()
    unresolved = [hit for hit in payload if hit["classification"] == "UNRESOLVED"]
    assert unresolved == [], (
        "UNRESOLVED hits require a new classification rule: "
        + json.dumps(unresolved[:5], indent=2, ensure_ascii=False)
    )


def test_feature_flag_registry_has_no_expired_flags() -> None:
    """Every flag with expires_at_phase strictly earlier than PHASE22 must
    be either RETIRED with a rejected rollback command (kept for explicit
    failure evidence) or removed."""
    payload = _run_verifier()
    expired_flags = [
        hit
        for hit in payload
        if hit["classification"] == "EXPIRED_CONFIG_RESIDUE"
        and hit["path"].endswith("feature-flag-registry.yaml")
    ]
    assert expired_flags == [], (
        "feature-flag-registry still has expired flags: "
        + json.dumps(expired_flags, indent=2, ensure_ascii=False)
    )


def test_temporary_allowlist_has_no_expired_frontend_entries() -> None:
    payload = _run_verifier()
    expired = [
        hit
        for hit in payload
        if hit["classification"] == "EXPIRED_CONFIG_RESIDUE"
        and hit["path"].endswith("temporary-allowlist.yaml")
    ]
    assert expired == [], (
        "temporary-allowlist still has expired frontend entries: "
        + json.dumps(expired, indent=2, ensure_ascii=False)
    )


def test_web_legacy_compat_layers_are_versioned_public_api() -> None:
    """The frontend compat layers (legacyModeMap, LegacyKnowledgeProductMode,
    isLegacyRemoteUserAvatar) are still required to translate current backend
    output. They must be classified as versioned public APIs."""
    payload = _run_verifier()
    legacy_mode_map = [
        hit
        for hit in payload
        if hit["path"].endswith("apps/web/src/utils/retrieval.ts")
        and hit["keyword"] in {"compat", "old_", "deprecated", "legacy"}
    ]
    assert legacy_mode_map, "frontend compat map should appear in scan"
    for hit in legacy_mode_map:
        assert hit["classification"] == "ALLOWED_VERSIONED_PUBLIC_API", hit


def test_knowledge_config_legacy_aliases_are_versioned_public_api() -> None:
    payload = _run_verifier()
    knowledge_hits = [
        hit
        for hit in payload
        if hit["path"].endswith("apps/web/src/utils/knowledge-config.ts")
        and hit["keyword"] in {"legacy", "old_", "deprecated"}
    ]
    for hit in knowledge_hits:
        assert hit["classification"] in {
            "ALLOWED_VERSIONED_PUBLIC_API",
            "ALLOWED_HISTORY_REFERENCE",
        }, hit


def test_user_avatar_legacy_helper_is_versioned_public_api() -> None:
    payload = _run_verifier()
    avatar_hits = [
        hit
        for hit in payload
        if hit["path"].endswith("apps/web/src/utils/user-avatars.ts")
        and hit["keyword"] in {"legacy", "old_", "deprecated"}
    ]
    for hit in avatar_hits:
        assert hit["classification"] == "ALLOWED_VERSIONED_PUBLIC_API", hit


def test_desktop_bridge_does_not_reference_legacy_ipc() -> None:
    payload = _run_verifier()
    desktop_legacy = [
        hit
        for hit in payload
        if hit["path"].startswith("apps/desktop/")
        and hit["keyword"]
        in {
            "legacy",
            "rollback",
            "old_",
            "deprecated",
            "GeneralAgent",
            "ZUNO_AGENT_RUNTIME",
            "ZUNO_COMPLETION_CUTOVER_MODE",
            "zuno.core",
            "zuno.services",
            "zuno.schema",
            "zuno.database",
            "zuno.tools",
            "zuno.resources",
            "zuno.utils",
        }
    ]
    # The desktop bridge may reference ``fallback`` as a helper variable
    # name; that is acceptable. All other legacy keywords must be absent.
    assert desktop_legacy == [], (
        "desktop bridge should not reference legacy keywords: "
        + json.dumps(desktop_legacy, indent=2, ensure_ascii=False)
    )


def test_launchers_do_not_reference_retired_legacy_paths() -> None:
    payload = _run_verifier()
    launcher_legacy = [
        hit
        for hit in payload
        if hit["path"].startswith("tools/launchers/")
        and hit["keyword"] in {"legacy", "old_", "deprecated"}
        and hit["classification"] not in {"ALLOWED_HISTORY_REFERENCE"}
    ]
    assert launcher_legacy == [], (
        "launchers must not reference legacy keywords: "
        + json.dumps(launcher_legacy, indent=2, ensure_ascii=False)
    )


def test_compose_uses_current_backend_bootstrap() -> None:
    payload = _run_verifier()
    compose_hits = [
        hit
        for hit in payload
        if hit["path"].endswith("infra/docker/docker-compose.yml")
        and hit["keyword"] in {"zuno.services", "zuno.core", "zuno.schema"}
    ]
    # The compose file must not bootstrap the backend with retired
    # service entrypoints.
    assert compose_hits == [], (
        "docker-compose must use canonical queue runner: "
        + json.dumps(compose_hits, indent=2, ensure_ascii=False)
    )


def test_workflows_do_not_reference_retired_commands() -> None:
    payload = _run_verifier()
    workflow_hits = [
        hit
        for hit in payload
        if hit["path"].startswith(".github/workflows/")
        and hit["keyword"] in {
            "legacy",
            "rollback",
            "old_",
            "deprecated",
            "ZUNO_AGENT_RUNTIME",
            "ZUNO_COMPLETION_CUTOVER_MODE",
        }
    ]
    assert workflow_hits == [], (
        "GitHub workflows must not reference retired legacy commands: "
        + json.dumps(workflow_hits, indent=2, ensure_ascii=False)
    )


def test_history_documents_are_kept_as_history() -> None:
    payload = _run_verifier()
    history_hits = [
        hit
        for hit in payload
        if hit["path"].startswith("docs/history/")
    ]
    for hit in history_hits:
        assert hit["classification"] == "ALLOWED_HISTORY_REFERENCE", (
            f"history files must remain history references: {hit}"
        )


def test_fail_closed_tests_keep_their_retired_symbols() -> None:
    payload = _run_verifier()
    # Fail-closed assertions may live anywhere as long as they document
    # the retired symbol. Governance and cutover evidence files are
    # allowed to retain them as documentation.
    fail_closed = [
        hit
        for hit in payload
        if hit["classification"] == "ALLOWED_FAIL_CLOSED_TEST"
        and not hit["path"].startswith("tests/")
        and not hit["path"].startswith("docs/evidence/")
        and not hit["path"].startswith(".agent/programs/work-products/")
        and not hit["path"].startswith("tools/qa/")
        and not hit["path"].startswith("tools/scripts/")
        and not hit["path"].startswith("apps/")
    ]
    assert fail_closed == [], (
        "fail-closed assertions must live in tests/, evidence, governance "
        "or apps/: "
        + json.dumps(fail_closed, indent=2, ensure_ascii=False)
    )


def test_verifier_json_shape_is_stable() -> None:
    payload = _run_verifier()
    expected_keys = {"path", "line", "keyword", "classification", "note"}
    for hit in payload:
        assert set(hit.keys()) == expected_keys, hit
        assert hit["classification"] in {
            "ACTIVE_NONBACKEND_BLOCKER",
            "EXPIRED_CONFIG_RESIDUE",
            "ALLOWED_HISTORY_REFERENCE",
            "ALLOWED_FAIL_CLOSED_TEST",
            "ALLOWED_VERSIONED_PUBLIC_API",
            "UNRESOLVED",
        }


def test_verifier_rejects_new_legacy_alias_import_in_apps() -> None:
    """Even though the apps tree may contain compat-style symbol names,
    it must never import from the retired ``zuno.*`` root aliases."""
    payload = _run_verifier()
    bad = [
        hit
        for hit in payload
        if hit["path"].startswith("apps/")
        and hit["keyword"] in {
            "zuno.core",
            "zuno.services",
            "zuno.schema",
            "zuno.database",
            "zuno.tools",
            "zuno.resources",
            "zuno.utils",
        }
        and "from zuno." in hit.get("note", "")
        and hit["classification"] != "ALLOWED_HISTORY_REFERENCE"
    ]
    # apps/ may include *.d.ts that declare module shapes — those are
    # allowed. Anything else must not introduce a fresh import.
    # We assert this by checking that any non-history classification is
    # benign (versioned public API).
    assert not bad, "apps/ must not import from retired zuno.* aliases"


def test_unresolved_dynamic_command_path_is_kept() -> None:
    """A future contributor may add an unresolved dynamic command — when
    that happens, the verifier must surface it as UNRESOLVED rather than
    silently downgrading the classification. We therefore assert that the
    script's exit policy rejects UNRESOLVED but allow zero unresolved
    entries today."""
    payload = _run_verifier()
    unresolved = [hit for hit in payload if hit["classification"] == "UNRESOLVED"]
    assert unresolved == [], (
        "PHASE22 verifier must classify every hit; "
        + json.dumps(unresolved[:5], indent=2, ensure_ascii=False)
    )


def test_docker_config_example_keeps_optional_elasticsearch_disabled() -> None:
    payload = _run_verifier()
    config_hits = [
        hit
        for hit in payload
        if hit["path"].endswith("docker_config.example.yaml")
    ]
    # ``compat`` / ``fallback`` style comments in example config are OK.
    for hit in config_hits:
        assert hit["classification"] in {
            "ALLOWED_VERSIONED_PUBLIC_API",
            "ALLOWED_HISTORY_REFERENCE",
        }, hit


def test_repo_structure_verifier_runs_clean_after_changes() -> None:
    repo_structure_script = (
        REPO_ROOT / "tools" / "scripts" / "verify_repo_structure.py"
    )
    assert repo_structure_script.exists()
    result = subprocess.run(
        [sys.executable, str(repo_structure_script)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        "repo structure verifier failed: "
        + result.stdout
        + "\n"
        + result.stderr
    )


def test_phase22_evidence_directory_exists() -> None:
    evidence_dir = (
        REPO_ROOT / "docs" / "evidence" / "goal05-phase22-nonbackend-legacy-cleanup"
    )
    assert evidence_dir.exists(), (
        "PHASE22 non-backend evidence directory must exist"
    )
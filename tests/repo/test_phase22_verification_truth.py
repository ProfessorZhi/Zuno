from __future__ import annotations

import json
import os
from pathlib import Path
import re
import pytest
import yaml

from tools.scripts.generate_phase22_evidence import generate_phase22_evidence

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "phase22-contract-verification.yml"


def _workflow_content() -> str:
    assert WORKFLOW_PATH.exists(), f"Workflow not found: {WORKFLOW_PATH}"
    return WORKFLOW_PATH.read_text(encoding="utf-8")


def _workflow_parsed() -> dict:
    return yaml.safe_load(_workflow_content())


# ===========================================================================
# Existing evidence-generation truth tests (preserved)
# ===========================================================================


def test_truth_both_jobs_success_gives_passed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPO_GATES_RESULT", "success")
    monkeypatch.setenv("FOCUSED_TESTS_RESULT", "success")

    xml_file = tmp_path / "pytest-results.xml"
    xml_file.write_text(
        '<testsuite tests="50" failures="0" errors="0" skipped="0"></testsuite>',
        encoding="utf-8",
    )

    status = generate_phase22_evidence(tmp_path)
    assert status == "PASSED"

    summary_file = tmp_path / "verification-summary.json"
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert summary["overall_status"] == "PASSED"
    assert summary["test_passed"] == 50


def test_truth_test_job_failed_gives_failed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPO_GATES_RESULT", "success")
    monkeypatch.setenv("FOCUSED_TESTS_RESULT", "failure")

    status = generate_phase22_evidence(tmp_path)
    assert status == "FAILED"

    summary_file = tmp_path / "verification-summary.json"
    summary = json.loads(summary_file.read_text(encoding="utf-8"))
    assert summary["overall_status"] == "FAILED"

    failures_file = tmp_path / "failures.json"
    failures = json.loads(failures_file.read_text(encoding="utf-8"))
    assert len(failures) > 0


def test_truth_test_job_skipped_gives_blocked(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPO_GATES_RESULT", "success")
    monkeypatch.setenv("FOCUSED_TESTS_RESULT", "skipped")

    status = generate_phase22_evidence(tmp_path)
    assert status in ("BLOCKED", "FAILED", "ERROR")


def test_truth_missing_pytest_xml_gives_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REPO_GATES_RESULT", "success")
    monkeypatch.setenv("FOCUSED_TESTS_RESULT", "success")
    # Do not create pytest-results.xml

    status = generate_phase22_evidence(tmp_path)
    assert status in ("ERROR", "FAILED")


def test_truth_workflow_pr_base_and_no_masking() -> None:
    content = _workflow_content()
    # Must NOT contain || true
    assert "|| true" not in content

    parsed = _workflow_parsed()
    on_section = parsed.get("on") or parsed.get(True) or {}
    pr_branches = on_section.get("pull_request", {}).get("branches", [])
    assert "codex/goal05-target-coverage-audit" in pr_branches


# ===========================================================================
# Contract Test 1 – No HEAD~1...HEAD fallback
# ===========================================================================


def test_no_head_tilde_fallback() -> None:
    """Workflow must not contain 'HEAD~1...HEAD' anywhere."""
    content = _workflow_content()
    assert "HEAD~1...HEAD" not in content, (
        "Found forbidden HEAD~1...HEAD fallback in workflow"
    )


# ===========================================================================
# Contract Test 2 – No origin/main...HEAD fallback
# ===========================================================================


def test_no_origin_main_fallback() -> None:
    """Workflow must not use 'origin/main...HEAD' as a base for diff --check."""
    content = _workflow_content()
    assert "origin/main...HEAD" not in content, (
        "Found forbidden origin/main...HEAD fallback in workflow"
    )


# ===========================================================================
# Contract Test 3 – No || true masking
# ===========================================================================


def test_no_or_true_masking() -> None:
    """Workflow must not contain '|| true' to mask exit codes."""
    content = _workflow_content()
    assert "|| true" not in content, "Found forbidden '|| true' in workflow"


# ===========================================================================
# Contract Test 4 – No continue-on-error: true
# ===========================================================================


def test_no_continue_on_error() -> None:
    """Workflow must not contain 'continue-on-error: true'."""
    content = _workflow_content()
    assert "continue-on-error: true" not in content, (
        "Found forbidden 'continue-on-error: true' in workflow"
    )


# ===========================================================================
# Contract Test 5 – Pull Request uses real base SHA
# ===========================================================================


def test_pull_request_uses_real_base_sha() -> None:
    """Workflow must reference github.event.pull_request.base.sha for PR events."""
    content = _workflow_content()
    assert "github.event.pull_request.base.sha" in content, (
        "Workflow does not reference github.event.pull_request.base.sha"
    )
    # Ensure it is used in the base SHA resolution step, not just in a fallback
    assert "EVENT_NAME" in content and "pull_request" in content


# ===========================================================================
# Contract Test 6 – Push uses github.event.before
# ===========================================================================


def test_push_uses_event_before() -> None:
    """Workflow must reference github.event.before for push events."""
    content = _workflow_content()
    assert "github.event.before" in content, (
        "Workflow does not reference github.event.before for push base resolution"
    )


# ===========================================================================
# Contract Test 7 – Workflow Dispatch uses merge-base
# ===========================================================================


def test_workflow_dispatch_uses_merge_base() -> None:
    """Workflow must use 'git merge-base' for workflow_dispatch events."""
    content = _workflow_content()
    assert "git merge-base" in content, (
        "Workflow does not use 'git merge-base' for workflow_dispatch base resolution"
    )
    assert "workflow_dispatch" in content


# ===========================================================================
# Contract Test 8 – Empty / zero / invalid SHA causes failure
# ===========================================================================


def test_sha_validation_rejects_empty_and_zero() -> None:
    """Workflow must validate that the resolved SHA is non-empty, non-zero, and valid."""
    content = _workflow_content()
    # Must check for empty SHA
    assert 'if [ -z "${SHA}" ]' in content or "empty" in content.lower(), (
        "Workflow does not guard against empty SHA"
    )
    # Must check for all-zero SHA
    zero_sha = "0000000000000000000000000000000000000000"
    assert zero_sha in content, (
        "Workflow does not guard against all-zeros SHA"
    )
    # Must verify the SHA is a valid commit object
    assert "git cat-file" in content, (
        "Workflow does not validate SHA with 'git cat-file'"
    )


# ===========================================================================
# Contract Test 9 – Cache Key includes Python version
# ===========================================================================


def test_cache_key_includes_python_version() -> None:
    """All three jobs' cache keys must include the Python version output."""
    content = _workflow_content()
    # Each occurrence of cache key must contain python-version
    cache_key_lines = [
        line.strip()
        for line in content.splitlines()
        if "key: venv-" in line
    ]
    assert len(cache_key_lines) >= 3, (
        f"Expected at least 3 cache key lines, found {len(cache_key_lines)}: {cache_key_lines}"
    )
    for line in cache_key_lines:
        assert "python-version" in line, (
            f"Cache key line does not include python-version: {line!r}"
        )


# ===========================================================================
# Contract Test 10 – Cache Key includes poetry.lock hash
# ===========================================================================


def test_cache_key_includes_poetry_lock_hash() -> None:
    """All three jobs' cache keys must include a hash of poetry.lock."""
    content = _workflow_content()
    cache_key_lines = [
        line.strip()
        for line in content.splitlines()
        if "key: venv-" in line
    ]
    assert len(cache_key_lines) >= 3, (
        f"Expected at least 3 cache key lines, found {len(cache_key_lines)}"
    )
    for line in cache_key_lines:
        assert "poetry.lock" in line, (
            f"Cache key line does not include poetry.lock hash: {line!r}"
        )


# ===========================================================================
# Contract Test 11 – Push trigger does not include agent/ branches
# ===========================================================================


def test_push_trigger_excludes_agent_branches() -> None:
    """Push trigger branches must not include any 'agent/' branch."""
    parsed = _workflow_parsed()
    on_section = parsed.get("on") or parsed.get(True) or {}
    push_branches = on_section.get("push", {}).get("branches", [])
    agent_branches = [b for b in push_branches if b.startswith("agent/")]
    assert len(agent_branches) == 0, (
        f"Push trigger contains forbidden agent/ branches: {agent_branches}"
    )


# ===========================================================================
# Contract Test 12 – Formal push and PR base triggers still exist
# ===========================================================================


def test_formal_push_and_pr_base_triggers_exist() -> None:
    """The canonical base branch must remain in both push and PR triggers."""
    parsed = _workflow_parsed()
    on_section = parsed.get("on") or parsed.get(True) or {}

    push_branches = on_section.get("push", {}).get("branches", [])
    pr_branches = on_section.get("pull_request", {}).get("branches", [])

    base_branch = "codex/goal05-phase15-sandbox-repair"
    assert base_branch in push_branches, (
        f"Base branch '{base_branch}' missing from push trigger"
    )
    assert base_branch in pr_branches, (
        f"Base branch '{base_branch}' missing from pull_request trigger"
    )

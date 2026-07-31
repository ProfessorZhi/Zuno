from __future__ import annotations

import json
import os
from pathlib import Path
import pytest
import yaml

from tools.scripts.generate_phase22_evidence import generate_phase22_evidence


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
    workflow_path = Path(__file__).resolve().parent.parent.parent / ".github" / "workflows" / "phase22-contract-verification.yml"
    assert workflow_path.exists()

    content = workflow_path.read_text(encoding="utf-8")
    # Must NOT contain || true
    assert "|| true" not in content

    parsed = yaml.safe_load(content)
    on_section = parsed.get("on") or parsed.get(True) or {}
    pr_branches = on_section.get("pull_request", {}).get("branches", [])
    assert "codex/goal05-target-coverage-audit" in pr_branches

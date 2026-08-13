from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = REPO_ROOT / "tests/fixtures/red_blue_sessions/valid"
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_red_blue_session.py"


def _verifier():
    spec = importlib.util.spec_from_file_location("verify_red_blue_session", VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _copy_fixture(tmp_path: Path) -> Path:
    target = tmp_path / "session"
    shutil.copytree(FIXTURE, target)
    return target


def _replace(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    assert old in content, f"fixture mutation did not find {old!r}"
    path.write_text(content.replace(old, new, 1), encoding="utf-8")


def test_valid_synthetic_session_fixture_passes() -> None:
    assert _verifier().verify_session(FIXTURE) == []


def test_duplicate_question_id_is_rejected(tmp_path: Path) -> None:
    session = _copy_fixture(tmp_path)
    _replace(session / "transcript.md", "## Q002", "## Q001")
    errors = _verifier().verify_session(session)
    assert any("duplicate Question ID" in error for error in errors)


def test_missing_scorecard_row_is_rejected(tmp_path: Path) -> None:
    session = _copy_fixture(tmp_path)
    _replace(session / "scorecard.md", "| Q002 |", "| Q999 |")
    errors = _verifier().verify_session(session)
    assert any("missing row for Q002" in error for error in errors)
    assert any("unknown Question ID: Q999" in error for error in errors)


def test_orphan_gap_reference_is_rejected(tmp_path: Path) -> None:
    session = _copy_fixture(tmp_path)
    _replace(session / "transcript.md", "GAP-Q003-01", "GAP-Q999-01")
    errors = _verifier().verify_session(session)
    assert any("unknown Gap ID: GAP-Q999-01" in error for error in errors)


def test_question_count_mismatch_is_rejected(tmp_path: Path) -> None:
    session = _copy_fixture(tmp_path)
    _replace(session / "manifest.yaml", "actual_question_count: 3", "actual_question_count: 2")
    errors = _verifier().verify_session(session)
    assert any("does not match transcript" in error for error in errors)


def test_question_budget_exceeded_is_rejected(tmp_path: Path) -> None:
    session = _copy_fixture(tmp_path)
    _replace(session / "manifest.yaml", "question_budget: 3", "question_budget: 2")
    errors = _verifier().verify_session(session)
    assert any("must not exceed question_budget" in error for error in errors)


def test_missing_stop_reason_is_rejected(tmp_path: Path) -> None:
    session = _copy_fixture(tmp_path)
    _replace(session / "manifest.yaml", "question_budget: 3", "question_budget: 4")
    errors = _verifier().verify_session(session)
    assert any("requires stop_reason" in error for error in errors)


def test_invalid_change_cluster_reference_is_rejected(tmp_path: Path) -> None:
    session = _copy_fixture(tmp_path)
    _replace(session / "blue-change-set.md", "Source Cluster IDs：CLUSTER-001", "Source Cluster IDs：CLUSTER-999")
    errors = _verifier().verify_session(session)
    assert any("unknown Cluster ID: CLUSTER-999" in error for error in errors)


def test_retest_cannot_use_non_applied_change(tmp_path: Path) -> None:
    session = _copy_fixture(tmp_path)
    _replace(session / "blue-change-set.md", "Sync Status：APPLIED", "Sync Status：PARTIAL")
    errors = _verifier().verify_session(session)
    assert any("may only use APPLIED Change" in error for error in errors)


def test_not_started_retest_is_allowed(tmp_path: Path) -> None:
    session = _copy_fixture(tmp_path)
    _replace(session / "retest.md", "Result：PASS", "Result：NOT_STARTED")
    assert _verifier().verify_session(session) == []


def test_reset_audit_is_not_a_campaign_session() -> None:
    sessions_root = REPO_ROOT / "project-reconstruction-lab/sessions"
    session_names = {path.name for path in _verifier()._session_dirs(sessions_root)}
    assert "RB-RESET-001" not in session_names

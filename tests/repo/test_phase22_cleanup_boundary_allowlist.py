from __future__ import annotations

from pathlib import Path

import pytest

from tools.scripts.verify_phase22_cleanup_boundary import (
    _load_active_candidate_allowlist,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCT = (
    REPO_ROOT
    / ".agent"
    / "programs"
    / "work-products"
    / "phase22-removal-candidates.yaml"
)
LEGACY_CUTOVER_PATH = "src/backend/zuno/knowledge/ingestion/legacy_cutover.py"
GENERAL_AGENT_PATH = "src/backend/zuno/agent/core/agents/general_agent.py"


def _write_work_product(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "phase22-removal-candidates.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def test_active_candidate_paths_are_admitted(tmp_path: Path) -> None:
    """legacy_cutover.py is a real fixed blocker registered as active_candidate."""
    body = f"""
phase_id: PHASE22
mandatory_removal_candidates:
  - path: "{LEGACY_CUTOVER_PATH}"
    current_status: "active_candidate"
    removal_task: "P16-RETIRE-CHUNKMODEL"
  - path: "{GENERAL_AGENT_PATH}"
    current_status: "active_candidate"
    removal_task: "P22-T03"
resolved_this_slice:
  - path: "src/backend/zuno/platform/compatibility/legacy_aliases.py"
    current_status: "resolved_retired"
unrelated_section:
  - path: "src/backend/zuno/knowledge/ingestion/legacy_chunk_projection.py"
"""
    allowlist, errors = _load_active_candidate_allowlist(_write_work_product(tmp_path, body))
    assert errors == []
    assert LEGACY_CUTOVER_PATH in allowlist
    assert GENERAL_AGENT_PATH in allowlist


def test_resolved_retired_path_does_not_enter_allowlist(tmp_path: Path) -> None:
    """A path marked resolved_retired must never widen the allowlist."""
    body = f"""
mandatory_removal_candidates:
  - path: "src/backend/zuno/platform/compatibility/legacy_aliases.py"
    current_status: "resolved_retired"
  - path: "src/backend/zuno/knowledge/ingestion/legacy_cutover.py"
    current_status: "active_candidate"
"""
    allowlist, errors = _load_active_candidate_allowlist(_write_work_product(tmp_path, body))
    assert errors == []
    assert "src/backend/zuno/platform/compatibility/legacy_aliases.py" not in allowlist
    assert LEGACY_CUTOVER_PATH in allowlist


def test_resolved_this_slice_does_not_create_allowlist_entry(tmp_path: Path) -> None:
    """resolved_this_slice items are below the strict allowlist boundary."""
    body = """
mandatory_removal_candidates:
  - path: "src/backend/zuno/agent/core/agents/general_agent.py"
    current_status: "active_candidate"
resolved_this_slice:
  - path: "src/backend/zuno/knowledge/ingestion/legacy_cutover.py"
    current_status: "resolved_this_slice"
"""
    allowlist, errors = _load_active_candidate_allowlist(_write_work_product(tmp_path, body))
    assert errors == []
    assert LEGACY_CUTOVER_PATH not in allowlist


def test_unrelated_section_does_not_create_allowlist_entry(tmp_path: Path) -> None:
    """A `- path:` line in any non-mandatory section must not enter the allowlist."""
    body = """
phase_id: PHASE22
task_id: P22-T03
status: frozen_from_phase21_runtime_and_phase22_startup_scan
mandatory_removal_candidates:
  - path: "src/backend/zuno/agent/core/agents/general_agent.py"
    current_status: "active_candidate"
fixed_blockers:
  - path: "src/backend/zuno/knowledge/ingestion/legacy_cutover.py"
    note: "PHASE16 owns this retirement"
remaining_not_closed:
  - "src/backend/zuno/knowledge/ingestion/legacy_cutover.py is fixed."
"""
    allowlist, errors = _load_active_candidate_allowlist(_write_work_product(tmp_path, body))
    assert errors == []
    assert LEGACY_CUTOVER_PATH not in allowlist


def test_missing_current_status_fails_closed(tmp_path: Path) -> None:
    """A mandatory entry without current_status must NOT widen the allowlist."""
    body = """
mandatory_removal_candidates:
  - path: "src/backend/zuno/agent/core/agents/general_agent.py"
  - path: "src/backend/zuno/agent/core/agents/react_agent.py"
    current_status: "active_candidate"
"""
    allowlist, errors = _load_active_candidate_allowlist(_write_work_product(tmp_path, body))
    assert errors == []
    assert "src/backend/zuno/agent/core/agents/general_agent.py" not in allowlist
    assert "src/backend/zuno/agent/core/agents/react_agent.py" in allowlist


def test_unknown_status_fails_closed(tmp_path: Path) -> None:
    """An unrecognized current_status value must NOT widen the allowlist."""
    body = """
mandatory_removal_candidates:
  - path: "src/backend/zuno/agent/core/agents/legacy_thing.py"
    current_status: "retired"
  - path: "src/backend/zuno/agent/core/agents/general_agent.py"
    current_status: "active_candidate"
"""
    allowlist, errors = _load_active_candidate_allowlist(_write_work_product(tmp_path, body))
    assert errors == []
    assert "src/backend/zuno/agent/core/agents/legacy_thing.py" not in allowlist


def test_missing_work_product_is_reported(tmp_path: Path) -> None:
    """A missing work product must surface as an error and empty allowlist."""
    allowlist, errors = _load_active_candidate_allowlist(tmp_path / "absent.yaml")
    assert allowlist == set()
    assert any("missing" in err for err in errors)


def test_real_work_product_admits_only_mandatory_active_candidates() -> None:
    """Live guard: the real work product only admits mandatory+active_candidate."""
    allowlist, errors = _load_active_candidate_allowlist(WORK_PRODUCT)
    assert errors == [], errors
    assert LEGACY_CUTOVER_PATH in allowlist
    # resolved_retired entries inside mandatory must NOT leak in
    assert "tests/legacy_guards/" not in allowlist
    assert "legacy_general_agent_completion_rollback" not in allowlist
    # legacy_aliases.py IS a real active_candidate in mandatory (Wave 0 has
    # not yet retired the source file); its presence in the allowlist is the
    # intended safety net while the directory remains registered for
    # P22-T03.
    assert "src/backend/zuno/platform/compatibility/legacy_aliases.py" in allowlist


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/scripts/verify_red_blue_workflow_v4.py"


def _module():
    spec = importlib.util.spec_from_file_location("verify_red_blue_workflow_v4", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_round(tmp_path: Path, *, state: str = "WAITING_FOR_CHATGPT_REVIEW") -> Path:
    directory = tmp_path / "round"
    (directory / "context-packets").mkdir(parents=True)
    questions = "\n".join(f"## Q{index:03d}\n\nQuestion {index}.\n" for index in range(1, 101))
    (directory / "red-questions.md").write_text(questions, encoding="utf-8")
    question_sha = _sha(directory / "red-questions.md")
    snapshot = """round_id: R006\nbase_sha: 0123456789abcdef0123456789abcdef01234567\ncanonical_files:\n  - docs/architecture/architecture.md\nfact_baseline: docs/facts\nactive_adr: []\ngovernance_files: []\narchitecture_state: ACCEPTED_TARGET\nmaturity_state: ACCEPTED_TARGET\nfixed_constraints: []\ngenerated_at: 2026-08-13T00:00:00Z\n"""
    (directory / "canonical-snapshot.yaml").write_text(snapshot, encoding="utf-8")
    snapshot_sha = _sha(directory / "canonical-snapshot.yaml")
    base = "0123456789abcdef0123456789abcdef01234567"
    red = f"# Red\n\nbase_sha: {base}\ncanonical_snapshot_sha: {snapshot_sha}\nread-only\n"
    blue = f"# Blue Canonical Writer\n\nbase_sha: {base}\ncanonical_snapshot_sha: {snapshot_sha}\nred-questions\nquestions_frozen_sha: {question_sha}\n"
    (directory / "context-packets/red-context.md").write_text(red, encoding="utf-8")
    (directory / "context-packets/blue-context.md").write_text(blue, encoding="utf-8")
    final_sha = "abcdef0123456789abcdef0123456789abcdef01"
    judge = f"# Original Snapshot\nbase_sha: {base}\ncanonical_snapshot_sha: {snapshot_sha}\n# Blue Answers\n# Blue Decisions\n# Canonical Diff\nblue_final_sha: {final_sha}\n"
    (directory / "context-packets/red-judge-context.md").write_text(judge, encoding="utf-8")
    judge_sha = _sha(directory / "context-packets/red-judge-context.md")
    for name, content in {
        "blue-answers.md": "answers",
        "blue-decisions.md": "decisions",
        "architecture-deltas.md": "deltas",
        "canonical-sync-record.md": f"blue_final_sha: {final_sha}",
        "scorecard.md": f"scored_final_sha: {final_sha}",
        "chatgpt-review-package.md": f"BASE_SHA: {base}\nFINAL_SHA: {final_sha}\n",
    }.items():
        (directory / name).write_text(content, encoding="utf-8")
    manifest = f"""round_id: R006\nbase_sha: {base}\nred_session_id: RB-R006-RED\nblue_session_id: RB-R006-BLUE\nred_fresh_context: true\nblue_fresh_context: true\ncanonical_snapshot_sha: {snapshot_sha}\nquestions_frozen_sha: {question_sha}\nblue_questions_sha: {question_sha}\nblue_final_sha: {final_sha}\nred_judge_packet_sha: {judge_sha}\nchatgpt_review_status: WAITING_FOR_CHATGPT_REVIEW\nround_status: {state}\nred_session_closed: false\nblue_session_closed: false\nred_read_only: true\nblue_canonical_writer: true\ncanonical_sync_mode: FULL_PART_REWRITE\nfacts_changed: NONE\nprevious_reasoning_included: false\nhistory_chat_included: false\n"""
    (directory / "manifest.yaml").write_text(manifest, encoding="utf-8")
    return directory


def test_bootstrap_contract_passes() -> None:
    errors = _module().verify_bootstrap(ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V4-BOOTSTRAP")
    assert errors == []


def test_fresh_dual_thread_round_contract_passes(tmp_path: Path) -> None:
    assert _module().verify_round(_write_round(tmp_path)) == []


def test_same_session_ids_are_rejected(tmp_path: Path) -> None:
    directory = _write_round(tmp_path)
    path = directory / "manifest.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("RB-R006-BLUE", "RB-R006-RED"), encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("different non-empty Session IDs" in error for error in errors)


def test_blue_cannot_change_frozen_questions(tmp_path: Path) -> None:
    directory = _write_round(tmp_path)
    path = directory / "manifest.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("blue_questions_sha:", "blue_questions_sha: 0000000000000000000000000000000000000000000000000000000000000000 #"), encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("different question SHA" in error for error in errors)


def test_round_cannot_close_without_user_verdict(tmp_path: Path) -> None:
    directory = _write_round(tmp_path, state="CLOSED")
    manifest = directory / "manifest.yaml"
    content = manifest.read_text(encoding="utf-8").replace("round_status: CLOSED", "round_status: CLOSED").replace("red_session_closed: false", "red_session_closed: true").replace("blue_session_closed: false", "blue_session_closed: true").replace("chatgpt_review_status: WAITING_FOR_CHATGPT_REVIEW", "chatgpt_review_status: VERDICT_PROVIDED")
    manifest.write_text(content, encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("requires chatgpt-verdict.md" in error for error in errors)


def test_append_only_sync_is_rejected(tmp_path: Path) -> None:
    directory = _write_round(tmp_path)
    path = directory / "manifest.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("FULL_PART_REWRITE", "APPEND"), encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("must not be APPEND" in error for error in errors)

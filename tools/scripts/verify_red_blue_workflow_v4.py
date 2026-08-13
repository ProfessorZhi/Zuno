"""Validate the V4 Fresh-Context / Dual-Thread Red/Blue artifact contract.

This verifier is deliberately an artifact checker. It never creates a Codex
session, launches a thread, edits Canonical documents, or signs ChatGPT's
external verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

import yaml


VALID_ROUND_STATES = {
    "PREPARING",
    "RED_ATTACK",
    "RED_QUESTIONS_FROZEN",
    "BLUE_DEFENSE",
    "BLUE_CANONICAL_SYNC",
    "RED_COUNTER_REVIEW",
    "WAITING_FOR_CHATGPT_REVIEW",
    "CHATGPT_REPAIR_REQUIRED",
    "CLOSED",
    "BLOCKED_BY_USER_GATE",
}
STATE_ORDER = {state: index for index, state in enumerate(VALID_ROUND_STATES)}
VALID_VERDICTS = {
    "ACCEPT",
    "ACCEPT_WITH_DEBT",
    "BLUE_REPAIR_REQUIRED",
    "ROUND_REPLAY_REQUIRED",
    "USER_GATE_REQUIRED",
}
VALID_SYNC_MODES = {"SECTION_REWRITE", "FULL_PART_REWRITE", "NO_CHANGE", "ESCALATION"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _yaml(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"missing {path.name}")
        return {}
    try:
        value = yaml.safe_load(_read(path))
    except yaml.YAMLError as exc:
        errors.append(f"{path.name} is invalid YAML: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path.name} must contain a mapping")
        return {}
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing required artifact: {path.name}")


def _contains(path: Path, marker: str, errors: list[str], label: str | None = None) -> None:
    if path.exists() and marker.lower() not in _read(path).lower():
        errors.append(f"{label or path.name} must contain marker: {marker}")


def verify_bootstrap(directory: Path) -> list[str]:
    errors: list[str] = []
    manifest = _yaml(directory / "manifest.yaml", errors)
    required = {
        "workflow_id",
        "bootstrap_id",
        "base_sha",
        "final_sha",
        "historical_rounds_immutable",
        "round_006_status",
        "round_006_started",
        "chatgpt_review_status",
        "round_status",
        "facts_changed",
        "runtime_changed",
        "schema_changed",
        "migration_changed",
        "adr_changed",
        "architecture_track",
        "implementation_track",
        "canonical_writer",
        "external_auditor",
        "session_creation",
    }
    for key in sorted(required - manifest.keys()):
        errors.append(f"bootstrap manifest missing required field: {key}")
    if manifest.get("workflow_id") != "ZUNO-RED-BLUE-WORKFLOW-V4":
        errors.append("bootstrap manifest workflow_id must be ZUNO-RED-BLUE-WORKFLOW-V4")
    base_sha = str(manifest.get("base_sha", ""))
    if not SHA40.fullmatch(base_sha):
        errors.append("bootstrap manifest base_sha must be a 40-character SHA")
    if manifest.get("historical_rounds_immutable") is not True:
        errors.append("historical_rounds_immutable must be true")
    if manifest.get("round_006_status") != "READY_FOR_FRESH_RED_THREAD":
        errors.append("round_006_status must be READY_FOR_FRESH_RED_THREAD")
    if manifest.get("round_006_started") is not False:
        errors.append("round_006_started must be false")
    if manifest.get("chatgpt_review_status") != "WAITING_FOR_CHATGPT_REVIEW":
        errors.append("bootstrap must wait for ChatGPT review")
    if manifest.get("facts_changed") != "NONE":
        errors.append("bootstrap must not change Facts")
    for key in ("runtime_changed", "schema_changed", "migration_changed", "adr_changed"):
        if manifest.get(key) != "NONE":
            errors.append(f"bootstrap must not change {key.removesuffix('_changed').capitalize()}")
    if manifest.get("canonical_writer") != "BLUE_THREAD_ONLY":
        errors.append("canonical_writer must be BLUE_THREAD_ONLY")
    if manifest.get("external_auditor") != "CHATGPT":
        errors.append("external_auditor must be CHATGPT")
    if manifest.get("session_creation") != "MANUAL_ARTIFACT_ONLY":
        errors.append("session_creation must be MANUAL_ARTIFACT_ONLY")
    _require(directory / "README.md", errors)
    _require(directory / "review-package.md", errors)
    _require(directory / "manual-launch-instructions.md", errors)
    package = directory / "review-package.md"
    _contains(package, "BASE_SHA:", errors)
    _contains(package, "FINAL_SHA:", errors)
    _contains(package, "READY_FOR_FRESH_RED_THREAD", errors)
    _contains(package, "WAITING_FOR_CHATGPT_REVIEW", errors)
    verdict = directory / "chatgpt-verdict.md"
    if verdict.exists() and "NOT_PROVIDED" not in _read(verdict):
        errors.append("bootstrap chatgpt-verdict.md must remain NOT_PROVIDED")
    return errors


def _verify_snapshot(directory: Path, manifest: dict[str, Any], errors: list[str]) -> str:
    path = directory / "canonical-snapshot.yaml"
    snapshot = _yaml(path, errors)
    required = {
        "round_id",
        "base_sha",
        "canonical_files",
        "fact_baseline",
        "active_adr",
        "governance_files",
        "architecture_state",
        "maturity_state",
        "fixed_constraints",
        "generated_at",
    }
    for key in sorted(required - snapshot.keys()):
        errors.append(f"canonical-snapshot.yaml missing required field: {key}")
    if snapshot.get("round_id") != manifest.get("round_id"):
        errors.append("snapshot round_id must match manifest round_id")
    if snapshot.get("base_sha") != manifest.get("base_sha"):
        errors.append("snapshot base_sha must match manifest base_sha")
    if not isinstance(snapshot.get("canonical_files"), list) or not snapshot.get("canonical_files"):
        errors.append("snapshot canonical_files must be a non-empty list")
    snapshot_sha = _sha256(path) if path.exists() else ""
    declared = manifest.get("canonical_snapshot_sha")
    if declared != snapshot_sha:
        errors.append("manifest canonical_snapshot_sha must match canonical-snapshot.yaml")
    return snapshot_sha


def _verify_contexts(directory: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    context_root = directory / "context-packets"
    red = context_root / "red-context.md"
    blue = context_root / "blue-context.md"
    judge = context_root / "red-judge-context.md"
    for path in (red, blue, judge):
        _require(path, errors)
    base_sha = str(manifest.get("base_sha", ""))
    snapshot_sha = str(manifest.get("canonical_snapshot_sha", ""))
    for path in (red, blue, judge):
        if path.exists():
            content = _read(path)
            if base_sha not in content:
                errors.append(f"{path.name} must reference manifest base_sha")
            if snapshot_sha not in content:
                errors.append(f"{path.name} must reference canonical_snapshot_sha")
    if red.exists():
        _contains(red, "read-only", errors, "red-context.md")
        _contains(red, "red", errors, "red-context.md")
    if blue.exists():
        _contains(blue, "canonical writer", errors, "blue-context.md")
        _contains(blue, "red-questions", errors, "blue-context.md")
    if judge.exists():
        for marker in ("Original Snapshot", "Blue Answers", "Blue Decisions", "Canonical Diff"):
            _contains(judge, marker, errors, "red-judge-context.md")
    for key in ("previous_reasoning_included", "history_chat_included"):
        if manifest.get(key) is not False:
            errors.append(f"manifest {key} must be false")


def _verify_frozen_questions(directory: Path, manifest: dict[str, Any], state: str, errors: list[str]) -> None:
    questions = directory / "red-questions.md"
    frozen_states = {"RED_QUESTIONS_FROZEN", "BLUE_DEFENSE", "BLUE_CANONICAL_SYNC", "RED_COUNTER_REVIEW", "WAITING_FOR_CHATGPT_REVIEW", "CHATGPT_REPAIR_REQUIRED", "CLOSED"}
    if state not in frozen_states:
        return
    _require(questions, errors)
    if not questions.exists():
        return
    question_ids = re.findall(r"(?m)^##\s+(Q\d{3})\b", _read(questions))
    if len(question_ids) != 100 or len(set(question_ids)) != 100:
        errors.append("red-questions.md must contain exactly 100 unique Q001..Q100 questions")
    expected = [f"Q{index:03d}" for index in range(1, 101)]
    if question_ids != expected:
        errors.append("red-questions.md question IDs must be continuous Q001..Q100")
    declared = str(manifest.get("questions_frozen_sha", ""))
    if not SHA64.fullmatch(declared) or declared != _sha256(questions):
        errors.append("questions_frozen_sha must match red-questions.md")
    blue = directory / "context-packets" / "blue-context.md"
    if blue.exists() and declared not in _read(blue):
        errors.append("blue-context.md must reference questions_frozen_sha")
    if manifest.get("blue_questions_sha") not in (None, declared):
        errors.append("Blue cannot use a different question SHA")


def _verify_final_artifacts(directory: Path, manifest: dict[str, Any], state: str, errors: list[str]) -> None:
    post_blue = {"BLUE_CANONICAL_SYNC", "RED_COUNTER_REVIEW", "WAITING_FOR_CHATGPT_REVIEW", "CHATGPT_REPAIR_REQUIRED", "CLOSED"}
    if state not in post_blue:
        return
    blue_final_sha = str(manifest.get("blue_final_sha", ""))
    if not SHA40.fullmatch(blue_final_sha):
        errors.append("blue_final_sha must be a 40-character SHA after Canonical Sync")
    for name in ("blue-answers.md", "blue-decisions.md", "architecture-deltas.md", "canonical-sync-record.md", "red-judge-context.md"):
        path = (directory / "context-packets" / name) if name == "red-judge-context.md" else (directory / name)
        _require(path, errors)
    sync = directory / "canonical-sync-record.md"
    if sync.exists() and blue_final_sha not in _read(sync):
        errors.append("canonical-sync-record.md must reference blue_final_sha")
    judge_sha = str(manifest.get("red_judge_packet_sha", ""))
    judge = directory / "context-packets" / "red-judge-context.md"
    if not SHA64.fullmatch(judge_sha) or not judge.exists() or judge_sha != _sha256(judge):
        errors.append("red_judge_packet_sha must match red-judge-context.md")
    if judge.exists() and blue_final_sha not in _read(judge):
        errors.append("red-judge-context.md must reference blue_final_sha")
    if state in {"RED_COUNTER_REVIEW", "WAITING_FOR_CHATGPT_REVIEW", "CHATGPT_REPAIR_REQUIRED", "CLOSED"}:
        scorecard = directory / "scorecard.md"
        _require(scorecard, errors)
        if scorecard.exists() and blue_final_sha not in _read(scorecard):
            errors.append("scorecard.md must score the final Canonical SHA")


def _verify_external_gate(directory: Path, manifest: dict[str, Any], state: str, errors: list[str]) -> None:
    review = directory / "chatgpt-review-package.md"
    verdict = directory / "chatgpt-verdict.md"
    if state in {"WAITING_FOR_CHATGPT_REVIEW", "CHATGPT_REPAIR_REQUIRED", "CLOSED"}:
        _require(review, errors)
    review_status = manifest.get("chatgpt_review_status")
    if state in {"WAITING_FOR_CHATGPT_REVIEW", "RED_COUNTER_REVIEW"} and review_status != "WAITING_FOR_CHATGPT_REVIEW":
        errors.append("Round before external verdict must be WAITING_FOR_CHATGPT_REVIEW")
    if state == "CLOSED":
        if review_status != "VERDICT_PROVIDED":
            errors.append("CLOSED round requires VERDICT_PROVIDED")
        if not verdict.exists():
            errors.append("CLOSED round requires chatgpt-verdict.md")
        else:
            verdict_data = _yaml(verdict, errors)
            if verdict_data.get("provided_by") != "USER":
                errors.append("ChatGPT verdict must be user-provided; Codex cannot self-sign")
            if verdict_data.get("verdict") not in {"ACCEPT", "ACCEPT_WITH_DEBT"}:
                errors.append("CLOSED round requires ACCEPT or ACCEPT_WITH_DEBT")
            if verdict_data.get("reviewed_final_sha") != manifest.get("blue_final_sha"):
                errors.append("ChatGPT reviewed_final_sha must match blue_final_sha")
    elif verdict.exists():
        data = _yaml(verdict, errors)
        if data.get("verdict") in VALID_VERDICTS and data.get("provided_by") != "USER":
            errors.append("Codex/verifier cannot self-sign a ChatGPT verdict")


def verify_round(directory: Path) -> list[str]:
    errors: list[str] = []
    manifest = _yaml(directory / "manifest.yaml", errors)
    required = {
        "round_id", "base_sha", "red_session_id", "blue_session_id", "red_fresh_context",
        "blue_fresh_context", "canonical_snapshot_sha", "questions_frozen_sha", "blue_final_sha",
        "red_judge_packet_sha", "chatgpt_review_status", "round_status", "red_session_closed",
        "blue_session_closed", "red_read_only", "blue_canonical_writer", "canonical_sync_mode",
        "facts_changed", "previous_reasoning_included", "history_chat_included",
    }
    for key in sorted(required - manifest.keys()):
        errors.append(f"round manifest missing required field: {key}")
    state = str(manifest.get("round_status", ""))
    if state not in VALID_ROUND_STATES:
        errors.append(f"invalid round_status: {state}")
    if manifest.get("red_session_id") == manifest.get("blue_session_id") or not manifest.get("red_session_id") or not manifest.get("blue_session_id"):
        errors.append("Red and Blue must have different non-empty Session IDs")
    for key in ("red_fresh_context", "blue_fresh_context", "red_read_only", "blue_canonical_writer"):
        if manifest.get(key) is not True:
            errors.append(f"{key} must be true")
    if not SHA40.fullmatch(str(manifest.get("base_sha", ""))):
        errors.append("round base_sha must be a 40-character SHA")
    if manifest.get("facts_changed") != "NONE":
        errors.append("Architecture Round must not change Facts")
    if manifest.get("canonical_sync_mode") not in VALID_SYNC_MODES:
        errors.append("canonical_sync_mode must not be APPEND and must use a V4 mode")
    if manifest.get("red_session_closed") or manifest.get("blue_session_closed"):
        if state != "CLOSED":
            errors.append("Session closure is only valid after an external verdict and CLOSED state")
    if state == "CLOSED" and not (manifest.get("red_session_closed") and manifest.get("blue_session_closed")):
        errors.append("CLOSED round requires both sessions closed")
    _verify_snapshot(directory, manifest, errors)
    _verify_contexts(directory, manifest, errors)
    _verify_frozen_questions(directory, manifest, state, errors)
    _verify_final_artifacts(directory, manifest, state, errors)
    _verify_external_gate(directory, manifest, state, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bootstrap", type=Path)
    group.add_argument("--round", type=Path)
    args = parser.parse_args()
    errors = verify_bootstrap(args.bootstrap) if args.bootstrap else verify_round(args.round)
    if errors:
        print("RED_BLUE_WORKFLOW_V4_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RED_BLUE_WORKFLOW_V4_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

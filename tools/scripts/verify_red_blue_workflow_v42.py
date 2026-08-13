"""Validate the V4.2 question-by-question adaptive interrogation contract.

This verifier validates recorded artifacts only. It does not create sessions, start a
round, read business code, modify Canonical documents, or provide an external verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
V42_WORKFLOW = "ZUNO-RED-BLUE-WORKFLOW-V4.2"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")
POST_LIVE_STATES = {
    "BLUE_ARCHITECTURE_SYNTHESIS",
    "BLUE_CANONICAL_SYNC",
    "BLUE_CANDIDATE_READY",
    "RED_COUNTER_REVIEW",
    "WAITING_FOR_CHATGPT_REVIEW",
    "CHATGPT_REPAIR_REQUIRED",
    "CLOSED",
}
VALID_SUPPORT = {"SUFFICIENT", "PARTIAL", "GAP"}
VALID_SOURCES = {"PART_A", "PART_A_PLUS_GENERAL_KNOWLEDGE", "GENERAL_ARCHITECTURE_REASONING"}
VALID_DECISIONS = {"CONTINUE_CHAIN", "CLOSE_CHAIN", "ESCALATE_FINDING"}
VALID_STATES = {
    "PREPARING",
    "RED_THREAD_READY",
    "BLUE_THREAD_READY",
    "LIVE_ATTACK",
    "CHAIN_OPEN",
    "QUESTION_FROZEN",
    "BLUE_ANSWER_FROZEN",
    "CHAIN_CLOSED",
    "LIVE_ATTACK_COMPLETE",
    *POST_LIVE_STATES,
    "BLOCKED_BY_USER_GATE",
}
VALID_FOLLOWUP_REASONS = {
    "ANSWER_AMBIGUITY",
    "UNJUSTIFIED_ASSUMPTION",
    "OWNER_CONFLICT",
    "FAILURE_GAP",
    "ALTERNATIVE_NOT_ADDRESSED",
    "TRADEOFF_NOT_ADDRESSED",
    "COUNTEREXAMPLE_TRIGGERED",
    "OVERDESIGN_RISK",
    "REVERSAL_MISSING",
    "BOUNDARY_UNCLEAR",
    "CONCEPT_NOT_CLEAR",
    "SCALE_OR_COST_PRESSURE",
    "SECURITY_PRESSURE",
    "RECOVERY_PRESSURE",
    "CHAIN_COMPLETION_PROBE",
}
ALLOWED_CHAIN_KEYS = {
    "chain_id",
    "root_claim",
    "primary_concept",
    "attack_intent",
    "possible_pressure_axes",
}


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


def _sha256(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _file_sha(path: Path) -> str:
    return _sha256(path.read_bytes())


def _require(path: Path, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing required artifact: {path.name}")


def _marker(path: Path, marker: str, errors: list[str]) -> None:
    if path.exists() and marker.lower() not in _read(path).lower():
        errors.append(f"{path.name} must contain marker: {marker}")


def _jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    if not path.exists():
        errors.append(f"missing required artifact: {path.name}")
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(_read(path).splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name} line {line_number} is invalid JSON: {exc}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.name} line {line_number} must be a JSON object")
            continue
        events.append(value)
    return events


def verify_bootstrap(directory: Path) -> list[str]:
    errors: list[str] = []
    manifest = _yaml(directory / "manifest.yaml", errors)
    required = {
        "workflow_id",
        "bootstrap_id",
        "artifact_base_sha",
        "artifact_content_state",
        "external_reviewed_sha",
        "historical_rounds_immutable",
        "round_006_status",
        "round_006_started",
        "chatgpt_review_status",
        "round_status",
        "architecture_track",
        "implementation_track",
        "facts_changed",
        "runtime_changed",
        "schema_changed",
        "migration_changed",
        "adr_changed",
        "canonical_content_changed",
        "question_mode",
        "whole_round_question_freeze",
        "question_target",
        "question_max",
        "normal_min",
        "blue_canonical_write_during_live",
        "main_integrator",
        "main_merge_requires_chatgpt_verdict",
        "human_writing_verifier_mode",
        "session_creation",
        "interview_calibration_source_policy",
        "blue_reads_interview_calibration",
    }
    for key in sorted(required - manifest.keys()):
        errors.append(f"bootstrap manifest missing required field: {key}")
    if manifest.get("workflow_id") != V42_WORKFLOW:
        errors.append("bootstrap workflow_id must be ZUNO-RED-BLUE-WORKFLOW-V4.2")
    if not SHA40.fullmatch(str(manifest.get("artifact_base_sha", ""))):
        errors.append("artifact_base_sha must be a 40-character SHA")
    if "final_sha" in manifest:
        errors.append("self-referential final_sha is forbidden; use external_reviewed_sha")
    if manifest.get("artifact_content_state") != "WORKFLOW_CONTRACT_AVAILABLE":
        errors.append("artifact_content_state must be WORKFLOW_CONTRACT_AVAILABLE")
    if manifest.get("external_reviewed_sha") != "NOT_PROVIDED":
        errors.append("bootstrap external_reviewed_sha must be NOT_PROVIDED")
    if manifest.get("historical_rounds_immutable") is not True:
        errors.append("historical_rounds_immutable must be true")
    if manifest.get("round_006_status") != "READY_FOR_ADAPTIVE_RED_BLUE_PILOT":
        errors.append("round_006_status must be READY_FOR_ADAPTIVE_RED_BLUE_PILOT")
    if manifest.get("round_006_started") is not False:
        errors.append("round_006_started must be false")
    if manifest.get("chatgpt_review_status") != "WAITING_FOR_CHATGPT_REVIEW":
        errors.append("bootstrap must wait for ChatGPT review")
    if manifest.get("round_status") != "V4.2_WORKFLOW_READY_FOR_CHATGPT_REVIEW":
        errors.append("round_status must be V4.2_WORKFLOW_READY_FOR_CHATGPT_REVIEW")
    for key in ("facts_changed", "runtime_changed", "schema_changed", "migration_changed", "adr_changed", "canonical_content_changed"):
        if manifest.get(key) != "NONE":
            errors.append(f"bootstrap must keep {key} as NONE")
    if manifest.get("question_mode") != "QUESTION_BY_QUESTION_ADAPTIVE_INTERROGATION":
        errors.append("question_mode must be QUESTION_BY_QUESTION_ADAPTIVE_INTERROGATION")
    if manifest.get("whole_round_question_freeze") != "FORBIDDEN":
        errors.append("whole_round_question_freeze must be FORBIDDEN")
    if (manifest.get("question_target"), manifest.get("question_max"), manifest.get("normal_min")) != (100, 100, 80):
        errors.append("question budget must be target=100, max=100, normal_min=80")
    if manifest.get("blue_canonical_write_during_live") is not False:
        errors.append("Blue Canonical write during Live Attack must be false")
    if manifest.get("main_integrator") != "MAIN_THREAD":
        errors.append("main_integrator must be MAIN_THREAD")
    if manifest.get("main_merge_requires_chatgpt_verdict") is not True:
        errors.append("Main merge must require ChatGPT verdict")
    if manifest.get("human_writing_verifier_mode") != "WARNING_ONLY":
        errors.append("human_writing_verifier_mode must be WARNING_ONLY")
    if manifest.get("session_creation") != "MANUAL_ARTIFACT_ONLY":
        errors.append("session_creation must be MANUAL_ARTIFACT_ONLY")
    if manifest.get("interview_calibration_source_policy") != "RED_ONLY_SYNTHESIS":
        errors.append("interview_calibration_source_policy must be RED_ONLY_SYNTHESIS")
    if manifest.get("blue_reads_interview_calibration") is not False:
        errors.append("Blue must not read interview calibration")
    for key in ("red_reads_business_code", "blue_reads_business_code", "blue_uses_code_as_architecture_reason", "blue_push_main"):
        if manifest.get(key) is not False:
            errors.append(f"{key} must be false")
    if manifest.get("candidate_branch") not in (None, ""):
        errors.append("bootstrap candidate_branch must be null")
    for name in ("README.md", "review-package.md", "manual-launch-instructions.md", "chatgpt-verdict.md"):
        _require(directory / name, errors)
    package = directory / "review-package.md"
    for marker in ("WORKFLOW_CONTRACT_AVAILABLE", "READY_FOR_ADAPTIVE_RED_BLUE_PILOT", "NOT_STARTED", "external_reviewed_sha: NOT_PROVIDED"):
        _marker(package, marker, errors)
    verdict = directory / "chatgpt-verdict.md"
    _marker(verdict, "NOT_PROVIDED", errors)
    return errors


def _verify_contexts(directory: Path, manifest: dict[str, Any], errors: list[str]) -> None:
    red = directory / "context-packets" / "red-context.md"
    blue = directory / "context-packets" / "blue-context.md"
    for path in (red, blue):
        _require(path, errors)
        if not path.exists():
            continue
        content = _read(path)
        _marker(path, "business_implementation_code: PROHIBITED", errors)
        _marker(path, "part_a_role: ARCHITECTURE_KNOWLEDGE_SOURCE", errors)
        if re.search(r"(?im)(?:^|\s)(?:src/backend/|apps/|infra/)", content):
            errors.append(f"{path.name} contains a business implementation path")
        if "questions_frozen_sha" in content or "red-questions.md" in content:
            errors.append(f"{path.name} contains forbidden whole-round question freeze")
    red_base = red_snapshot = blue_base = blue_snapshot = None
    if red.exists():
        _marker(red, "interview_calibration: RED_ONLY", errors)
        _marker(red, "base_sha:", errors)
        _marker(red, "canonical_snapshot_sha:", errors)
        red_base_match = re.search(r"(?im)^base_sha:\s*([0-9a-f]{40})\s*$", _read(red))
        red_snapshot_match = re.search(r"(?im)^canonical_snapshot_sha:\s*([0-9a-f]{64})\s*$", _read(red))
        red_base = red_base_match.group(1) if red_base_match else None
        red_snapshot = red_snapshot_match.group(1) if red_snapshot_match else None
    if blue.exists():
        _marker(blue, "interview_calibration: PROHIBITED", errors)
        _marker(blue, "answer_context: BASE_SNAPSHOT_ONLY", errors)
        _marker(blue, "canonical_write_phase: AFTER_LIVE_ATTACK_COMPLETE", errors)
        blue_base_match = re.search(r"(?im)^base_sha:\s*([0-9a-f]{40})\s*$", _read(blue))
        blue_snapshot_match = re.search(r"(?im)^canonical_snapshot_sha:\s*([0-9a-f]{64})\s*$", _read(blue))
        blue_base = blue_base_match.group(1) if blue_base_match else None
        blue_snapshot = blue_snapshot_match.group(1) if blue_snapshot_match else None
    if red_base and blue_base and red_base != blue_base:
        errors.append("Red and Blue must use the same BASE snapshot SHA")
    if red_snapshot and blue_snapshot and red_snapshot != blue_snapshot:
        errors.append("Red and Blue must use the same canonical snapshot SHA")
    if manifest.get("red_reads_business_code") is not False or manifest.get("blue_reads_business_code") is not False:
        errors.append("red_reads_business_code and blue_reads_business_code must be false")
    if manifest.get("blue_canonical_modified_during_live") is not False:
        errors.append("blue_canonical_modified_during_live must be false")


def _verify_chain_specs(manifest: dict[str, Any], errors: list[str]) -> set[str]:
    specs = manifest.get("chain_specs")
    if not isinstance(specs, list) or not specs:
        errors.append("chain_specs must be a non-empty list")
        return set()
    ids: set[str] = set()
    allowed = ALLOWED_CHAIN_KEYS
    for index, spec in enumerate(specs, start=1):
        if not isinstance(spec, dict):
            errors.append(f"chain_specs[{index}] must be a mapping")
            continue
        missing = allowed - spec.keys()
        for key in sorted(missing):
            errors.append(f"chain_specs[{index}] missing required field: {key}")
        forbidden = set(spec) - allowed
        if forbidden:
            errors.append("PREGENERATED_QUESTION_SET_VIOLATION: chain spec contains forbidden question fields: " + ", ".join(sorted(forbidden)))
        chain_id = str(spec.get("chain_id", ""))
        if not chain_id or chain_id in ids:
            errors.append(f"chain_specs[{index}] has duplicate or empty chain_id")
        ids.add(chain_id)
        if not isinstance(spec.get("possible_pressure_axes"), list) or not spec.get("possible_pressure_axes"):
            errors.append(f"chain_specs[{index}] possible_pressure_axes must be non-empty")
    return ids


def _verify_ledger(directory: Path, manifest: dict[str, Any], state: str, errors: list[str]) -> tuple[list[dict[str, Any]], int]:
    if "questions_frozen_sha" in manifest:
        errors.append("questions_frozen_sha is forbidden in V4.2")
    if manifest.get("ledger_artifact") != "question-answer-ledger.jsonl":
        errors.append("ledger_artifact must be question-answer-ledger.jsonl")
    path = directory / "question-answer-ledger.jsonl"
    events = _jsonl(path, errors)
    specs = _verify_chain_specs(manifest, errors)
    previous_hash = "0" * 64
    question_events: list[dict[str, Any]] = []
    questions: dict[str, dict[str, Any]] = {}
    answers: dict[str, dict[str, Any]] = {}
    decisions: dict[str, dict[str, Any]] = {}
    open_question: str | None = None
    last_chain: str | None = None
    question_number = 0
    event_ids: set[str] = set()
    first_answer_seen = False
    for position, event in enumerate(events, start=1):
        if event.get("event_seq") != position:
            errors.append(f"ledger event_seq must be contiguous at {position}")
        event_id = str(event.get("event_id", ""))
        if not event_id or event_id in event_ids:
            errors.append(f"ledger event_id must be unique at {position}")
        event_ids.add(event_id)
        body = {key: value for key, value in event.items() if key != "rolling_hash"}
        expected_hash = _sha256(previous_hash + _canonical(body))
        if event.get("rolling_hash") != expected_hash:
            errors.append(f"rolling hash mismatch at event {position}")
        previous_hash = expected_hash
        event_type = event.get("event_type")
        qid = str(event.get("question_id", ""))
        if event_type == "QUESTION_FROZEN":
            if open_question is not None:
                errors.append("PREGENERATED_QUESTION_SET_VIOLATION: a second question appeared before the prior answer and decision")
            question_number += 1
            expected_qid = f"Q{question_number:03d}"
            if qid != expected_qid:
                errors.append(f"question_id must be sequential; expected {expected_qid}")
            if qid in questions:
                errors.append(f"duplicate question_id: {qid}")
            chain_id = str(event.get("chain_id", ""))
            if chain_id not in specs:
                errors.append(f"question {qid} references unknown chain {chain_id}")
            question = event.get("question")
            if not isinstance(question, str) or not question.strip():
                errors.append(f"question {qid} must be non-empty")
            if event.get("question_sha") != _sha256(str(question or "")):
                errors.append(f"question_sha mismatch for {qid}")
            if event.get("blue_answer") not in (None, "") or event.get("answer_sha") not in (None, ""):
                errors.append(f"QUESTION_FROZEN {qid} must not contain an answer")
            root = event.get("is_root") is True
            if root:
                if event.get("followup_reason") not in (None, "") or event.get("previous_turn_ref") not in (None, ""):
                    errors.append(f"root question {qid} must not have follow-up fields")
            else:
                reason = event.get("followup_reason")
                if reason not in VALID_FOLLOWUP_REASONS:
                    errors.append(f"follow-up question {qid} has invalid followup_reason")
                if not isinstance(event.get("followup_trigger_detail"), str) or not event.get("followup_trigger_detail").strip():
                    errors.append(f"follow-up question {qid} must explain its trigger")
                ref = str(event.get("previous_turn_ref", ""))
                if not ref or not ref.startswith("A:"):
                    errors.append(f"follow-up question {qid} must reference a prior answer")
                if ref[2:] not in answers:
                    errors.append(f"follow-up question {qid} references an answer not yet frozen: {ref}")
            question_events.append(event)
            questions[qid] = event
            open_question = qid
            last_chain = str(event.get("chain_id", ""))
        elif event_type == "ANSWER_FROZEN":
            if open_question is None or qid != open_question:
                errors.append(f"answer {qid} appeared before its question or out of order")
            question = questions.get(qid)
            answer = event.get("blue_answer")
            if not isinstance(answer, str) or not answer.strip():
                errors.append(f"answer {qid} must be non-empty")
            if event.get("answer_sha") != _sha256(str(answer or "")):
                errors.append(f"answer_sha mismatch for {qid}")
            if question and event.get("question_sha") != question.get("question_sha"):
                errors.append(f"answer {qid} does not repeat the frozen question hash")
            if question and event.get("question") != question.get("question"):
                errors.append(f"answer {qid} does not repeat the immutable frozen question")
            if event.get("part_a_support") not in VALID_SUPPORT:
                errors.append(f"answer {qid} has invalid part_a_support")
            source = event.get("answer_source")
            if source not in VALID_SOURCES:
                errors.append(f"answer {qid} has invalid answer_source")
            if source == "GENERAL_ARCHITECTURE_REASONING" and not str(event.get("part_a_gap_detail", "")).strip():
                errors.append(f"answer {qid} must explain its Part-A gap")
            if qid in answers:
                errors.append(f"duplicate answer for {qid}")
            answers[qid] = event
            first_answer_seen = True
        elif event_type == "CHAIN_DECISION":
            if qid not in answers:
                errors.append(f"chain decision for {qid} must follow a frozen answer")
            decision = event.get("chain_decision")
            if decision not in VALID_DECISIONS:
                errors.append(f"chain decision for {qid} is invalid")
            if not str(event.get("chain_stop_reason", "")).strip():
                errors.append(f"chain decision for {qid} requires chain_stop_reason")
            if qid in decisions:
                errors.append(f"duplicate chain decision for {qid}")
            decisions[qid] = event
            if open_question == qid:
                open_question = None
        else:
            errors.append(f"unknown ledger event_type at {position}: {event_type}")
        if not first_answer_seen and event_type == "QUESTION_FROZEN" and position > 1:
            errors.append("PREGENERATED_QUESTION_SET_VIOLATION: multiple pre-answer events detected")
    if open_question is not None:
        errors.append(f"question {open_question} has no following answer and chain decision")
    if not SHA64.fullmatch(previous_hash):
        errors.append("rolling ledger hash is not a SHA-256 value")
    if manifest.get("rolling_ledger_hash") != previous_hash:
        errors.append("manifest rolling_ledger_hash does not match ledger")
    if manifest.get("question_count") != len(question_events):
        errors.append("manifest question_count does not match ledger")
    if state in POST_LIVE_STATES:
        for qid in questions:
            if qid not in answers or qid not in decisions:
                errors.append(f"post-live ledger is incomplete for {qid}")
    count = len(question_events)
    if count > 100:
        errors.append("question count cannot exceed 100")
    if count < 80 and manifest.get("question_budget_stop_reason") not in {"USER_GATE", "ARCHITECTURE_BLOCKER"}:
        errors.append("QUESTION_COVERAGE_INSUFFICIENT: fewer than 80 questions require a blocking reason")
    if 80 <= count < 100 and manifest.get("question_budget_stop_reason") not in {"NO_NEW_ARCHITECTURE_INFORMATION", "ALL_PRIORITY_CHAINS_CLOSED"}:
        errors.append("80-99 questions require a valid question_budget_stop_reason")
    if count == 100 and not str(manifest.get("question_budget_stop_reason", "")).strip():
        errors.append("100 questions require question_budget_stop_reason")
    novelty = sum(event.get("novelty") == "NOVEL" for event in question_events)
    regression = sum(event.get("novelty") == "REGRESSION" for event in question_events)
    if novelty + regression != count:
        errors.append("each question must be marked NOVEL or REGRESSION")
    if manifest.get("novel_question_count") != novelty or manifest.get("regression_question_count") != regression:
        errors.append("novelty counts do not match ledger")
    if count and abs(float(manifest.get("adaptive_followup_ratio", -1)) - ((count - len({event.get('chain_id') for event in question_events if event.get('is_root') is True})) / count)) > 1e-9:
        errors.append("adaptive_followup_ratio does not match actual questions")
    if state not in {"PREPARING", "RED_THREAD_READY", "BLUE_THREAD_READY", "LIVE_ATTACK", "CHAIN_OPEN", "QUESTION_FROZEN", "BLUE_ANSWER_FROZEN", "CHAIN_CLOSED"}:
        if count and novelty / count < 0.75:
            errors.append("QUESTION_QUALITY_BLOCKED: novel question ratio is below 75%")
        if count and regression / count > 0.25:
            errors.append("QUESTION_QUALITY_BLOCKED: regression question ratio is above 25%")
    if path.exists() and "questions_frozen_sha" in _read(path):
        errors.append("questions_frozen_sha is forbidden in question-answer-ledger.jsonl")
    if (directory / "red-questions.md").exists():
        errors.append("PREGENERATED_QUESTION_SET_VIOLATION: red-questions.md is forbidden")
    for qid, question in questions.items():
        if question.get("is_root") is not True and str(question.get("previous_turn_ref", ""))[2:] not in answers:
            errors.append(f"follow-up {qid} does not point to an earlier answer")
    for earlier, later in zip(question_events, question_events[1:]):
        previous_decision = decisions.get(str(earlier.get("question_id")))
        if previous_decision and previous_decision.get("chain_decision") == "CONTINUE_CHAIN" and later.get("chain_id") != earlier.get("chain_id"):
            errors.append("CONTINUE_CHAIN must be followed by a question in the same chain")
        if previous_decision and previous_decision.get("chain_decision") in {"CLOSE_CHAIN", "ESCALATE_FINDING"} and later.get("chain_id") == earlier.get("chain_id"):
            errors.append("closed or escalated chain must move to a new root chain")
    return events, len(question_events)


def _verify_transcript(directory: Path, question_count: int, state: str, errors: list[str]) -> None:
    path = directory / "live-interrogation.md"
    _require(path, errors)
    if not path.exists() or state not in POST_LIVE_STATES:
        return
    markers = re.findall(r"(?im)^\s*(RED Q\d{3}|BLUE A\d{3}|RED CHAIN DECISION)\b", _read(path))
    expected: list[str] = []
    for index in range(1, question_count + 1):
        expected.extend([f"RED Q{index:03d}", f"BLUE A{index:03d}", "RED CHAIN DECISION"])
    if markers != expected:
        errors.append("live-interrogation.md must alternate RED Question, BLUE Answer, RED CHAIN DECISION")


def _verify_phase(directory: Path, manifest: dict[str, Any], state: str, last_event_seq: int, errors: list[str]) -> None:
    if state not in VALID_STATES:
        errors.append(f"invalid V4.2 round state: {state}")
    if manifest.get("workflow_id") != V42_WORKFLOW:
        errors.append("round workflow_id must be ZUNO-RED-BLUE-WORKFLOW-V4.2")
    for key in ("facts_changed", "runtime_changed", "schema_changed", "migration_changed", "adr_changed", "canonical_content_changed"):
        if manifest.get(key) != "NONE":
            errors.append(f"V4.2 scope violation: {key} must be NONE")
    if manifest.get("whole_round_question_freeze") != "FORBIDDEN":
        errors.append("whole_round_question_freeze must be FORBIDDEN")
    if manifest.get("question_mode") != "QUESTION_BY_QUESTION_ADAPTIVE_INTERROGATION":
        errors.append("question_mode must be QUESTION_BY_QUESTION_ADAPTIVE_INTERROGATION")
    if (manifest.get("question_target"), manifest.get("question_max"), manifest.get("normal_min")) != (100, 100, 80):
        errors.append("question budget must be target=100, max=100, normal_min=80")
    if manifest.get("blue_reads_interview_calibration") is not False:
        errors.append("blue_reads_interview_calibration must be false")
    red_session = str(manifest.get("red_session_id", ""))
    blue_session = str(manifest.get("blue_session_id", ""))
    if not red_session or not blue_session or red_session == blue_session:
        errors.append("V4.2 round requires distinct Red and Blue session IDs")
    if manifest.get("blue_canonical_modified_during_live") is not False:
        errors.append("blue_canonical_modified_during_live must be false")
    if manifest.get("canonical_write_phase") != "AFTER_LIVE_ATTACK_COMPLETE":
        errors.append("canonical_write_phase must be AFTER_LIVE_ATTACK_COMPLETE")
    if state in POST_LIVE_STATES:
        if manifest.get("blue_synthesis_started_after_event_seq", 0) <= last_event_seq:
            errors.append("Blue synthesis must start after the final Live Attack event")
        candidate = str(manifest.get("candidate_branch", ""))
        main = str(manifest.get("main_branch", "main"))
        if not candidate or candidate == main:
            errors.append("candidate_branch must be distinct from main")
        if manifest.get("candidate_created_after_live_attack") is not True:
            errors.append("candidate must be created after LIVE_ATTACK_COMPLETE")


def _verify_post_live_artifacts(directory: Path, manifest: dict[str, Any], state: str, errors: list[str]) -> None:
    if state not in POST_LIVE_STATES:
        return
    required = (
        "blue-architecture-decisions.md",
        "architecture-deltas.md",
        "canonical-sync-record.md",
        "red-counter-review.md",
        "part-a-explainability.md",
        "scorecard.md",
        "counter-retest.jsonl",
        "chatgpt-review-package.md",
        "context-packets/red-judge-context.md",
    )
    for name in required:
        _require(directory / name, errors)
    explainability = directory / "part-a-explainability.md"
    for marker in ("PART_A_EXPLAINABILITY", "CLEAR", "DENSE", "TERM_DEPENDENT", "MISSING"):
        _marker(explainability, marker, errors)
    judge = directory / "context-packets/red-judge-context.md"
    for marker in ("BASE Part A", "Complete Q/A Ledger", "Blue Architecture Decisions", "Canonical Delta", "Final Part A", "Final Part B", "Candidate SHA"):
        _marker(judge, marker, errors)
    package = directory / "chatgpt-review-package.md"
    for marker in ("adaptive_followup_ratio", "pregenerated_question_violation", "chain_stop_quality", "highest_depth_chains", "weakest_chains", "part_a_gap_triggered_questions", "canonical_rewrite_mapping", "counter_retest_results"):
        _marker(package, marker, errors)
    retests = _jsonl(directory / "counter-retest.jsonl", errors)
    high_risk = manifest.get("high_risk_chain_ids", [])
    if not isinstance(high_risk, list):
        errors.append("high_risk_chain_ids must be a list")
        high_risk = []
    actual = {str(item.get("chain_id")) for item in retests}
    for chain_id in high_risk:
        if str(chain_id) not in actual:
            errors.append(f"missing counter-retest for high-risk chain {chain_id}")
    for item in retests:
        if not isinstance(item.get("question"), str) or not item.get("question").strip():
            errors.append("each counter-retest must contain a question")
        if not str(item.get("changed_scenario_or_constraint", "")).strip():
            errors.append("each counter-retest must change scenario, constraint or failure")


def _verify_external_gate(manifest: dict[str, Any], state: str, errors: list[str]) -> None:
    if manifest.get("main_merge_requires_chatgpt_verdict") is not True:
        errors.append("main_merge_requires_chatgpt_verdict must be true")
    if state == "WAITING_FOR_CHATGPT_REVIEW":
        if manifest.get("chatgpt_review_status") != "WAITING_FOR_CHATGPT_REVIEW":
            errors.append("WAITING_FOR_CHATGPT_REVIEW requires matching review status")
        if manifest.get("external_reviewed_sha") != "NOT_PROVIDED":
            errors.append("external_reviewed_sha must be NOT_PROVIDED before review")
    if state == "CLOSED":
        if manifest.get("chatgpt_review_status") != "VERDICT_PROVIDED":
            errors.append("CLOSED requires VERDICT_PROVIDED")
        if manifest.get("chatgpt_verdict") not in {"ACCEPT", "ACCEPT_WITH_DEBT"}:
            errors.append("CLOSED requires ACCEPT or ACCEPT_WITH_DEBT")
        candidate_sha = str(manifest.get("candidate_sha", ""))
        if not SHA40.fullmatch(candidate_sha) or manifest.get("external_reviewed_sha") != candidate_sha:
            errors.append("external_reviewed_sha must equal the reviewed candidate SHA")
        if manifest.get("merge_status") != "MERGED":
            errors.append("CLOSED requires MERGED")


def verify_round(directory: Path) -> list[str]:
    errors: list[str] = []
    manifest = _yaml(directory / "manifest.yaml", errors)
    state = str(manifest.get("state", manifest.get("round_state", "")))
    if "final_sha" in manifest:
        errors.append("self-referential final_sha is forbidden; use external_reviewed_sha")
    events, question_count = _verify_ledger(directory, manifest, state, errors)
    _verify_contexts(directory, manifest, errors)
    _verify_phase(directory, manifest, state, len(events), errors)
    _verify_transcript(directory, question_count, state, errors)
    _verify_post_live_artifacts(directory, manifest, state, errors)
    _verify_external_gate(manifest, state, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Zuno Red/Blue Workflow V4.2 artifacts")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bootstrap", type=Path)
    group.add_argument("--round", type=Path)
    args = parser.parse_args()
    errors = verify_bootstrap(args.bootstrap) if args.bootstrap else verify_round(args.round)
    if errors:
        print("RED_BLUE_WORKFLOW_V4_2_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RED_BLUE_WORKFLOW_V4_2_VALID")
    print("HUMAN_WRITING_REVIEW: WARNING_ONLY")
    return 0


if __name__ == "__main__":
    sys.exit(main())

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
CLOSURE_STATES = {"ABORTED_OPERATIONAL_PILOT"}
BATCH_PROFILE = "BATCH_ADVERSARIAL"
LIVE_PROFILE = "LIVE_ADAPTIVE"
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
    *CLOSURE_STATES,
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
    reviewed_sha = str(manifest.get("external_reviewed_sha", ""))
    if not (reviewed_sha == "NOT_PROVIDED" or SHA40.fullmatch(reviewed_sha)):
        errors.append("external_reviewed_sha must be NOT_PROVIDED or a 40-character SHA")
    if reviewed_sha != "NOT_PROVIDED":
        if manifest.get("chatgpt_verdict") not in {"ACCEPT", "ACCEPT_WITH_DEBT"}:
            errors.append("provided external review requires ACCEPT or ACCEPT_WITH_DEBT")
        if manifest.get("blocking_findings") != "NONE":
            errors.append("provided external review must declare blocking_findings: NONE")
    if manifest.get("historical_rounds_immutable") is not True:
        errors.append("historical_rounds_immutable must be true")
    if manifest.get("round_006_status") != "READY_FOR_ADAPTIVE_RED_BLUE_PILOT":
        errors.append("round_006_status must be READY_FOR_ADAPTIVE_RED_BLUE_PILOT")
    if manifest.get("round_006_started") is not False:
        errors.append("round_006_started must be false")
    expected_review_status = "VERDICT_PROVIDED" if reviewed_sha != "NOT_PROVIDED" else "WAITING_FOR_CHATGPT_REVIEW"
    if manifest.get("chatgpt_review_status") != expected_review_status:
        errors.append(f"bootstrap chatgpt_review_status must be {expected_review_status}")
    expected_round_status = "V4.2_WORKFLOW_ACCEPTED_WITH_DEBT" if manifest.get("chatgpt_verdict") == "ACCEPT_WITH_DEBT" else "V4.2_WORKFLOW_READY_FOR_CHATGPT_REVIEW"
    if manifest.get("round_status") != expected_round_status:
        errors.append(f"round_status must be {expected_round_status}")
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
    package_markers = ("WORKFLOW_CONTRACT_AVAILABLE", "READY_FOR_ADAPTIVE_RED_BLUE_PILOT")
    package_markers += (("NOT_STARTED", "external_reviewed_sha: NOT_PROVIDED") if reviewed_sha == "NOT_PROVIDED" else ("ACCEPT_WITH_DEBT", "blocking_findings: NONE", "external_reviewed_sha:"))
    for marker in package_markers:
        _marker(package, marker, errors)
    verdict = directory / "chatgpt-verdict.md"
    _marker(verdict, "NOT_PROVIDED" if reviewed_sha == "NOT_PROVIDED" else "ACCEPT_WITH_DEBT", errors)
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
    if state in POST_LIVE_STATES or state in CLOSURE_STATES:
        for qid in questions:
            if qid not in answers or qid not in decisions:
                errors.append(f"post-live ledger is incomplete for {qid}")
    count = len(question_events)
    if count > 100:
        errors.append("question count cannot exceed 100")
    allowed_insufficient_reasons = {"USER_GATE", "ARCHITECTURE_BLOCKER"}
    if state in CLOSURE_STATES:
        allowed_insufficient_reasons.add("WORKFLOW_EXECUTION_BLOCKER")
    if count < 80 and manifest.get("question_budget_stop_reason") not in allowed_insufficient_reasons:
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
    if not path.exists() or state not in POST_LIVE_STATES and state not in CLOSURE_STATES:
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
    elif state in CLOSURE_STATES:
        if manifest.get("candidate") != "NONE":
            errors.append("aborted operational pilot must have candidate: NONE")
        if manifest.get("candidate_branch") not in (None, ""):
            errors.append("aborted operational pilot must not have a candidate branch")
        if manifest.get("main_merge") != "NOT_ATTEMPTED":
            errors.append("aborted operational pilot must not attempt main merge")
        if manifest.get("architecture_score") != "INVALID":
            errors.append("aborted operational pilot architecture_score must be INVALID")
        if manifest.get("architecture_blocker") != "NONE_ESTABLISHED":
            errors.append("aborted operational pilot architecture_blocker must be NONE_ESTABLISHED")
        if manifest.get("user_gate") != "NOT_TRIGGERED":
            errors.append("aborted operational pilot user_gate must be NOT_TRIGGERED")


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


def _verify_batch_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    """Read a batch-profile JSONL artifact without imposing Live Ledger rules."""
    return _jsonl(path, errors)


def verify_batch_round(directory: Path) -> list[str]:
    """Validate the default V4.2 batch adversarial profile.

    Batch review intentionally permits a complete 100-question artifact.  Its
    anti-fabrication boundary is different from Live Adaptive: every answer,
    counter question, session role, and synthesis transition must be explicit.
    """
    errors: list[str] = []
    manifest = _yaml(directory / "manifest.yaml", errors)
    if manifest.get("workflow_id") != V42_WORKFLOW:
        errors.append("batch workflow_id must be ZUNO-RED-BLUE-WORKFLOW-V4.2")
    if manifest.get("execution_profile") != BATCH_PROFILE:
        errors.append("execution_profile must be BATCH_ADVERSARIAL")
    if manifest.get("state") not in POST_LIVE_STATES:
        errors.append("batch profile must be in a post-attack state")
    if not SHA40.fullmatch(str(manifest.get("artifact_base_sha", ""))):
        errors.append("batch artifact_base_sha must be a 40-character SHA")
    if manifest.get("question_count") != 100:
        errors.append("batch profile requires exactly 100 recorded questions")
    if not isinstance(manifest.get("chain_count"), int) or not 12 <= manifest.get("chain_count", 0) <= 18:
        errors.append("batch chain_count must be between 12 and 18")
    if manifest.get("red_reads_interview_calibration") is not True:
        errors.append("Red must read interview calibration in the batch profile")
    if manifest.get("blue_reads_interview_calibration") is not False:
        errors.append("Blue must not read interview calibration in the batch profile")
    if manifest.get("red_reads_business_code") is not False or manifest.get("blue_reads_business_code") is not False:
        errors.append("Red and Blue business-code access must be false")
    if manifest.get("blue_defense_candidate_write") is not False:
        errors.append("Blue defense candidate write must be false")
    if manifest.get("synthesis_after_counter") is not True:
        errors.append("Blue synthesis must occur after the counter-defense phase")

    roles = {
        "red_attack_session_id": "red attack",
        "blue_defense_session_id": "blue defense",
        "red_counter_session_id": "red counter",
        "blue_counter_defense_session_id": "blue counter defense",
        "blue_synthesis_session_id": "blue synthesis",
        "red_judge_session_id": "red judge",
    }
    session_ids: dict[str, str] = {}
    for key, label in roles.items():
        value = str(manifest.get(key, ""))
        if not value:
            errors.append(f"missing {label} session id: {key}")
        session_ids[key] = value
    nonempty = [value for value in session_ids.values() if value]
    if len(nonempty) != len(set(nonempty)):
        errors.append("session reuse across incompatible roles is forbidden")
    if session_ids.get("red_judge_session_id") in {
        session_ids.get("red_attack_session_id"),
        session_ids.get("red_counter_session_id"),
    }:
        errors.append("Red Judge must use a fresh session distinct from Red Attack and Counter")

    base = str(manifest.get("artifact_base_sha", ""))
    session_bases = manifest.get("session_base_shas", {})
    if not isinstance(session_bases, dict):
        errors.append("session_base_shas must be a mapping")
    else:
        for key in roles:
            if session_bases.get(key) != base:
                errors.append(f"{key} must use the same BASE snapshot")

    question_events = _verify_batch_jsonl(directory / "batch-red-questions.jsonl", errors)
    answer_events = _verify_batch_jsonl(directory / "batch-blue-answers.jsonl", errors)
    counter_events = _verify_batch_jsonl(directory / "batch-red-counter.jsonl", errors)
    counter_answers = _verify_batch_jsonl(directory / "batch-blue-counter-answers.jsonl", errors)
    questions: dict[str, dict[str, Any]] = {}
    answers: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(question_events, start=1):
        qid = str(item.get("question_id", ""))
        expected = f"Q{index:03d}"
        if qid != expected:
            errors.append(f"batch question ids must be sequential; expected {expected}")
        if not str(item.get("chain_id", "")):
            errors.append(f"batch question {qid} must have a chain_id")
        question = str(item.get("question", ""))
        if not question.strip() or item.get("question_sha") != _sha256(question):
            errors.append(f"batch question {qid} has invalid question hash")
        questions[qid] = item
    for item in answer_events:
        qid = str(item.get("question_id", ""))
        if qid not in questions:
            errors.append(f"batch answer references unknown question {qid}")
            continue
        answer = str(item.get("blue_answer", ""))
        if not answer.strip() or item.get("answer_sha") != _sha256(answer):
            errors.append(f"batch answer {qid} has invalid answer hash")
        if item.get("question_sha") != questions[qid].get("question_sha"):
            errors.append(f"batch answer {qid} does not preserve question identity")
        if item.get("part_a_support") not in VALID_SUPPORT or item.get("answer_source") not in VALID_SOURCES:
            errors.append(f"batch answer {qid} has invalid Part-A support/source")
        answers[qid] = item
    if len(question_events) != 100 or set(answers) != set(questions):
        errors.append("batch answers must cover all 100 questions")

    defense = directory / "batch-blue-defense.md"
    _require(defense, errors)
    if defense.exists():
        text = _read(defense).lower()
        for marker in ("live_defense", "interview_calibration: prohibited", "canonical_write: prohibited"):
            if marker not in text:
                errors.append(f"batch-blue-defense.md must contain {marker}")
        for forbidden in ("interview_calibration: read", "calibration_access: allowed", "candidate_write: true", "canonical_write: allowed"):
            if forbidden in text:
                errors.append(f"batch-blue-defense.md contains forbidden marker: {forbidden}")

    counter_ids: set[str] = set()
    for item in counter_events:
        counter_id = str(item.get("counter_question_id", ""))
        original = str(item.get("original_question_id", ""))
        answer_ref = str(item.get("blue_answer_ref", ""))
        if not counter_id or counter_id in counter_ids:
            errors.append("counter question ids must be unique and non-empty")
        counter_ids.add(counter_id)
        if original not in answers:
            errors.append(f"counter question {counter_id} must reference a real original Blue answer")
        if answer_ref != f"A:{original}" or answer_ref[2:] not in answers:
            errors.append(f"counter question {counter_id} has an invalid original answer reference")
        if not str(item.get("trigger_detail", "")).strip():
            errors.append(f"counter question {counter_id} must explain its trigger")
    for item in counter_answers:
        if str(item.get("counter_question_id", "")) not in counter_ids:
            errors.append("counter defense answer must reference a real counter question")

    synthesis = directory / "batch-blue-synthesis.md"
    judge = directory / "batch-red-judge.md"
    candidate = directory / "batch-candidate-manifest.yaml"
    for path in (synthesis, judge, candidate):
        _require(path, errors)
    if synthesis.exists():
        for marker in ("SYNTHESIS_AFTER_COUNTER", "ROOT_ARCHITECTURE_GAPS", "CANDIDATE_WRITE_AFTER_COUNTER"):
            _marker(synthesis, marker, errors)
    if judge.exists():
        for marker in ("FRESH_JUDGE_SESSION", "COUNTER_RETEST", "PART_A_FIRST"):
            _marker(judge, marker, errors)
    candidate_manifest = _yaml(candidate, errors) if candidate.exists() else {}
    candidate_branch = str(candidate_manifest.get("candidate_branch", manifest.get("candidate_branch", "")))
    main_branch = str(manifest.get("main_branch", "main"))
    if not candidate_branch or candidate_branch == main_branch:
        errors.append("batch candidate branch must be distinct from main")
    if candidate_manifest.get("candidate_created_after_synthesis") is not True:
        errors.append("batch candidate must be created after synthesis")

    counter_seq = int(manifest.get("counter_event_seq", 0))
    synthesis_seq = int(manifest.get("synthesis_event_seq", 0))
    judge_seq = int(manifest.get("judge_event_seq", 0))
    if not counter_seq or not synthesis_seq or synthesis_seq <= counter_seq:
        errors.append("synthesis must occur after counter-defense")
    if not judge_seq or judge_seq <= synthesis_seq:
        errors.append("fresh Red Judge must occur after synthesis")
    if manifest.get("chatgpt_review_status") != "WAITING_FOR_CHATGPT_REVIEW":
        errors.append("batch candidate must wait for ChatGPT review")
    if manifest.get("external_reviewed_sha") != "NOT_PROVIDED":
        errors.append("batch merge gate must not claim an external verdict")
    if manifest.get("main_merge_status") != "NOT_ATTEMPTED":
        errors.append("batch merge must not occur before external verdict")
    return errors


def verify_round(directory: Path) -> list[str]:
    manifest_path = directory / "manifest.yaml"
    if manifest_path.exists():
        try:
            manifest = yaml.safe_load(_read(manifest_path))
        except yaml.YAMLError:
            manifest = {}
        if isinstance(manifest, dict) and manifest.get("execution_profile") == BATCH_PROFILE:
            return verify_batch_round(directory)
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
    parser.add_argument("--profile", choices=("auto", "live_adaptive", "batch_adversarial"), default="auto")
    args = parser.parse_args()
    if args.bootstrap:
        errors = verify_bootstrap(args.bootstrap)
    elif args.profile == "batch_adversarial":
        errors = verify_batch_round(args.round)
    elif args.profile == "live_adaptive":
        errors = verify_round(args.round)
    else:
        errors = verify_round(args.round)
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

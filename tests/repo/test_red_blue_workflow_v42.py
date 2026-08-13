from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from shutil import copytree

import yaml


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/scripts/verify_red_blue_workflow_v42.py"
BOOTSTRAP = ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-BOOTSTRAP"


def _module():
    spec = importlib.util.spec_from_file_location("verify_red_blue_workflow_v42", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(value: str | bytes) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _write_events(path: Path, events: list[dict[str, object]]) -> str:
    previous = "0" * 64
    lines: list[str] = []
    for event in events:
        body = dict(event)
        body["rolling_hash"] = _sha(previous + _canonical(body))
        previous = body["rolling_hash"]  # type: ignore[assignment]
        lines.append(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return previous


def _write_common(directory: Path) -> dict[str, object]:
    (directory / "context-packets").mkdir(parents=True)
    base = "0123456789abcdef0123456789abcdef01234567"
    snapshot = directory / "canonical-snapshot.yaml"
    snapshot.write_text(
        f"round_id: R006\nbase_sha: {base}\ncanonical_part_a: docs/architecture/architecture.md\n",
        encoding="utf-8",
    )
    snapshot_sha = _sha(snapshot.read_bytes())
    (directory / "context-packets/red-context.md").write_text(
        f"base_sha: {base}\ncanonical_snapshot_sha: {snapshot_sha}\nbusiness_implementation_code: PROHIBITED\npart_a_role: ARCHITECTURE_KNOWLEDGE_SOURCE\ninterview_calibration: RED_ONLY\n",
        encoding="utf-8",
    )
    (directory / "context-packets/blue-context.md").write_text(
        f"base_sha: {base}\ncanonical_snapshot_sha: {snapshot_sha}\nbusiness_implementation_code: PROHIBITED\npart_a_role: ARCHITECTURE_KNOWLEDGE_SOURCE\nanswer_context: BASE_SNAPSHOT_ONLY\ncanonical_write_phase: AFTER_LIVE_ATTACK_COMPLETE\ninterview_calibration: PROHIBITED\n",
        encoding="utf-8",
    )
    return {"base": base, "snapshot_sha": snapshot_sha}


def _write_round(tmp_path: Path, *, state: str = "WAITING_FOR_CHATGPT_REVIEW") -> Path:
    directory = tmp_path / "round"
    context = _write_common(directory)
    specs = [
        {
            "chain_id": f"C{index:02d}",
            "root_claim": f"claim-{index}",
            "primary_concept": f"concept-{index}",
            "attack_intent": "test the smallest defensible boundary",
            "possible_pressure_axes": ["failure", "alternative", "reversal"],
        }
        for index in range(1, 13)
    ]
    counts = [7] * 8 + [6] * 4
    events: list[dict[str, object]] = []
    transcript: list[str] = []
    question_number = 0
    event_seq = 0
    previous_by_chain: dict[str, str] = {}
    for chain_index, count in enumerate(counts, start=1):
        chain_id = f"C{chain_index:02d}"
        for local_index in range(count):
            question_number += 1
            qid = f"Q{question_number:03d}"
            is_root = local_index == 0
            question = f"How does {chain_id} preserve its boundary under pressure {question_number}?"
            q_event = {
                "event_seq": event_seq + 1,
                "event_id": f"E{event_seq + 1:04d}",
                "event_type": "QUESTION_FROZEN",
                "turn_id": f"T{question_number:03d}",
                "chain_id": chain_id,
                "question_id": qid,
                "question": question,
                "question_sha": _sha(question),
                "blue_answer": None,
                "answer_sha": None,
                "is_root": is_root,
                "novelty": "NOVEL" if question_number <= 64 else "REGRESSION",
                "followup_reason": None if is_root else "FAILURE_GAP",
                "followup_trigger_detail": None if is_root else f"A{question_number - 1:03d} left recovery pressure unresolved.",
                "previous_turn_ref": None if is_root else f"A:Q{question_number - 1:03d}",
                "timestamp": question_number,
            }
            events.append(q_event)
            event_seq += 1
            answer = f"The canonical owner for {chain_id} is explicit, and retry is bounded for turn {question_number}."
            a_event = {
                "event_seq": event_seq + 1,
                "event_id": f"E{event_seq + 1:04d}",
                "event_type": "ANSWER_FROZEN",
                "turn_id": f"T{question_number:03d}",
                "chain_id": chain_id,
                "question_id": qid,
                "question": question,
                "question_sha": _sha(question),
                "blue_answer": answer,
                "answer_sha": _sha(answer),
                "part_a_support": "SUFFICIENT",
                "answer_source": "PART_A",
                "previous_turn_ref": f"Q:{qid}",
                "timestamp": question_number,
            }
            events.append(a_event)
            event_seq += 1
            decision = "CONTINUE_CHAIN" if local_index < count - 1 else "CLOSE_CHAIN"
            d_event = {
                "event_seq": event_seq + 1,
                "event_id": f"E{event_seq + 1:04d}",
                "event_type": "CHAIN_DECISION",
                "turn_id": f"T{question_number:03d}",
                "chain_id": chain_id,
                "question_id": qid,
                "chain_decision": decision,
                "chain_stop_reason": "CONTINUE_FROM_ANSWER" if decision == "CONTINUE_CHAIN" else "ALL_PRIORITY_CHAINS_CLOSED",
                "previous_turn_ref": f"A:{qid}",
                "timestamp": question_number,
            }
            events.append(d_event)
            event_seq += 1
            previous_by_chain[chain_id] = qid
            transcript.extend([f"RED Q{question_number:03d}", f"BLUE A{question_number:03d}", "RED CHAIN DECISION"])
    ledger_hash = _write_events(directory / "question-answer-ledger.jsonl", events)
    (directory / "live-interrogation.md").write_text("\n".join(transcript) + "\n", encoding="utf-8")
    final_sha = "abcdef0123456789abcdef0123456789abcdef01"
    for name, content in {
        "blue-architecture-decisions.md": "Architecture Decision Set",
        "architecture-deltas.md": "Canonical Delta",
        "canonical-sync-record.md": "Candidate Canonical Sync",
        "red-counter-review.md": "Counter-Retest Review",
        "part-a-explainability.md": "PART_A_EXPLAINABILITY\nCLEAR DENSE TERM_DEPENDENT MISSING",
        "scorecard.md": "Interview depth scorecard",
        "chatgpt-review-package.md": "adaptive_followup_ratio\npregenerated_question_violation\nchain_stop_quality\nhighest_depth_chains\nweakest_chains\npart_a_gap_triggered_questions\ncanonical_rewrite_mapping\ncounter_retest_results",
        "context-packets/red-judge-context.md": "BASE Part A\nComplete Q/A Ledger\nBlue Architecture Decisions\nCanonical Delta\nFinal Part A\nFinal Part B\nCandidate SHA",
    }.items():
        (directory / name).write_text(content, encoding="utf-8")
    retests = [
        {"chain_id": "C01", "question": "What if the provider has no query endpoint?", "changed_scenario_or_constraint": "provider has no query endpoint"},
        {"chain_id": "C02", "question": "What if the database commit succeeds before the checkpoint?", "changed_scenario_or_constraint": "commit/checkpoint order reversed"},
    ]
    (directory / "counter-retest.jsonl").write_text("\n".join(json.dumps(item) for item in retests) + "\n", encoding="utf-8")
    manifest = {
        "workflow_id": "ZUNO-RED-BLUE-WORKFLOW-V4.2",
        "round_id": "RB-WORKFLOW-V4.2-ROUND-006-SYNTHETIC",
        "state": state,
        "artifact_base_sha": context["base"],
        "red_session_id": "red-r006-fresh",
        "blue_session_id": "blue-r006-fresh",
        "external_reviewed_sha": "NOT_PROVIDED",
        "question_mode": "QUESTION_BY_QUESTION_ADAPTIVE_INTERROGATION",
        "question_target": 100,
        "question_max": 100,
        "normal_min": 80,
        "blue_reads_interview_calibration": False,
        "ledger_artifact": "question-answer-ledger.jsonl",
        "rolling_ledger_hash": ledger_hash,
        "question_count": 80,
        "question_budget_stop_reason": "ALL_PRIORITY_CHAINS_CLOSED",
        "adaptive_followup_ratio": 0.85,
        "novel_question_count": 64,
        "regression_question_count": 16,
        "chain_specs": specs,
        "facts_changed": "NONE",
        "runtime_changed": "NONE",
        "red_reads_business_code": False,
        "blue_reads_business_code": False,
        "blue_uses_code_as_architecture_reason": False,
        "blue_push_main": False,
        "schema_changed": "NONE",
        "migration_changed": "NONE",
        "adr_changed": "NONE",
        "canonical_content_changed": "NONE",
        "whole_round_question_freeze": "FORBIDDEN",
        "blue_canonical_modified_during_live": False,
        "canonical_write_phase": "AFTER_LIVE_ATTACK_COMPLETE",
        "blue_synthesis_started_after_event_seq": len(events) + 1,
        "candidate_created_after_live_attack": True,
        "candidate_branch": "codex/r006-blue-candidate",
        "main_branch": "main",
        "chatgpt_review_status": "WAITING_FOR_CHATGPT_REVIEW",
        "main_merge_requires_chatgpt_verdict": True,
        "high_risk_chain_ids": ["C01", "C02"],
        "candidate_sha": final_sha,
    }
    (directory / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return directory


def test_v42_bootstrap_passes():
    module = _module()
    assert module.verify_bootstrap(BOOTSTRAP) == []


def test_v42_adaptive_round_passes(tmp_path: Path):
    module = _module()
    assert module.verify_round(_write_round(tmp_path)) == []


def test_chain_spec_question_ids_are_rejected(tmp_path: Path):
    module = _module()
    directory = _write_round(tmp_path)
    manifest_path = directory / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["chain_specs"][0]["question_ids"] = ["Q001", "Q002"]
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    errors = module.verify_round(directory)
    assert any("PREGENERATED_QUESTION_SET_VIOLATION" in error for error in errors)


def test_second_question_before_first_answer_is_rejected(tmp_path: Path):
    module = _module()
    directory = _write_round(tmp_path)
    path = directory / "question-answer-ledger.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    first_q, first_a, first_d, second_q = [json.loads(line) for line in lines[:4]]
    reordered = [first_q, second_q, first_a, first_d] + [json.loads(line) for line in lines[4:]]
    _write_events(path, reordered)
    errors = module.verify_round(directory)
    assert any("PREGENERATED_QUESTION_SET_VIOLATION" in error for error in errors)


def test_answer_before_question_is_rejected(tmp_path: Path):
    module = _module()
    directory = _write_round(tmp_path)
    path = directory / "question-answer-ledger.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    first_q, first_a = json.loads(lines[0]), json.loads(lines[1])
    _write_events(path, [first_a, first_q] + [json.loads(line) for line in lines[2:]])
    errors = module.verify_round(directory)
    assert any("appeared before its question" in error for error in errors)


def test_followup_reason_is_required(tmp_path: Path):
    module = _module()
    directory = _write_round(tmp_path)
    path = directory / "question-answer-ledger.jsonl"
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    events[3]["followup_reason"] = None
    _write_events(path, events)
    errors = module.verify_round(directory)
    assert any("invalid followup_reason" in error for error in errors)


def test_rolling_hash_tamper_is_rejected(tmp_path: Path):
    module = _module()
    directory = _write_round(tmp_path)
    path = directory / "question-answer-ledger.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    event = json.loads(lines[1])
    event["blue_answer"] = "tampered"
    lines[1] = json.dumps(event)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    errors = module.verify_round(directory)
    assert any("rolling hash mismatch" in error for error in errors)


def test_blue_canonical_change_during_live_is_rejected(tmp_path: Path):
    module = _module()
    directory = _write_round(tmp_path)
    manifest_path = directory / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["blue_canonical_modified_during_live"] = True
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    errors = module.verify_round(directory)
    assert any("blue_canonical_modified_during_live" in error for error in errors)


def test_old_questions_frozen_sha_is_rejected(tmp_path: Path):
    module = _module()
    directory = _write_round(tmp_path)
    manifest_path = directory / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["questions_frozen_sha"] = "forbidden"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    errors = module.verify_round(directory)
    assert any("questions_frozen_sha is forbidden" in error for error in errors)

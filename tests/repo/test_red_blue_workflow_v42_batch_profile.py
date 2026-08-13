from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/scripts/verify_red_blue_workflow_v42.py"


def _module():
    spec = importlib.util.spec_from_file_location("verify_red_blue_workflow_v42_batch", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def _write_batch(tmp_path: Path) -> Path:
    directory = tmp_path / "batch-round"
    directory.mkdir()
    base = "0123456789abcdef0123456789abcdef01234567"
    session_keys = (
        "red_attack_session_id",
        "blue_defense_session_id",
        "red_counter_session_id",
        "blue_counter_defense_session_id",
        "blue_synthesis_session_id",
        "red_judge_session_id",
    )
    manifest: dict[str, object] = {
        "workflow_id": "ZUNO-RED-BLUE-WORKFLOW-V4.2",
        "round_id": "RB-WORKFLOW-V4.2-ROUND-007-SYNTHETIC",
        "execution_profile": "BATCH_ADVERSARIAL",
        "state": "WAITING_FOR_CHATGPT_REVIEW",
        "artifact_base_sha": base,
        "question_count": 100,
        "chain_count": 12,
        "red_reads_interview_calibration": True,
        "blue_reads_interview_calibration": False,
        "red_reads_business_code": False,
        "blue_reads_business_code": False,
        "blue_defense_candidate_write": False,
        "synthesis_after_counter": True,
        "candidate_branch": "codex/r007-blue-candidate",
        "main_branch": "main",
        "counter_event_seq": 200,
        "synthesis_event_seq": 300,
        "judge_event_seq": 400,
        "chatgpt_review_status": "WAITING_FOR_CHATGPT_REVIEW",
        "external_reviewed_sha": "NOT_PROVIDED",
        "main_merge_status": "NOT_ATTEMPTED",
    }
    for index, key in enumerate(session_keys, start=1):
        manifest[key] = f"session-{index}"
    manifest["session_base_shas"] = {key: base for key in session_keys}
    questions: list[dict[str, object]] = []
    answers: list[dict[str, object]] = []
    for index in range(1, 101):
        qid = f"Q{index:03d}"
        question = f"How does chain C{(index - 1) % 12 + 1:02d} survive pressure {index}?"
        question_sha = _sha(question)
        questions.append({"question_id": qid, "chain_id": f"C{(index - 1) % 12 + 1:02d}", "question": question, "question_sha": question_sha})
        answer = f"The owner and recovery boundary for {qid} are explicit."
        answers.append({"question_id": qid, "question_sha": question_sha, "blue_answer": answer, "answer_sha": _sha(answer), "part_a_support": "SUFFICIENT", "answer_source": "PART_A"})
    counters = [
        {"counter_question_id": f"CQ{index:03d}", "original_question_id": f"Q{index:03d}", "blue_answer_ref": f"A:Q{index:03d}", "trigger_detail": "The original answer leaves a changed failure constraint unresolved."}
        for index in range(1, 13)
    ]
    counter_answers = [{"counter_question_id": item["counter_question_id"], "answer": "The invariant still holds under the changed constraint."} for item in counters]
    _write_jsonl(directory / "batch-red-questions.jsonl", questions)
    _write_jsonl(directory / "batch-blue-answers.jsonl", answers)
    _write_jsonl(directory / "batch-red-counter.jsonl", counters)
    _write_jsonl(directory / "batch-blue-counter-answers.jsonl", counter_answers)
    (directory / "batch-blue-defense.md").write_text(
        "LIVE_DEFENSE\ninterview_calibration: PROHIBITED\ncanonical_write: PROHIBITED\n",
        encoding="utf-8",
    )
    (directory / "batch-blue-synthesis.md").write_text(
        "SYNTHESIS_AFTER_COUNTER\nROOT_ARCHITECTURE_GAPS\nCANDIDATE_WRITE_AFTER_COUNTER\n",
        encoding="utf-8",
    )
    (directory / "batch-red-judge.md").write_text(
        "FRESH_JUDGE_SESSION\nCOUNTER_RETEST\nPART_A_FIRST\n",
        encoding="utf-8",
    )
    (directory / "batch-candidate-manifest.yaml").write_text(
        yaml.safe_dump({"candidate_branch": "codex/r007-blue-candidate", "candidate_created_after_synthesis": True}, sort_keys=False),
        encoding="utf-8",
    )
    (directory / "manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return directory


def _errors(tmp_path: Path):
    directory = _write_batch(tmp_path)
    return directory, _module().verify_round(directory)


def test_batch_100_questions_are_allowed(tmp_path: Path):
    _, errors = _errors(tmp_path)
    assert errors == []


def test_v42_header_scopes_question_generation_by_profile():
    protocol = (ROOT / "project-reconstruction-lab/05-red-blue/round-protocol-v4.2.md").read_text(encoding="utf-8")
    assert "review_mode: PROFILE_DEPENDENT" in protocol
    assert "whole_round_question_freeze: PROFILE_DEPENDENT" in protocol
    assert "batch_adversarial:\n  full_round_question_generation: ALLOWED" in protocol
    assert "live_adaptive:\n  full_round_question_generation: FORBIDDEN" in protocol


def test_live_pregen_question_set_remains_rejected(tmp_path: Path):
    directory = _write_batch(tmp_path)
    manifest_path = directory / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["execution_profile"] = "LIVE_ADAPTIVE"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("missing required artifact: question-answer-ledger.jsonl" in error for error in errors)


def test_blue_calibration_access_is_rejected(tmp_path: Path):
    directory = _write_batch(tmp_path)
    path = directory / "batch-blue-defense.md"
    path.write_text(path.read_text(encoding="utf-8") + "interview_calibration: READ\n", encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("forbidden marker" in error for error in errors)


def test_blue_defense_candidate_write_is_rejected(tmp_path: Path):
    directory = _write_batch(tmp_path)
    path = directory / "batch-blue-defense.md"
    path.write_text(path.read_text(encoding="utf-8") + "candidate_write: true\n", encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("forbidden marker" in error for error in errors)


def test_counter_missing_original_answer_reference_is_rejected(tmp_path: Path):
    directory = _write_batch(tmp_path)
    path = directory / "batch-red-counter.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    rows[0]["blue_answer_ref"] = "A:Q999"
    _write_jsonl(path, rows)
    errors = _module().verify_round(directory)
    assert any("invalid original answer reference" in error for error in errors)


def test_session_reuse_across_roles_is_rejected(tmp_path: Path):
    directory = _write_batch(tmp_path)
    path = directory / "manifest.yaml"
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    manifest["red_counter_session_id"] = manifest["red_attack_session_id"]
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("session reuse" in error for error in errors)


def test_synthesis_before_counter_is_rejected(tmp_path: Path):
    directory = _write_batch(tmp_path)
    path = directory / "manifest.yaml"
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    manifest["synthesis_event_seq"] = 100
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("synthesis must occur after counter-defense" in error for error in errors)


def test_judge_reusing_red_attack_session_is_rejected(tmp_path: Path):
    directory = _write_batch(tmp_path)
    path = directory / "manifest.yaml"
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    manifest["red_judge_session_id"] = manifest["red_attack_session_id"]
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("session reuse" in error or "fresh session" in error for error in errors)


def test_candidate_on_main_is_rejected(tmp_path: Path):
    directory = _write_batch(tmp_path)
    path = directory / "batch-candidate-manifest.yaml"
    candidate = yaml.safe_load(path.read_text(encoding="utf-8"))
    candidate["candidate_branch"] = "main"
    path.write_text(yaml.safe_dump(candidate, sort_keys=False), encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("candidate branch must be distinct" in error for error in errors)


def test_merge_without_external_verdict_is_rejected(tmp_path: Path):
    directory = _write_batch(tmp_path)
    path = directory / "manifest.yaml"
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    manifest["main_merge_status"] = "MERGED"
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    errors = _module().verify_round(directory)
    assert any("must not occur before external verdict" in error for error in errors)

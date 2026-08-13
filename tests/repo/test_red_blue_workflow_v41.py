from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/scripts/verify_red_blue_workflow_v41.py"


def _module():
    spec = importlib.util.spec_from_file_location("verify_red_blue_workflow_v41", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_round(tmp_path: Path, *, state: str = "WAITING_FOR_CHATGPT_REVIEW") -> Path:
    directory = tmp_path / "round"
    (directory / "context-packets").mkdir(parents=True)
    questions = "\n".join(f"## Q{index:03d}\n\nConceptual question {index}.\n" for index in range(1, 101))
    (directory / "red-questions.md").write_text(questions, encoding="utf-8")
    question_sha = _sha(directory / "red-questions.md")
    base = "0123456789abcdef0123456789abcdef01234567"
    packet = "# Interview Calibration\naudience: RED_THREAD_ONLY\nanswer_content_included: `NO`\n"
    (directory / "interview-calibration-packet.md").write_text(packet, encoding="utf-8")
    packet_sha = _sha(directory / "interview-calibration-packet.md")
    snapshot = f"""round_id: R006\nbase_sha: {base}\ncanonical_files:\n  - docs/project/architecture/architecture.md\ncanonical_part_a_files:\n  - docs/project/architecture/architecture.md\ncanonical_part_b_files:\n  - docs/project/domain/legal-domain-model.md\nfact_baseline: docs/project/facts\nactive_adr: []\ngovernance_files: []\narchitecture_state: ACCEPTED_TARGET\nmaturity_state: ACCEPTED_TARGET\nfixed_constraints: []\ngenerated_at: 2026-08-13T00:00:00Z\n"""
    (directory / "canonical-snapshot.yaml").write_text(snapshot, encoding="utf-8")
    snapshot_sha = _sha(directory / "canonical-snapshot.yaml")
    red = f"# Red Context\nbase_sha: {base}\ncanonical_snapshot_sha: {snapshot_sha}\nread-only\nbusiness_implementation_code: PROHIBITED\npart_a_role: ARCHITECTURE_KNOWLEDGE_SOURCE\ninterview_calibration: RED_ONLY\ninterview_calibration_packet_sha: {packet_sha}\n"
    blue = f"# Blue Canonical Writer\nbase_sha: {base}\ncanonical_snapshot_sha: {snapshot_sha}\ncanonical writer\nred-questions\nquestions_frozen_sha: {question_sha}\nbusiness_implementation_code: PROHIBITED\npart_a_role: ARCHITECTURE_KNOWLEDGE_SOURCE\ncode_is_not_architecture_reason\ninterview_calibration: PROHIBITED\n"
    (directory / "context-packets/red-context.md").write_text(red, encoding="utf-8")
    (directory / "context-packets/blue-context.md").write_text(blue, encoding="utf-8")
    final_sha = "abcdef0123456789abcdef0123456789abcdef01"
    judge = f"# Original Snapshot\nbase_sha: {base}\ncanonical_snapshot_sha: {snapshot_sha}\n# Blue Answers\n# Blue Decisions\n# Canonical Diff\nblue_final_sha: {final_sha}\n"
    (directory / "context-packets/red-judge-context.md").write_text(judge, encoding="utf-8")
    judge_sha = _sha(directory / "context-packets/red-judge-context.md")
    (directory / "part-a-explainability.md").write_text(
        "# PART_A_EXPLAINABILITY\n\nCLEAR: 70\nPARTIAL: 25\nMISSING: 5\n\nINTERVIEW_EXPLAINABILITY: CLEAR 70 / DENSE 20 / TERM_DEPENDENT 5 / MISSING 5\n",
        encoding="utf-8",
    )
    (directory / "interview-depth.md").write_text(
        "# INTERVIEW_DEPTH\n\nEach chain is scored on a 0–5 scale.\n",
        encoding="utf-8",
    )
    for name, content in {
        "blue-answers.md": "answers",
        "blue-decisions.md": "decisions",
        "architecture-deltas.md": "deltas",
        "canonical-sync-record.md": f"blue_final_sha: {final_sha}",
        "scorecard.md": f"scored_final_sha: {final_sha}",
        "chatgpt-review-package.md": "WAITING_FOR_CHATGPT_REVIEW",
    }.items():
        (directory / name).write_text(content, encoding="utf-8")
    chain_lines = []
    cursor = 1
    for chain_index in range(1, 13):
        count = 10 if chain_index <= 2 else 8
        ids = [f"Q{value:03d}" for value in range(cursor, cursor + count)]
        cursor += count
        chain_lines.extend(
            [
                f"  - chain_id: C{chain_index:02d}",
                f"    root_claim: claim-{chain_index}",
                "    question_ids: [" + ", ".join(ids) + "]",
                f"    primary_concept: concept-{chain_index}",
                "    questioning_pattern_source: REAL_SELF_INTERVIEW",
                "    counterfactual_used: true",
                "    alternative_used: false",
                "    failure_used: true",
                "    reversal_used: false",
                "    constraint_injected: true",
                "    interview_depth: 4",
            ]
        )
    manifest = f"""workflow_id: ZUNO-RED-BLUE-WORKFLOW-V4.1\nround_id: R006\nbase_sha: {base}\nred_session_id: RB-R006-RED\nblue_session_id: RB-R006-BLUE\nred_fresh_context: true\nblue_fresh_context: true\ncanonical_snapshot_sha: {snapshot_sha}\nquestions_frozen_sha: {question_sha}\nblue_questions_sha: {question_sha}\nblue_final_sha: {final_sha}\nred_judge_packet_sha: {judge_sha}\nchatgpt_review_status: WAITING_FOR_CHATGPT_REVIEW\nround_status: {state}\nred_session_closed: false\nblue_session_closed: false\nred_read_only: true\nblue_canonical_writer: true\ncanonical_sync_mode: FULL_PART_REWRITE\nfacts_changed: NONE\nprevious_reasoning_included: false\nhistory_chat_included: false\nconceptual_architecture_review: true\nred_reads_business_code: false\nblue_reads_business_code: false\nblue_uses_code_as_architecture_reason: false\ninterview_calibration_packet: interview-calibration-packet.md\ninterview_calibration_packet_sha: {packet_sha}\ninterview_calibration_read_by_red: true\ninterview_calibration_read_by_blue: false\ninterview_depth_artifact: interview-depth.md\ncandidate_branch: codex/r006-blue\nintegration_branch: main\nmain_branch: main\nblue_push_main: false\nmain_integrator: MAIN_THREAD\nmain_merge_requires_chatgpt_verdict: true\nred_judge_part_a_first_pass: true\npart_a_explainability_artifact: part-a-explainability.md\npart_a_clear_count: 70\npart_a_partial_count: 25\npart_a_missing_count: 5\nhuman_writing_verifier_mode: WARNING_ONLY\nmerge_status: NOT_MERGED\nmain_final_sha: null\nblue_candidate_ready: true\ncanonical_part_a_files: []\ndeep_dive_chains:\n""" + "\n".join(chain_lines) + "\n"
    manifest += "question_quality_status: READY\nnovel_question_count: 80\nregression_question_count: 20\n"
    (directory / "manifest.yaml").write_text(manifest, encoding="utf-8")
    return directory


def test_v41_bootstrap_contract_passes() -> None:
    errors = _module().verify_bootstrap(ROOT / "project-reconstruction-lab/sessions/RB-WORKFLOW-V4.1-BOOTSTRAP")
    assert errors == []


def test_v41_conceptual_round_contract_passes(tmp_path: Path) -> None:
    errors, warnings = _module().verify_round(_write_round(tmp_path))
    assert errors == []
    assert isinstance(warnings, list)


def test_candidate_branch_must_not_be_main(tmp_path: Path) -> None:
    directory = _write_round(tmp_path)
    path = directory / "manifest.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("candidate_branch: codex/r006-blue", "candidate_branch: main"), encoding="utf-8")
    errors, _ = _module().verify_round(directory)
    assert any("different from main_branch" in error for error in errors)


def test_conceptual_context_rejects_business_code_path(tmp_path: Path) -> None:
    directory = _write_round(tmp_path)
    path = directory / "context-packets/blue-context.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nsource: src/backend/zuno/agent/runtime.py\n", encoding="utf-8")
    errors, _ = _module().verify_round(directory)
    assert any("business implementation path" in error for error in errors)


def test_part_a_explainability_counts_must_sum_to_100(tmp_path: Path) -> None:
    directory = _write_round(tmp_path)
    path = directory / "manifest.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("part_a_missing_count: 5", "part_a_missing_count: 6"), encoding="utf-8")
    errors, _ = _module().verify_round(directory)
    assert any("sum to 100" in error for error in errors)


def test_human_writing_is_not_machine_pass(tmp_path: Path) -> None:
    directory = _write_round(tmp_path)
    path = directory / "manifest.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("human_writing_verifier_mode: WARNING_ONLY", "human_writing_verifier_mode: PASS"), encoding="utf-8")
    errors, _ = _module().verify_round(directory)
    assert any("WARNING_ONLY" in error for error in errors)


def test_interview_calibration_rejects_answer_content(tmp_path: Path) -> None:
    directory = _write_round(tmp_path)
    path = directory / "interview-calibration-packet.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nanswer key: do this\n", encoding="utf-8")
    errors, _ = _module().verify_round(directory)
    assert any("answer or candidate-script" in error for error in errors)

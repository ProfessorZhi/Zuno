from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_red_blue_defaults_to_two_wave_batch_duel() -> None:
    system = _read(".agent/system.yaml")
    current = _read(".agent/red-blue/current.md")
    protocol = _read(".agent/red-blue/protocol.md")

    for marker in (
        'red_blue_default_execution_mode: "BATCH_DUEL"',
        "red_batch_wave_question_count: 100",
        "blue_batch_wave_answer_count: 100",
        "red_wave_1_exact_question_count_required: true",
        "blue_wave_1_exact_answer_count_required: true",
        "red_wave_2_exact_question_count_required: true",
        "blue_wave_2_exact_answer_count_required: true",
        'red_blue_batch_checkpoint_policy: "link_only_pause"',
        "red_blue_user_does_not_answer_batch_questions: true",
    ):
        assert marker in system

    for marker in (
        "execution_mode: `BATCH_DUEL`",
        "red_wave_1_question_target: `100`",
        "blue_wave_1_answer_target: `100`",
        "red_wave_2_question_target: `100`",
        "blue_wave_2_answer_target: `100`",
        "batch_checkpoint_policy: `LINK_ONLY_PAUSE`",
    ):
        assert marker in current

    for marker in (
        "RED_WAVE_1",
        "BLUE_WAVE_1",
        "RED_WAVE_2",
        "BLUE_WAVE_2",
        "BATCH_CHECKPOINT_RED_1",
        "BATCH_CHECKPOINT_BLUE_1",
        "BATCH_CHECKPOINT_RED_2",
        "BATCH_CHECKPOINT_BLUE_2",
    ):
        assert marker in protocol


def test_simulated_resume_is_real_resume_surface_and_freezes_before_red() -> None:
    system = _read(".agent/system.yaml")
    protocol = _read(".agent/red-blue/protocol.md")
    turn = _read(".agent/red-blue/templates/turn.md")

    for marker in (
        "simulated_resume_must_match_real_resume_register: true",
        "simulated_resume_one_page_style: true",
        'simulated_resume_project_bullets_target: "4-6"',
        "simulated_resume_one_bullet_one_story: true",
        "resume_must_freeze_before_red: true",
    ):
        assert marker in system

    assert "真实问题" in protocol
    assert "真实工程问题" in turn
    assert "USER_RESUME_REVIEW" in protocol


def test_red_wave2_is_blind_evaluation_plus_answer_driven_100_questions() -> None:
    system = _read(".agent/system.yaml")
    protocol = _read(".agent/red-blue/protocol.md")
    attack = _read(".agent/red-blue/attack-model.md")
    turn = _read(".agent/red-blue/templates/turn.md")

    for marker in (
        "red_wave_2_requires_blue_1_blind_evaluation: true",
        "red_wave_2_must_be_answer_driven: true",
        "red_wave_2_cannot_read_blue_architecture_notes: true",
    ):
        assert marker in system

    assert "Part A — Blue Wave 1 Blind Evaluation" in protocol
    assert "Exactly 100 Targeted Follow-ups" in protocol
    assert "Red Wave 2：评价 + 追杀" in attack
    assert "Answer-driven handles" in attack
    assert "Part A — Blue Wave 1 Blind Evaluation" in turn
    assert "Part B — 100 Targeted Follow-ups" in turn


def test_blue_candidate_answers_are_separated_from_architecture_diagnosis() -> None:
    system = _read(".agent/system.yaml")
    defense = _read(".agent/red-blue/defense-model.md")
    protocol = _read(".agent/red-blue/protocol.md")
    turn = _read(".agent/red-blue/templates/turn.md")

    for marker in (
        "blue_architecture_notes_sealed_from_red: true",
        "blue_wave_2_candidate_cannot_read_wave_1_architecture_notes: true",
        "blue_architecture_reflection_after_blue_2_required: true",
    ):
        assert marker in system

    for marker in (
        "Candidate Mode",
        "Architecture Reviewer Mode",
        "03_blue_architecture_notes.md",
        "04_blue_wave2_architecture_notes.md",
        "Final Architecture Reflection",
    ):
        assert marker in defense

    assert "03_blue_architecture_notes.md` 对后续 Red **封存**" in protocol
    assert "Sealed Wave 1 Diagnosis" in turn
    assert "Sealed Wave 2 Diagnosis" in turn


def test_red_final_remains_blind_to_canonical_truth_and_blue_notes() -> None:
    system = _read(".agent/system.yaml")
    protocol = _read(".agent/red-blue/protocol.md")
    judge = _read(".agent/red-blue/judge.md")

    assert "red_final_cannot_read_blue_architecture_notes: true" in system
    assert "不读取任何 Blue architecture notes、Zuno docs、source 或 Evidence" in protocol
    assert "Red 不读 Zuno docs" in judge
    assert "仍然不读取 canonical docs 或任何 Blue architecture notes" in judge


def test_blue_internal_mode_distinguishes_history_current_target_open_design_and_fundamentals() -> None:
    defense = _read(".agent/red-blue/defense-model.md")
    for marker in (
        "HISTORICAL_OWNERSHIP",
        "CURRENT_SYSTEM",
        "TARGET_DESIGN",
        "OPEN_DESIGN",
        "FUNDAMENTAL",
        "Unknown 与边界",
        "Build / Buy / Delete",
        "Multi-Agent 的回答框架",
    ):
        assert marker in defense


def test_workflow_retrospective_reviews_reasoning_frameworks_and_harness() -> None:
    system = _read(".agent/system.yaml")
    protocol = _read(".agent/red-blue/protocol.md")
    judge = _read(".agent/red-blue/judge.md")
    turn = _read(".agent/red-blue/templates/turn.md")

    for marker in (
        "red_blue_red_thinking_framework_retrospective_required: true",
        "red_blue_blue_candidate_framework_retrospective_required: true",
        "red_blue_blue_architecture_framework_retrospective_required: true",
        "red_blue_harness_retrospective_required: true",
    ):
        assert marker in system

    for marker in (
        "Red Thinking Framework Reflection",
        "Blue Candidate Framework Reflection",
        "Blue Architecture Framework Reflection",
        "Harness Reflection",
    ):
        assert marker in turn

    assert "Red Thinking Framework" in judge
    assert "Blue Thinking Framework" in judge
    assert "Harness" in judge
    assert "模拟系统本身" in protocol


def test_architecture_can_change_but_complexity_must_be_measurement_gated() -> None:
    system = _read(".agent/system.yaml")
    protocol = _read(".agent/red-blue/protocol.md")
    defense = _read(".agent/red-blue/defense-model.md")

    assert "red_blue_architecture_can_be_revised_after_user_gate: true" in system
    assert "Multi-Agent 不是默认升级路线" in protocol
    assert "Tool\n→ Subgraph\n→ parallel worker\n→ Specialist Agent\n→ Persistent Multi-Agent" in defense
    for marker in ("native_runtime", "graphrag_default_path", "persistent_multi_agent"):
        assert marker in system


def test_round_has_improvement_ledger_round_report_and_next_resume() -> None:
    system = _read(".agent/system.yaml")
    protocol = _read(".agent/red-blue/protocol.md")
    judge = _read(".agent/red-blue/judge.md")
    turn = _read(".agent/red-blue/templates/turn.md")

    for marker in (
        "red_blue_round_improvement_ledger_required: true",
        "red_blue_round_report_required: true",
        "red_blue_improvement_user_review_gate_supported: true",
        "red_blue_post_round_changes_next_round_only: true",
        "red_blue_next_resume_candidate_required: true",
        "red_blue_next_round_revalidates_resume: true",
    ):
        assert marker in system

    for marker in (
        "RESUME_GAP",
        "RED_SKILL_GAP",
        "BLUE_SKILL_GAP",
        "HARNESS_GAP",
        "ARCHITECTURE_GAP",
        "EVIDENCE_GAP",
        "FUNDAMENTAL_GAP",
    ):
        assert marker in protocol
        assert marker in judge

    assert "09_improvement_ledger.md" in turn
    assert "09_round_report.md" in turn
    assert "10_next_resume_candidate.md" in turn
    assert "NEXT_ROUND_ONLY" in protocol


def test_current_round_verdict_is_immutable_after_post_round_changes() -> None:
    system = _read(".agent/system.yaml")
    protocol = _read(".agent/red-blue/protocol.md")
    judge = _read(".agent/red-blue/judge.md")

    assert "red_blue_current_round_verdict_immutable_after_reflection: true" in system
    assert "不得回头重新计算本轮 PASS/FAIL" in protocol
    assert "不能回头重算当前轮 verdict" in judge


def test_live_interview_remains_optional_compatibility_mode() -> None:
    system = _read(".agent/system.yaml")
    protocol = _read(".agent/red-blue/protocol.md")
    round_template = _read(".agent/red-blue/templates/round.md")

    assert 'red_blue_optional_execution_mode: "LIVE_INTERVIEW"' in system
    assert "LIVE_INTERVIEW：可选模式，不是自动 Round 默认" in protocol
    assert "RED_TURN allowlist" in round_template
    assert "BLUE_TURN allowlist" in round_template


def test_interview_behavior_evidence_keeps_bytedance_depth_as_behavior_not_question_bank() -> None:
    evidence = _read("docs/red-blue/interview-behavior-evidence-2026-09.md")
    for marker in ("字节样本补充", "连续追 3–5 层", "共享屏幕看代码", "线上 log", "不是公司官方面试规范"):
        assert marker in evidence

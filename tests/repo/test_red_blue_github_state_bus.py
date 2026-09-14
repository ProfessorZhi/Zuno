from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_red_blue_uses_github_as_stage_state_bus() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    current = (ROOT / ".agent/red-blue/current.md").read_text(encoding="utf-8")

    for marker in (
        "red_blue_github_state_bus: true",
        'red_blue_stage_handoff: "commit_then_reread"',
        "red_blue_round_branch_required: true",
        "red_blue_draft_pr_required: true",
        "resume_must_freeze_before_red: true",
        "red_questions_must_freeze_before_blue: true",
    ):
        assert marker in system

    for marker in (
        "GitHub 是运行时状态总线",
        "USER_RESUME_REVIEW",
        "USER_RED_REVIEW",
        "IMPROVEMENT_SYNTHESIS",
        "USER_IMPROVEMENT_REVIEW",
        "BUILD_NEXT_RESUME_CANDIDATE",
    ):
        assert marker in protocol

    for marker in (
        "live_interview_status:",
        "next_actor:",
        "improvement_ledger_status:",
        "next_resume_candidate_status:",
        "commit-then-reread",
    ):
        assert marker in current


def test_batch_duel_is_default_for_automated_rounds() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    round_template = (ROOT / ".agent/red-blue/templates/round.md").read_text(encoding="utf-8")
    turn = (ROOT / ".agent/red-blue/templates/turn.md").read_text(encoding="utf-8")

    for marker in (
        'red_blue_execution_modes: ["BATCH_DUEL", "LIVE_INTERVIEW"]',
        'red_blue_automated_default_execution_mode: "BATCH_DUEL"',
        "red_blue_batch_duel_supported: true",
        "red_blue_batch_wave_count_default: 2",
        'red_blue_batch_wave1_question_target: "20-40"',
        'red_blue_batch_wave2_question_target: "10-30"',
        "red_blue_batch_wave2_requires_blue_wave1: true",
        "red_blue_batch_wave_commit_barrier: true",
        "red_blue_live_interview_optional: true",
    ):
        assert marker in system

    for marker in (
        "BATCH_DUEL — 自动 Round 默认",
        "RED_WAVE_1",
        "BLUE_WAVE_1",
        "RED_WAVE_2",
        "BLUE_WAVE_2",
        "Wave 2 Red **必须在 Blue Wave 1 commit 以后生成**",
        "Pressure Suite 仍是离线覆盖库",
    ):
        assert marker in protocol

    assert "execution_mode: BATCH_DUEL | LIVE_INTERVIEW" in round_template
    assert "Red Wave 2 必须明确从 Blue Wave 1 的 observable gaps 产生" in round_template
    assert "BATCH_DUEL — Batch Answer Ledger" in turn
    assert "PRESSURE_SUITE" in turn


def test_live_interview_remains_optional_and_committed() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    round_template = (ROOT / ".agent/red-blue/templates/round.md").read_text(encoding="utf-8")
    turn = (ROOT / ".agent/red-blue/templates/turn.md").read_text(encoding="utf-8")

    for marker in (
        "red_blue_live_interview_optional: true",
        "red_blue_live_alternating_turns: true",
        "red_turn_must_commit_before_blue_turn: true",
        "blue_turn_must_commit_before_next_red_turn: true",
    ):
        assert marker in system

    for marker in ("LIVE_INTERVIEW", "RED_TURN", "BLUE_TURN", "DYNAMIC_FOLLOWUP"):
        assert marker in protocol

    for marker in (
        "Red question commit 必须先于对应 Blue answer commit",
        "Blue answer commit 必须先于下一 Red follow-up commit",
        "next_actor: RED | BLUE | NONE",
    ):
        assert marker in round_template

    assert "LIVE_INTERVIEW — Exchange Ledger" in turn
    assert "Red question committed" in turn
    assert "Blue answer committed" in turn


def test_simulated_resume_is_a_real_resume_surface() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    turn = (ROOT / ".agent/red-blue/templates/turn.md").read_text(encoding="utf-8")

    for marker in (
        "simulated_resume_must_match_real_resume_register: true",
        "simulated_resume_one_page_style: true",
        'simulated_resume_project_bullets_target: "4-6"',
        "simulated_resume_one_bullet_one_story: true",
    ):
        assert marker in system

    assert "真实问题" in protocol
    assert "真实工程问题" in turn
    assert "USER_RESUME_REVIEW" in protocol


def test_blue_candidate_skill_is_pinned_and_reviewed() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    defense = (ROOT / ".agent/red-blue/defense-model.md").read_text(encoding="utf-8")
    judge = (ROOT / ".agent/red-blue/judge.md").read_text(encoding="utf-8")
    round_template = (ROOT / ".agent/red-blue/templates/round.md").read_text(encoding="utf-8")

    for marker in (
        "blue_candidate_skill_required: true",
        'blue_candidate_skill_path: ".agent/red-blue/defense-model.md"',
        "red_blue_skill_versions_pinned_per_round: true",
        "red_blue_blue_skill_retrospective_required: true",
    ):
        assert marker in system

    for marker in (
        "Ownership",
        "技术回答优先讲工程矛盾",
        "Evidence",
        "Unknown 与边界",
        "Failure / Recovery",
        "面试口语",
    ):
        assert marker in defense

    assert "Blue Skill" in judge
    assert "defense_skill_version" in round_template


def test_round_has_improvement_ledger_and_next_resume_handoff() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    judge = (ROOT / ".agent/red-blue/judge.md").read_text(encoding="utf-8")
    turn = (ROOT / ".agent/red-blue/templates/turn.md").read_text(encoding="utf-8")

    for marker in (
        "red_blue_round_improvement_ledger_required: true",
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
    assert "10_next_resume_candidate.md" in turn
    assert "NEXT_ROUND_ONLY" in protocol


def test_current_round_verdict_is_not_rewritten_after_skill_changes() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    judge = (ROOT / ".agent/red-blue/judge.md").read_text(encoding="utf-8")

    assert "red_blue_current_round_verdict_immutable_after_reflection: true" in system
    assert "current_round_verdict_recomputed: false" in protocol
    assert "不能回头重算当前轮 verdict" in judge


def test_live_red_is_answer_driven_not_static_primary_path() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    attack = (ROOT / ".agent/red-blue/attack-model.md").read_text(encoding="utf-8")

    for marker in (
        "red_pressure_suite_count_default: 100",
        "red_live_seed_question_target_default: 8",
        "red_live_followups_dynamic: true",
        "red_live_one_question_one_intent: true",
        "red_live_static_primary_path_forbidden: true",
    ):
        assert marker in system

    for marker in (
        "有状态对话",
        "一问一个主要意图",
        "Pressure Suite",
        "CLAIM_IMPLEMENTATION_NOT_ESTABLISHED",
        "“人话”不等于浅",
        "3–5 层",
        "字节式工程深挖",
    ):
        assert marker in attack

    assert "PRIMARY_PATH: 30" not in attack


def test_interview_behavior_evidence_keeps_bytedance_depth_as_behavior_not_question_bank() -> None:
    evidence = (ROOT / "docs/red-blue/interview-behavior-evidence-2026-09.md").read_text(encoding="utf-8")
    for marker in ("字节样本补充", "连续追 3–5 层", "共享屏幕看代码", "线上 log", "不是公司官方面试规范"):
        assert marker in evidence

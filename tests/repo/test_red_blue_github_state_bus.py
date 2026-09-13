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
        "resume_user_review_gate_supported: true",
        "resume_must_freeze_before_red: true",
        "red_user_review_gate_supported: true",
        "red_questions_must_freeze_before_blue: true",
    ):
        assert marker in system

    for marker in (
        "GitHub 是运行时状态总线",
        "USER_RESUME_REVIEW",
        "RESUME_REVISION",
        "USER_RED_REVIEW",
        "RED_REVISION",
        "DYNAMIC_FOLLOWUP",
        "PRESSURE_SUITE",
        "LOGICAL_GITHUB_MEDIATED",
        "PHYSICAL_CONTEXT_ISOLATION",
    ):
        assert marker in protocol

    for marker in (
        "round_branch:",
        "round_pr:",
        "last_consumed_head_sha:",
        "red_review_gate:",
        "red_questions_status:",
    ):
        assert marker in current


def test_simulated_resume_is_a_real_resume_surface() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    turn = (ROOT / ".agent/red-blue/templates/turn.md").read_text(encoding="utf-8")
    round_template = (ROOT / ".agent/red-blue/templates/round.md").read_text(encoding="utf-8")

    for marker in (
        "simulated_resume_must_match_real_resume_register: true",
        "simulated_resume_one_page_style: true",
        'simulated_resume_project_bullets_target: "4-5"',
        "simulated_resume_one_bullet_one_story: true",
        "resume_user_review_gate_default_for_calibration: true",
    ):
        assert marker in system

    for marker in (
        "写简历，不写证据报告",
        "4–5 条核心 bullet",
        "45–90 个字符",
        "USER_RESUME_REVIEW",
    ):
        assert marker in protocol

    for marker in (
        "候选人真的会投出去的一页简历项目块",
        "4–5 条核心 bullet",
        "45–90 字符",
        "USER_RESUME_REVIEW",
    ):
        assert marker in turn

    assert "resume_review_gate: REQUIRED | OPTIONAL | SKIP" in round_template
    assert "resume_status: DRAFT | REVISION_REQUESTED | FROZEN" in round_template
    assert "INVALIDATED_BY_RESUME_CHANGE" in round_template


def test_red_questions_require_user_review_before_blue_when_configured() -> None:
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    template = (ROOT / ".agent/red-blue/templates/round.md").read_text(encoding="utf-8")

    assert "## USER_RED_REVIEW" in protocol
    assert "red_questions_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | FROZEN | INVALIDATED_BY_RESUME_CHANGE" in template
    assert "resume_status: FROZEN` 且 `red_questions_status: FROZEN" in template


def test_live_red_is_answer_driven_not_static_primary_path() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    attack = (ROOT / ".agent/red-blue/attack-model.md").read_text(encoding="utf-8")
    turn = (ROOT / ".agent/red-blue/templates/turn.md").read_text(encoding="utf-8")

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

    for marker in ("SPOKEN_SEEDS", "FOLLOWUP_POLICY", "BRANCH_EXAMPLES", "PRESSURE_SUITE"):
        assert marker in turn

    assert "PRIMARY_PATH: 30" not in attack


def test_interview_behavior_evidence_keeps_bytedance_depth_as_behavior_not_question_bank() -> None:
    evidence = (ROOT / "docs/red-blue/interview-behavior-evidence-2026-09.md").read_text(encoding="utf-8")
    for marker in ("字节样本补充", "连续追 3–5 层", "共享屏幕看代码", "线上 log", "不是公司官方面试规范"):
        assert marker in evidence

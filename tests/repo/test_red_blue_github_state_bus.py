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
        "chatgpt_auto_strict_blind_red_certification: false",
        "agent_auto_strict_blind_red_certification: true",
        "red_user_review_gate_supported: true",
        "red_questions_must_freeze_before_blue: true",
        "round_init_must_capture_known_user_feedback: true",
    ):
        assert marker in system

    for marker in (
        "GitHub 是运行时状态总线",
        "Round branch / PR",
        "Draft PR",
        "commit barrier",
        "USER_RED_REVIEW",
        "RED_REVISION",
        "LIVE_INTERVIEW_SEEDS",
        "DYNAMIC_FOLLOWUP",
        "PRESSURE_SUITE",
        "KILL_SWITCH",
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
        "commit-then-reread",
        "LOGICAL_GITHUB_MEDIATED",
        "PHYSICAL_CONTEXT_ISOLATION",
    ):
        assert marker in current

    assert "stage_head_sha:" not in current


def test_chatgpt_auto_does_not_claim_strict_context_isolation() -> None:
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    assert "strict_blind_red_certification: false" in protocol
    assert "strict_blind_red_certification: true" in protocol
    assert "如果某轮要把 **blind Red** 当作正式验收结论，必须用 `AGENT_AUTO` 重跑" in protocol


def test_red_questions_require_user_review_before_blue_when_configured() -> None:
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    template = (ROOT / ".agent/red-blue/templates/round.md").read_text(encoding="utf-8")

    assert "APPROVE → FREEZE_RED_QUESTIONS → BLUE_ANSWERS" in protocol
    assert "只有 `APPROVE` 后" in protocol
    assert "red_questions_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | FROZEN" in template
    assert "只有 `red_questions_status: FROZEN` 才允许 Blue" in template


def test_live_red_is_answer_driven_not_static_primary_path() -> None:
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    attack = (ROOT / ".agent/red-blue/attack-model.md").read_text(encoding="utf-8")
    stage_template = (ROOT / ".agent/red-blue/templates/turn.md").read_text(encoding="utf-8")

    for marker in (
        "red_pressure_suite_count_default: 100",
        "red_live_seed_question_target_default: 8",
        "red_live_followups_dynamic: true",
        "red_live_one_question_one_intent: true",
        "red_pressure_suite_separate_from_live_interview: true",
        "red_live_static_primary_path_forbidden: true",
    ):
        assert marker in system

    for marker in (
        "有状态对话",
        "6-10 个 Seed Questions",
        "Follow-up Policy",
        "一问一个主要意图",
        "上一答",
        "Pressure Suite",
        "CLAIM_IMPLEMENTATION_NOT_ESTABLISHED",
        "避免 AI 面试官味",
    ):
        assert marker in attack

    for marker in (
        "SPOKEN_SEEDS",
        "FOLLOWUP_POLICY",
        "BRANCH_EXAMPLES",
        "PRESSURE_SUITE",
        "live_followups: DYNAMIC",
        "one_question_one_intent: true",
    ):
        assert marker in stage_template

    assert "PRIMARY_PATH: 30" not in attack
    assert "primary_path_count: 30" not in stage_template

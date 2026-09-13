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
    ):
        assert marker in system

    for marker in (
        "GitHub 是运行时状态总线",
        "Round branch / PR",
        "Draft PR",
        "commit barrier",
        "LOGICAL_GITHUB_MEDIATED",
        "PHYSICAL_CONTEXT_ISOLATION",
    ):
        assert marker in protocol

    for marker in (
        "round_branch:",
        "round_pr:",
        "stage_head_sha:",
        "github_state_bus:",
        "commit-then-reread",
        "LOGICAL_GITHUB_MEDIATED",
        "PHYSICAL_CONTEXT_ISOLATION",
    ):
        assert marker in current


def test_chatgpt_auto_does_not_claim_strict_context_isolation() -> None:
    protocol = (ROOT / ".agent/red-blue/protocol.md").read_text(encoding="utf-8")
    assert "strict_blind_red_certification: false" in protocol
    assert "strict_blind_red_certification: true" in protocol
    assert "如果某轮要把 **blind Red** 当作正式验收结论，必须用 `AGENT_AUTO` 重跑" in protocol

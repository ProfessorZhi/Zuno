from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_round_init_requires_stable_artifact_links_and_placeholders() -> None:
    runtime_readme = _read(".agent/red-blue/README.md")
    workspace_readme = _read("docs/red-blue/workspace/README.md")
    contract = _read(".agent/red-blue/artifact-links.md")
    template = _read(".agent/red-blue/templates/artifact-links.md")

    for text in (runtime_readme, workspace_readme, contract):
        assert "00_artifact_links.md" in text
        assert "NOT_STARTED" in text
        assert "原地更新" in text

    for marker in (
        "01_simulated_resume.md",
        "02_red_questions.md",
        "03_blue_answers.md",
        "03_blue_architecture_notes.md",
        "04_red_wave2_review_and_questions.md",
        "04_blue_wave2_answers.md",
        "04_blue_wave2_architecture_notes.md",
        "04_red_evaluation.md",
        "05_blue_architecture_reflection.md",
        "06_workflow_retrospective.md",
        "09_improvement_ledger.md",
        "09_round_report.md",
        "10_next_resume_candidate.md",
    ):
        assert marker in contract
        assert marker in template


def test_every_checkpoint_requires_direct_clickable_links() -> None:
    runtime_readme = _read(".agent/red-blue/README.md")
    workspace_readme = _read("docs/red-blue/workspace/README.md")
    contract = _read(".agent/red-blue/artifact-links.md")

    assert "直接可点击链接" in runtime_readme
    assert "当前 stage artifact 直链" in workspace_readme
    assert "当前 stage artifact 的直接 GitHub 链接" in contract

    for forbidden_fallback in ("文件名", "相对路径", "commit SHA", "已完成"):
        assert forbidden_fallback in contract


def test_stable_links_do_not_weaken_red_blue_firewall() -> None:
    contract = _read(".agent/red-blue/artifact-links.md")
    workspace_readme = _read("docs/red-blue/workspace/README.md")

    assert "稳定链接不能成为越权输入" in contract
    assert "Red Wave 2 / Red Final" in contract
    assert "Blue Wave 2 Candidate" in contract
    assert "这不改变 Red allowlist" in workspace_readme

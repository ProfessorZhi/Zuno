from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


def _files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []
    expected_history_front = {
        "docs/history/README.md",
        "docs/history/architecture-evolution.md",
        "docs/history/program-history.md",
        "docs/history/project-background-history.md",
        "docs/history/requirements-and-workflows-history.md",
        "docs/history/team-and-ownership-history.md",
        "docs/history/development-history.md",
        "docs/history/incidents-and-improvements.md",
        "docs/history/delivery-and-usage.md",
        "docs/history/technology-history.md",
        "docs/history/production-readiness-baseline.md",
    }
    expected_evidence = {
        "docs/evidence/README.md",
        "docs/evidence/repository-closure.md",
        "docs/evidence/local-workspace-closure.md",
        "docs/evidence/current-runtime-baseline.md",
        "docs/evidence/current-test-baseline.md",
        "docs/evidence/current-eval-baseline.md",
    }
    history_front = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "docs/history").iterdir()
        if path.is_file()
    }
    if history_front != expected_history_front:
        errors.append("docs/history front does not match the approved historical summaries")
    if _files(ROOT / "docs/evidence") != expected_evidence:
        errors.append("docs/evidence must contain only current evidence entries")

    expected_facts = {
        "docs/facts/README.md",
        "docs/facts/project-context.md",
        "docs/facts/current-state.md",
        "docs/facts/assets/zuno-banner.svg",
    }
    if _files(ROOT / "docs/facts") != expected_facts:
        errors.append("docs/facts must contain only current fact entrypoints and local assets")
    if _files(ROOT / "docs/modules") != {"docs/modules/README.md"}:
        errors.append("docs/modules must contain only its boundary README")
    expected_history_interview = {
        "docs/history/interview-qa/README.md",
        "docs/history/interview-qa/architecture-coverage-matrix.md",
        "docs/history/interview-qa/architecture-gap-report.md",
        "docs/history/interview-qa/deep-dive-chains.md",
        "docs/history/interview-qa/question-taxonomy.md",
        "docs/history/interview-qa/source-audit.md",
        "docs/history/interview-qa/zuno-agent-core-qa.md",
        "docs/history/interview-qa/zuno-agentic-graphrag-qa.md",
        "docs/history/interview-qa/zuno-cross-module-system-design-qa.md",
        "docs/history/interview-qa/zuno-memory-context-qa.md",
        "docs/history/interview-qa/zuno-memory-information-extraction-qa.md",
        "docs/history/interview-qa/zuno-tool-mcp-security-qa.md",
    }
    if _files(ROOT / "docs/history/interview-qa") != expected_history_interview:
        errors.append("docs/history/interview-qa must contain the approved historical interview files")
    for directory in ("product", "domain", "agents", "knowledge", "services", "data", "security", "eval", "deployment"):
        if (ROOT / "docs" / directory).exists():
            errors.append(f"old docs/{directory} topic path must be absent")

    program_root = ROOT / ".agent" / "programs"
    if {path.name for path in program_root.glob("*.md")} != {"README.md", "current.md"}:
        errors.append(".agent/programs front must contain README.md and current.md")
    current = (program_root / "current.md").read_text(encoding="utf-8")
    has_no_active_state = all(phrase in current for phrase in ("state: `no-active`", "active_program: `none`"))
    has_design_state = "state: `active-design-program`" in current and re.search(
        r"active_program: `(?!none`)[^`]+`", current
    ) is not None
    has_implementation_evidence_state = "state: `active-implementation-evidence-program`" in current and re.search(
        r"active_program: `(?!none`)[^`]+`", current
    ) is not None
    if not (has_no_active_state or has_design_state or has_implementation_evidence_state):
        errors.append("current program has no recognized design/implementation state")
    if "SUPERSEDED / RETIRED" not in current:
        errors.append("current program missing SUPERSEDED / RETIRED")

    architecture = ROOT / "docs" / "architecture"
    if {path.name for path in architecture.iterdir() if path.is_file()} != {
        "README.md", "architecture.md", "architecture-views.md", "architecture.html"
    }:
        errors.append("docs/architecture must contain its four canonical files")

    if (ROOT / "src/backend/zuno/api/services/workspace_task_runtime.py").exists():
        errors.append("retired workspace runtime module still exists")
    if (ROOT / "src/backend/zuno/agent/runtime/phase08_cutover.py").exists():
        errors.append("retired cutover module still exists")
    for directory in (ROOT / "tools/scripts", ROOT / "tests"):
        for path in directory.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and re.search(r"(?:phase|legacy|cutover)", path.name, re.IGNORECASE):
                errors.append(f"retired phase/legacy/cutover file: {path.relative_to(ROOT)}")

    if errors:
        print("REPO_STRUCTURE_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("REPO_STRUCTURE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

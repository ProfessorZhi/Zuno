from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _relative_files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []
    history = ROOT / "docs" / "history"
    evidence = ROOT / "docs" / "evidence"
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
    actual_history_front = {
        path.relative_to(ROOT).as_posix()
        for path in history.iterdir()
        if path.is_file()
    }
    actual_evidence = _relative_files(evidence)
    if actual_history_front != expected_history_front:
        errors.append(f"history boundary mismatch: {sorted(actual_history_front)}")
    if actual_evidence != expected_evidence:
        errors.append(f"evidence boundary mismatch: {sorted(actual_evidence)}")

    expected_facts = {
        "docs/facts/README.md",
        "docs/facts/project-context.md",
        "docs/facts/current-state.md",
        "docs/facts/assets/zuno-banner.svg",
    }
    expected_modules = {"docs/modules/README.md"}
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
    if _relative_files(ROOT / "docs/facts") != expected_facts:
        errors.append("facts boundary mismatch")
    if _relative_files(ROOT / "docs/modules") != expected_modules:
        errors.append("modules boundary mismatch")
    if _relative_files(ROOT / "docs/history/interview-qa") != expected_history_interview:
        errors.append("historical interview material boundary mismatch")

    architecture = ROOT / "docs" / "architecture"
    expected_architecture = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}
    actual_architecture = {path.name for path in architecture.iterdir() if path.is_file()}
    if actual_architecture != expected_architecture:
        errors.append(f"architecture boundary mismatch: {sorted(actual_architecture)}")

    if errors:
        print("DOC_BOUNDARIES_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DOC_BOUNDARIES_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

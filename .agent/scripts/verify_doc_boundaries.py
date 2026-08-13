from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _relative_files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []
    history = ROOT / "docs" / "history"
    evidence = ROOT / "docs" / "evidence"
    expected_history = {
        "docs/history/README.md",
        "docs/history/architecture-evolution.md",
        "docs/history/program-history.md",
    }
    expected_evidence = {
        "docs/evidence/README.md",
        "docs/evidence/repository-closure.md",
        "docs/evidence/local-workspace-closure.md",
        "docs/evidence/current-runtime-baseline.md",
        "docs/evidence/current-test-baseline.md",
        "docs/evidence/current-eval-baseline.md",
    }
    actual_history = {
        path.relative_to(ROOT).as_posix()
        for path in history.iterdir()
        if path.is_file()
    }
    actual_evidence = _relative_files(evidence)
    if actual_history != expected_history:
        errors.append(f"history boundary mismatch: {sorted(actual_history)}")
    if actual_evidence != expected_evidence:
        errors.append(f"evidence boundary mismatch: {sorted(actual_evidence)}")

    expected_project_history = {
        "docs/project/history/README.md",
        "docs/project/history/project-background.md",
        "docs/project/history/requirements-and-workflows.md",
        "docs/project/history/team-and-ownership.md",
        "docs/project/history/development-history.md",
        "docs/project/history/incidents-and-improvements.md",
        "docs/project/history/delivery-and-usage.md",
        "docs/project/history/technology-history.md",
    }
    expected_project_status = {
        "docs/project/status/README.md",
        "docs/project/status/current-reality.md",
        "docs/project/status/target-status.md",
        "docs/project/status/production-readiness.md",
    }
    if _relative_files(ROOT / "docs/project/history") != expected_project_history:
        errors.append("project history boundary mismatch")
    if _relative_files(ROOT / "docs/project/status") != expected_project_status:
        errors.append("project status boundary mismatch")
    if (ROOT / "docs/project/facts").exists() or (ROOT / "docs/project/modules").exists():
        errors.append("old project facts/modules directories must not remain active")

    architecture = ROOT / "docs" / "project" / "architecture"
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

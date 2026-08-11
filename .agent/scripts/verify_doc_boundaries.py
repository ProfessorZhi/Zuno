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
    actual_history = _relative_files(history)
    actual_evidence = _relative_files(evidence)
    if actual_history != expected_history:
        errors.append(f"history boundary mismatch: {sorted(actual_history)}")
    if actual_evidence != expected_evidence:
        errors.append(f"evidence boundary mismatch: {sorted(actual_evidence)}")

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

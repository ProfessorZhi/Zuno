from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _relative_files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []
    expected_history_front = {"docs/history/README.md"}
    expected_evidence = {
        "docs/evidence/README.md",
        "docs/evidence/current-runtime-baseline.md",
        "docs/evidence/current-test-baseline.md",
        "docs/evidence/current-eval-baseline.md",
        "docs/evidence/implementation-wave-001.md",
    }
    actual_history_front = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "docs/history").iterdir()
        if path.is_file()
    }
    actual_evidence = _relative_files(ROOT / "docs/evidence")
    if actual_history_front != expected_history_front:
        errors.append(f"history boundary mismatch: {sorted(actual_history_front)}")
    if actual_evidence != expected_evidence:
        errors.append(f"evidence boundary mismatch: {sorted(actual_evidence)}")

    expected_facts = {
        "docs/facts/README.md",
        "docs/facts/project-background.md",
        "docs/facts/requirements-and-workflows.md",
        "docs/facts/development-and-evolution.md",
        "docs/facts/team-and-ownership.md",
        "docs/facts/delivery-and-feedback.md",
        "docs/facts/technology-reality.md",
    }
    expected_modules = {"docs/modules/README.md"}
    if _relative_files(ROOT / "docs/facts") != expected_facts:
        errors.append("facts boundary mismatch")
    if _relative_files(ROOT / "docs/modules") != expected_modules:
        errors.append("modules boundary mismatch")

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

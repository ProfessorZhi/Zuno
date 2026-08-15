from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _relative_files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []
    if _relative_files(ROOT / "docs/project") != {
        "docs/project/project-background.md", "docs/project/development-process.md"
    }:
        errors.append("project boundary mismatch")
    if _relative_files(ROOT / "docs/history") != {
        "docs/history/README.md", "docs/history/red-blue/README.md",
        "docs/history/red-blue/manual-round-01-overall-architecture.md",
        "docs/history/red-blue/manual-round-02-overall-architecture-freeze-review.md",
        "docs/history/red-blue/legacy-automated-rounds.md",
    }:
        errors.append("history boundary mismatch")
    if _relative_files(ROOT / "docs/modules") != {"docs/modules/README.md"}:
        errors.append("modules boundary mismatch")
    if {path.name for path in (ROOT / "docs/architecture").iterdir() if path.is_file()} != {
        "README.md", "architecture.md", "architecture-views.md", "architecture.html"
    }:
        errors.append("architecture boundary mismatch")
    if _relative_files(ROOT / "docs/governance") != {
        "docs/governance/wave1-cross-module-contract-registry.md",
        "docs/governance/repo-ownership-matrix.md",
    }:
        errors.append("governance compatibility boundary mismatch")
    for obsolete in (ROOT / "docs/facts", ROOT / "project-reconstruction-lab"):
        if obsolete.exists():
            errors.append(f"obsolete boundary still exists: {obsolete.relative_to(ROOT)}")
    if errors:
        print("DOC_BOUNDARIES_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("DOC_BOUNDARIES_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

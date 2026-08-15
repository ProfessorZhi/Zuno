from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []
    if _files(ROOT / "docs/project") != {
        "docs/project/README.md", "docs/project/project-background.md",
        "docs/project/team-and-contributions.md", "docs/project/development-process.md",
    }:
        errors.append("docs/project must contain exactly its four canonical project documents")
    if _files(ROOT / "docs/evidence") != {
        "docs/evidence/README.md", "docs/evidence/current-runtime-baseline.md",
        "docs/evidence/current-test-baseline.md", "docs/evidence/current-eval-baseline.md",
        "docs/evidence/implementation-wave-001.md",
    }:
        errors.append("docs/evidence must contain only current evidence entries")
    if _files(ROOT / "docs/operations") != {
        "docs/operations/postgresql-migration-runbook.md",
        "docs/operations/infrastructure-dr-profile.yaml",
    }:
        errors.append("docs/operations must contain only current operational entries")
    if _files(ROOT / "docs/governance") != {
        "docs/governance/wave1-cross-module-contract-registry.md",
        "docs/governance/repo-ownership-matrix.md",
        "docs/governance/project-fact-provenance.md",
    }:
        errors.append("docs/governance may contain only source-compatible current boundary inputs")
    if _files(ROOT / "docs/modules") != {"docs/modules/README.md"}:
        errors.append("docs/modules must contain only its boundary README")
    if _files(ROOT / "docs/history") != {
        "docs/history/README.md", "docs/history/red-blue/README.md",
        "docs/history/red-blue/manual-round-01-overall-architecture.md",
        "docs/history/red-blue/manual-round-02-overall-architecture-freeze-review.md",
        "docs/history/red-blue/legacy-automated-rounds.md",
    }:
        errors.append("docs/history must contain only high-value Red/Blue review records")
    for obsolete in (ROOT / "docs/facts", ROOT / "project-reconstruction-lab"):
        if obsolete.exists():
            errors.append(f"obsolete documentation workspace must be absent: {obsolete.relative_to(ROOT)}")
    for directory in ("product", "domain", "agents", "knowledge", "services", "data", "security", "eval", "deployment"):
        if (ROOT / "docs" / directory).exists():
            errors.append(f"old docs/{directory} topic path must be absent")
    program_root = ROOT / ".agent" / "programs"
    if {path.name for path in program_root.glob("*.md")} != {"README.md", "current.md"}:
        errors.append(".agent/programs front must contain README.md and current.md")
    current = (program_root / "current.md").read_text(encoding="utf-8")
    if "state: `no-active`" not in current or "active_program: `none`" not in current:
        errors.append("current program has no recognized inactive state")
    if "SUPERSEDED / RETIRED" not in current:
        errors.append("current program missing SUPERSEDED / RETIRED")
    if {path.name for path in (ROOT / "docs/architecture").iterdir() if path.is_file()} != {
        "README.md", "architecture.md", "architecture-views.md", "architecture.html"
    }:
        errors.append("docs/architecture must contain its four canonical files")
    if errors:
        print("REPO_STRUCTURE_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("REPO_STRUCTURE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

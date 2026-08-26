from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT_FILES = {
    "docs/project/README.md",
    "docs/project/project.md",
}
MODULE_FILES = {
    "docs/modules/README.md",
    "docs/modules/01-application-integration.md",
    "docs/modules/02-legal-domain-work-product.md",
    "docs/modules/03-knowledge-evidence.md",
    "docs/modules/04-agent-runtime-control.md",
    "docs/modules/05-capability-skill.md",
    "docs/modules/06-tool-runtime-effects.md",
    "docs/modules/07-model-gateway.md",
    "docs/modules/08-security-governance.md",
    "docs/modules/09-observability-evaluation.md",
}


def _relative_files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []
    if _relative_files(ROOT / "docs/project") != PROJECT_FILES:
        errors.append("project boundary mismatch: expected README.md + project.md")
    if _relative_files(ROOT / "docs/history") != {
        "docs/history/README.md", "docs/history/red-blue/README.md",
        "docs/history/red-blue/manual-round-01-overall-architecture.md",
        "docs/history/red-blue/manual-round-02-overall-architecture-freeze-review.md",
        "docs/history/red-blue/legacy-automated-rounds.md",
    }:
        errors.append("history boundary mismatch")
    if _relative_files(ROOT / "docs/modules") != MODULE_FILES:
        errors.append("modules boundary mismatch")
    if {path.name for path in (ROOT / "docs/architecture").iterdir() if path.is_file()} != {
        "README.md", "architecture.md", "architecture-views.md", "architecture.html"
    }:
        errors.append("architecture boundary mismatch")
    if _relative_files(ROOT / "docs/governance") != {
        "docs/governance/human-first-documentation-standard.md",
        "docs/governance/architecture-narrative-quality-standard.md",
        "docs/governance/wave1-cross-module-contract-registry.md",
        "docs/governance/repo-ownership-matrix.md",
        "docs/governance/project-fact-provenance.md",
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

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT_FILES = {
    "docs/project/README.md",
    "docs/project/reference.md",
}
RESEARCH_FILES = {
    "docs/research/README.md",
    "docs/research/deep-research-report-2026-08-27.md",
    "docs/research/jidong-ge-liplab-lineage.md",
    "docs/research/research-to-engineering-traceability.md",
    "docs/research/agent-platform-baseline.md",
    "docs/research/documentation-narrative-blueprint.md",
    "docs/research/legal-ai-domain-problem-evidence.md",
    "docs/research/legal-agent-value-strategy-2026-09.md",
}
MODULE_NAMES = (
    "application",
    "domain",
    "knowledge",
    "runtime",
    "capability",
    "effects",
    "model-gateway",
    "security",
    "evaluation",
)
MODULE_FILES = {
    "docs/modules/README.md",
    "docs/modules/reference.md",
    *{
        f"docs/modules/{name}/{filename}"
        for name in MODULE_NAMES
        for filename in ("README.md", "reference.md")
    },
}
ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
    "reference.md",
}
GOVERNANCE_REQUIRED = {
    "docs/governance/README.md",
    "docs/governance/documentation-architecture.md",
    "docs/governance/human-first-documentation-standard.md",
    "docs/governance/architecture-narrative-quality-standard.md",
    "docs/governance/wave1-cross-module-contract-registry.md",
    "docs/governance/repo-ownership-matrix.md",
    "docs/governance/project-fact-provenance.md",
    "docs/governance/terminology.md",
    "docs/governance/workflows/agent-workflow.md",
    "docs/governance/operations/postgresql-migration-runbook.md",
    "docs/governance/operations/infrastructure-dr-profile.yaml",
}
RED_BLUE_REQUIRED = {
    "docs/red-blue/README.md",
    "docs/red-blue/archive/legacy/README.md",
    "docs/red-blue/archive/legacy/manual-round-01-overall-architecture.md",
    "docs/red-blue/archive/legacy/manual-round-02-overall-architecture-freeze-review.md",
    "docs/red-blue/archive/legacy/legacy-automated-rounds.md",
}
TOP_LEVEL_DIRS = {
    "project",
    "architecture",
    "modules",
    "red-blue",
    "research",
    "decisions",
    "evidence",
    "governance",
}


def _relative_files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []

    docs_root = ROOT / "docs"
    actual_top = {path.name for path in docs_root.iterdir() if path.is_dir()}
    if actual_top != TOP_LEVEL_DIRS:
        errors.append(f"docs top-level boundary mismatch: expected {sorted(TOP_LEVEL_DIRS)}, got {sorted(actual_top)}")

    if _relative_files(ROOT / "docs/project") != PROJECT_FILES:
        errors.append("project boundary mismatch: expected human narrative plus machine reference")
    if _relative_files(ROOT / "docs/research") != RESEARCH_FILES:
        errors.append("research boundary mismatch")
    if _relative_files(ROOT / "docs/modules") != MODULE_FILES:
        errors.append("modules boundary mismatch: expected root human/router plus README/reference pair for each current Target responsibility")
    if {path.name for path in (ROOT / "docs/architecture").iterdir() if path.is_file()} != ARCHITECTURE_FILES:
        errors.append("architecture boundary mismatch: expected README entry, architecture.md human narrative, visual/rendered entries, and machine reference")

    governance_files = _relative_files(ROOT / "docs/governance")
    missing_governance = GOVERNANCE_REQUIRED - governance_files
    if missing_governance:
        errors.append(f"governance boundary missing required files: {sorted(missing_governance)}")

    red_blue_files = _relative_files(ROOT / "docs/red-blue")
    missing_red_blue = RED_BLUE_REQUIRED - red_blue_files
    if missing_red_blue:
        errors.append(f"red-blue boundary missing required files: {sorted(missing_red_blue)}")

    documentation_architecture = ROOT / "docs/governance/documentation-architecture.md"
    if not documentation_architecture.exists():
        errors.append("missing canonical documentation architecture")
    else:
        text = documentation_architecture.read_text(encoding="utf-8")
        for marker in (
            "Physical layout",
            "Truth ownership",
            "Human / Machine projection",
            "Default reading paths",
            "Research boundary",
            "Red / Blue boundary",
            "Architecture reasoning contract",
            "architecture/README.md",
            "architecture/architecture.md",
            "architecture/reference.md",
        ):
            if marker not in text:
                errors.append(f"documentation architecture missing marker: {marker}")

    for name in MODULE_NAMES:
        readme = ROOT / "docs/modules" / name / "README.md"
        reference = ROOT / "docs/modules" / name / "reference.md"
        if not readme.exists() or not reference.exists():
            errors.append(f"module boundary {name} must expose both README.md and reference.md")

    for obsolete in (
        ROOT / "docs/maintenance",
        ROOT / "docs/terminology.md",
        ROOT / "docs/facts",
        ROOT / "docs/history",
        ROOT / "docs/operations",
        ROOT / "project-reconstruction-lab",
    ):
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

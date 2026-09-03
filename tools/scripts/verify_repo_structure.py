from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
# Physical compatibility paths still include research/ and maintenance/.  The
# canonical documentation ownership model is the six-domain model documented in
# docs/governance/documentation-architecture.md.
DOC_DIRS = {
    "project", "research", "architecture", "modules",
    "decisions", "evidence", "governance", "maintenance",
}
PROJECT_FILES = {
    "docs/project/README.md",
    "docs/project/project.md",
    "docs/project/reference.md",
}
RESEARCH_FILES = {
    "docs/research/README.md",
    "docs/research/deep-research-report-2026-08-27.md",
    "docs/research/jidong-ge-liplab-lineage.md",
    "docs/research/research-to-engineering-traceability.md",
    "docs/research/agent-platform-baseline.md",
    "docs/research/documentation-narrative-blueprint.md",
}
MODULE_FILES = {
    "docs/modules/README.md",
    "docs/modules/reference.md",
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
GOVERNANCE_FILES = {
    "docs/governance/README.md",
    "docs/governance/documentation-architecture.md",
    "docs/governance/human-first-documentation-standard.md",
    "docs/governance/architecture-narrative-quality-standard.md",
    "docs/governance/wave1-cross-module-contract-registry.md",
    "docs/governance/repo-ownership-matrix.md",
    "docs/governance/project-fact-provenance.md",
}
ARCHITECTURE_FILES = {
    "README.md", "architecture.md", "architecture-views.md", "architecture.html", "reference.md"
}
MAINTENANCE_FILES = {
    "docs/maintenance/README.md",
    "docs/maintenance/agent-workflow/README.md",
    "docs/maintenance/red-blue/README.md",
    "docs/maintenance/operations/postgresql-migration-runbook.md",
    "docs/maintenance/operations/infrastructure-dr-profile.yaml",
    "docs/maintenance/history/README.md",
    "docs/maintenance/history/red-blue/README.md",
    "docs/maintenance/history/red-blue/manual-round-01-overall-architecture.md",
    "docs/maintenance/history/red-blue/manual-round-02-overall-architecture-freeze-review.md",
    "docs/maintenance/history/red-blue/legacy-automated-rounds.md",
}
RED_BLUE_FILES = {
    ".agent/red-blue/README.md",
    ".agent/red-blue/current.md",
    ".agent/red-blue/protocol.md",
    ".agent/red-blue/attack-model.md",
    ".agent/red-blue/judge.md",
    ".agent/red-blue/templates/round.md",
    ".agent/red-blue/templates/turn.md",
}


def _files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []

    actual_doc_dirs = {path.name for path in (ROOT / "docs").iterdir() if path.is_dir()}
    if actual_doc_dirs != DOC_DIRS:
        errors.append(
            "docs physical compatibility paths changed unexpectedly: "
            f"expected {sorted(DOC_DIRS)}; got {sorted(actual_doc_dirs)}"
        )

    if _files(ROOT / "docs/project") != PROJECT_FILES:
        errors.append("docs/project must contain human narrative plus project machine reference")
    if _files(ROOT / "docs/research") != RESEARCH_FILES:
        errors.append("docs/research must contain only the curated upstream research knowledge set")
    if _files(ROOT / "docs/evidence") != {
        "docs/evidence/README.md", "docs/evidence/current-runtime-baseline.md",
        "docs/evidence/current-test-baseline.md", "docs/evidence/current-eval-baseline.md",
        "docs/evidence/implementation-wave-001.md",
    }:
        errors.append("docs/evidence must contain only current evidence entries")
    if _files(ROOT / "docs/governance") != GOVERNANCE_FILES:
        errors.append("docs/governance must contain only canonical documentation/provenance/ownership governance inputs")
    if _files(ROOT / "docs/modules") != MODULE_FILES:
        errors.append("docs/modules must contain the human entry, machine router, and current Target module documents")
    if _files(ROOT / "docs/maintenance") != MAINTENANCE_FILES:
        errors.append("docs/maintenance must contain only governance-controlled operations, workflows and high-value history")

    for obsolete in (
        ROOT / "docs/facts",
        ROOT / "docs/history",
        ROOT / "docs/operations",
        ROOT / "project-reconstruction-lab",
    ):
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

    red_blue_root = ROOT / ".agent" / "red-blue"
    if not red_blue_root.exists() or _files(red_blue_root) != RED_BLUE_FILES:
        errors.append(".agent/red-blue must contain only the canonical Red/Blue harness files")
    else:
        red_blue_current = (red_blue_root / "current.md").read_text(encoding="utf-8")
        inactive = "state: `no-active`" in red_blue_current and "active_round: `none`" in red_blue_current
        active = "state: `active-red-blue`" in red_blue_current
        if not (inactive or active):
            errors.append("Red/Blue current state is neither recognized inactive nor active-red-blue")

    if {path.name for path in (ROOT / "docs/architecture").iterdir() if path.is_file()} != ARCHITECTURE_FILES:
        errors.append("docs/architecture must contain human/visual/rendered entries plus machine reference")

    if errors:
        print("REPO_STRUCTURE_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("REPO_STRUCTURE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

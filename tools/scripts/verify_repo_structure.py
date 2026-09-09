from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC_DIRS = {
    "project",
    "architecture",
    "modules",
    "red-blue",
    "research",
    "decisions",
    "evidence",
    "governance",
}
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
}
MODULE_FILES = {
    "docs/modules/README.md",
    "docs/modules/reference.md",
    "docs/modules/application/README.md",
    "docs/modules/domain/README.md",
    "docs/modules/knowledge/README.md",
    "docs/modules/runtime/README.md",
    "docs/modules/capability/README.md",
    "docs/modules/effects/README.md",
    "docs/modules/model-gateway/README.md",
    "docs/modules/security/README.md",
    "docs/modules/evaluation/README.md",
}
ARCHITECTURE_FILES = {
    "README.md",
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
RED_BLUE_RUNTIME_FILES = {
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
        errors.append(f"docs top-level domains mismatch: expected {sorted(DOC_DIRS)}; got {sorted(actual_doc_dirs)}")

    if _files(ROOT / "docs/project") != PROJECT_FILES:
        errors.append("docs/project must contain the canonical README narrative plus machine reference")
    if _files(ROOT / "docs/research") != RESEARCH_FILES:
        errors.append("docs/research must contain only the curated upstream research knowledge set")
    if _files(ROOT / "docs/evidence") != {
        "docs/evidence/README.md",
        "docs/evidence/current-runtime-baseline.md",
        "docs/evidence/current-test-baseline.md",
        "docs/evidence/current-eval-baseline.md",
        "docs/evidence/implementation-wave-001.md",
    }:
        errors.append("docs/evidence must contain only current evidence entries")
    if _files(ROOT / "docs/modules") != MODULE_FILES:
        errors.append("docs/modules must contain the human entry, machine router, and semantic Target module directories")
    if {path.name for path in (ROOT / "docs/architecture").iterdir() if path.is_file()} != ARCHITECTURE_FILES:
        errors.append("docs/architecture must contain the canonical README target, visual/rendered entries, and machine reference")

    governance_files = _files(ROOT / "docs/governance")
    missing_governance = GOVERNANCE_REQUIRED - governance_files
    if missing_governance:
        errors.append(f"docs/governance missing required files: {sorted(missing_governance)}")

    red_blue_files = _files(ROOT / "docs/red-blue")
    missing_red_blue = RED_BLUE_REQUIRED - red_blue_files
    if missing_red_blue:
        errors.append(f"docs/red-blue missing required files: {sorted(missing_red_blue)}")

    for obsolete in (
        ROOT / "docs/maintenance",
        ROOT / "docs/terminology.md",
        ROOT / "docs/project/project.md",
        ROOT / "docs/architecture/architecture.md",
        ROOT / "docs/facts",
        ROOT / "docs/history",
        ROOT / "docs/operations",
        ROOT / "project-reconstruction-lab",
    ):
        if obsolete.exists():
            errors.append(f"obsolete documentation workspace must be absent: {obsolete.relative_to(ROOT)}")

    program_root = ROOT / ".agent" / "programs"
    if {path.name for path in program_root.glob("*.md")} != {"README.md", "current.md"}:
        errors.append(".agent/programs front must contain README.md and current.md")

    red_blue_root = ROOT / ".agent" / "red-blue"
    if not red_blue_root.exists() or _files(red_blue_root) != RED_BLUE_RUNTIME_FILES:
        errors.append(".agent/red-blue must contain only the canonical runtime harness files")
    else:
        red_blue_current = (red_blue_root / "current.md").read_text(encoding="utf-8")
        inactive = "state: `no-active`" in red_blue_current and "active_round: `none`" in red_blue_current
        active = "state: `active-red-blue`" in red_blue_current
        if not (inactive or active):
            errors.append("Red/Blue current state is neither recognized inactive nor active-red-blue")
        for marker in ("CHATGPT_AUTO", "AGENT_AUTO"):
            if marker not in red_blue_current:
                errors.append(f"Red/Blue current contract missing mode: {marker}")

    if errors:
        print("REPO_STRUCTURE_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("REPO_STRUCTURE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

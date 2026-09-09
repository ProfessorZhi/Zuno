from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCH_ROOT = REPO_ROOT / "docs/architecture"
ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
    "reference.md",
}
MODULE_DIRS = (
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


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    files = {path.name for path in ARCH_ROOT.iterdir() if path.is_file()}
    dirs = [path.name for path in ARCH_ROOT.iterdir() if path.is_dir()]
    if files != ARCHITECTURE_FILES:
        errors.append(f"architecture file set mismatch: {sorted(files)}")
    if dirs:
        errors.append(f"architecture directory must not contain subdirectories: {dirs}")

    required_paths = [
        REPO_ROOT / "docs/README.md",
        REPO_ROOT / "docs/project/README.md",
        REPO_ROOT / "docs/project/reference.md",
        REPO_ROOT / "docs/architecture/README.md",
        REPO_ROOT / "docs/architecture/architecture.md",
        REPO_ROOT / "docs/architecture/reference.md",
        REPO_ROOT / "docs/modules/README.md",
        REPO_ROOT / "docs/modules/reference.md",
        REPO_ROOT / "docs/red-blue/README.md",
        REPO_ROOT / "docs/research/README.md",
        REPO_ROOT / "docs/decisions/README.md",
        REPO_ROOT / "docs/evidence/README.md",
        REPO_ROOT / "docs/governance/README.md",
        REPO_ROOT / "docs/governance/documentation-architecture.md",
        REPO_ROOT / "docs/red-blue/archive/legacy/README.md",
    ]
    for name in MODULE_DIRS:
        required_paths.extend(
            [
                REPO_ROOT / "docs/modules" / name / "README.md",
                REPO_ROOT / "docs/modules" / name / "reference.md",
            ]
        )
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing canonical documentation entrypoint: {path.relative_to(REPO_ROOT)}")

    for obsolete in (
        REPO_ROOT / "docs/maintenance",
        REPO_ROOT / "docs/terminology.md",
        REPO_ROOT / "docs/project/project.md",
    ):
        if obsolete.exists():
            errors.append(f"obsolete documentation path must be absent: {obsolete.relative_to(REPO_ROOT)}")

    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")

    index = read("docs/README.md")
    project = read("docs/project/README.md")
    architecture_entry = read("docs/architecture/README.md")
    design = read("docs/architecture/architecture.md")
    arch_reference = read("docs/architecture/reference.md")
    modules_index = read("docs/modules/README.md")
    modules_reference = read("docs/modules/reference.md")
    governance_index = read("docs/governance/README.md")
    docs_architecture = read("docs/governance/documentation-architecture.md")
    system = read(".agent/system.yaml")

    for marker in (
        "project/",
        "architecture/",
        "modules/",
        "red-blue/",
        "research/",
        "decisions/",
        "evidence/",
        "governance/",
        "System & Review",
        "Trust & Evolution",
    ):
        if marker not in index:
            errors.append(f"docs README missing eight-domain marker: {marker}")

    for marker in ("project/README.md", "architecture/architecture.md", "modules/README.md"):
        if marker not in index:
            errors.append(f"docs README missing canonical human route: {marker}")
    for marker in ("architecture/reference.md", "modules/reference.md", "reference.md"):
        if marker not in index:
            errors.append(f"docs README missing engineering-route marker: {marker}")
    if "docs/architecture" not in system:
        errors.append("system.yaml must route to architecture surface")

    for marker in ("architecture.md", "reference.md", "architecture-views.md", "architecture.html"):
        if marker not in architecture_entry:
            errors.append(f"architecture README missing directory-entry marker: {marker}")

    human_markers = (
        "# Zuno 目标架构",
        "## Part A — Human Narrative（人类技术叙事）",
        "target_logical_module_count: 9",
        "overall_architecture_state: ROUND_02_FROZEN",
        "implementation_authorization: NO",
        "reference.md",
    )
    for marker in human_markers:
        if marker not in design:
            errors.append(f"architecture.md missing human/target marker: {marker}")
    if "## Part B — Engineering / Agent Reference（工程 / Agent 参考）" in design:
        errors.append("architecture.md must not contain Part B after human/reference split")
    if "Single Controller" not in design + "\n" + arch_reference:
        errors.append("architecture split views must preserve Single Controller target semantics")

    engineering_markers = (
        "status: canonical-architecture-engineering-reference",
        "human_source: docs/architecture/architecture.md",
        "module_router: docs/modules/reference.md",
        "## Part B — Engineering / Agent Reference（工程 / Agent 参考）",
        "### B1. Scope / Global Invariants",
        "### B2. Authority / Ownership Matrix",
        "### B3. Cross-boundary Contract Map",
        "### B6. Completion Proof / Non-proof",
        "### B7. Failure Taxonomy / Recovery Order",
        "### B10. Security / Approval / Human Authority",
        "### B13. Current / Target / Evidence / Unknown",
        "### B14. Machine Navigation / Source Precedence",
        "AdmissionReceipt",
        "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
        "EvidenceCandidate != Evidence",
        "CitationLineage != WorkProductCitationBinding",
        "Retry != Replan != Reconcile",
        "PreparedAction",
        "EffectReceipt",
    )
    for marker in engineering_markers:
        if marker not in arch_reference:
            errors.append(f"architecture reference missing engineering marker: {marker}")

    for marker in (
        "canonical-module-router",
        "Documentation rule",
        "Current Target module routes",
        "For a module implementation task",
        "Part C  Cross-Module Consistency",
        "Cancellation（取消）是停止未来工作，不是全局回滚",
        "Idempotency（幂等）不是一个全局 key",
        "恢复时先找 Owner Fact，再修复 Projection",
        "Module Detail Freeze Review",
    ):
        if marker not in modules_reference:
            errors.append(f"modules reference missing engineering marker: {marker}")

    for marker in (
        "module_design_baseline: AVAILABLE_V1",
        "module_deep_design: AVAILABLE_V2",
        "module_deep_design_coverage: 9/9",
        "cross_module_consistency: AVAILABLE_V1",
        "module_detail_freeze: NOT_YET",
        "implementation_authorization: NO",
        "application/README.md",
        "domain/README.md",
        "knowledge/README.md",
        "runtime/README.md",
        "capability/README.md",
        "effects/README.md",
        "model-gateway/README.md",
        "security/README.md",
        "evaluation/README.md",
        "reference.md",
    ):
        if marker not in modules_index:
            errors.append(f"modules README missing human/current-design marker: {marker}")

    for marker in (
        "documentation-architecture.md",
        "System & Review",
        "Trust & Evolution",
        "Governance 内部结构",
    ):
        if marker not in governance_index:
            errors.append(f"governance README missing documentation architecture marker: {marker}")

    for marker in (
        "canonical-documentation-architecture",
        "Physical layout",
        "Truth ownership",
        "Human / Machine projection",
        "Default reading paths",
        "Module decomposition",
        "Research boundary",
        "Red / Blue boundary",
        "Architecture reasoning contract",
        "architecture/architecture.md",
        "architecture/reference.md",
    ):
        if marker not in docs_architecture:
            errors.append(f"documentation architecture reference missing marker: {marker}")

    for marker in ("project-fact-provenance.md", "Pilot Validation", "Production", "Current", "Target", "Unknown"):
        if marker not in project:
            errors.append(f"project README missing factual-boundary marker: {marker}")

    for marker in ("Current", "Target", "Unknown"):
        if marker not in index:
            errors.append(f"docs README must explain {marker}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("architecture document set verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
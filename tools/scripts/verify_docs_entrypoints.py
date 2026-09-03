from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
    "reference.md",
}
PROJECT_FILES = [
    "docs/project/README.md",
    "docs/project/project.md",
    "docs/project/reference.md",
]
RESEARCH_FILES = [
    "docs/research/README.md",
    "docs/research/deep-research-report-2026-08-27.md",
    "docs/research/jidong-ge-liplab-lineage.md",
    "docs/research/research-to-engineering-traceability.md",
    "docs/research/agent-platform-baseline.md",
    "docs/research/documentation-narrative-blueprint.md",
]
MODULE_FILES = [
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
]
MODULE_BASELINE_HEADINGS = [
    "### B1 Scope / Global Invariants",
    "### B2 Responsibility / Ownership",
    "### B3 Upstream / Downstream",
    "### B4 Authoritative Facts / Core Objects",
    "### B5 Cross-boundary Contracts",
    "### B6 Normal Flow",
    "### B7 State / Lifecycle",
    "### B8 Failure Taxonomy",
    "### B9 Retry / Replan / Reconcile / Recovery / Idempotency",
    "### B10 Security / Approval / Audit",
    "### B11 Persistence / Transaction Boundaries",
    "### B12 Observability / Evaluation",
    "### B13 Current / Target / Gap / Evidence",
    "### B14 Code / Database / Migration Constraints",
]
DETAIL_CANDIDATE_HEADINGS = [
    f"#### B14.{number} Detail Freeze Candidate" for number in range(1, 9)
]


def _load_links():
    path = REPO_ROOT / "tools/scripts/verify_markdown_internal_links.py"
    spec = importlib.util.spec_from_file_location("verify_markdown_internal_links", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load markdown link verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _has_candidate_status(content: str) -> bool:
    return "detail_design: candidate-v1" in content or "detail-design: candidate-v1" in content


def verify() -> list[str]:
    errors = list(_load_links().verify())
    required = [
        "README.md", "docs/README.md", *PROJECT_FILES, *RESEARCH_FILES,
        "docs/architecture/README.md", "docs/architecture/architecture.md",
        "docs/architecture/architecture-views.md", "docs/architecture/architecture.html",
        "docs/architecture/reference.md",
        "docs/modules/reference.md", *MODULE_FILES,
        "docs/decisions/README.md",
        "docs/evidence/README.md",
        "docs/governance/README.md",
        "docs/governance/documentation-architecture.md",
        "docs/governance/project-fact-provenance.md",
        "docs/governance/human-first-documentation-standard.md",
        "docs/terminology.md",
        "docs/maintenance/README.md",
        "docs/maintenance/agent-workflow/README.md",
        "docs/maintenance/red-blue/README.md",
        "docs/maintenance/history/README.md",
        "docs/maintenance/history/red-blue/README.md",
        "docs/maintenance/history/red-blue/manual-round-01-overall-architecture.md",
        "docs/maintenance/history/red-blue/manual-round-02-overall-architecture-freeze-review.md",
        "docs/maintenance/history/red-blue/legacy-automated-rounds.md",
        "docs/maintenance/operations/postgresql-migration-runbook.md",
        "docs/maintenance/operations/infrastructure-dr-profile.yaml",
        ".agent/references/docs-map.md", ".agent/references/workflow.md", ".agent/system.yaml",
        ".agent/red-blue/README.md", ".agent/red-blue/current.md",
        ".agent/red-blue/protocol.md", ".agent/red-blue/attack-model.md", ".agent/red-blue/judge.md",
    ]
    for path in required:
        if not (REPO_ROOT / path).exists():
            errors.append(f"missing documentation entrypoint: {path}")

    root = REPO_ROOT / "docs/architecture"
    if {path.name for path in root.iterdir() if path.is_file()} != ARCHITECTURE_FILES:
        errors.append(f"docs/architecture file set mismatch: {sorted(path.name for path in root.iterdir() if path.is_file())}")
    if any(path.is_dir() for path in root.iterdir()):
        errors.append("docs/architecture must not contain subdirectories")

    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")
    for forbidden in (
        REPO_ROOT / "docs/facts",
        REPO_ROOT / "docs/history",
        REPO_ROOT / "docs/operations",
        REPO_ROOT / "project-reconstruction-lab",
    ):
        if forbidden.exists():
            errors.append(f"obsolete documentation workspace must be absent: {forbidden.relative_to(REPO_ROOT)}")

    index = (REPO_ROOT / "docs/README.md").read_text(encoding="utf-8")
    for marker in (
        "System Story", "Knowledge Control",
        "project/", "architecture/", "modules/",
        "decisions/", "evidence/", "governance/",
        "Human View", "Engineering / Agent View",
        "Current", "Target", "Unknown",
        "research/", "maintenance/",
        "Project 解释现实",
    ):
        if marker not in index:
            errors.append(f"docs/README.md missing six-domain/navigation marker: {marker}")

    research = (REPO_ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    for marker in (
        "DIRECT_LINEAGE", "CAPABILITY_LINEAGE", "CONCEPTUAL_LINEAGE", "BACKGROUND_ONLY", "UNVERIFIED",
        "Paper != Capability != Provider != Qualified Provider != Formal Business Fact",
        "last_verified",
    ):
        if marker not in research:
            errors.append(f"docs/research/README.md missing research boundary marker: {marker}")

    red_blue = (REPO_ROOT / "docs/maintenance/red-blue/README.md").read_text(encoding="utf-8")
    for marker in (
        ".agent/red-blue/", "Closed-book", "Part A", "chatgpt-duel", "autonomous-agent",
        "ProfessorZhi/internship-work", "ProfessorZhi/interview-notes",
    ):
        if marker not in red_blue:
            errors.append(f"docs/maintenance/red-blue/README.md missing workflow marker: {marker}")

    project_readme = (REPO_ROOT / "docs/project/README.md").read_text(encoding="utf-8")
    for marker in ("Project — Zuno 为什么会出现", "Human View", "Machine View", "project.md", "reference.md", "project-fact-provenance.md"):
        if marker not in project_readme:
            errors.append(f"docs/project/README.md missing project navigation marker: {marker}")

    project_reference = (REPO_ROOT / "docs/project/reference.md").read_text(encoding="utf-8")
    for marker in ("canonical-project-machine-index", "Historical baseline", "Confirmed personal participation", "Claim boundaries"):
        if marker not in project_reference:
            errors.append(f"docs/project/reference.md missing machine reference marker: {marker}")

    architecture_reference = (REPO_ROOT / "docs/architecture/reference.md").read_text(encoding="utf-8")
    for marker in ("canonical-architecture-machine-router", "Read order for implementation", "Cross-cutting facts that belong here", "Non-goals"):
        if marker not in architecture_reference:
            errors.append(f"docs/architecture/reference.md missing machine reference marker: {marker}")

    modules_reference = (REPO_ROOT / "docs/modules/reference.md").read_text(encoding="utf-8")
    for marker in ("canonical-module-router", "Documentation rule", "Current Target module routes", "For a module implementation task"):
        if marker not in modules_reference:
            errors.append(f"docs/modules/reference.md missing machine reference marker: {marker}")

    documentation_architecture = (REPO_ROOT / "docs/governance/documentation-architecture.md").read_text(encoding="utf-8")
    for marker in ("canonical-documentation-architecture", "system_story", "knowledge_control", "Human / Machine projection", "Module decomposition", "Navigation contracts"):
        if marker not in documentation_architecture:
            errors.append(f"docs/governance/documentation-architecture.md missing marker: {marker}")

    project = (REPO_ROOT / "docs/project/project.md").read_text(encoding="utf-8")
    for marker in (
        "为什么不直接用 Dify、Coze",
        "项目是怎样发展到今天的",
        "团队是什么形态，我在里面做了什么",
        "相比通用方案，我们今天到底证明了什么",
        "Current", "Target", "Unknown",
    ):
        if marker not in project:
            errors.append(f"project.md missing coverage marker: {marker}")

    provenance = (REPO_ROOT / "docs/governance/project-fact-provenance.md").read_text(encoding="utf-8")
    for marker in ("PF-001", "PF-020", "PF-024", "PF-028", "Target / 产品价值假设", "Unknown / 未恢复"):
        if marker not in provenance:
            errors.append(f"project fact provenance missing ledger marker: {marker}")

    modules = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    for marker in (
        "01-application-integration.md", "09-observability-evaluation.md", "module_design_baseline",
        "module_detail_design_candidate: AVAILABLE_V1", "module_detail_design_candidate_coverage: 9/9",
        "module_detail_freeze: NOT_YET", "implementation_authorization: NO",
    ):
        if marker not in modules:
            errors.append(f"docs/modules/README.md missing current Target decomposition marker: {marker}")

    for module_path in MODULE_FILES[1:]:
        content = (REPO_ROOT / module_path).read_text(encoding="utf-8")
        for marker in (
            "status: design-baseline-v1",
            "implementation: not-authorized",
            "## Part A — Human Narrative",
            "## Part B — Engineering / Agent Reference",
        ):
            if marker not in content:
                errors.append(f"{module_path} missing module baseline marker: {marker}")
        if not _has_candidate_status(content):
            errors.append(f"{module_path} missing detail candidate status")
        for heading in MODULE_BASELINE_HEADINGS + DETAIL_CANDIDATE_HEADINGS:
            if heading not in content:
                errors.append(f"{module_path} missing required heading: {heading}")
        if not all(status in content for status in ("Current", "Target", "Gap")):
            errors.append(f"{module_path} must distinguish Current / Target / Gap")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("documentation entrypoint verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

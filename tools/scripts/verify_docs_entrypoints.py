from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}
PROJECT_FILES = [
    "docs/project/README.md",
    "docs/project/project.md",
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
        "docs/governance/project-fact-provenance.md",
        "docs/governance/human-first-documentation-standard.md",
        "docs/evidence/README.md", *MODULE_FILES,
        "docs/maintenance/README.md",
        "docs/maintenance/agent-workflow/README.md",
        "docs/maintenance/history/README.md",
        "docs/maintenance/history/red-blue/README.md",
        "docs/maintenance/history/red-blue/manual-round-01-overall-architecture.md",
        "docs/maintenance/history/red-blue/manual-round-02-overall-architecture-freeze-review.md",
        "docs/maintenance/history/red-blue/legacy-automated-rounds.md",
        "docs/architecture/README.md", "docs/architecture/architecture.md",
        "docs/architecture/architecture-views.md", "docs/architecture/architecture.html",
        "docs/decisions/README.md", "docs/terminology.md",
        "docs/maintenance/operations/postgresql-migration-runbook.md",
        "docs/maintenance/operations/infrastructure-dr-profile.yaml",
        ".agent/references/docs-map.md", ".agent/system.yaml",
    ]
    for path in required:
        if not (REPO_ROOT / path).exists():
            errors.append(f"missing documentation entrypoint: {path}")

    root = REPO_ROOT / "docs/architecture"
    if {path.name for path in root.iterdir() if path.is_file()} != ARCHITECTURE_FILES:
        errors.append("docs/architecture must contain exactly four files")
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
        "Current", "Target", "Unknown", "project/", "research/", "architecture/", "modules/",
        "evidence/", "maintenance/", "maintenance/history/red-blue/",
        "module_deep_design", "module_detail_design_candidate", "module_detail_design_candidate_coverage: 9/9",
    ):
        if marker not in index:
            errors.append(f"docs/README.md missing status/architecture marker: {marker}")

    research = (REPO_ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    for marker in (
        "DIRECT_LINEAGE", "CAPABILITY_LINEAGE", "CONCEPTUAL_LINEAGE", "BACKGROUND_ONLY", "UNVERIFIED",
        "Paper != Capability != Provider != Qualified Provider != Formal Business Fact",
        "last_verified",
    ):
        if marker not in research:
            errors.append(f"docs/research/README.md missing research boundary marker: {marker}")

    project_readme = (REPO_ROOT / "docs/project/README.md").read_text(encoding="utf-8")
    for marker in ("project.md", "project-fact-provenance.md", "Project 文档入口"):
        if marker not in project_readme:
            errors.append(f"docs/project/README.md missing project navigation marker: {marker}")

    project = (REPO_ROOT / "docs/project/project.md").read_text(encoding="utf-8")
    for marker in (
        "为什么不直接用 Dify、Coze",
        "项目是怎样发展到今天的",
        "团队是什么形态，我在里面做了什么",
        "相比通用方案，我们今天到底证明了什么",
        "如果我是大厂面试官，我会继续追问什么",
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
            errors.append(f"docs/modules/README.md missing module design marker: {marker}")

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

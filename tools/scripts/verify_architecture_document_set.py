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

    for path in (
        REPO_ROOT / "docs/README.md",
        REPO_ROOT / "docs/project/README.md",
        REPO_ROOT / "docs/project/project.md",
        REPO_ROOT / "docs/project/reference.md",
        REPO_ROOT / "docs/architecture/README.md",
        REPO_ROOT / "docs/architecture/architecture.md",
        REPO_ROOT / "docs/architecture/reference.md",
        REPO_ROOT / "docs/modules/README.md",
        REPO_ROOT / "docs/modules/reference.md",
        REPO_ROOT / "docs/decisions/README.md",
        REPO_ROOT / "docs/evidence/README.md",
        REPO_ROOT / "docs/governance/README.md",
        REPO_ROOT / "docs/governance/documentation-architecture.md",
        REPO_ROOT / "docs/maintenance/history/red-blue/README.md",
    ):
        if not path.exists():
            errors.append(f"missing canonical documentation entrypoint: {path.relative_to(REPO_ROOT)}")

    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")

    design = read("docs/architecture/architecture.md")
    index = read("docs/README.md")
    project = read("docs/project/project.md")
    arch_index = read("docs/architecture/README.md")
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
        "decisions/",
        "evidence/",
        "governance/",
        "System Story",
        "Knowledge Control",
        "Project 解释现实",
    ):
        if marker not in index:
            errors.append(f"docs README missing six-domain marker: {marker}")

    if "project.md" not in index:
        errors.append("docs README must route to consolidated project.md")
    if "docs/architecture/" not in system:
        errors.append("system.yaml must route to architecture surface")

    for marker in (
        "Human View",
        "Engineering / Agent View",
        "reference.md",
        "模块数量不是文档先验",
        "Evidence",
    ):
        if marker not in arch_index:
            errors.append(f"architecture README missing new documentation-boundary marker: {marker}")

    for marker in (
        "canonical-architecture-machine-router",
        "Read order for implementation",
        "Cross-cutting facts that belong here",
        "Non-goals",
    ):
        if marker not in arch_reference:
            errors.append(f"architecture reference missing machine-routing marker: {marker}")

    for marker in (
        "canonical-module-router",
        "Documentation rule",
        "Current Target module routes",
        "For a module implementation task",
    ):
        if marker not in modules_reference:
            errors.append(f"modules reference missing machine-routing marker: {marker}")

    for marker in (
        "六域文档模型",
        "documentation-architecture.md",
        "三个系统域",
        "三个治理域",
    ):
        if marker not in governance_index:
            errors.append(f"governance README missing documentation architecture marker: {marker}")

    for marker in (
        "canonical-documentation-architecture",
        "system_story",
        "knowledge_control",
        "Human / Machine projection",
        "Module decomposition",
        "Navigation contracts",
    ):
        if marker not in docs_architecture:
            errors.append(f"documentation architecture reference missing marker: {marker}")

    for marker in (
        "为什么会有这个项目",
        "为什么不直接用 Dify、Coze",
        "项目是怎样发展到今天的",
        "团队是什么形态，我在里面做了什么",
        "相比通用方案，我们今天到底证明了什么",
    ):
        if marker not in project:
            errors.append(f"project.md missing human narrative marker: {marker}")

    # Protect semantic coverage and the dual-view documentation model, not one prose template.
    for marker in (
        "target_logical_module_count: 9",
        "overall_architecture_state: ROUND_02_FROZEN",
        "implementation_authorization: NO",
        "# Zuno 目标架构",
        "## Part A — Human Narrative（人类技术叙事）",
        "法律智能真正变难的时刻",
        "一件案件里的五种事实",
        "四次跨边界决定系统是否可信",
        "九个责任域如何从这些边界产生",
        "故障以后，先找事实再恢复控制",
        "研究成果怎样变成工程能力",
        "复杂度必须在测量中证明收益",
        "## Part B — Engineering / Agent Reference（工程 / Agent 参考）",
        "### B1. Scope / Global Invariants",
        "### B2. Authority / Ownership Matrix",
        "### B3. Cross-boundary Contract Map",
        "### B6. Completion Proof / Non-proof",
        "### B7. Failure Taxonomy / Recovery Order",
        "### B10. Security / Approval / Human Authority",
        "### B13. Current / Target / Evidence / Unknown",
        "### B14. Machine Navigation / Source Precedence",
        "Single Controller",
        "AdmissionReceipt",
        "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
        "EvidenceCandidate != Evidence",
        "CitationLineage != WorkProductCitationBinding",
        "Retry != Replan != Reconcile",
        "PreparedAction",
        "EffectReceipt",
    ):
        if marker not in design:
            errors.append(f"architecture.md missing target architecture marker: {marker}")

    part_a = design.find("## Part A — Human Narrative（人类技术叙事）")
    part_b = design.find("## Part B — Engineering / Agent Reference（工程 / Agent 参考）")
    if part_a < 0 or part_b < 0 or part_a >= part_b:
        errors.append("architecture.md must keep ordered Part A Human Narrative and Part B Engineering / Agent Reference")

    for marker in (
        "module_design_baseline: AVAILABLE_V1",
        "module_deep_design: AVAILABLE_V2",
        "module_deep_design_coverage: 9/9",
        "cross_module_consistency: AVAILABLE_V1",
        "module_detail_freeze: NOT_YET",
        "implementation_authorization: NO",
        "01-application-integration.md",
        "02-legal-domain-work-product.md",
        "03-knowledge-evidence.md",
        "04-agent-runtime-control.md",
        "05-capability-skill.md",
        "06-tool-runtime-effects.md",
        "07-model-gateway.md",
        "08-security-governance.md",
        "09-observability-evaluation.md",
        "Part C  Cross-Module Consistency",
        "Cancellation（取消）是停止未来工作，不是全局回滚",
        "Idempotency（幂等）不是一个全局 key",
    ):
        if marker not in modules_index:
            errors.append(f"modules README missing current design marker: {marker}")

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

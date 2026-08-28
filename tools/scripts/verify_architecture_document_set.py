from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ARCH_ROOT = REPO_ROOT / "docs/architecture"
ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}


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
        REPO_ROOT / "docs/architecture/architecture.md",
        REPO_ROOT / "docs/modules/README.md",
        REPO_ROOT / "docs/maintenance/history/red-blue/README.md",
    ):
        if not path.exists():
            errors.append(f"missing canonical project entrypoint: {path.relative_to(REPO_ROOT)}")

    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")

    design = read("docs/architecture/architecture.md")
    index = read("docs/README.md")
    project = read("docs/project/project.md")
    arch_index = read("docs/architecture/README.md")
    modules_index = read("docs/modules/README.md")
    system = read(".agent/system.yaml")

    if "project/" not in index or "architecture/" not in index:
        errors.append("docs README must route to project and architecture")
    if "project.md" not in index:
        errors.append("docs README must route to consolidated project.md")
    if "docs/architecture/" not in system:
        errors.append("system.yaml must route to architecture surface")

    for marker in (
        "architecture.md",
        "architecture-views.md",
        "architecture.html",
        "../project/project.md",
        "../modules/",
        "../decisions/",
        "../evidence/",
        "ADR",
    ):
        if marker not in arch_index:
            errors.append(f"architecture README missing boundary marker: {marker}")

    for marker in (
        "为什么会有这个项目",
        "为什么不直接用 Dify、Coze",
        "项目是怎样发展到今天的",
        "团队是什么形态，我在里面做了什么",
        "相比通用方案，我们今天到底证明了什么",
    ):
        if marker not in project:
            errors.append(f"project.md missing human narrative marker: {marker}")

    if "target_logical_module_count: 9" not in design or "overall_architecture_state: ROUND_02_FROZEN" not in design:
        errors.append("architecture.md must record the frozen nine-module Target and Round 02 source")

    narrative_markers = (
        "Zuno 的总体架构围绕一个问题展开",
        "简单问答",
        "按事实权威划分责任",
        "九个逻辑责任域",
        "复杂度的退出机制",
        "Single Controller",
        "Runtime Control State",
        "AdmissionReceipt",
        "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
        "EvidenceCandidate != Evidence",
        "CitationLineage != WorkProductCitationBinding",
        "Retry != Replan != Reconcile",
        "EffectReceipt",
        "AuditPersistenceReceipt",
    )
    for marker in narrative_markers:
        if marker not in design:
            errors.append(f"architecture.md missing current narrative marker: {marker}")

    for marker in (
        "module_design_baseline: AVAILABLE_V1",
        "module_deep_design: AVAILABLE_V2",
        "module_deep_design_coverage: 9/9",
        "cross_module_consistency: AVAILABLE_V1",
        "module_detail_freeze: NOT_YET",
        "implementation_authorization: NO",
    ):
        if marker not in design:
            errors.append(f"architecture.md missing module governance marker: {marker}")

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

    if "Current" not in index or "Target" not in index or "Unknown" not in index:
        errors.append("docs README must explain Current/Target/Unknown")
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

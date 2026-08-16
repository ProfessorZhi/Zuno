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
        REPO_ROOT / "docs/project/project-background.md",
        REPO_ROOT / "docs/project/development-process.md",
        REPO_ROOT / "docs/architecture/architecture.md",
        REPO_ROOT / "docs/modules/README.md",
        REPO_ROOT / "docs/history/red-blue/README.md",
    ):
        if not path.exists():
            errors.append(f"missing canonical project entrypoint: {path.relative_to(REPO_ROOT)}")

    for mirror in (REPO_ROOT / ".agent/architecture", REPO_ROOT / ".agent/modules"):
        if mirror.exists():
            errors.append(f"documentation mirror must not exist: {mirror.relative_to(REPO_ROOT)}")

    design = read("docs/architecture/architecture.md")
    index = read("docs/README.md")
    arch_index = read("docs/architecture/README.md")
    modules_index = read("docs/modules/README.md")
    system = read(".agent/system.yaml")

    if "project/" not in index or "architecture/" not in index:
        errors.append("project README must route to project and architecture")
    if "docs/architecture/" not in system:
        errors.append("system.yaml must route to architecture surface")

    for marker in (
        "architecture.md",
        "architecture-views.md",
        "architecture.html",
        "../project/",
        "../modules/",
        "../decisions/",
        "../evidence/",
        "ADR",
    ):
        if marker not in arch_index:
            errors.append(f"architecture README missing boundary marker: {marker}")

    if "9 个 Target Logical Modules" not in design or "Round 02" not in design:
        errors.append("architecture.md must record the frozen nine-module Target and Round 02 source")

    narrative_markers = (
        "Zuno 面向智慧司法和法律专业工作",
        "不是所有法律任务都需要同样复杂的系统",
        "简单问答",
        "Generic Host（通用 Agent 宿主）",
        "A/B/C",
        "Platform / Infrastructure",
        "可选上下文边界",
        "Runtime Control State（运行控制状态）",
        "AdmissionReceipt（正式准入回执）",
        "KnowledgeGeneration 生命周期",
        "ReadinessDecision（知识就绪判断）",
        "EvidenceCandidate != Evidence",
        "CitationLineage != WorkProductCitationBinding",
    )
    for marker in narrative_markers:
        if marker not in design:
            errors.append(f"architecture.md missing current narrative marker: {marker}")

    for marker in (
        "module_design_baseline: AVAILABLE_V1",
        "module_detail_freeze: NOT_YET",
        "implementation_authorization: NO",
    ):
        if marker not in design:
            errors.append(f"architecture.md missing module governance marker: {marker}")

    # The module index owns module-design progress. Once the first deep-design pass
    # covers all nine modules, validation should check that canonical state rather
    # than preserve the earlier 02+03-only sequencing sentence.
    for marker in (
        "module_design_baseline: AVAILABLE_V1",
        "module_deep_design: AVAILABLE_V1",
        "module_deep_design_coverage: 9/9",
        "module_detail_freeze: NOT_YET",
        "implementation_authorization: NO",
        "01 应用与集成",
        "02 法律领域",
        "03 知识证据",
        "04 运行控制",
        "05 专业能力",
        "06 工具外部效果",
        "07 模型网关",
        "08 安全治理",
        "09 可观测性评测",
    ):
        if marker not in modules_index:
            errors.append(f"modules README missing current design marker: {marker}")

    if "Current" not in index or "Target" not in index or "Unknown" not in index:
        errors.append("project README must explain Current/Target/Unknown")
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

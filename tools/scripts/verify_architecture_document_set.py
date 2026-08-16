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
        REPO_ROOT / "docs/history/red-blue/README.md",
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

    if "9 个 Target Logical Modules" not in design or "Round 02" not in design:
        errors.append("architecture.md must record the frozen nine-module Target and Round 02 source")

    # Human-first narrative validation deliberately checks semantic topics instead of
    # pinning one historical sentence. Exact prose markers made the validator resist
    # editorial improvements and encouraged architecture.md to read like a spec sheet.
    narrative_topics = {
        "project positioning": (
            "LIPLAB",
            "智慧司法",
            "法律智能 Agent 平台",
        ),
        "task complexity": (
            "不是所有法律任务都需要同样复杂的系统",
            "复杂度跟着任务走",
        ),
        "ownership over technology stack": (
            "为什么按“事实谁负责”切架构",
            "事实所有权",
        ),
        "non-pipeline module model": (
            "九个责任域不是九段必须依次经过的流水线",
            "不是请求的固定执行顺序",
        ),
        "complexity deletion": (
            "一项复杂机制什么时候应该主动删除",
            "复杂度淘汰",
        ),
        "simple QA": ("简单问答",),
        "generic host boundary": ("Generic Host（通用 Agent 宿主）",),
        "runtime comparison": ("A/B/C", "Generic Host + Legal Backend"),
        "platform responsibility layer": ("Platform / Infrastructure", "平台与基础设施"),
        "optional context boundary": ("可选上下文边界", "Context / Memory", "Optional Context"),
        "runtime control state": ("Runtime Control State", "运行控制状态"),
        "formal admission receipt": ("AdmissionReceipt（正式准入回执）",),
        "knowledge generation lifecycle": ("KnowledgeGeneration 生命周期", "KnowledgeGeneration（知识生成版本）"),
        "task readiness": ("ReadinessDecision（知识就绪判断）", "task-level ReadinessDecision（任务级知识就绪判断）"),
        "candidate vs evidence": ("EvidenceCandidate != Evidence",),
        "retrieval lineage vs formal citation": ("CitationLineage != WorkProductCitationBinding",),
    }
    for topic, alternatives in narrative_topics.items():
        if not any(marker in design for marker in alternatives):
            errors.append(
                f"architecture.md missing current narrative topic: {topic}; "
                f"expected one of {alternatives}"
            )

    for marker in (
        "module_design_baseline: AVAILABLE_V1",
        "module_deep_design: AVAILABLE_V2",
        "module_deep_design_coverage: 9/9",
        "cross_module_consistency: AVAILABLE_V1",
        "module_detail_design_candidate: AVAILABLE_V1",
        "module_detail_design_candidate_coverage: 9/9",
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
        "module_detail_design_candidate: AVAILABLE_V1",
        "module_detail_design_candidate_coverage: 9/9",
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

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

COMPLETED_PROGRAM_NAME = "zuno-eight-deliverables-full-realization-v1"
COMPLETED_PROGRAM_ARCHIVE = f"docs/history/programs/{COMPLETED_PROGRAM_NAME}"
COMPLETED_PROGRAM_PHASE_FILES = [
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE01_program-boot-baseline.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE02_workflow-self-maintenance-system.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE03_architecture-docs-html-system.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE04_query-router-mode-policy.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE05_context-builder-memory-system.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE06_capability-toolcard-mcp-system.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE07_hooks-evidence-trace-artifact-system.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE08_graphrag-knowledge-runtime-system.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE09_runtime-upgrade-integration.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/PHASE10_validation-release-closure.md",
]

FORBIDDEN_CURRENT_DIRS = [
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
    "docs/architecture/history",
    "docs/architecture/audits",
    "docs/architecture/specs",
    "docs/development",
    "docs/prototypes",
    "docs/ui-review",
    "docs/ui-gallery",
    "docs/superpowers",
]

REQUIRED_DOCS = [
    "docs/README.md",
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/history/README.md",
    "docs/evidence/public-demo.md",
]

REQUIRED_AGENT_PROGRAMS = [
    "docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
    ".agent/programs/current.md",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/closure-checklist.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/README.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/current.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/implementation-roadmap.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/closure-checklist.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/closure-summary.md",
    *COMPLETED_PROGRAM_PHASE_FILES,
    ".agent/architecture/future/programs/README.md",
    ".agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md",
    ".agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-workflow-doc-system-v1/README.md",
    "docs/history/programs/zuno-target-architecture-refresh-v1/README.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/README.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE01_repo-layout-audit.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE05_hygiene-verifier-closure.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE06_backend-directory-clarity-audit.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE07_fastapi-jwt-auth-compat-retirement-plan.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE08_backend-physical-cleanup-slices.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE09_target-layout-visual-compat-shell-retirement.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE10_alias-inventory-and-target-contract.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE11_import-smoke-and-compat-registry-design.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE12_low-risk-alias-surface-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE13_medium-risk-alias-surface-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE14_high-risk-core-services-settings-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE15_final-root-surface-guard-and-closure.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/README.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/current.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE01_six-layer-current-inventory.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE02_memory-layer-foundation-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE03_capability-layer-foundation-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE04_knowledge-layer-foundation-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE05_agent-runtime-boundary-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE06_platform-boundary-hardening.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE07_docs-verifier-and-closure.md",
    "docs/history/programs/zuno-target-runtime-v2/README.md",
    "docs/history/programs/official-graphrag-cleanup-v1/implementation-roadmap.md",
    ".agent/architecture/near-term/00-architecture-index.md",
]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _section_body(content: str, heading: str) -> str:
    marker = f"## {heading}"
    start = content.find(marker)
    if start == -1:
        return ""
    next_heading = content.find("\n## ", start + len(marker))
    if next_heading == -1:
        return content[start:]
    return content[start:next_heading]


def verify_future_only_terms() -> list[str]:
    errors: list[str] = []
    future_terms = [
        "Java",
        "microservice",
        "microservices",
        "微服务",
        "event-driven worker",
        "event workers",
        "事件驱动 worker",
        "事件 worker",
        "product-level multi-agent",
        "product/runtime default multi-agent",
        "产品级多 Agent",
        "Coding Agent",
    ]
    allowed_context_markers = [
        "Future",
        "非近期目标",
        "不属于 Current",
        "当前不是什么",
        "当前路线图不实施",
        "不能写成 Current",
        "不作为近期实现",
        "不默认实施",
        "不是当前",
        "不是近期",
        "不是默认",
        "不是微服务",
        "不实施",
    ]
    docs_to_scan = [
        "README.md",
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/architecture.md",
    ]

    for relative_path in docs_to_scan:
        content = _read(relative_path)
        lines = content.splitlines()
        for index, line in enumerate(lines, start=1):
            if not any(term in line for term in future_terms):
                continue
            window = "\n".join(lines[max(0, index - 12) : min(len(lines), index + 3)])
            if not any(marker in window for marker in allowed_context_markers):
                errors.append(
                    f"{relative_path}:{index} mentions future-only term outside explicit Future/not-Current context: {line.strip()}"
                )

    current = _read("docs/architecture/current-architecture.md")
    not_current_section = _section_body(current, "不属于 Current")
    for term in future_terms:
        if term in current and term not in not_current_section:
            errors.append(
                f"current-architecture.md mentions future-only term outside 不属于 Current section: {term}"
            )

    return errors


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_DOCS + REQUIRED_AGENT_PROGRAMS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing boundary path: {relative_path}")

    for relative_path in FORBIDDEN_CURRENT_DIRS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"retired docs directory still on current path: {relative_path}")

    for path in [*REPO_ROOT.glob("docs/**/*.md"), *REPO_ROOT.glob(".agent/**/*.md")]:
        content = path.read_text(encoding="utf-8")
        if "C:\\Users\\Administrator\\Downloads" in content:
            errors.append(f"{path.relative_to(REPO_ROOT)} contains local Downloads path")

    current = _read("docs/architecture/current-architecture.md")
    if "以下仍是 Target，不是当前成熟事实" not in current:
        errors.append("current architecture must not promote Target behavior to Current")

    target = _read("docs/architecture/target-architecture.md")
    for phrase in [
        "Summary Compression",
        "Structured Extraction",
        "Native BM25",
        "ToolCard",
        "RRF",
        "`auto` 是 router",
        "GraphRAG 实体抽取默认主路径是 LLM 抽取",
        "知识库配置必须能选择 `graph_index_settings.entity_extraction_mode = llm`",
    ]:
        if phrase not in target:
            errors.append(f"target architecture missing canonical phrase: {phrase}")

    current_program = _read(".agent/references/current-program.md")
    for phrase in [
        "当前没有 active program",
        "state: no-active",
        "current_phase: none",
        COMPLETED_PROGRAM_NAME,
        COMPLETED_PROGRAM_ARCHIVE,
        "PHASE01-PHASE10",
        "八大交付物",
        "默认开启线程内多 agent",
        "zuno-six-layer-internalization-v1",
        "docs/history/programs/zuno-six-layer-internalization-v1/",
        "final alias surface closure",
        "legacy_aliases.py",
        "__init__.py",
        "main.py",
        "zuno-repo-layout-cleanup-v1",
        "zuno-runtime-architecture-upgrade-v1",
        "zuno-architecture-visuals-v1",
    ]:
        if phrase not in current_program:
            errors.append(f"current-program.md missing program-status phrase: {phrase}")

    docs_front_path = ["README.md", "docs/README.md", "docs/architecture/README.md"]
    for relative_path in docs_front_path:
        content = _read(relative_path)
        if "zuno-ideal-architecture-and-repo-layout.html" in content:
            errors.append(f"{relative_path} must not place retired .agent target HTML in docs front path")

    forbidden_front_path_text = [
        "docs/architecture/phases/README.md",
        "docs/architecture/plans/",
        "docs/architecture/programs/",
        "docs/architecture/audits/",
        "docs/architecture/specs/",
        "docs/architecture/history/",
        "docs/development/",
        "docs/prototypes/",
        "docs/ui-review/",
        "docs/superpowers/",
    ]
    for relative_path in docs_front_path:
        content = _read(relative_path)
        for phrase in forbidden_front_path_text:
            if phrase in content:
                errors.append(f"{relative_path} contains retired front-path text: {phrase}")

    forbidden_active_doc_text = [
        "docs/architecture/phases/",
        "docs/architecture/plans/",
        "docs/architecture/programs/",
        "docs/architecture/audits/",
        "docs/architecture/specs/",
        "docs/architecture/history/",
        "docs/development/",
        "docs/prototypes/",
        "docs/ui-review/",
    ]
    for path in sorted(REPO_ROOT.glob("docs/**/*.md")):
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if relative_path.startswith("docs/history/"):
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden_active_doc_text:
            if phrase in content:
                errors.append(
                    f"{relative_path} links retired architecture current path: {phrase}"
                )

    errors.extend(verify_future_only_terms())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Doc boundary verification failed.")
        return 1

    print("Doc boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

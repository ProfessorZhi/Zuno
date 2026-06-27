from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


REQUIRED_PATHS = [
    "AGENTS.md",
    "apps/web/AGENTS.md",
    "src/backend/zuno/AGENTS.md",
    "tools/evals/zuno/AGENTS.md",
    ".agent/README.md",
    ".agent/system.yaml",
    ".agent/references/README.md",
    ".agent/references/task-routing.md",
    ".agent/references/workflow.md",
    ".agent/references/code-map.md",
    ".agent/references/runtime-call-chain.md",
    ".agent/references/verification-map.md",
    ".agent/references/docs-map.md",
    ".agent/references/current-program.md",
    ".agent/references/command-catalog.md",
    ".agent/references/known-pitfalls.md",
    ".agent/scripts/verify_module_boundaries.py",
    ".agent/architecture/README.md",
    ".agent/architecture/decisions/README.md",
    ".agent/architecture/future/README.md",
    ".agent/architecture/near-term/README.md",
    ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
    ".agent/architecture/near-term/01-target-runtime-architecture.md",
    ".agent/architecture/near-term/02-context-memory-architecture.md",
    ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
    ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
    ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
    ".agent/programs/README.md",
    ".agent/programs/current.md",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/PHASE01_public-architecture-surface.md",
    ".agent/programs/PHASE02_local-agent-skill-system.md",
    ".agent/programs/PHASE03_tools-tests-guardrails.md",
    ".agent/programs/PHASE04_backend-facade-layers.md",
    ".agent/programs/PHASE05_large-file-light-split.md",
    ".agent/programs/PHASE06_architecture-diagrams-html.md",
    ".agent/programs/closure-checklist.md",
    "docs/history/programs/zuno-target-runtime-v2/README.md",
    "docs/history/programs/zuno-target-architecture-migration-v1/README.md",
    "docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-target-architecture-migration-v1/implementation-phases/README.md",
    "docs/history/programs/README.md",
]

FORBIDDEN_PATHS = [
    "agent.md",
    ".agent.md",
    ".agentmd",
    ".agents",
    ".agent/skills",
    ".agent/workflows",
    ".agent/programs/context-memory-agent-runtime-v1",
    ".agent/programs/zuno-target-runtime-v2",
    ".agent/programs/implementation-phases",
    ".agent/programs/evidence",
    ".agent/programs/phase-05-memory-engine.md",
    ".agent/programs/phase-06-capability-tool-retrieval.md",
    ".agent/programs/phase-07-graphrag-llm-entity-extraction.md",
    ".agent/programs/phase-08-langgraph-runtime.md",
    ".agent/programs/phase-09-product-trace-eval-closure.md",
    ".agent/notes",
    ".agent/tmp",
    ".agent/logs",
    ".agent/secrets",
]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing required Agent system path: {relative_path}")

    for relative_path in FORBIDDEN_PATHS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"unexpected retired Agent path exists: {relative_path}")

    gitignore = _read(".gitignore")
    if "apps/web/AGENTS.md" in gitignore:
        errors.append(".gitignore must not ignore apps/web/AGENTS.md")
    if ".agent/local/*" not in gitignore:
        errors.append(".gitignore must ignore .agent/local/*")

    agent_entry = _read("AGENTS.md")
    for phrase in [
        "这是仓库唯一的 Agent 入口",
        "## 任务路由",
        "apps/web/AGENTS.md",
        "src/backend/zuno/AGENTS.md",
        "tools/evals/zuno/AGENTS.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/system.yaml",
        ".agent/programs/",
        "zuno-ideal-architecture-and-repo-layout.html",
        "前台文档默认中文",
    ]:
        if phrase not in agent_entry:
            errors.append(f"AGENTS.md missing routing phrase: {phrase}")

    html = _read(".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html")
    if "<html" not in html.lower() or "</html>" not in html.lower():
        errors.append("target architecture HTML is not valid HTML")
    for phrase in [
        "Target / Proposed",
        "Summary Compression",
        "Structured Extraction",
        "ToolCard",
        "Native BM25",
        "RRF",
        "auto 是 router",
        "Phase 05",
        "Execution Contract",
        "Query Journey",
        "产品入口层",
        "RAG / GraphRAG 层",
    ]:
        if phrase not in html:
            errors.append(f"target architecture HTML missing canonical phrase: {phrase}")

    for relative_path in [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/architecture/README.md",
        ".agent/architecture/near-term/README.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
    ]:
        if "zuno-ideal-architecture-and-repo-layout.html" not in _read(relative_path):
            errors.append(f"{relative_path} missing target architecture HTML reference")

    agent_readme = _read(".agent/README.md")
    for phrase in [
        ".agent/references/",
        ".agent/programs/",
        ".agent/architecture/",
        "本地 Agent Skill System",
        "新写或重写的 Agent 文档默认使用中文",
    ]:
        if phrase not in agent_readme:
            errors.append(f".agent/README.md missing system phrase: {phrase}")

    reference_files = sorted(
        path.name for path in (REPO_ROOT / ".agent/references").iterdir() if path.is_file()
    )
    expected_references = sorted(
        [
            "README.md",
            "current-program.md",
            "docs-map.md",
            "code-map.md",
            "runtime-call-chain.md",
            "verification-map.md",
            "command-catalog.md",
            "known-pitfalls.md",
            "task-routing.md",
            "workflow.md",
        ]
    )
    if reference_files != expected_references:
        errors.append(f".agent/references files are not slim canonical set: {reference_files}")

    active_program_files = sorted(
        path.name for path in (REPO_ROOT / ".agent/programs").iterdir() if path.is_file()
    )
    expected_program_files = sorted(
        [
            "README.md",
            "current.md",
            "implementation-roadmap.md",
            "PHASE01_public-architecture-surface.md",
            "PHASE02_local-agent-skill-system.md",
            "PHASE03_tools-tests-guardrails.md",
            "PHASE04_backend-facade-layers.md",
            "PHASE05_large-file-light-split.md",
            "PHASE06_architecture-diagrams-html.md",
            "closure-checklist.md",
        ]
    )
    if active_program_files != expected_program_files:
        errors.append(f"active program files are not flat canonical set: {active_program_files}")

    roadmap = _read(".agent/programs/implementation-roadmap.md")
    for phrase in [
        "zuno-architecture-surface-cleanup-v1",
        "PHASE01：公开封面与架构叙事收口",
        "PHASE02：本地 Agent Skill System 收口",
        "PHASE03：tools / tests 工作流防回归",
        "PHASE04：后端六层 facade 分层",
        "PHASE05：大文件轻拆",
        "PHASE06：架构图与 HTML 展示页",
        "每次新 program 都从 `PHASE01` 开始编号",
    ]:
        if phrase not in roadmap:
            errors.append(f"active architecture surface roadmap missing phrase: {phrase}")

    phase02 = _read(".agent/programs/PHASE02_local-agent-skill-system.md")
    for phrase in [
        "Zuno Local Agent Skill System",
        "When To Use",
        "Lessons Learned",
    ]:
        if phrase not in phase02:
            errors.append(f"PHASE02 missing local skill system phrase: {phrase}")

    system_yaml = _read(".agent/system.yaml")
    for phrase in [
        "new_program_first_phase: \"PHASE01\"",
        "skill_routes:",
        ".agent/references/workflow.md",
    ]:
        if phrase not in system_yaml:
            errors.append(f".agent/system.yaml missing route phrase: {phrase}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Agent system verification failed.")
        return 1

    print("Agent system verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

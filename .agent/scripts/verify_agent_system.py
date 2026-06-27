from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


REQUIRED_PATHS = [
    "AGENTS.md",
    "apps/web/AGENTS.md",
    "src/backend/zuno/AGENTS.md",
    "tools/evals/zuno/AGENTS.md",
    ".agent/README.md",
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
    ".agent/programs/zuno-target-runtime-v2/README.md",
    ".agent/programs/zuno-target-runtime-v2/implementation-roadmap.md",
    ".agent/programs/zuno-target-runtime-v2/current-phase.md",
    ".agent/programs/zuno-target-runtime-v2/closure-checklist.md",
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
    ".agent/programs/zuno-target-runtime-v2/implementation-phases",
    ".agent/programs/zuno-target-runtime-v2/evidence",
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
        ".agent/programs/zuno-target-runtime-v2/",
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
        "类似 skill 的任务路由",
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
        path.name
        for path in (REPO_ROOT / ".agent/programs/zuno-target-runtime-v2").iterdir()
        if path.is_file()
    )
    expected_program_files = sorted(
        ["README.md", "implementation-roadmap.md", "current-phase.md", "closure-checklist.md"]
    )
    if active_program_files != expected_program_files:
        errors.append(f"active V2 program files are not slim canonical set: {active_program_files}")

    roadmap = _read(".agent/programs/zuno-target-runtime-v2/implementation-roadmap.md")
    for phrase in [
        "Phase 05：记忆引擎",
        "Phase 06：能力与工具检索",
        "Phase 07：知识检索与融合",
        "Phase 08：GeneralAgent LangGraph 运行时",
        "Phase 09：产品边界、Trace 与 Eval 收口",
        "`docs/` 保持精简",
    ]:
        if phrase not in roadmap:
            errors.append(f"active V2 roadmap missing phase execution phrase: {phrase}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Agent system verification failed.")
        return 1

    print("Agent system verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

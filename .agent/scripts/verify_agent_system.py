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
    ".agent/references/code-map.md",
    ".agent/references/runtime-call-chain.md",
    ".agent/references/verification-map.md",
    ".agent/references/docs-map.md",
    ".agent/references/current-program.md",
    ".agent/references/command-catalog.md",
    ".agent/references/known-pitfalls.md",
    ".agent/scripts/verify_module_boundaries.py",
    ".agent/workflows/README.md",
    ".agent/workflows/read-only-audit.md",
    ".agent/workflows/docs-maintenance.md",
    ".agent/workflows/repo-hygiene.md",
    ".agent/workflows/frontend-change.md",
    ".agent/workflows/backend-change.md",
    ".agent/workflows/api-contract-change.md",
    ".agent/workflows/architecture-refactor.md",
    ".agent/workflows/eval-change.md",
    ".agent/workflows/bugfix-root-cause.md",
    ".agent/workflows/task-closure.md",
    ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
    ".agent/architecture/near-term/01-target-runtime-architecture.md",
    ".agent/architecture/near-term/02-context-memory-architecture.md",
    ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
    ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
    ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
    ".agent/programs/zuno-target-runtime-v2/README.md",
    ".agent/programs/zuno-target-runtime-v2/implementation-roadmap.md",
    ".agent/programs/zuno-target-runtime-v2/current-phase.md",
    ".agent/programs/zuno-target-runtime-v2/closure-checklist.md",
    "docs/architecture/history/programs/zuno-target-runtime-v2/README.md",
    "docs/architecture/history/programs/zuno-target-architecture-migration-v1/README.md",
    "docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
    "docs/architecture/history/programs/zuno-target-architecture-migration-v1/implementation-phases/README.md",
    "docs/architecture/history/programs/README.md",
    "docs/architecture/history/programs/context-memory-agent-runtime-v1/README.md",
    ".agent/skills/README.md",
    ".agent/skills/zuno-read-only-audit/SKILL.md",
    ".agent/skills/zuno-docs-maintenance/SKILL.md",
    ".agent/skills/zuno-repo-hygiene/SKILL.md",
    ".agent/skills/zuno-frontend-change/SKILL.md",
    ".agent/skills/zuno-backend-change/SKILL.md",
    ".agent/skills/zuno-api-contract-change/SKILL.md",
    ".agent/skills/zuno-architecture-refactor/SKILL.md",
    ".agent/skills/zuno-eval-change/SKILL.md",
]

FORBIDDEN_PATHS = [
    "agent.md",
    ".agent.md",
    ".agentmd",
    ".agents",
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
            errors.append(f"unexpected legacy Agent path exists: {relative_path}")

    gitignore = _read(".gitignore")
    if "apps/web/AGENTS.md" in gitignore:
        errors.append(".gitignore must not ignore apps/web/AGENTS.md")
    if ".agent/local/*" not in gitignore:
        errors.append(".gitignore must ignore .agent/local/*")

    agent_entry = _read("AGENTS.md")
    for phrase in [
        "## Task Routing",
        "apps/web/AGENTS.md",
        "src/backend/zuno/AGENTS.md",
        "tools/evals/zuno/AGENTS.md",
        ".agent/skills/zuno-docs-maintenance/SKILL.md",
        ".agent/skills/zuno-repo-hygiene/SKILL.md",
        ".agent/programs/zuno-target-runtime-v2/",
        "zuno-ideal-architecture-and-repo-layout.html",
        "01-target-runtime-architecture.md",
    ]:
        if phrase not in agent_entry:
            errors.append(f"AGENTS.md missing routing phrase: {phrase}")

    html = _read(".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html")
    if "<html" not in html.lower() or "</html>" not in html.lower():
        errors.append("target architecture HTML is not valid HTML")
    if not any(marker in html for marker in ["Target", "Proposed", "目标"]):
        errors.append("target architecture HTML missing Target/Proposed marker")
    for phrase in [
        "Summary Compression",
        "Structured Extraction",
        "ToolCard",
        "Native BM25",
        "RRF",
        "auto 是 router",
    ]:
        if phrase not in html:
            errors.append(f"target architecture HTML missing canonical phrase: {phrase}")

    required_html_references = [
        "AGENTS.md",
        ".agent/architecture/near-term/README.md",
        ".agent/workflows/architecture-refactor.md",
        ".agent/workflows/repo-hygiene.md",
        ".agent/skills/zuno-architecture-refactor/SKILL.md",
        ".agent/skills/zuno-repo-hygiene/SKILL.md",
    ]
    for relative_path in required_html_references:
        if "zuno-ideal-architecture-and-repo-layout.html" not in _read(relative_path):
            errors.append(f"{relative_path} missing target architecture HTML reference")

    agent_readme = _read(".agent/README.md")
    for phrase in [
        ".agent/workflows/",
        ".agent/skills/",
        "Temporary discovery -> `.agent/local/notes/`",
        "Implemented, verified, human-facing facts -> `docs/`",
    ]:
        if phrase not in agent_readme:
            errors.append(f".agent/README.md missing system phrase: {phrase}")

    near_term_files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent/architecture/near-term").iterdir()
        if path.is_file()
    )
    expected_near_term = sorted(
        [
            "README.md",
            "zuno-ideal-architecture-and-repo-layout.html",
            "01-target-runtime-architecture.md",
            "02-context-memory-architecture.md",
            "03-capability-tool-retrieval-architecture.md",
            "04-knowledge-graphrag-retrieval-fusion.md",
            "05-repository-boundaries-and-acceptance-gates.md",
        ]
    )
    if near_term_files != expected_near_term:
        errors.append(f"near-term architecture files are not canonical: {near_term_files}")

    reference_files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent/references").iterdir()
        if path.is_file()
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

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Agent system verification failed.")
        return 1

    print("Agent system verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

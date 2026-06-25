from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "AGENTS.md",
    "apps/web/AGENTS.md",
    "src/backend/zuno/AGENTS.md",
    "tools/evals/zuno/AGENTS.md",
    ".agent/README.md",
    ".agent/references/workflow-map.md",
    ".agent/references/skills-map.md",
    ".agent/references/local-state-map.md",
    ".agent/references/frontend-map.md",
    ".agent/references/backend-map.md",
    ".agent/references/api-contract-map.md",
    ".agent/references/runtime-call-chain.md",
    ".agent/references/test-eval-map.md",
    ".agent/references/repo-hygiene-map.md",
    ".agent/references/context-memory-map.md",
    ".agent/references/graphrag-map.md",
    ".agent/references/command-catalog.md",
    ".agent/references/known-pitfalls.md",
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
    ".agent/architecture/near-term/18-context-memory-ideal-architecture.md",
    ".agent/architecture/near-term/19-repository-layout-and-module-boundaries.md",
    ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
    ".agent/programs/zuno-target-architecture-migration-v1/README.md",
    ".agent/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
    ".agent/programs/zuno-target-architecture-migration-v1/implementation-phases/README.md",
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
    ".agent/lessons/README.md",
]

FORBIDDEN_PATHS = [
    "agent.md",
    ".agent.md",
    ".agentmd",
    ".agents",
    ".agent/programs/context-memory-agent-runtime-v1",
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
        "zuno-target-architecture-migration-v1",
        "zuno-ideal-architecture-and-repo-layout.html",
    ]:
        if phrase not in agent_entry:
            errors.append(f"AGENTS.md missing routing phrase: {phrase}")

    html = _read(".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html")
    if "<html" not in html.lower() or "</html>" not in html.lower():
        errors.append("target architecture HTML is not valid HTML")
    if not any(marker in html for marker in ["Target", "Proposed", "目标"]):
        errors.append("target architecture HTML missing Target/Proposed marker")

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
        ".agent/lessons/",
        "Temporary discovery -> `.agent/local/notes/`",
        "Implemented, verified, human-facing facts -> `docs/`",
    ]:
        if phrase not in agent_readme:
            errors.append(f".agent/README.md missing system phrase: {phrase}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Agent system verification failed.")
        return 1

    print("Agent system verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

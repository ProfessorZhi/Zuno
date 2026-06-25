from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_IGNORES = [
    ".local/",
    ".codex/",
    "node_modules/",
    "apps/web/node_modules/",
    "apps/web/dist/",
    "data/evals/multihop/raw/",
    "reports/evals/multihop/real_runtime/",
    ".agent/local/*",
]

FORBIDDEN_IGNORE_LINES = [
    "apps/web/AGENTS.md",
    "src/frontend/node_modules",
    "src/frontend/dist",
    "$null",
    "&1",
]

BLOCKED_LEGACY_PATHS = [
    "domain-packs",
    "tests/compat",
    "src/backend/zuno/services/domain_pack",
    "src/backend/zuno/core/graphs/domain_qa_graph.py",
    "src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py",
]

FORBIDDEN_CURRENT_PATHS = [
    "src/frontend",
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _tracked_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return proc.stdout.splitlines()


def main() -> int:
    errors: list[str] = []
    gitignore = _read(".gitignore")
    dockerignore = _read(".dockerignore")

    for entry in REQUIRED_IGNORES:
        if entry not in gitignore:
            errors.append(f".gitignore missing required ignore: {entry}")

    for line in FORBIDDEN_IGNORE_LINES:
        if line in gitignore or line in dockerignore:
            errors.append(f"ignore files contain retired or wrong entry: {line}")

    for path in BLOCKED_LEGACY_PATHS:
        if not (REPO_ROOT / path).exists():
            errors.append(f"Blocked Legacy path missing without Phase 11 proof: {path}")

    repo_hygiene_map = _read(".agent/references/repo-hygiene-map.md")
    if "must not be treated as target repository layout" not in repo_hygiene_map:
        errors.append("repo hygiene map must keep Domain Pack out of target layout")

    backend_router = _read("src/backend/zuno/api/router.py")
    backend_v1_init = _read("src/backend/zuno/api/v1/__init__.py")
    if "domain_packs" in backend_router or "router.include_router(domain_packs.router)" in backend_router:
        errors.append("Domain Pack router must not be mounted on the current FastAPI router")
    if "domain_packs" in backend_v1_init:
        errors.append("Domain Pack module must not be exported from the current API v1 front path")

    frontend_active_paths = [
        "apps/web/src/router/index.ts",
        "apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue",
        "apps/web/src/pages/knowledge/knowledge.vue",
        "apps/web/src/pages/knowledge/knowledge-create.vue",
        "apps/web/src/pages/knowledge/knowledge-settings.vue",
    ]
    forbidden_frontend_phrases = [
        "workspaceSettingsKnowledgeDomainPacks",
        "workspaceSettingsKnowledgeDomainPackCreate",
        "workspaceSettingsKnowledgeDomainPackDetail",
        "knowledge-domain-packs",
        "settings/knowledge/domain-packs",
        "/knowledge/domain-packs",
        "KnowledgeDomainPacks",
        "KnowledgeDomainPackCreate",
        "KnowledgeDomainPackDetail",
        "getDomainPacksAPI",
        "openDomainPacks",
        "openDomainPackBuilder",
    ]
    for relative_path in frontend_active_paths:
        content = _read(relative_path)
        for phrase in forbidden_frontend_phrases:
            if phrase in content:
                errors.append(f"{relative_path} still exposes active Domain Pack frontend phrase: {phrase}")

    workspace_agent = _read("src/backend/zuno/services/workspace/simple_agent.py")
    if "from zuno.core.runtime.agent_runtime import AgentRuntime" in workspace_agent:
        errors.append("Workspace knowledge path must not import AgentRuntime")
    if "domain_qa_runtime" in workspace_agent:
        errors.append("Workspace knowledge path must not expose domain_qa_runtime")
    if "_run_domain_pack_query" in workspace_agent:
        errors.append("Workspace knowledge path must not call _run_domain_pack_query")
    if "KnowledgeQueryService" not in workspace_agent:
        errors.append("Workspace knowledge path must use KnowledgeQueryService")

    html_matches = [
        path
        for path in _tracked_files()
        if path.replace("\\", "/").endswith("zuno-ideal-architecture-and-repo-layout.html")
    ]
    if html_matches != [".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html"]:
        errors.append("canonical target architecture HTML must be the only tracked copy")

    for path in FORBIDDEN_CURRENT_PATHS:
        if (REPO_ROOT / path).exists():
            errors.append(f"retired current path exists: {path}")

    tracked = set(_tracked_files())
    forbidden_tracked_prefixes = [
        "node_modules/",
        "apps/web/node_modules/",
        "apps/web/dist/",
        ".local/",
        ".codex/",
        "data/evals/multihop/raw/",
        "reports/evals/multihop/real_runtime/",
    ]
    for tracked_path in tracked:
        normalized = tracked_path.replace("\\", "/")
        for prefix in forbidden_tracked_prefixes:
            if normalized.startswith(prefix):
                errors.append(f"generated/local path is tracked: {normalized}")
                break

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Repo hygiene verification failed.")
        return 1

    print("Repo hygiene verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

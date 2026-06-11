from __future__ import annotations

import subprocess
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

GROUP_RULES: list[tuple[str, tuple[str, ...]]] = [
    (
        "docs_and_readme",
        (
            "README.md",
            "docs/",
        ),
    ),
    (
        "infra_and_launch",
        (
            "infra/docker/",
            "tools/scripts/start.py",
            "tools/scripts/rebuild_rag_indexes.py",
            "tools/migrations/",
        ),
    ),
    (
        "backend_domain_runtime",
        (
            "src/backend/agentchat/core/",
            "src/backend/agentchat/domain_packs/",
            "src/backend/agentchat/services/domain_pack/",
            "src/backend/agentchat/services/runtime_registry.py",
            "src/backend/agentchat/services/workspace/simple_agent.py",
            "src/backend/agentchat/services/embedding/",
            "src/backend/agentchat/services/llm/",
            "src/backend/agentchat/evals/contract_review_eval/",
        ),
    ),
    (
        "backend_rag_graphrag_eval",
        (
            "src/backend/agentchat/evals/rag_eval/",
            "src/backend/agentchat/services/graphrag/",
            "src/backend/agentchat/services/pipeline/manager.py",
            "src/backend/agentchat/services/retrieval/",
            "src/backend/agentchat/services/rag/",
        ),
    ),
    (
        "backend_public_entrypoints",
        (
            "src/backend/agentchat/main.py",
            "src/backend/agentchat/settings.py",
            "src/backend/agentchat/api/",
            "src/backend/agentchat/database/",
            "src/backend/agentchat/schema/",
            "src/backend/agentchat/tools/",
            "src/backend/agentchat/config/",
            "src/backend/zuno/",
        ),
    ),
    (
        "frontend_workspace",
        (
            "src/frontend/",
            "package.json",
        ),
    ),
    (
        "tests_and_release_guards",
        (
            ".gitignore",
            "tests/",
            "src/backend/agentchat/test/",
            "tools/scripts/audit_public_release.py",
            "tools/scripts/preview_public_release_group.py",
            "tools/scripts/preview_public_release_stage_dry_run.py",
            "tools/scripts/print_public_release_commit_order.py",
            "tools/scripts/print_public_release_stage_commands.py",
            "tools/scripts/summarize_public_release_scope.py",
            "tools/scripts/verify_docs_and_readme_ready.py",
        ),
    ),
]

EXCLUDED_LOCAL_PREFIXES = [
    "docs/superpowers/",
    "src/frontend/AGENTS.md",
]


def _git_status_paths() -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            proc.stderr.strip() or proc.stdout.strip() or "git status --short failed"
        )

    paths: list[str] = []
    for raw_line in proc.stdout.splitlines():
        if len(raw_line) < 4:
            continue
        paths.append(raw_line[3:].replace("\\", "/"))
    return paths


def _classify(path: str) -> str:
    if any(path == prefix or path.startswith(prefix) for prefix in EXCLUDED_LOCAL_PREFIXES):
        return "excluded_local_only"
    for group_name, prefixes in GROUP_RULES:
        if any(path == prefix or path.startswith(prefix) for prefix in prefixes):
            return group_name
    return "manual_review"


def main() -> int:
    paths = _git_status_paths()
    grouped: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        grouped[_classify(path)].append(path)

    total = sum(len(items) for items in grouped.values())
    print(f"Changed paths: {total}")
    for group_name, _ in GROUP_RULES:
        items = grouped.get(group_name)
        if not items:
            continue
        print(f"\n[{group_name}] ({len(items)})")
        for item in sorted(items):
            print(f"  - {item}")

    excluded = grouped.get("excluded_local_only", [])
    print(f"\n[excluded_local_only] ({len(excluded)})")
    for item in sorted(excluded):
        print(f"  - {item}")

    manual = grouped.get("manual_review", [])
    print(f"\n[manual_review] ({len(manual)})")
    for item in sorted(manual):
        print(f"  - {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import subprocess
import sys
from collections import defaultdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_AND_README_READY_NOTE = "docs/development/docs-and-readme-ready.md"

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
            "src/backend/zuno/core/",
            "src/backend/zuno/services/domain_pack/",
            "src/backend/zuno/services/runtime_registry.py",
            "src/backend/zuno/services/workspace/simple_agent.py",
            "src/backend/zuno/services/embedding/",
            "src/backend/zuno/services/llm/",
            "tools/evals/zuno/contract_review_eval/",
        ),
    ),
    (
        "backend_rag_graphrag_eval",
        (
            "tools/evals/zuno/rag_eval/",
            "src/backend/zuno/services/graphrag/",
            "src/backend/zuno/services/pipeline/manager.py",
            "src/backend/zuno/services/retrieval/",
            "src/backend/zuno/services/rag/",
        ),
    ),
    (
        "backend_public_entrypoints",
        (
            "src/backend/zuno/main.py",
            "src/backend/zuno/settings.py",
            "src/backend/zuno/api/",
            "src/backend/zuno/database/",
            "src/backend/zuno/schema/",
            "src/backend/zuno/tools/",
            "src/backend/zuno/config/",
            "src/backend/zuno/",
        ),
    ),
    (
        "frontend_workspace",
        (
            "apps/web/",
            "package.json",
        ),
    ),
    (
        "tests_and_release_guards",
        (
            ".gitignore",
            "tests/",
            "tests/compat/",
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
    "apps/web/AGENTS.md",
]


def _group_prefixes(group_name: str) -> tuple[str, ...]:
    if group_name == "excluded_local_only":
        return tuple(EXCLUDED_LOCAL_PREFIXES)
    for candidate, prefixes in GROUP_RULES:
        if candidate == group_name:
            return prefixes
    return ()


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


def _print_group_stat(group_name: str) -> int:
    prefixes = _group_prefixes(group_name)
    if not prefixes:
        print(f"[{group_name}] has no direct diff-stat preview rule.")
        return 0

    proc = subprocess.run(
        ["git", "diff", "--stat", "--", *prefixes],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr.strip() or proc.stdout.strip() or "git diff --stat failed")
        return 1

    output = proc.stdout.strip()
    if not output:
        print(f"[{group_name}] has no current diff stat.")
        return 0

    print(output)
    return 0


def main() -> int:
    args = list(sys.argv[1:])
    show_stat = False
    if "--stat" in args:
        show_stat = True
        args.remove("--stat")

    requested_group = args[0] if args else "docs_and_readme"
    valid_groups = {group_name for group_name, _ in GROUP_RULES} | {
        "excluded_local_only",
        "manual_review",
    }

    if requested_group not in valid_groups:
        print(f"Unknown group: {requested_group}")
        print("Valid groups:")
        for group_name in sorted(valid_groups):
            print(f"  - {group_name}")
        return 1

    grouped: dict[str, list[str]] = defaultdict(list)
    for path in _git_status_paths():
        grouped[_classify(path)].append(path)

    items = sorted(grouped.get(requested_group, []))
    print(f"[{requested_group}] ({len(items)})")
    for item in items:
        print(f"  - {item}")
    if requested_group == "docs_and_readme":
        print(f"\n[ready_note]\n  see {DOCS_AND_README_READY_NOTE}")
    if show_stat:
        print("\n[diff_stat]")
        return _print_group_stat(requested_group)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import subprocess
import sys


GROUP_PATHS = {
    "docs_and_readme": ["README.md", "docs/"],
    "tests_and_release_guards": [
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
    ],
    "infra_and_launch": [
        "infra/docker/",
        "tools/migrations/",
        "tools/scripts/start.py",
        "tools/scripts/rebuild_rag_indexes.py",
    ],
    "backend_domain_runtime": [
        "src/backend/zuno/legacy/agentchat/core/",
        "src/backend/zuno/legacy/agentchat/domain_packs/",
        "src/backend/zuno/legacy/agentchat/services/domain_pack/",
        "src/backend/zuno/legacy/agentchat/services/runtime_registry.py",
        "src/backend/zuno/legacy/agentchat/services/workspace/simple_agent.py",
        "src/backend/zuno/legacy/agentchat/services/embedding/",
        "src/backend/zuno/legacy/agentchat/services/llm/",
        "tools/evals/zuno/contract_review_eval/",
    ],
    "backend_rag_graphrag_eval": [
        "tools/evals/zuno/rag_eval/",
        "src/backend/zuno/legacy/agentchat/services/graphrag/",
        "src/backend/zuno/legacy/agentchat/services/pipeline/manager.py",
        "src/backend/zuno/legacy/agentchat/services/retrieval/",
        "src/backend/zuno/legacy/agentchat/services/rag/",
    ],
    "backend_public_entrypoints": [
        "src/backend/zuno/legacy/agentchat/main.py",
        "src/backend/zuno/legacy/agentchat/settings.py",
        "src/backend/zuno/legacy/agentchat/api/",
        "src/backend/zuno/legacy/agentchat/database/",
        "src/backend/zuno/legacy/agentchat/schema/",
        "src/backend/zuno/legacy/agentchat/tools/",
        "src/backend/zuno/legacy/agentchat/config/",
        "src/backend/zuno/",
    ],
    "frontend_workspace": [
        "package.json",
        "apps/web/",
    ],
}


def main() -> int:
    requested_group = sys.argv[1] if len(sys.argv) > 1 else "docs_and_readme"
    if requested_group not in GROUP_PATHS:
        print(f"Unknown group: {requested_group}")
        print("Valid groups:")
        for group_name in sorted(GROUP_PATHS):
            print(f"  - {group_name}")
        return 1

    proc = subprocess.run(
        ["git", "status", "--short", "--", *GROUP_PATHS[requested_group]],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr.strip() or proc.stdout.strip() or "git status --short failed")
        return 1

    changed = [line.rstrip() for line in proc.stdout.splitlines() if line.strip()]
    print(f"[{requested_group}] stage_dry_run ({len(changed)})")
    for item in changed:
        print(f"  - {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

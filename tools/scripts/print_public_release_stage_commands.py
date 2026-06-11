from __future__ import annotations


STAGE_GROUPS = [
    (
        "docs_and_readme",
        [
            "git add README.md docs/",
        ],
    ),
    (
        "tests_and_release_guards",
        [
            "git add .gitignore tests/ src/backend/agentchat/test/",
            "git add tools/scripts/audit_public_release.py tools/scripts/print_public_release_commit_order.py tools/scripts/print_public_release_stage_commands.py tools/scripts/summarize_public_release_scope.py",
        ],
    ),
    (
        "infra_and_launch",
        [
            "git add infra/docker/ tools/migrations/ tools/scripts/start.py tools/scripts/rebuild_rag_indexes.py",
        ],
    ),
    (
        "backend_domain_runtime",
        [
            "git add src/backend/zuno/legacy/agentchat/core/ src/backend/zuno/legacy/agentchat/domain_packs/ src/backend/zuno/legacy/agentchat/services/domain_pack/ src/backend/zuno/legacy/agentchat/services/runtime_registry.py src/backend/zuno/legacy/agentchat/services/workspace/simple_agent.py src/backend/zuno/legacy/agentchat/services/embedding/ src/backend/zuno/legacy/agentchat/services/llm/ src/backend/agentchat/evals/contract_review_eval/",
        ],
    ),
    (
        "backend_rag_graphrag_eval",
        [
            "git add src/backend/agentchat/evals/rag_eval/ src/backend/zuno/legacy/agentchat/services/graphrag/ src/backend/zuno/legacy/agentchat/services/pipeline/manager.py src/backend/zuno/legacy/agentchat/services/retrieval/ src/backend/zuno/legacy/agentchat/services/rag/",
        ],
    ),
    (
        "backend_public_entrypoints",
        [
            "git add src/backend/zuno/legacy/agentchat/main.py src/backend/zuno/legacy/agentchat/settings.py src/backend/zuno/legacy/agentchat/api/ src/backend/zuno/legacy/agentchat/database/ src/backend/zuno/legacy/agentchat/schema/ src/backend/zuno/legacy/agentchat/tools/ src/backend/zuno/legacy/agentchat/config/ src/backend/zuno/",
        ],
    ),
    (
        "frontend_workspace",
        [
            "git add package.json src/frontend/src/pages/workspace/ src/frontend/src/router/index.ts src/frontend/src/utils/settings-preferences.ts",
        ],
    ),
]

EXCLUDED_LOCAL_ONLY = [
    "docs/superpowers/",
    "src/frontend/AGENTS.md",
]


def main() -> int:
    print("Suggested staging commands by public release group:\n")
    for index, (group_name, commands) in enumerate(STAGE_GROUPS, start=1):
        print(f"{index}. {group_name}")
        for command in commands:
            print(f"   {command}")
        print()

    print("Do not stage these local-only paths:")
    for path in EXCLUDED_LOCAL_ONLY:
        print(f"  - {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

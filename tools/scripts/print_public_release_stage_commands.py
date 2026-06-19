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
            "git add .gitignore tests/compat/ tests/",
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
            "git add src/backend/zuno/core/ src/backend/zuno/domain_packs/ src/backend/zuno/services/domain_pack/ src/backend/zuno/services/runtime_registry.py src/backend/zuno/services/workspace/simple_agent.py src/backend/zuno/services/embedding/ src/backend/zuno/services/llm/ tools/evals/zuno/contract_review_eval/",
        ],
    ),
    (
        "backend_rag_graphrag_eval",
        [
            "git add tools/evals/zuno/rag_eval/ src/backend/zuno/services/graphrag/ src/backend/zuno/services/pipeline/manager.py src/backend/zuno/services/retrieval/ src/backend/zuno/services/rag/",
        ],
    ),
    (
        "backend_public_entrypoints",
        [
            "git add src/backend/zuno/main.py src/backend/zuno/settings.py src/backend/zuno/api/ src/backend/zuno/database/ src/backend/zuno/schema/ src/backend/zuno/tools/ src/backend/zuno/config/ src/backend/zuno/",
        ],
    ),
    (
        "frontend_workspace",
        [
            "git add package.json apps/web/src/pages/workspace/ apps/web/src/router/index.ts apps/web/src/utils/settings-preferences.ts",
        ],
    ),
]

EXCLUDED_LOCAL_ONLY = [
    "docs/superpowers/",
    "apps/web/AGENTS.md",
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

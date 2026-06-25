from __future__ import annotations


COMMIT_GROUPS = [
    (
        "docs_and_readme",
        "Public-facing docs, README, architecture and demo narrative.",
        "Do not mix with backend runtime refactors unless the docs would otherwise become false.",
    ),
    (
        "tests_and_release_guards",
        "Publish-boundary tests, runtime guards, release audit scripts, and .gitignore boundary updates.",
        "Can be merged with docs only if the diff stays small; otherwise keep as a separate guardrail commit.",
    ),
    (
        "infra_and_launch",
        "Docker defaults, rebuild/start scripts, and reproducible local launch changes.",
        "Keep separate from frontend polish and GraphRAG internals so infra rollback stays easy.",
    ),
    (
        "retired_runtime_legacy",
        "Deleted or retired legacy runtime source, routes, graph modules, and package assets.",
        "Keep separate from current runtime behavior so reviewers can confirm the absence boundary.",
    ),
    (
        "backend_domain_runtime",
        "Current Agent, LangGraph, workspace-agent, embedding, LLM, and contract-review runtime convergence.",
        "Do not mix with broad zuno rename commits if runtime behavior and rename-only work can be reviewed separately.",
    ),
    (
        "backend_rag_graphrag_eval",
        "Local embedding/rerank eval harness, GraphRAG retrieval, compare matrix, datasets, and evaluation support.",
        "This is the heaviest technical group; keep it isolated from docs-only or frontend-only commits.",
    ),
    (
        "backend_public_entrypoints",
        "zuno to zuno public runtime surface, API, DAO, schema, config, and startup convergence.",
        "Keep separate from evaluation-heavy GraphRAG commits when possible because review intent is different.",
    ),
    (
        "frontend_workspace",
        "Workspace UI, routing, component, and styling changes.",
        "Do not mix with backend runtime or publish-boundary commits.",
    ),
]

EXCLUDED_LOCAL_ONLY = [
    "docs/superpowers/",
    "apps/web/AGENTS.md",
]


def main() -> int:
    print("Recommended public release commit order:\n")
    for index, (group, summary, boundary) in enumerate(COMMIT_GROUPS, start=1):
        print(f"{index}. {group}")
        print(f"   Summary: {summary}")
        print(f"   Boundary: {boundary}\n")

    print("Excluded local-only content:")
    for path in EXCLUDED_LOCAL_ONLY:
        print(f"  - {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

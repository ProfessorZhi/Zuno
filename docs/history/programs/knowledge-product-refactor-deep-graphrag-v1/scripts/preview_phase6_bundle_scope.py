from __future__ import annotations

import subprocess
import sys
from collections import OrderedDict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PHASE6_BUNDLE_GROUPS: "OrderedDict[str, list[str]]" = OrderedDict(
    [
        (
            "docs_and_contract",
            [
                "docs/history/plans/current-phase-audit.md",
                "docs/history/plans/zuno-refactor-execution-plan.md",
                "tools/evals/zuno/rag_eval/README.md",
            ],
        ),
        (
            "logical_phase6_delta",
            [
                "tools/evals/zuno/rag_eval/run_local_embedding_eval.py",
                "tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py",
                "tools/evals/zuno/rag_eval/generate_contract_review_scale_corpus.py",
                "tests/test_rag_eval_local_launcher.py",
                "tests/test_stackless_compare_matrix.py",
            ],
        ),
        (
            "eval_entrypoints",
            [
                "tools/evals/zuno/rag_eval/run_stackless_local_eval.py",
                "tools/evals/zuno/rag_eval/summarize_eval_profiles.py",
                "tools/evals/zuno/rag_eval/local_embedding_server.py",
                "tools/evals/zuno/rag_eval/local_rerank_server.py",
            ],
        ),
        (
            "runtime_foundations",
            [
                "src/backend/zuno/services/runtime_registry.py",
                "src/backend/zuno/services/graphrag/extractors/",
                "src/backend/zuno/services/graphrag/retrievers/",
                "src/backend/zuno/core/graphs/",
                "src/backend/zuno/core/runtime/",
            ],
        ),
        (
            "verification_tests",
            [
                "tests/test_rag_eval_local_scheme.py",
                "tests/test_contract_eval_runner.py",
                "tests/test_contract_graph_query_routing.py",
                "tests/test_contract_graph_retriever.py",
                "tests/test_phase11c_agent_runtime_retirement.py",
                "tests/test_phase11c_graph_public_export_retirement.py",
                "tests/test_domain_pack_runtime_flow.py",
                "tests/test_general_agent_domain_pack_runtime.py",
                "tests/test_graph_retriever_local_runtime.py",
                "tests/test_local_embedding_server.py",
                "tests/test_local_rerank_server.py",
                "tests/test_local_runtime_registry.py",
                "tests/test_stackless_local_eval_contract_domain_pack.py",
                "tests/test_stackless_local_eval_manifest_filter.py",
                "tests/test_stackless_local_eval_rerank_runtime.py",
                "tests/test_completion_domain_pack_runtime.py",
                "tests/test_workspace_domain_pack_runtime.py",
                "tests/test_zuno_alias_imports.py",
            ],
        ),
        (
            "phase6_node_ops",
            [
                "docs/history/plans/README.md",
                "docs/history/plans/phase6-bundle-prestage.md",
                "docs/history/plans/phase6-bundle-ready.md",
                "tools/scripts/preview_phase6_bundle_scope.py",
                "tools/scripts/verify_phase6_bundle_ready.py",
                "tests/test_phase6_bundle_scope.py",
            ],
        ),
    ]
)

GROUP_DESCRIPTIONS = {
    "docs_and_contract": "docs and architecture-plan sync that explain the Phase 6 closure claim",
    "logical_phase6_delta": "the smallest direct code/test delta that carries the newly proven Phase 6 behavior",
    "eval_entrypoints": "stackless/local-eval helpers that the logical delta still imports on the current branch tip",
    "runtime_foundations": "domain/runtime foundations required when the branch base does not already contain Phase 1-5 foundations",
    "verification_tests": "associated tests that prove the bundled runtime still works as one GitHub node",
    "phase6_node_ops": "the local scripts/tests/docs that operationalize this Phase 6 node as a repeatable staging contract",
}

PHASE6_BUNDLE_PATHS = [
    path
    for group_paths in PHASE6_BUNDLE_GROUPS.values()
    for path in group_paths
]


def _run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _all_groups() -> list[str]:
    return list(PHASE6_BUNDLE_GROUPS)


def _paths_for_group(group_name: str | None) -> list[str]:
    if group_name is None:
        return PHASE6_BUNDLE_PATHS
    return PHASE6_BUNDLE_GROUPS[group_name]


def _print_groups() -> int:
    print("[phase6_bundle_groups]")
    for group_name, paths in PHASE6_BUNDLE_GROUPS.items():
        description = GROUP_DESCRIPTIONS[group_name]
        print(f"  - {group_name} ({len(paths)}): {description}")
    return 0


def _changed_entries(group_name: str | None) -> list[str]:
    scope = _paths_for_group(group_name)
    proc = _run_git(["status", "--short", "--", *scope])
    if proc.returncode != 0:
        raise RuntimeError(
            proc.stderr.strip() or proc.stdout.strip() or "git status --short failed"
        )
    return [line.rstrip() for line in proc.stdout.splitlines() if line.strip()]


def _print_paths(group_name: str | None) -> int:
    title = group_name or "all"
    print(f"[phase6_bundle_paths:{title}]")
    for path in _paths_for_group(group_name):
        print(f"  - {path}")
    return 0


def _print_status(group_name: str | None) -> int:
    try:
        changed = _changed_entries(group_name)
    except RuntimeError as exc:
        print(str(exc))
        return 1
    title = group_name or "all"
    print(f"[phase6_bundle_scope:{title}] ({len(changed)})")
    for item in changed:
        print(f"  - {item}")
    return 0


def _print_stat(group_name: str | None) -> int:
    scope = _paths_for_group(group_name)
    proc = _run_git(["diff", "--stat", "--", *scope])
    if proc.returncode != 0:
        print(proc.stderr.strip() or proc.stdout.strip() or "git diff --stat failed")
        return 1
    title = group_name or "all"
    print(proc.stdout.strip() or f"[phase6_bundle_scope:{title}] no current diff stat")
    return 0


def _print_stage_command(group_name: str | None) -> int:
    scope = _paths_for_group(group_name)
    title = group_name or "all"
    print(f"[phase6_bundle_stage_command:{title}]")
    print("git add " + " ".join(scope))
    return 0


def _print_summary() -> int:
    print("[phase6_bundle_summary]")
    total_changed = 0
    for group_name in PHASE6_BUNDLE_GROUPS:
        changed = _changed_entries(group_name)
        total_changed += len(changed)
        description = GROUP_DESCRIPTIONS[group_name]
        print(f"  - {group_name}: {len(changed)} changed")
        print(f"    {description}")
    print(f"[phase6_bundle_total_changed] {total_changed}")
    print("[recommended_sequence]")
    print("  - review docs_and_contract first to keep the closure claim honest")
    print("  - then confirm logical_phase6_delta matches the direct Phase 6 behavior change")
    print("  - if branch base lacks earlier foundations, include eval_entrypoints and runtime_foundations together")
    print("  - keep verification_tests with the final bundled node, not as a separate proof story")
    print("  - keep phase6_node_ops with the same node so the staging contract stays reproducible")
    return 0


def _print_dry_run() -> int:
    print("[phase6_bundle_dry_run]")
    for group_name in PHASE6_BUNDLE_GROUPS:
        changed = _changed_entries(group_name)
        print(f"  - {group_name} ({len(changed)})")
        for item in changed:
            print(f"    {item}")
    print("[phase6_bundle_stage_command:all]")
    print("git add " + " ".join(PHASE6_BUNDLE_PATHS))
    return 0


def _parse_args(argv: list[str]) -> tuple[str | None, str]:
    args = list(argv)
    action = "status"
    group_name: str | None = None

    if "--groups" in args:
        action = "groups"
        args.remove("--groups")
    if "--paths" in args:
        action = "paths"
        args.remove("--paths")
    if "--summary" in args:
        action = "summary"
        args.remove("--summary")
    if "--dry-run" in args:
        action = "dry_run"
        args.remove("--dry-run")
    if "--stat" in args:
        action = "stat"
        args.remove("--stat")
    if "--stage-command" in args:
        action = "stage_command"
        args.remove("--stage-command")

    if "--group" in args:
        index = args.index("--group")
        try:
            group_name = args[index + 1]
        except IndexError:
            raise SystemExit("Missing group name after --group")
        del args[index : index + 2]
    elif args:
        group_name = args[0]
        del args[0]

    if args:
        raise SystemExit(f"Unexpected arguments: {' '.join(args)}")

    if group_name is not None and group_name not in PHASE6_BUNDLE_GROUPS:
        valid = ", ".join(_all_groups())
        raise SystemExit(f"Unknown Phase 6 bundle group: {group_name}. Valid groups: {valid}")

    return group_name, action


def main() -> int:
    try:
        group_name, action = _parse_args(sys.argv[1:])
    except SystemExit as exc:
        print(str(exc))
        return 1

    if action == "groups":
        return _print_groups()
    if action == "paths":
        return _print_paths(group_name)
    if action == "summary":
        return _print_summary()
    if action == "dry_run":
        return _print_dry_run()
    if action == "stat":
        return _print_stat(group_name)
    if action == "stage_command":
        return _print_stage_command(group_name)
    return _print_status(group_name)


if __name__ == "__main__":
    raise SystemExit(main())

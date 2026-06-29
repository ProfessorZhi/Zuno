from __future__ import annotations

import runpy
import shlex
import subprocess
from fnmatch import fnmatch
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_IGNORES = [
    ".local/",
    ".codex/",
    "node_modules/",
    "apps/desktop/node_modules/",
    "apps/web/node_modules/",
    "apps/web/dist/",
    ".pytest_cache/",
    ".test-tmp/",
    "tmp/",
    "output/",
    "data/evals/multihop/raw/",
    "data/evals/multihop/normalized/",
    "data/evals/multihop/corpus/",
    "data/evals/multihop/ingested/",
    "data/evals/multihop/**/*.zip",
    "data/evals/multihop/**/*.json",
    "data/evals/multihop/**/*.jsonl",
    "reports/evals/multihop/stackless_ingestion_smoke.json",
    "reports/evals/multihop/stackless_ingestion_smoke_*.json",
    "reports/evals/multihop/real_runtime/",
    ".agent/local/*",
]

FORBIDDEN_BROAD_IGNORE_LINES = [
    "data/",
    "/data/",
    "reports/",
    "/reports/",
]

FORBIDDEN_TRACKED_PREFIXES = [
    "node_modules/",
    "apps/desktop/node_modules/",
    "apps/web/node_modules/",
    "apps/web/dist/",
    ".local/",
    ".codex/",
    ".pytest_cache/",
    ".test-tmp/",
    "tmp/",
    "output/",
    "data/evals/multihop/raw/",
    "data/evals/multihop/normalized/",
    "data/evals/multihop/corpus/",
    "data/evals/multihop/ingested/",
    "reports/evals/multihop/real_runtime/",
]

FORBIDDEN_TRACKED_PATTERNS = [
    "data/evals/multihop/**/*.zip",
    "data/evals/multihop/**/*.json",
    "data/evals/multihop/**/*.jsonl",
    "reports/evals/multihop/stackless_ingestion_smoke.json",
    "reports/evals/multihop/stackless_ingestion_smoke_*.json",
]

FORBIDDEN_ROOT_ARTIFACT_PATTERNS = [
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.bmp",
    "*.pdf",
    "*.pid",
    "*screenshot*",
    "*preview*",
]

TRACKED_DATA_REPORTS_ALLOWLIST = [
    "data/evals/multihop/README.md",
    "reports/README.md",
]

FORBIDDEN_IGNORE_LINES = [
    "apps/web/AGENTS.md",
    "src/frontend/node_modules",
    "src/frontend/dist",
    "$null",
    "&1",
]

BLOCKED_LEGACY_PATHS = []

FORBIDDEN_CURRENT_PATHS = [
    "src/frontend",
    ".agent/skills",
    ".agent/workflows",
    "docs/architecture/history",
    "docs/architecture/audits",
    "docs/architecture/specs",
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
    "docs/development",
    "docs/prototypes",
    "docs/ui-review",
    "docs/ui-gallery",
    ".agent/programs/official-graphrag-cleanup-v1",
    "domain-packs",
    "tests/compat",
    "docs/development/history",
    "docs/reference/history",
]

RETIRED_FRONTEND_DOMAIN_PACK_FILES = [
    "apps/web/src/apis/domain-packs.ts",
    "apps/web/src/pages/knowledge/domain-pack-list.vue",
    "apps/web/src/pages/knowledge/domain-pack-create.vue",
    "apps/web/src/pages/knowledge/domain-pack-detail.vue",
]

RETIRED_DOMAIN_PACK_API_WRAPPERS = [
    "src/backend/zuno/api/v1/domain_packs.py",
    "src/backend/zuno/api/services/domain_pack.py",
]

REQUIRED_CONTRACT_REVIEW_HISTORY_ASSETS = [
    "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml",
    "docs/history/domain-packs/root-contract-review/contract_review/schema.json",
    "docs/history/domain-packs/root-contract-review/contract_review/retrieval_policy.yaml",
    "docs/history/domain-packs/root-contract-review/contract_review/extraction_prompt.md",
    "docs/history/domain-packs/root-contract-review/contract_review/answer_template.md",
    "docs/history/domain-packs/root-contract-review/contract_review/report_template.md",
    "docs/history/domain-packs/root-contract-review/contract_review/eval_dataset.jsonl",
]

REQUIRED_RETIRED_UI_SCRIPT_ARCHIVES = [
    "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/capture_knowledge_product_ui_gallery.py",
    "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/check_knowledge_product_responsive.py",
    "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/check_settings_navigation_interaction.py",
]

REQUIRED_PHASE6_BUNDLE_HELPER_ARCHIVES = [
    "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/preview_phase6_bundle_scope.py",
    "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/verify_phase6_bundle_ready.py",
]

RETIRED_PHASE6_BUNDLE_ACTIVE_TOOLS = [
    "tools/scripts/preview_phase6_bundle_scope.py",
    "tools/scripts/verify_phase6_bundle_ready.py",
]

REQUIRED_ARCHIVED_MIGRATION_SPECS = [
    "docs/history/specs/deep-graphrag-v1-runtime.md",
    "docs/history/specs/domain-pack-langgraph-graphrag-architecture.md",
    "docs/history/specs/domain-pack-builder.md",
    "docs/history/specs/knowledge-product-boundary.md",
]

RETIRED_ACTIVE_MIGRATION_SPECS = [
    "docs/architecture/specs/deep-graphrag-v1-runtime.md",
    "docs/architecture/specs/domain-pack-langgraph-graphrag-architecture.md",
    "docs/architecture/specs/domain-pack-builder.md",
    "docs/architecture/specs/knowledge-product-boundary.md",
]

REQUIRED_ARCHIVED_DECISIONS = [
    "docs/history/decisions/0001-domain-pack-binding.md",
]

RETIRED_ACTIVE_DECISIONS = [
    "docs/architecture/decisions/0001-domain-pack-binding.md",
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

    for path in sorted(REPO_ROOT.iterdir()):
        if not path.is_file():
            continue
        for pattern in FORBIDDEN_ROOT_ARTIFACT_PATTERNS:
            if fnmatch(path.name.lower(), pattern):
                errors.append(
                    "repository root must stay clean; move temporary artifacts to "
                    f".local/, tmp/, or formal docs assets: {path.name}"
                )
                break

    for entry in REQUIRED_IGNORES:
        if entry not in gitignore:
            errors.append(f".gitignore missing required ignore: {entry}")

    gitignore_lines = {line.strip() for line in gitignore.splitlines() if line.strip()}
    for line in FORBIDDEN_BROAD_IGNORE_LINES:
        if line in gitignore_lines:
            errors.append(
                "data/ and reports/ must use whitelist semantics, not broad ignore lines: "
                f"{line}"
            )

    for line in FORBIDDEN_IGNORE_LINES:
        if line in gitignore or line in dockerignore:
            errors.append(f"ignore files contain retired or wrong entry: {line}")

    for path in BLOCKED_LEGACY_PATHS:
        if not (REPO_ROOT / path).exists():
            errors.append(f"Blocked Legacy path missing without Phase 11 proof: {path}")

    for relative_path in REQUIRED_CONTRACT_REVIEW_HISTORY_ASSETS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"root Domain Pack archive asset missing after Phase 11C asset migration: {relative_path}")

    for relative_path in REQUIRED_RETIRED_UI_SCRIPT_ARCHIVES:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"retired Domain Pack UI script archive missing: {relative_path}")

    for relative_path in REQUIRED_PHASE6_BUNDLE_HELPER_ARCHIVES:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"retired Phase 6 bundle helper archive missing: {relative_path}")

    for relative_path in RETIRED_PHASE6_BUNDLE_ACTIVE_TOOLS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"retired Phase 6 bundle helper must not remain active: {relative_path}")

    for relative_path in REQUIRED_ARCHIVED_MIGRATION_SPECS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"superseded migration spec archive missing: {relative_path}")

    for relative_path in RETIRED_ACTIVE_MIGRATION_SPECS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"superseded migration spec must not remain active: {relative_path}")

    for relative_path in REQUIRED_ARCHIVED_DECISIONS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"superseded architecture decision archive missing: {relative_path}")

    for relative_path in RETIRED_ACTIVE_DECISIONS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"superseded architecture decision must not remain active: {relative_path}")

    known_pitfalls = _read(".agent/references/known-pitfalls.md")
    if "must not be restored" not in known_pitfalls:
        errors.append("known pitfalls must keep retired surfaces out of target layout")

    backend_router = _read("src/backend/zuno/api/router.py")
    backend_v1_init = _read("src/backend/zuno/api/v1/__init__.py")
    if "domain_packs" in backend_router or "router.include_router(domain_packs.router)" in backend_router:
        errors.append("Domain Pack router must not be mounted on the current FastAPI router")
    if "domain_packs" in backend_v1_init:
        errors.append("Domain Pack module must not be exported from the current API v1 front path")
    for relative_path in RETIRED_DOMAIN_PACK_API_WRAPPERS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"Retired Domain Pack API wrapper must not remain: {relative_path}")

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
    for relative_path in RETIRED_FRONTEND_DOMAIN_PACK_FILES:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"Retired Domain Pack frontend file must not remain: {relative_path}")

    workspace_agent = _read("src/backend/zuno/platform/services/workspace/simple_agent.py")
    if "from zuno.core.runtime.agent_runtime import AgentRuntime" in workspace_agent:
        errors.append("Workspace knowledge path must not import AgentRuntime")
    if "domain_qa_runtime" in workspace_agent:
        errors.append("Workspace knowledge path must not expose domain_qa_runtime")
    if "_run_domain_pack_query" in workspace_agent:
        errors.append("Workspace knowledge path must not call _run_domain_pack_query")
    if "KnowledgeQueryService" not in workspace_agent:
        errors.append("Workspace knowledge path must use KnowledgeQueryService")

    knowledge_service = _read("src/backend/zuno/api/services/knowledge.py")
    if "from zuno.services.domain_pack.loader import DomainPackLoader" in knowledge_service:
        errors.append("KnowledgeService runtime settings must not load DomainPackLoader")
    if "DomainPackLoader().load" in knowledge_service:
        errors.append("KnowledgeService runtime settings must not load DomainPackLoader")

    graph_retriever = _read("src/backend/zuno/platform/services/graphrag/retriever.py")
    if "from zuno.services.domain_pack.loader import DomainPackLoader" in graph_retriever:
        errors.append("GraphRetriever policy defaults must not load DomainPackLoader")
    if "DomainPackLoader().load" in graph_retriever:
        errors.append("GraphRetriever policy defaults must not load DomainPackLoader")

    contract_eval = _read("tools/evals/zuno/contract_review_eval/run_contract_eval.py")
    if "from zuno.services.domain_pack.loader import DomainPackLoader" in contract_eval:
        errors.append("Contract Review eval must load GraphRAG Project assets")
    if "DomainPackLoader().load" in contract_eval:
        errors.append("Contract Review eval must load GraphRAG Project assets")
    if "GraphRAGProjectLoader" not in contract_eval:
        errors.append("Contract Review eval must load GraphRAG Project assets")
    if "from zuno.core.graphs.domain_qa_graph import DomainQAGraph" in contract_eval:
        errors.append("Contract Review eval must not use DomainQAGraph")
    if "DomainQAGraph(" in contract_eval:
        errors.append("Contract Review eval must not use DomainQAGraph")
    if "domain_pack=project_payload" in contract_eval:
        errors.append("GraphRAG eval paths must call extractors with project_payload")
    if "project_payload=project_payload" not in contract_eval:
        errors.append("GraphRAG eval paths must call extractors with project_payload")

    stackless_eval = _read("tools/evals/zuno/rag_eval/run_stackless_local_eval.py")
    real_runtime_eval = _read("tools/evals/zuno/multihop_eval/run_real_runtime_eval.py")
    if "_load_legacy_domain_pack_payload" in stackless_eval:
        errors.append("Stackless local eval must not fall back to DomainPackLoader")
    if "from zuno.services.domain_pack.loader import DomainPackLoader" in stackless_eval:
        errors.append("Stackless local eval must not fall back to DomainPackLoader")
    if "DomainPackLoader().load" in stackless_eval:
        errors.append("Stackless local eval must not fall back to DomainPackLoader")
    if "_load_graph_project_domain_payload" in stackless_eval:
        errors.append("Stackless local eval must not keep a graph project domain payload alias")
    if "domain_pack=project_payload" in stackless_eval:
        errors.append("GraphRAG eval paths must call extractors with project_payload")
    if "project_payload=project_payload" not in stackless_eval:
        errors.append("GraphRAG eval paths must call extractors with project_payload")
    if '"domain_pack": project_payload' in stackless_eval:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")
    if '"project_payload": project_payload' not in stackless_eval:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")
    if '"domain_pack": None' in real_runtime_eval:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")
    if '"project_payload": None' not in real_runtime_eval:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")
    knowledge_service = _read("src/backend/zuno/api/services/knowledge.py")
    if 'runtime.get("project_payload") or runtime.get("domain_pack")' not in knowledge_service:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")
    if 'runtime["project_payload"] = project_payload' not in knowledge_service:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")
    if 'runtime["domain_pack"]' in knowledge_service:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")
    if '"domain_pack": domain_pack' in knowledge_service:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")
    pipeline_manager = _read("src/backend/zuno/platform/services/pipeline/manager.py")
    if "domain_pack=domain_pack" in pipeline_manager:
        errors.append("Pipeline graph extraction must call extractors with project_payload")
    if 'runtime_settings.get("project_payload")' not in pipeline_manager:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")
    project_loader = _read("src/backend/zuno/platform/services/graphrag/project/loader.py")
    if "def to_domain_pack_payload" in project_loader:
        errors.append("GraphRAG Project loader must expose only to_project_payload")
    structured_contract_test = _read("tests/graphrag/test_structured_graph_extractor_contract.py")
    if "domain_pack=contract_review" in structured_contract_test:
        errors.append("Structured graph extractor contract tests must use project_payload")
    if (REPO_ROOT / "tests/evals/test_stackless_local_eval_contract_domain_pack.py").exists():
        errors.append("Stackless Contract Review eval test must use project query policy naming")
    if not (REPO_ROOT / "tests/evals/test_stackless_local_eval_contract_project_query_policy.py").exists():
        errors.append("Stackless Contract Review eval test must use project query policy naming")
    retired_root_migration_test_names = [
        "tests/legacy_guards/test_completion_domain_pack_runtime.py",
        "tests/legacy_guards/test_contract_review_domain_pack.py",
        "tests/legacy_guards/test_domain_pack_runtime_flow.py",
        "tests/legacy_guards/test_general_agent_domain_pack_runtime.py",
        "tests/legacy_guards/test_workspace_domain_pack_runtime.py",
    ]
    project_root_migration_test_names = [
        "tests/agent/test_completion_agent_config_compatibility.py",
        "tests/graphrag/test_contract_review_project_payload.py",
        "tests/legacy_guards/test_project_query_compatibility_boundaries.py",
        "tests/agent/test_general_agent_project_query_runtime.py",
        "tests/agent/test_workspace_project_query_runtime.py",
    ]
    for relative_path in retired_root_migration_test_names:
        if (REPO_ROOT / relative_path).exists():
            errors.append("Root migration tests must use project or retirement naming")
    for relative_path in project_root_migration_test_names:
        if not (REPO_ROOT / relative_path).exists():
            errors.append("Root migration tests must use project or retirement naming")

    structured_extractor = _read("src/backend/zuno/platform/services/graphrag/extractors/structured_extractor.py")
    cached_extractor = _read("src/backend/zuno/platform/services/graphrag/extractors/cached_extractor.py")
    if "project_payload:" not in structured_extractor or "project_payload:" not in cached_extractor:
        errors.append("GraphRAG extractors must expose project_payload as the primary payload parameter")
    if "domain_pack:" in structured_extractor or "domain_pack:" in cached_extractor:
        errors.append("GraphRAG extractors must not expose domain_pack payload aliases")

    graph_retrievers = _read("src/backend/zuno/platform/services/retrieval/retrievers.py")
    if 'scope_policy.get("graphrag_project_id")' not in graph_retrievers:
        errors.append("GraphRetrieverAdapter must use GraphRAG Project scope from graphrag_project_id")
    if 'runtime_settings.get("project_payload")' not in graph_retrievers:
        errors.append("Runtime settings must expose GraphRAG Project payload via project_payload")

    retired_ui_script_phrases = [
        "docs/ui-gallery/knowledge-product-refactor-deep-graphrag-v1",
        "docs/ui-review/",
        "docs/prototypes/",
        "/api/v1/domain-packs",
        "/workspace/settings/knowledge/domain-packs",
        "domain-pack-list.vue",
        "domain-pack-create.vue",
        "domain-pack-detail.vue",
        ".domain-pack-page",
        ".domain-pack-create-page",
        ".domain-pack-detail-page",
    ]
    for script_path in sorted((REPO_ROOT / "tools/scripts").glob("*.py")):
        if script_path.name.startswith("verify_"):
            continue
        content = script_path.read_text(encoding="utf-8")
        for phrase in retired_ui_script_phrases:
            if phrase in content:
                errors.append(
                    f"active tool script references retired Domain Pack UI surface: {script_path.relative_to(REPO_ROOT)}"
                )
                break

    retired_runtime_source_phrases = [
        "retired_runtime_legacy",
        "src/backend/zuno/api/v1/domain_packs.py",
        "src/backend/zuno/api/services/domain_pack.py",
        "src/backend/zuno/core/graphs/domain_qa_graph.py",
        "src/backend/zuno/core/graphs/states.py",
        "src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py",
        "src/backend/zuno/core/runtime/agent_runtime.py",
        "src/backend/zuno/services/domain_pack/",
    ]
    active_public_release_tools = [
        "tools/scripts/preview_public_release_group.py",
        "tools/scripts/preview_public_release_stage_dry_run.py",
        "tools/scripts/print_public_release_stage_commands.py",
        "tools/scripts/summarize_public_release_scope.py",
    ]
    for relative_path in active_public_release_tools:
        content = _read(relative_path)
        for phrase in retired_runtime_source_phrases:
            if phrase in content:
                errors.append(
                    f"active public release tool stages retired runtime source: {relative_path}"
                )
                break

    stage_namespace = runpy.run_path(
        str(REPO_ROOT / "tools/scripts/print_public_release_stage_commands.py")
    )
    stage_groups = dict(stage_namespace["STAGE_GROUPS"])
    backend_public_commands = stage_groups.get("backend_public_entrypoints", [])
    backend_public_paths = [
        token
        for command in backend_public_commands
        for token in shlex.split(command, posix=False)
        if token not in {"git", "add"}
    ]
    if "src/backend/zuno/" in backend_public_paths:
        errors.append(
            "active public release tool crosses backend release-group boundary: "
            "tools/scripts/print_public_release_stage_commands.py"
        )

    agent_runtime_path = REPO_ROOT / "src/backend/zuno/agent/core/runtime/agent_runtime.py"
    if agent_runtime_path.exists():
        errors.append("AgentRuntime facade must not remain as current backend source")
    core_init = _read("src/backend/zuno/agent/core/__init__.py")
    runtime_init = _read("src/backend/zuno/agent/core/runtime/__init__.py")
    if '"AgentRuntime"' in core_init or "AgentRuntime" in runtime_init:
        errors.append("AgentRuntime facade must not be exported from current backend source")
    graphs_init = _read("src/backend/zuno/agent/core/graphs/__init__.py")
    legacy_graph_exports = ["DomainQAGraph", "MultiAgentSupervisorGraph"]
    if any(name in core_init or name in graphs_init for name in legacy_graph_exports):
        errors.append("Legacy graph facades must not be exported from current backend packages")
    supervisor_graph_path = REPO_ROOT / "src/backend/zuno/agent/core/graphs/multi_agent_supervisor_graph.py"
    if supervisor_graph_path.exists():
        errors.append("MultiAgentSupervisorGraph source must not remain as current backend source")
    domain_qa_graph_path = REPO_ROOT / "src/backend/zuno/agent/core/graphs/domain_qa_graph.py"
    if domain_qa_graph_path.exists():
        errors.append("DomainQAGraph source must not remain as current backend source")
    legacy_graph_states_path = REPO_ROOT / "src/backend/zuno/agent/core/graphs/states.py"
    if legacy_graph_states_path.exists():
        errors.append("Legacy graph states must not remain without current graph source")
    domain_pack_service_path = REPO_ROOT / "src/backend/zuno/platform/services/domain_pack"
    if domain_pack_service_path.exists():
        errors.append("Domain Pack runtime service must not remain as current backend source")

    retired_html_matches = [
        path
        for path in _tracked_files()
        if path.replace("\\", "/").endswith("zuno-ideal-architecture-and-repo-layout.html")
        and (REPO_ROOT / path).exists()
    ]
    if retired_html_matches:
        errors.append(
            "retired target architecture HTML must not be tracked: "
            + ", ".join(path.replace("\\", "/") for path in retired_html_matches)
        )

    for path in FORBIDDEN_CURRENT_PATHS:
        if (REPO_ROOT / path).exists():
            errors.append(f"retired current path exists: {path}")

    tracked = set(_tracked_files())
    for tracked_path in tracked:
        normalized = tracked_path.replace("\\", "/")
        for prefix in FORBIDDEN_TRACKED_PREFIXES:
            if normalized.startswith(prefix):
                errors.append(f"generated/local path is tracked: {normalized}")
                break
        for pattern in FORBIDDEN_TRACKED_PATTERNS:
            if fnmatch(normalized, pattern):
                errors.append(f"generated/local file is tracked: {normalized}")
                break
        if normalized.startswith(("data/", "reports/")) and normalized not in TRACKED_DATA_REPORTS_ALLOWLIST:
            errors.append(
                "data/ and reports/ tracked files must be explicit metadata allowlist entries: "
                f"{normalized}"
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Repo hygiene verification failed.")
        return 1

    print("Repo hygiene verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

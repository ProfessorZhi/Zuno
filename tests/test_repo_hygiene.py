import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_ignore_files_match_current_structure() -> None:
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    dockerignore = (REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")

    for entry in [
        ".codex/",
        ".local/",
        "apps/web/node_modules/",
        "apps/web/dist/",
        ".agent/local/*",
    ]:
        assert entry in gitignore

    for forbidden in ["apps/web/AGENTS.md", "$null", "&1"]:
        assert forbidden not in gitignore

    assert "apps/web/node_modules" in dockerignore
    assert "apps/web/dist" in dockerignore
    assert "src/frontend" not in dockerignore


def test_package_license_matches_root_license() -> None:
    package_json = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8")

    assert package_json["license"] == "MIT"
    assert license_text.startswith("MIT License")


def test_retired_legacy_paths_are_absent_and_classified() -> None:
    assert not (REPO_ROOT / "tests/compat").exists()
    assert not (REPO_ROOT / "domain-packs").exists()
    for relative_path in [
        "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml",
        "docs/history/domain-packs/root-contract-review/contract_review/schema.json",
        "docs/history/domain-packs/root-contract-review/contract_review/retrieval_policy.yaml",
        "docs/history/domain-packs/root-contract-review/contract_review/extraction_prompt.md",
        "docs/history/domain-packs/root-contract-review/contract_review/answer_template.md",
        "docs/history/domain-packs/root-contract-review/contract_review/report_template.md",
        "docs/history/domain-packs/root-contract-review/contract_review/eval_dataset.jsonl",
    ]:
        assert (REPO_ROOT / relative_path).exists()

    pitfalls = (
        REPO_ROOT / ".agent" / "references" / "known-pitfalls.md"
    ).read_text(encoding="utf-8")
    assert "root `domain-packs/`" in pitfalls
    assert "tests/compat" in pitfalls
    assert "Do not restore" in pitfalls


def test_repo_hygiene_verifier_preserves_full_contract_review_history() -> None:
    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")

    for relative_path in [
        "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml",
        "docs/history/domain-packs/root-contract-review/contract_review/schema.json",
        "docs/history/domain-packs/root-contract-review/contract_review/retrieval_policy.yaml",
        "docs/history/domain-packs/root-contract-review/contract_review/extraction_prompt.md",
        "docs/history/domain-packs/root-contract-review/contract_review/answer_template.md",
        "docs/history/domain-packs/root-contract-review/contract_review/report_template.md",
        "docs/history/domain-packs/root-contract-review/contract_review/eval_dataset.jsonl",
        "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/capture_knowledge_product_ui_gallery.py",
        "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/check_knowledge_product_responsive.py",
        "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/check_settings_navigation_interaction.py",
    ]:
        assert relative_path in verifier


def test_multi_agent_supervisor_source_stays_retired_from_current_backend() -> None:
    assert not (
        REPO_ROOT / "src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py"
    ).exists(), "MultiAgentSupervisorGraph should not remain as current backend source"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "MultiAgentSupervisorGraph source must not remain as current backend source" in verifier


def test_domain_qa_graph_source_stays_retired_from_current_backend() -> None:
    assert not (
        REPO_ROOT / "src/backend/zuno/core/graphs/domain_qa_graph.py"
    ).exists(), "DomainQAGraph should not remain as current backend source"
    assert not (
        REPO_ROOT / "src/backend/zuno/core/graphs/states.py"
    ).exists(), "legacy graph states should not remain without current graph source"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "DomainQAGraph source must not remain as current backend source" in verifier
    assert "Legacy graph states must not remain without current graph source" in verifier


def test_domain_pack_frontend_files_stay_retired() -> None:
    for path in [
        "apps/web/src/apis/domain-packs.ts",
        "apps/web/src/pages/knowledge/domain-pack-list.vue",
        "apps/web/src/pages/knowledge/domain-pack-create.vue",
        "apps/web/src/pages/knowledge/domain-pack-detail.vue",
    ]:
        assert not (REPO_ROOT / path).exists(), f"retired Domain Pack frontend file remains: {path}"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Retired Domain Pack frontend file must not remain" in verifier


def test_domain_pack_api_wrapper_files_stay_retired() -> None:
    for path in [
        "src/backend/zuno/api/v1/domain_packs.py",
        "src/backend/zuno/api/services/domain_pack.py",
    ]:
        assert not (REPO_ROOT / path).exists(), f"retired Domain Pack API wrapper remains: {path}"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Retired Domain Pack API wrapper must not remain" in verifier


def test_domain_pack_runtime_service_stays_retired_from_current_backend() -> None:
    assert not (
        REPO_ROOT / "src/backend/zuno/services/domain_pack"
    ).exists(), "Domain Pack runtime service should not remain as current backend source"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Domain Pack runtime service must not remain as current backend source" in verifier


def test_knowledge_service_stays_off_domain_pack_loader_runtime_defaults() -> None:
    knowledge_service = (
        REPO_ROOT / "src/backend/zuno/api/services/knowledge.py"
    ).read_text(encoding="utf-8")
    assert "from zuno.services.domain_pack.loader import DomainPackLoader" not in knowledge_service
    assert "DomainPackLoader().load" not in knowledge_service

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "KnowledgeService runtime settings must not load DomainPackLoader" in verifier


def test_graph_retriever_stays_off_domain_pack_loader_policy_defaults() -> None:
    graph_retriever = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/retriever.py"
    ).read_text(encoding="utf-8")
    assert "from zuno.services.domain_pack.loader import DomainPackLoader" not in graph_retriever
    assert "DomainPackLoader().load" not in graph_retriever

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "GraphRetriever policy defaults must not load DomainPackLoader" in verifier


def test_contract_eval_runner_stays_off_domain_pack_loader_project_defaults() -> None:
    contract_eval = (
        REPO_ROOT / "tools/evals/zuno/contract_review_eval/run_contract_eval.py"
    ).read_text(encoding="utf-8")
    assert "from zuno.services.domain_pack.loader import DomainPackLoader" not in contract_eval
    assert "DomainPackLoader().load" not in contract_eval
    assert "GraphRAGProjectLoader" in contract_eval
    assert "from zuno.core.graphs.domain_qa_graph import DomainQAGraph" not in contract_eval
    assert "DomainQAGraph(" not in contract_eval

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Contract Review eval must load GraphRAG Project assets" in verifier
    assert "Contract Review eval must not use DomainQAGraph" in verifier


def test_stackless_local_eval_stays_off_legacy_domain_pack_loader_fallback() -> None:
    stackless_eval = (
        REPO_ROOT / "tools/evals/zuno/rag_eval/run_stackless_local_eval.py"
    ).read_text(encoding="utf-8")
    assert "_load_legacy_domain_pack_payload" not in stackless_eval
    assert "from zuno.services.domain_pack.loader import DomainPackLoader" not in stackless_eval
    assert "DomainPackLoader().load" not in stackless_eval

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Stackless local eval must not fall back to DomainPackLoader" in verifier


def test_graph_project_payload_is_primary_in_eval_and_graph_extractor_paths() -> None:
    contract_eval = (
        REPO_ROOT / "tools/evals/zuno/contract_review_eval/run_contract_eval.py"
    ).read_text(encoding="utf-8")
    stackless_eval = (
        REPO_ROOT / "tools/evals/zuno/rag_eval/run_stackless_local_eval.py"
    ).read_text(encoding="utf-8")
    structured_extractor = (
        REPO_ROOT
        / "src/backend/zuno/services/graphrag/extractors/structured_extractor.py"
    ).read_text(encoding="utf-8")
    cached_extractor = (
        REPO_ROOT
        / "src/backend/zuno/services/graphrag/extractors/cached_extractor.py"
    ).read_text(encoding="utf-8")
    project_loader = (
        REPO_ROOT / "src/backend/zuno/services/graphrag/project/loader.py"
    ).read_text(encoding="utf-8")
    pipeline_manager = (
        REPO_ROOT / "src/backend/zuno/services/pipeline/manager.py"
    ).read_text(encoding="utf-8")
    knowledge_service = (
        REPO_ROOT / "src/backend/zuno/api/services/knowledge.py"
    ).read_text(encoding="utf-8")
    real_runtime_eval = (
        REPO_ROOT / "tools/evals/zuno/multihop_eval/run_real_runtime_eval.py"
    ).read_text(encoding="utf-8")
    structured_contract_test = (
        REPO_ROOT / "tests/test_structured_graph_extractor_contract.py"
    ).read_text(encoding="utf-8")
    graph_retrievers = (
        REPO_ROOT / "src/backend/zuno/services/retrieval/retrievers.py"
    ).read_text(encoding="utf-8")

    assert "project_payload=project_payload" in contract_eval
    assert "project_payload=project_payload" in stackless_eval
    assert "domain_pack=project_payload" not in contract_eval
    assert "domain_pack=project_payload" not in stackless_eval
    assert '"project_payload": project_payload' in stackless_eval
    assert '"domain_pack": project_payload' not in stackless_eval
    assert 'runtime_settings.get("project_payload")' in pipeline_manager
    assert 'runtime_settings.get("project_payload")' in graph_retrievers
    assert 'runtime.get("project_payload") or runtime.get("domain_pack")' in knowledge_service
    assert 'runtime["project_payload"] = project_payload' in knowledge_service
    assert 'runtime["domain_pack"]' not in knowledge_service
    assert '"project_payload": project_payload' in knowledge_service
    assert '"domain_pack": domain_pack' not in knowledge_service
    assert '"project_payload": None' in real_runtime_eval
    assert '"domain_pack": None' not in real_runtime_eval
    assert "domain_pack=domain_pack" not in pipeline_manager
    assert "domain_pack:" not in structured_extractor
    assert "domain_pack:" not in cached_extractor
    assert "domain_pack=contract_review" not in structured_contract_test
    assert "def to_domain_pack_payload" not in project_loader
    assert "_load_graph_project_domain_payload" not in stackless_eval
    assert "project_payload:" in structured_extractor
    assert "project_payload:" in cached_extractor
    assert 'scope_policy.get("graphrag_project_id")' in graph_retrievers

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "GraphRAG eval paths must call extractors with project_payload" in verifier
    assert "Pipeline graph extraction must call extractors with project_payload" in verifier
    assert "GraphRAG extractors must not expose domain_pack payload aliases" in verifier
    assert "GraphRAG Project loader must expose only to_project_payload" in verifier
    assert "Structured graph extractor contract tests must use project_payload" in verifier
    assert "Stackless local eval must not keep a graph project domain payload alias" in verifier
    assert "GraphRAG extractors must expose project_payload as the primary payload parameter" in verifier
    assert "GraphRetrieverAdapter must use GraphRAG Project scope from graphrag_project_id" in verifier
    assert "Runtime settings must expose GraphRAG Project payload via project_payload" in verifier


def test_stackless_contract_eval_test_is_project_query_policy_named() -> None:
    assert not (
        REPO_ROOT / "tests/test_stackless_local_eval_contract_domain_pack.py"
    ).exists()
    assert (
        REPO_ROOT / "tests/test_stackless_local_eval_contract_project_query_policy.py"
    ).exists()

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Stackless Contract Review eval test must use project query policy naming" in verifier


def test_root_runtime_tests_use_project_or_retirement_naming() -> None:
    retired_names = [
        "tests/test_completion_domain_pack_runtime.py",
        "tests/test_contract_review_domain_pack.py",
        "tests/test_domain_pack_runtime_flow.py",
        "tests/test_general_agent_domain_pack_runtime.py",
        "tests/test_workspace_domain_pack_runtime.py",
    ]
    project_names = [
        "tests/test_completion_agent_config_compatibility.py",
        "tests/test_contract_review_project_payload.py",
        "tests/test_project_query_compatibility_boundaries.py",
        "tests/test_general_agent_project_query_runtime.py",
        "tests/test_workspace_project_query_runtime.py",
    ]

    for relative_path in retired_names:
        assert not (REPO_ROOT / relative_path).exists(), f"retired test name remains: {relative_path}"
    for relative_path in project_names:
        assert (REPO_ROOT / relative_path).exists(), f"project-named test missing: {relative_path}"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Root migration tests must use project or retirement naming" in verifier


def test_retired_backend_domain_pack_asset_copy_is_removed() -> None:
    assert not (
        REPO_ROOT / "src/backend/zuno/domain_packs"
    ).exists(), "backend package Domain Pack asset copy should not remain a current path"


def test_active_repo_tools_do_not_reference_retired_backend_domain_pack_copy() -> None:
    for path in [
        "tools/scripts/preview_public_release_group.py",
        "tools/scripts/preview_public_release_stage_dry_run.py",
        "tools/scripts/print_public_release_stage_commands.py",
        "tools/scripts/summarize_public_release_scope.py",
    ]:
        content = (REPO_ROOT / path).read_text(encoding="utf-8")
        assert "src/backend/zuno/domain_packs" not in content, path

    roadmap = (
        REPO_ROOT
        / "docs/history/programs/official-graphrag-cleanup-v1/implementation-roadmap.md"
    ).read_text(encoding="utf-8")
    assert "`src/backend/zuno/domain_packs/` still exist" not in roadmap


def test_active_public_release_tools_do_not_stage_retired_runtime_sources() -> None:
    retired_runtime_sources = [
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

    for path in active_public_release_tools:
        content = (REPO_ROOT / path).read_text(encoding="utf-8")
        assert "retired_runtime_legacy" not in content, path
        for retired_source in retired_runtime_sources:
            assert retired_source not in content, f"{path} stages retired source {retired_source}"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "active public release tool stages retired runtime source" in verifier
    assert "active public release tool crosses backend release-group boundary" in verifier


def test_active_architecture_audits_do_not_list_retired_frontend_files_as_current_inputs() -> None:
    audit = (
        REPO_ROOT
        / "docs/history/audits/current-model-and-retrieval-config-audit.md"
    ).read_text(encoding="utf-8")

    assert "- `apps/web/src/apis/domain-packs.ts`" not in audit
    assert "Retired frontend evidence:" in audit
    assert "`apps/web/src/apis/domain-packs.ts`" in audit


def test_workspace_knowledge_path_stays_off_legacy_agent_runtime() -> None:
    workspace_agent = (
        REPO_ROOT / "src/backend/zuno/services/workspace/simple_agent.py"
    ).read_text(encoding="utf-8")
    assert "from zuno.core.runtime.agent_runtime import AgentRuntime" not in workspace_agent
    assert "domain_qa_runtime" not in workspace_agent
    assert "_run_domain_pack_query" not in workspace_agent
    assert "KnowledgeQueryService" in workspace_agent

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Workspace knowledge path must not import AgentRuntime" in verifier


def test_agent_runtime_facade_stays_retired() -> None:
    assert not (REPO_ROOT / "src/backend/zuno/core/runtime/agent_runtime.py").exists()

    core_init = (REPO_ROOT / "src/backend/zuno/core/__init__.py").read_text(
        encoding="utf-8"
    )
    runtime_init = (
        REPO_ROOT / "src/backend/zuno/core/runtime/__init__.py"
    ).read_text(encoding="utf-8")
    assert '"AgentRuntime"' not in core_init
    assert "AgentRuntime" not in runtime_init

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "AgentRuntime facade must not remain as current backend source" in verifier


def test_legacy_graphs_are_not_current_public_package_exports() -> None:
    core_init = (REPO_ROOT / "src/backend/zuno/core/__init__.py").read_text(
        encoding="utf-8"
    )
    graphs_init = (
        REPO_ROOT / "src/backend/zuno/core/graphs/__init__.py"
    ).read_text(encoding="utf-8")

    for legacy_name in ["DomainQAGraph", "MultiAgentSupervisorGraph"]:
        assert legacy_name not in core_init
        assert legacy_name not in graphs_init

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "Legacy graph facades must not be exported" in verifier


def test_domain_pack_is_not_current_api_or_frontend_entrypoint() -> None:
    router = (REPO_ROOT / "src/backend/zuno/api/router.py").read_text(encoding="utf-8")
    api_v1_init = (REPO_ROOT / "src/backend/zuno/api/v1/__init__.py").read_text(encoding="utf-8")
    assert "domain_packs" not in router
    assert "router.include_router(domain_packs.router)" not in router
    assert "domain_packs" not in api_v1_init

    active_frontend_paths = [
        "apps/web/src/router/index.ts",
        "apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue",
        "apps/web/src/pages/knowledge/knowledge.vue",
        "apps/web/src/pages/knowledge/knowledge-create.vue",
        "apps/web/src/pages/knowledge/knowledge-settings.vue",
    ]
    active_frontend = "\n".join(
        (REPO_ROOT / path).read_text(encoding="utf-8")
        for path in active_frontend_paths
    )
    for phrase in [
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
    ]:
        assert phrase not in active_frontend


def test_retired_domain_pack_ui_gallery_scripts_are_not_active_tools() -> None:
    active_scripts = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((REPO_ROOT / "tools/scripts").glob("*.py"))
        if not path.name.startswith("verify_")
    )

    for phrase in [
        "docs/ui-gallery/knowledge-product-refactor-deep-graphrag-v1",
        "/api/v1/domain-packs",
        "/workspace/settings/knowledge/domain-packs",
        "domain-pack-list.vue",
        "domain-pack-create.vue",
        "domain-pack-detail.vue",
        ".domain-pack-page",
        ".domain-pack-create-page",
        ".domain-pack-detail-page",
    ]:
        assert phrase not in active_scripts


def test_phase6_bundle_helpers_are_not_active_repo_tools() -> None:
    for relative_path in [
        "tools/scripts/preview_phase6_bundle_scope.py",
        "tools/scripts/verify_phase6_bundle_ready.py",
    ]:
        assert not (REPO_ROOT / relative_path).exists(), f"retired Phase 6 helper remains active: {relative_path}"

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    for relative_path in [
        "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/preview_phase6_bundle_scope.py",
        "docs/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/verify_phase6_bundle_ready.py",
        "tools/scripts/preview_phase6_bundle_scope.py",
        "tools/scripts/verify_phase6_bundle_ready.py",
    ]:
        assert relative_path in verifier


def test_superseded_migration_specs_are_not_active_specs() -> None:
    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")

    for relative_path in [
        "docs/history/specs/deep-graphrag-v1-runtime.md",
        "docs/history/specs/domain-pack-langgraph-graphrag-architecture.md",
        "docs/history/specs/domain-pack-builder.md",
        "docs/history/specs/knowledge-product-boundary.md",
        "docs/history/specs/deep-graphrag-v1-runtime.md",
        "docs/history/specs/domain-pack-langgraph-graphrag-architecture.md",
        "docs/history/specs/domain-pack-builder.md",
        "docs/history/specs/knowledge-product-boundary.md",
    ]:
        assert relative_path in verifier


def test_superseded_domain_pack_binding_decision_is_history() -> None:
    assert not (
        REPO_ROOT / "docs/architecture/decisions/0001-domain-pack-binding.md"
    ).exists()
    assert (
        REPO_ROOT
        / "docs/history/decisions/0001-domain-pack-binding.md"
    ).exists()

    verifier = (
        REPO_ROOT / ".agent/scripts/verify_repo_hygiene.py"
    ).read_text(encoding="utf-8")
    assert "docs/history/decisions/0001-domain-pack-binding.md" in verifier
    assert "docs/architecture/decisions/0001-domain-pack-binding.md" in verifier


def test_repo_hygiene_verifiers_are_registered() -> None:
    for path in [
        ".agent/scripts/verify_doc_boundaries.py",
        ".agent/scripts/verify_repo_hygiene.py",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
    ]:
        assert (REPO_ROOT / path).exists()

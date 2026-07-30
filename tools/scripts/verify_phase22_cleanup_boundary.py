from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
API_V1_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "v1"
API_ERRCODE_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "errcode"
PLATFORM_DATABASE_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "database"
PLATFORM_APPLICATION_KNOWLEDGE_ROOT = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "application" / "knowledge"
)
PLATFORM_REWRITE_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "rewrite"
PLATFORM_PIPELINE_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "pipeline"
PLATFORM_GRAPHRAG_COMMUNITY_ROOT = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "graphrag" / "community"
)
PLATFORM_GRAPHRAG_EXTRACTORS_ROOT = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "graphrag" / "extractors"
)
PLATFORM_GRAPHRAG_GRAPH_STORE_INIT = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "graphrag" / "graph_store" / "__init__.py"
)
PLATFORM_GRAPHRAG_PROMPTS_INIT = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "graphrag" / "prompts" / "__init__.py"
)
PLATFORM_GRAPHRAG_RETRIEVERS_ROOT = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "graphrag" / "retrievers"
)
PLATFORM_GRAPHRAG_PROJECT_LOADER = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "graphrag" / "project" / "loader.py"
)
PLATFORM_GRAPHRAG_QUERY_SERVICE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "graphrag" / "query_service.py"
)
PLATFORM_GRAPHRAG_ORCHESTRATOR = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "graphrag" / "orchestrator.py"
)
PLATFORM_GRAPHRAG_RETRIEVER = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "graphrag" / "retriever.py"
)
PLATFORM_RETRIEVAL_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "retrieval"
PLATFORM_RAG_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "rag"
PLATFORM_MEMORY_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "memory"
PLATFORM_WORKSPACE_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "workspace"
PLATFORM_DEEPSEARCH_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "deepsearch"
PLATFORM_AUTOBUILD_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "autobuild"
AGENT_RUNTIME_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "runtime"
PLATFORM_COMMON_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "common"
PLATFORM_MIDDLEWARE_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "middleware"
PLATFORM_CONFIG_ROOT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "config"
PLATFORM_MODEL_GATEWAY = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "model_gateway.py"
PLATFORM_MODEL_GATEWAY_ADAPTERS = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "model_gateway_adapters.py"
PLATFORM_APPLICATION_INIT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "application" / "__init__.py"
TOOLS_EVALS_ZUNO_ROOT = REPO_ROOT / "tools" / "evals" / "zuno"
TOOLS_SCRIPTS_CANONICAL_FILES = [
    REPO_ROOT / "tools" / "scripts" / "check_model_registry_defaults.py",
    REPO_ROOT / "tools" / "scripts" / "cleanup_model_registry_defaults.py",
    REPO_ROOT / "tools" / "scripts" / "rebuild_rag_indexes.py",
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_minio_manifest_adoption.py",
]
INFRA_ALEMBIC_ENV = REPO_ROOT / "infra" / "db" / "alembic" / "env.py"
TESTS_TOOLS_ROOT = REPO_ROOT / "tests" / "tools"
TESTS_STORAGE_ROOT = REPO_ROOT / "tests" / "storage"
TESTS_AGENT_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "agent" / "test_agent_api_project_contract.py",
    REPO_ROOT / "tests" / "agent" / "test_agent_empty_workspace.py",
    REPO_ROOT / "tests" / "agent" / "test_agent_layer_surfaces.py",
    REPO_ROOT / "tests" / "agent" / "test_capability_layer_surfaces.py",
    REPO_ROOT / "tests" / "agent" / "test_capability_registry.py",
    REPO_ROOT / "tests" / "agent" / "test_capability_system.py",
    REPO_ROOT / "tests" / "agent" / "test_completion_agent_config_compatibility.py",
    REPO_ROOT / "tests" / "agent" / "test_context_contracts.py",
    REPO_ROOT / "tests" / "agent" / "test_context_orchestrator.py",
    REPO_ROOT / "tests" / "agent" / "test_general_agent_project_query_runtime.py",
    REPO_ROOT / "tests" / "agent" / "test_generalagent_context_memory_runtime.py",
    REPO_ROOT / "tests" / "agent" / "test_hooks_evidence_trace_artifacts.py",
    REPO_ROOT / "tests" / "agent" / "test_knowledge_graphrag_runtime_contracts.py",
    REPO_ROOT / "tests" / "agent" / "test_knowledge_layer_surfaces.py",
    REPO_ROOT / "tests" / "agent" / "test_memory_layer_surfaces.py",
    REPO_ROOT / "tests" / "agent" / "test_memory_layers.py",
    REPO_ROOT / "tests" / "agent" / "test_mcp_server_service.py",
    REPO_ROOT / "tests" / "agent" / "test_mcp_stdio_server_security.py",
    REPO_ROOT / "tests" / "agent" / "test_phase05_admin_action_reauthorization.py",
    REPO_ROOT / "tests" / "agent" / "test_platform_layer_surfaces.py",
    REPO_ROOT / "tests" / "agent" / "test_runtime_observability.py",
    REPO_ROOT / "tests" / "agent" / "test_workspace_project_query_runtime.py",
    REPO_ROOT / "tests" / "agent" / "test_workspace_simple_agent.py",
    REPO_ROOT / "tests" / "agent" / "test_workspace_usage_agent_name.py",
    REPO_ROOT / "tests" / "agent" / "test_workspace_session_api.py",
    REPO_ROOT / "tests" / "agent" / "test_workspace_session_cleanup.py",
]
TESTS_API_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "api" / "test_completion_unified_runtime.py",
    REPO_ROOT / "tests" / "api" / "test_goal03_knowledge_route.py",
    REPO_ROOT / "tests" / "api" / "test_knowledge_api_contract.py",
    REPO_ROOT / "tests" / "api" / "test_usage_stats_filters.py",
    REPO_ROOT / "tests" / "api" / "test_workspace_agentic_product_contract.py",
    REPO_ROOT / "tests" / "api" / "test_workspace_product_loop_contract.py",
    REPO_ROOT / "tests" / "api" / "test_workspace_runtime_recovery.py",
    REPO_ROOT / "tests" / "api" / "test_workspace_task_runtime.py",
]
TESTS_E2E_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "e2e" / "test_unified_agent_product_scenario.py",
]
TESTS_FRONTEND_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "frontend" / "test_phase1_knowledge_product_skeleton.py",
    REPO_ROOT / "tests" / "frontend" / "test_product_wiring_v1_api_contract.py",
]
TESTS_EVALS_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "evals" / "test_phase5_deep_graphrag_eval_surface.py",
    REPO_ROOT / "tests" / "evals" / "test_local_runtime_registry.py",
    REPO_ROOT / "tests" / "evals" / "test_rag_eval_metrics.py",
    REPO_ROOT / "tests" / "evals" / "test_stackless_local_eval_contract_project_query_policy.py",
    REPO_ROOT / "tests" / "evals" / "test_stackless_local_eval_project_assets.py",
    REPO_ROOT / "tests" / "evals" / "test_stackless_local_eval_project_guard.py",
    REPO_ROOT / "tests" / "evals" / "test_stackless_local_eval_rerank_runtime.py",
]
TESTS_KNOWLEDGE_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "knowledge" / "test_parse_gateway_runtime.py",
]
TESTS_INTEGRATION_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "integration" / "test_goal03_wave_a_persistence.py",
]
TESTS_REPO_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "repo" / "test_graph_store_project_id_migration.py",
    REPO_ROOT / "tests" / "repo" / "test_hardening01_config_impact_contract.py",
    REPO_ROOT / "tests" / "repo" / "test_phase11c_agent_runtime_retirement.py",
    REPO_ROOT / "tests" / "repo" / "test_phase11c_domain_pack_api_retirement.py",
    REPO_ROOT / "tests" / "repo" / "test_phase11c_graph_public_export_retirement.py",
    REPO_ROOT / "tests" / "repo" / "test_phase25_legacy_boundary_hardening.py",
    REPO_ROOT / "tests" / "repo" / "test_phase5_domain_runtime_paths.py",
    REPO_ROOT / "tests" / "repo" / "test_phase5_general_agent_real_runtime_flow.py",
    REPO_ROOT / "tests" / "repo" / "test_phase5_workspace_real_runtime_flow.py",
    REPO_ROOT / "tests" / "repo" / "test_phase6_bundle_scope.py",
    REPO_ROOT / "tests" / "repo" / "test_phase5_docs_public_explanation_sync.py",
    REPO_ROOT / "tests" / "repo" / "test_zuno_canonical_import_surfaces.py",
    REPO_ROOT / "tests" / "repo" / "test_llm_system_sync.py",
    REPO_ROOT / "tests" / "repo" / "test_model_gateway_bypass.py",
]
TESTS_GRAPHRAG_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "graphrag" / "test_contract_graph_query_routing.py",
    REPO_ROOT / "tests" / "graphrag" / "test_contract_graph_retriever.py",
    REPO_ROOT / "tests" / "graphrag" / "test_contract_review_project_payload.py",
    REPO_ROOT / "tests" / "graphrag" / "test_2wiki_missed_opportunity_activation.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_baseline_preserving_fusion.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_bridge_guardrail.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_chain_aware_fusion.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_comparison_guardrail.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_entity_alias.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_genealogy_guardrail.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_genealogy_path_precision.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_index_versioning.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_path_ranking.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_project_contracts.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_project_loader.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_prompt_registry.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_route_activation_calibration.py",
    REPO_ROOT / "tests" / "graphrag" / "test_graphrag_seed_expansion.py",
    REPO_ROOT / "tests" / "graphrag" / "test_structured_graph_extractor_contract.py",
]
TESTS_RETRIEVAL_CANONICAL_FILES = [
    REPO_ROOT / "tests" / "retrieval" / "test_enhanced_requery_activation.py",
    REPO_ROOT / "tests" / "retrieval" / "test_enhanced_requery_precision_gate.py",
    REPO_ROOT / "tests" / "retrieval" / "test_enhanced_standard_floor_invariance.py",
    REPO_ROOT / "tests" / "retrieval" / "test_enhanced_retrieval_composition.py",
    REPO_ROOT / "tests" / "retrieval" / "test_graph_retriever_local_runtime.py",
    REPO_ROOT / "tests" / "retrieval" / "test_query_rewrite.py",
    REPO_ROOT / "tests" / "retrieval" / "test_rerank_fallback.py",
    REPO_ROOT / "tests" / "retrieval" / "test_retrieval_fusion.py",
    REPO_ROOT / "tests" / "retrieval" / "test_retrieval_orchestrator.py",
    REPO_ROOT / "tests" / "retrieval" / "test_retrieval_planner.py",
    REPO_ROOT / "tests" / "retrieval" / "test_standard_retrieval_composition.py",
    REPO_ROOT / "tests" / "retrieval" / "test_workspace_retrieval_trace.py",
]
SEND_EMAIL_MANIFEST = REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "send_email" / "manifest.yaml"
EMBEDDING_INIT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "embedding" / "__init__.py"
LLM_INIT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "llm" / "__init__.py"
CONVERT_FILES_INIT = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "convert_files" / "__init__.py"
)
QUEUE_WORKERS = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "queue" / "workers.py"
QUEUE_MESSAGES = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "queue" / "messages.py"
QUEUE_RUNNER = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "queue" / "runner.py"
PLATFORM_SETTINGS = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "settings.py"
MAIN_ENTRYPOINT = REPO_ROOT / "src" / "backend" / "zuno" / "main.py"
MEMORY_FEEDBACK_CONSUMER = REPO_ROOT / "src" / "backend" / "zuno" / "memory" / "feedback_consumer.py"
AGENT_PRODUCT_BASELINE = REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "product_baseline.py"
WORKSPACE_TASK_RUNTIME_SERVICE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "workspace_task_runtime.py"
)
KNOWLEDGE_DTO = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "dto" / "knowledge.py"
WORK_PRODUCT = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "phase22-removal-candidates.yaml"
)
PRODUCT_RUNTIME_BATCH = REPO_ROOT / "src" / "backend" / "zuno" / "product" / "runtime_batch.py"
PRODUCT_COMMAND_SERVICE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "product" / "command_service.py"
)
WORKSPACE_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "workspace.py"
ATTACHMENT_SERVICE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "workspace" / "attachment_service.py"
)
STORAGE_FACADE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "storage" / "__init__.py"
)
TEXT_TO_IMAGE_ACTION = (
    REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "text2image" / "action.py"
)
CONVERT_TO_DOCX_ACTION = (
    REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "convert_to_docx" / "action.py"
)
CONVERT_TO_PDF_ACTION = (
    REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "convert_to_pdf" / "action.py"
)
GET_WEATHER_ACTION = (
    REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "get_weather" / "action.py"
)
DELIVERY_ACTION = (
    REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "delivery" / "action.py"
)
IMAGE2TEXT_INIT = REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "image2text" / "__init__.py"
TEXT2IMAGE_INIT = REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "text2image" / "__init__.py"
SEND_EMAIL_CLI = REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "tools" / "send_email" / "cli.py"
REMOTE_PROXY_MAIN = (
    REPO_ROOT / "src" / "backend" / "zuno" / "capability" / "mcp" / "servers" / "remote_proxy" / "main.py"
)
KNOWLEDGE_LEGACY_CUTOVER = REPO_ROOT / "src" / "backend" / "zuno" / "knowledge" / "ingestion" / "legacy_cutover.py"
SANDBOX_INIT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "sandbox" / "__init__.py"
CAPABILITY_REGISTRY = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "capability_registry.py"
UPLOAD_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "upload.py"
KNOWLEDGE_FILE_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "knowledge_file.py"
WORKSPACE_SESSION_SERVICE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "workspace_session.py"
)
USER_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "user.py"
TOOL_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "tool.py"
KNOWLEDGE_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "knowledge.py"
AGENT_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "agent.py"
HISTORY_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "history.py"
LLM_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "llm.py"
MCP_SERVER_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "mcp_server.py"
MESSAGE_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "message.py"
DIALOG_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "dialog.py"
MESSAGE_EVENTS_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "message_events.py"
MCP_USER_CONFIG_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "mcp_user_config.py"
MCP_STDIO_SERVER_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "mcp_stdio_server.py"
USAGE_STATS_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "usage_stats.py"
MCP_AGENT_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "mcp_agent.py"
CAPABILITY_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "capability.py"
AGENT_SKILL_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "agent_skill.py"
COMPLETION_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "completion.py"
WECHAT_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "wechat.py"
MCP_CHAT_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "mcp_chat.py"
CLI_TOOL_DISCOVERY = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "cli_tool_discovery.py"
SIMPLE_API_TOOL = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "simple_api_tool.py"
TOOL_CREATION_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "tool_creation_service.py"
TOOL_CONNECTIVITY_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "tool_connectivity_service.py"
USER_DEFINED_TOOL_RUNTIME = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "user_defined_tool_runtime.py"
INIT_DATA = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "database" / "init_data.py"
MCP_MANAGER = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "mcp" / "manager.py"
MCP_MULTI_CLIENT = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "mcp" / "multi_client.py"
MCP_LOAD_TOOLS = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "mcp" / "load_mcp" / "tools.py"
MCP_OPENAI_MANAGER = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "mcp_openai" / "mcp_manager.py"
MCP_OPENAI_UTIL = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "services" / "mcp_openai" / "mcp_util.py"
AGENT_CORE_FILES = [
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "__init__.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "agents" / "codeact_agent.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "agents" / "general_agent.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "agents" / "plan_execute_agent.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "agents" / "react_agent.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "agents" / "structured_response_agent.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "callbacks" / "__init__.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "callbacks" / "usage_metadata.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "models" / "__init__.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "models" / "manager.py",
    REPO_ROOT / "src" / "backend" / "zuno" / "agent" / "core" / "models" / "usage_model.py",
]
CURRENT_PROGRAM = REPO_ROOT / ".agent" / "programs" / "current.md"
MANIFEST = REPO_ROOT / ".agent" / "programs" / "program-manifest.yaml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_phase22_cleanup_boundary() -> list[str]:
    errors: list[str] = []

    if not WORK_PRODUCT.exists():
        errors.append("missing phase22 removal candidates work product")
    else:
        candidates = _read(WORK_PRODUCT)
        for phrase in [
            "status: frozen_from_phase21_runtime_and_phase22_startup_scan",
            "src/backend/zuno/platform/compatibility/legacy_aliases.py",
            "tests/legacy_guards/",
            "legacy_general_agent_completion_rollback",
            "src/backend/zuno/product/runtime_batch.py",
            "src/backend/zuno/api/services/product/command_service.py",
            "src/backend/zuno/api/services/workspace.py",
            "src/backend/zuno/platform/services/workspace/attachment_service.py",
            "src/backend/zuno/platform/services/workspace/",
            "src/backend/zuno/capability/tools/convert_to_docx/action.py",
            "src/backend/zuno/capability/tools/convert_to_pdf/action.py",
            "src/backend/zuno/capability/tools/get_weather/action.py",
            "src/backend/zuno/capability/tools/delivery/action.py",
            "src/backend/zuno/api/services/upload.py",
            "src/backend/zuno/api/services/knowledge_file.py",
            "src/backend/zuno/api/services/workspace_session.py",
            "src/backend/zuno/api/services/user.py",
            "src/backend/zuno/api/services/tool.py",
            "src/backend/zuno/api/services/knowledge.py",
            "src/backend/zuno/api/services/agent.py",
            "src/backend/zuno/api/services/history.py",
            "src/backend/zuno/api/services/llm.py",
            "src/backend/zuno/api/services/mcp_server.py",
            "src/backend/zuno/api/services/message.py",
            "src/backend/zuno/api/services/dialog.py",
            "src/backend/zuno/api/services/message_events.py",
            "src/backend/zuno/api/services/mcp_user_config.py",
            "src/backend/zuno/api/services/mcp_stdio_server.py",
            "src/backend/zuno/api/services/usage_stats.py",
            "src/backend/zuno/api/services/mcp_agent.py",
            "src/backend/zuno/api/services/capability.py",
            "src/backend/zuno/api/services/agent_skill.py",
            "src/backend/zuno/api/services/completion.py",
            "src/backend/zuno/api/services/wechat.py",
            "src/backend/zuno/api/services/mcp_chat.py",
            "src/backend/zuno/platform/database/",
            "src/backend/zuno/platform/services/application/knowledge/",
            "src/backend/zuno/platform/services/rewrite/",
            "src/backend/zuno/platform/services/pipeline/",
            "src/backend/zuno/platform/services/graphrag/community/",
            "src/backend/zuno/platform/services/graphrag/extractors/",
            "src/backend/zuno/platform/services/graphrag/graph_store/__init__.py",
            "src/backend/zuno/platform/services/graphrag/prompts/__init__.py",
            "src/backend/zuno/platform/services/graphrag/retrievers/",
            "src/backend/zuno/platform/services/graphrag/project/loader.py",
            "src/backend/zuno/platform/services/graphrag/query_service.py",
            "src/backend/zuno/platform/services/graphrag/orchestrator.py",
            "src/backend/zuno/platform/services/graphrag/retriever.py",
            "src/backend/zuno/platform/services/retrieval/",
            "src/backend/zuno/platform/services/rag/",
            "src/backend/zuno/platform/services/memory/",
            "src/backend/zuno/platform/services/sandbox/__init__.py",
            "src/backend/zuno/platform/services/capability_registry.py",
            "src/backend/zuno/knowledge/ingestion/legacy_cutover.py",
            "src/backend/zuno/capability/mcp/servers/remote_proxy/main.py",
            "src/backend/zuno/capability/tools/image2text/__init__.py",
            "src/backend/zuno/capability/tools/text2image/__init__.py",
            "src/backend/zuno/capability/tools/send_email/cli.py",
            "src/backend/zuno/platform/services/embedding/__init__.py",
            "src/backend/zuno/platform/services/llm/__init__.py",
            "src/backend/zuno/platform/services/convert_files/__init__.py",
            "src/backend/zuno/platform/services/queue/workers.py",
            "src/backend/zuno/platform/services/queue/messages.py",
            "src/backend/zuno/platform/services/queue/runner.py",
            "src/backend/zuno/platform/services/deepsearch/",
            "src/backend/zuno/platform/services/autobuild/",
            "src/backend/zuno/agent/runtime/",
            "src/backend/zuno/platform/common/",
            "src/backend/zuno/platform/middleware/",
            "src/backend/zuno/platform/model_gateway.py",
            "src/backend/zuno/platform/model_gateway_adapters.py",
            "tools/evals/zuno/",
            "tools/scripts/check_model_registry_defaults.py",
            "tools/scripts/cleanup_model_registry_defaults.py",
            "tools/scripts/rebuild_rag_indexes.py",
            "tools/scripts/verify_phase04_minio_manifest_adoption.py",
            "infra/db/alembic/env.py",
            "tests/tools/",
            "tests/storage/",
            "tests/agent/test_agent_api_project_contract.py",
            "tests/agent/test_agent_empty_workspace.py",
            "tests/agent/test_agent_layer_surfaces.py",
            "tests/agent/test_capability_layer_surfaces.py",
            "tests/agent/test_capability_registry.py",
            "tests/agent/test_capability_system.py",
            "tests/agent/test_completion_agent_config_compatibility.py",
            "tests/agent/test_context_contracts.py",
            "tests/agent/test_context_orchestrator.py",
            "tests/agent/test_general_agent_project_query_runtime.py",
            "tests/agent/test_generalagent_context_memory_runtime.py",
            "tests/agent/test_hooks_evidence_trace_artifacts.py",
            "tests/agent/test_knowledge_graphrag_runtime_contracts.py",
            "tests/agent/test_knowledge_layer_surfaces.py",
            "tests/agent/test_memory_layer_surfaces.py",
            "tests/agent/test_memory_layers.py",
            "tests/agent/test_mcp_server_service.py",
            "tests/agent/test_mcp_stdio_server_security.py",
            "tests/agent/test_phase05_admin_action_reauthorization.py",
            "tests/agent/test_platform_layer_surfaces.py",
            "tests/agent/test_runtime_observability.py",
            "tests/agent/test_workspace_project_query_runtime.py",
            "tests/agent/test_workspace_simple_agent.py",
            "tests/agent/test_workspace_usage_agent_name.py",
            "tests/agent/test_workspace_session_api.py",
            "tests/agent/test_workspace_session_cleanup.py",
            "tests/api/test_completion_unified_runtime.py",
            "tests/api/test_goal03_knowledge_route.py",
            "tests/api/test_knowledge_api_contract.py",
            "tests/api/test_usage_stats_filters.py",
            "tests/api/test_workspace_agentic_product_contract.py",
            "tests/api/test_workspace_product_loop_contract.py",
            "tests/api/test_workspace_runtime_recovery.py",
            "tests/api/test_workspace_task_runtime.py",
            "tests/e2e/test_unified_agent_product_scenario.py",
            "tests/evals/test_local_runtime_registry.py",
            "tests/evals/test_phase5_deep_graphrag_eval_surface.py",
            "tests/evals/test_rag_eval_metrics.py",
            "tests/evals/test_stackless_local_eval_contract_project_query_policy.py",
            "tests/evals/test_stackless_local_eval_project_assets.py",
            "tests/evals/test_stackless_local_eval_project_guard.py",
            "tests/evals/test_stackless_local_eval_rerank_runtime.py",
            "tests/frontend/test_product_wiring_v1_api_contract.py",
            "tests/frontend/test_phase1_knowledge_product_skeleton.py",
            "tests/graphrag/test_contract_graph_query_routing.py",
            "tests/graphrag/test_contract_graph_retriever.py",
            "tests/graphrag/test_contract_review_project_payload.py",
            "tests/graphrag/test_2wiki_missed_opportunity_activation.py",
            "tests/graphrag/test_graphrag.py",
            "tests/graphrag/test_graphrag_baseline_preserving_fusion.py",
            "tests/graphrag/test_graphrag_bridge_guardrail.py",
            "tests/graphrag/test_graphrag_chain_aware_fusion.py",
            "tests/graphrag/test_graphrag_comparison_guardrail.py",
            "tests/graphrag/test_graphrag_entity_alias.py",
            "tests/graphrag/test_graphrag_genealogy_guardrail.py",
            "tests/graphrag/test_graphrag_genealogy_path_precision.py",
            "tests/graphrag/test_graphrag_index_versioning.py",
            "tests/graphrag/test_graphrag_path_ranking.py",
            "tests/graphrag/test_graphrag_project_contracts.py",
            "tests/graphrag/test_graphrag_project_loader.py",
            "tests/graphrag/test_graphrag_prompt_registry.py",
            "tests/graphrag/test_graphrag_route_activation_calibration.py",
            "tests/graphrag/test_graphrag_seed_expansion.py",
            "tests/graphrag/test_structured_graph_extractor_contract.py",
            "tests/knowledge/test_parse_gateway_runtime.py",
            "tests/integration/test_goal03_wave_a_persistence.py",
            "tests/repo/test_llm_system_sync.py",
            "tests/repo/test_graph_store_project_id_migration.py",
            "tests/repo/test_hardening01_config_impact_contract.py",
            "tests/repo/test_model_gateway_bypass.py",
            "tests/repo/test_phase11c_domain_pack_api_retirement.py",
            "tests/repo/test_phase11c_graph_public_export_retirement.py",
            "tests/repo/test_phase25_legacy_boundary_hardening.py",
            "tests/repo/test_phase5_domain_runtime_paths.py",
            "tests/repo/test_phase5_general_agent_real_runtime_flow.py",
            "tests/repo/test_phase5_workspace_real_runtime_flow.py",
            "tests/repo/test_phase6_bundle_scope.py",
            "tests/repo/test_phase5_docs_public_explanation_sync.py",
            "tests/repo/test_zuno_canonical_import_surfaces.py",
            "tests/retrieval/test_query_rewrite.py",
            "tests/retrieval/test_enhanced_requery_activation.py",
            "tests/retrieval/test_enhanced_requery_precision_gate.py",
            "tests/retrieval/test_enhanced_standard_floor_invariance.py",
            "tests/retrieval/test_enhanced_retrieval_composition.py",
            "tests/retrieval/test_graph_retriever_local_runtime.py",
            "tests/retrieval/test_rerank_fallback.py",
            "tests/retrieval/test_retrieval_fusion.py",
            "tests/retrieval/test_retrieval_orchestrator.py",
            "tests/retrieval/test_retrieval_planner.py",
            "tests/retrieval/test_standard_retrieval_composition.py",
            "tests/retrieval/test_workspace_retrieval_trace.py",
            "src/backend/zuno/capability/tools/send_email/manifest.yaml",
            "src/backend/zuno/platform/services/application/__init__.py",
            "src/backend/zuno/platform/settings.py",
            "src/backend/zuno/main.py",
            "src/backend/zuno/memory/feedback_consumer.py",
            "src/backend/zuno/agent/product_baseline.py",
            "src/backend/zuno/api/services/workspace_task_runtime.py",
            "src/backend/zuno/api/dto/knowledge.py",
            "src/backend/zuno/platform/services/cli_tool_discovery.py",
            "src/backend/zuno/platform/services/simple_api_tool.py",
            "src/backend/zuno/platform/services/tool_creation_service.py",
            "src/backend/zuno/platform/services/tool_connectivity_service.py",
            "src/backend/zuno/platform/services/user_defined_tool_runtime.py",
            "src/backend/zuno/platform/database/init_data.py",
            "src/backend/zuno/platform/services/mcp/manager.py",
            "src/backend/zuno/platform/services/mcp/multi_client.py",
            "src/backend/zuno/platform/services/mcp/load_mcp/tools.py",
            "src/backend/zuno/platform/services/mcp_openai/mcp_manager.py",
            "src/backend/zuno/platform/services/mcp_openai/mcp_util.py",
            "src/backend/zuno/agent/core/agents/codeact_agent.py",
            "src/backend/zuno/agent/__init__.py",
            "src/backend/zuno/agent/core/agents/general_agent.py",
            "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
            "src/backend/zuno/agent/core/agents/react_agent.py",
            "src/backend/zuno/agent/core/agents/structured_response_agent.py",
            "src/backend/zuno/agent/core/callbacks/usage_metadata.py",
            "src/backend/zuno/agent/core/models/manager.py",
            "src/backend/zuno/agent/core/models/usage_model.py",
            "src/backend/zuno/api/v1/",
            "src/backend/zuno/api/errcode/",
            "remaining_not_closed:",
        ]:
            if phrase not in candidates:
                errors.append(f"phase22 removal candidates missing phrase: {phrase}")

    runtime_batch = _read(PRODUCT_RUNTIME_BATCH)
    if "from zuno.schema.workspace import" in runtime_batch:
        errors.append("product runtime batch still imports workspace DTO through zuno.schema alias")
    if "from zuno.api.dto.workspace import" not in runtime_batch:
        errors.append("product runtime batch missing canonical workspace DTO import")

    command_service = _read(PRODUCT_COMMAND_SERVICE)
    if "from zuno.database import engine" in command_service:
        errors.append("product command service still imports engine through zuno.database alias")
    if "from zuno.platform.database import engine" not in command_service:
        errors.append("product command service missing canonical platform database import")

    alias_imports = [
        "from zuno.schema.",
        "import zuno.schema.",
        "from zuno.core.",
        "import zuno.core.",
        "from zuno.services.",
        "import zuno.services.",
        "from zuno.database import",
        "from zuno.database.",
        "import zuno.database.",
        "from zuno.tools.",
        "import zuno.tools.",
        "from zuno.utils.",
        "import zuno.utils.",
        "from zuno.resources.",
        "import zuno.resources.",
    ]
    checked_paths = [
        ("workspace service", WORKSPACE_SERVICE),
        ("workspace attachment service", ATTACHMENT_SERVICE),
        ("storage facade", STORAGE_FACADE),
        ("text2image action", TEXT_TO_IMAGE_ACTION),
        ("convert_to_docx action", CONVERT_TO_DOCX_ACTION),
        ("convert_to_pdf action", CONVERT_TO_PDF_ACTION),
        ("get_weather action", GET_WEATHER_ACTION),
        ("delivery action", DELIVERY_ACTION),
        ("image2text init", IMAGE2TEXT_INIT),
        ("text2image init", TEXT2IMAGE_INIT),
        ("send email cli", SEND_EMAIL_CLI),
        ("remote mcp proxy main", REMOTE_PROXY_MAIN),
        ("knowledge legacy cutover", KNOWLEDGE_LEGACY_CUTOVER),
        ("sandbox init", SANDBOX_INIT),
        ("capability registry", CAPABILITY_REGISTRY),
        ("upload service", UPLOAD_SERVICE),
        ("knowledge file service", KNOWLEDGE_FILE_SERVICE),
        ("workspace session service", WORKSPACE_SESSION_SERVICE),
        ("user service", USER_SERVICE),
        ("tool service", TOOL_SERVICE),
        ("knowledge service", KNOWLEDGE_SERVICE),
        ("agent service", AGENT_SERVICE),
        ("history service", HISTORY_SERVICE),
        ("llm service", LLM_SERVICE),
        ("mcp server service", MCP_SERVER_SERVICE),
        ("message service", MESSAGE_SERVICE),
        ("dialog service", DIALOG_SERVICE),
        ("message events service", MESSAGE_EVENTS_SERVICE),
        ("mcp user config service", MCP_USER_CONFIG_SERVICE),
        ("mcp stdio server service", MCP_STDIO_SERVER_SERVICE),
        ("usage stats service", USAGE_STATS_SERVICE),
        ("mcp agent service", MCP_AGENT_SERVICE),
        ("capability service", CAPABILITY_SERVICE),
        ("agent skill service", AGENT_SKILL_SERVICE),
        ("completion service", COMPLETION_SERVICE),
        ("wechat service", WECHAT_SERVICE),
        ("mcp chat service", MCP_CHAT_SERVICE),
        ("main entrypoint", MAIN_ENTRYPOINT),
        ("memory feedback consumer", MEMORY_FEEDBACK_CONSUMER),
        ("agent product baseline", AGENT_PRODUCT_BASELINE),
        ("workspace task runtime service", WORKSPACE_TASK_RUNTIME_SERVICE),
        ("knowledge dto", KNOWLEDGE_DTO),
        ("cli tool discovery", CLI_TOOL_DISCOVERY),
        ("simple api tool", SIMPLE_API_TOOL),
        ("tool creation service", TOOL_CREATION_SERVICE),
        ("tool connectivity service", TOOL_CONNECTIVITY_SERVICE),
        ("user defined tool runtime", USER_DEFINED_TOOL_RUNTIME),
        ("init data", INIT_DATA),
        ("mcp manager", MCP_MANAGER),
        ("mcp multi client", MCP_MULTI_CLIENT),
        ("mcp load tools", MCP_LOAD_TOOLS),
        ("mcp openai manager", MCP_OPENAI_MANAGER),
        ("mcp openai util", MCP_OPENAI_UTIL),
    ] + [(f"agent core {path.name}", path) for path in AGENT_CORE_FILES]
    checked_paths.extend((f"api v1 {path.name}", path) for path in sorted(API_V1_ROOT.glob("*.py")))
    checked_paths.extend((f"api errcode {path.name}", path) for path in sorted(API_ERRCODE_ROOT.glob("*.py")))
    checked_paths.extend(
        (f"platform database {path.relative_to(PLATFORM_DATABASE_ROOT)}", path)
        for path in sorted(PLATFORM_DATABASE_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform application knowledge {path.relative_to(PLATFORM_APPLICATION_KNOWLEDGE_ROOT)}", path)
        for path in sorted(PLATFORM_APPLICATION_KNOWLEDGE_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform rewrite {path.relative_to(PLATFORM_REWRITE_ROOT)}", path)
        for path in sorted(PLATFORM_REWRITE_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform pipeline {path.relative_to(PLATFORM_PIPELINE_ROOT)}", path)
        for path in sorted(PLATFORM_PIPELINE_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform graphrag community {path.relative_to(PLATFORM_GRAPHRAG_COMMUNITY_ROOT)}", path)
        for path in sorted(PLATFORM_GRAPHRAG_COMMUNITY_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform graphrag extractors {path.relative_to(PLATFORM_GRAPHRAG_EXTRACTORS_ROOT)}", path)
        for path in sorted(PLATFORM_GRAPHRAG_EXTRACTORS_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform graphrag retrievers {path.relative_to(PLATFORM_GRAPHRAG_RETRIEVERS_ROOT)}", path)
        for path in sorted(PLATFORM_GRAPHRAG_RETRIEVERS_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        [
            ("platform graphrag graph store init", PLATFORM_GRAPHRAG_GRAPH_STORE_INIT),
            ("platform graphrag prompts init", PLATFORM_GRAPHRAG_PROMPTS_INIT),
            ("platform graphrag project loader", PLATFORM_GRAPHRAG_PROJECT_LOADER),
            ("platform graphrag query service", PLATFORM_GRAPHRAG_QUERY_SERVICE),
            ("platform graphrag orchestrator", PLATFORM_GRAPHRAG_ORCHESTRATOR),
            ("platform graphrag retriever", PLATFORM_GRAPHRAG_RETRIEVER),
            ("platform embedding init", EMBEDDING_INIT),
            ("platform llm init", LLM_INIT),
            ("platform convert files init", CONVERT_FILES_INIT),
            ("platform queue workers", QUEUE_WORKERS),
            ("platform queue messages", QUEUE_MESSAGES),
            ("platform queue runner", QUEUE_RUNNER),
        ]
    )
    checked_paths.extend(
        (f"platform retrieval {path.relative_to(PLATFORM_RETRIEVAL_ROOT)}", path)
        for path in sorted(PLATFORM_RETRIEVAL_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform rag {path.relative_to(PLATFORM_RAG_ROOT)}", path)
        for path in sorted(PLATFORM_RAG_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform memory {path.relative_to(PLATFORM_MEMORY_ROOT)}", path)
        for path in sorted(PLATFORM_MEMORY_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform workspace {path.relative_to(PLATFORM_WORKSPACE_ROOT)}", path)
        for path in sorted(PLATFORM_WORKSPACE_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform deepsearch {path.relative_to(PLATFORM_DEEPSEARCH_ROOT)}", path)
        for path in sorted(PLATFORM_DEEPSEARCH_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform autobuild {path.relative_to(PLATFORM_AUTOBUILD_ROOT)}", path)
        for path in sorted(PLATFORM_AUTOBUILD_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"agent runtime {path.relative_to(AGENT_RUNTIME_ROOT)}", path)
        for path in sorted(AGENT_RUNTIME_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform common {path.relative_to(PLATFORM_COMMON_ROOT)}", path)
        for path in sorted(PLATFORM_COMMON_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform middleware {path.relative_to(PLATFORM_MIDDLEWARE_ROOT)}", path)
        for path in sorted(PLATFORM_MIDDLEWARE_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"platform config {path.relative_to(PLATFORM_CONFIG_ROOT)}", path)
        for path in sorted(PLATFORM_CONFIG_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        [
            ("platform model gateway", PLATFORM_MODEL_GATEWAY),
            ("platform model gateway adapters", PLATFORM_MODEL_GATEWAY_ADAPTERS),
        ]
    )
    checked_paths.extend(
        (f"tools evals zuno {path.relative_to(TOOLS_EVALS_ZUNO_ROOT)}", path)
        for path in sorted(TOOLS_EVALS_ZUNO_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"tools scripts canonical {path.name}", path)
        for path in TOOLS_SCRIPTS_CANONICAL_FILES
    )
    checked_paths.append(("infra alembic env", INFRA_ALEMBIC_ENV))
    checked_paths.extend(
        (f"tests tools {path.relative_to(TESTS_TOOLS_ROOT)}", path)
        for path in sorted(TESTS_TOOLS_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"tests storage {path.relative_to(TESTS_STORAGE_ROOT)}", path)
        for path in sorted(TESTS_STORAGE_ROOT.rglob("*.py"))
    )
    checked_paths.extend(
        (f"tests agent canonical {path.name}", path)
        for path in TESTS_AGENT_CANONICAL_FILES
    )
    checked_paths.extend(
        (f"tests api canonical {path.name}", path)
        for path in TESTS_API_CANONICAL_FILES
    )
    checked_paths.extend(
        (f"tests e2e canonical {path.name}", path)
        for path in TESTS_E2E_CANONICAL_FILES
    )
    checked_paths.extend(
        (f"tests frontend canonical {path.name}", path)
        for path in TESTS_FRONTEND_CANONICAL_FILES
    )
    checked_paths.extend(
        (f"tests evals canonical {path.name}", path)
        for path in TESTS_EVALS_CANONICAL_FILES
    )
    checked_paths.extend(
        (f"tests knowledge canonical {path.name}", path)
        for path in TESTS_KNOWLEDGE_CANONICAL_FILES
    )
    checked_paths.extend(
        (f"tests integration canonical {path.name}", path)
        for path in TESTS_INTEGRATION_CANONICAL_FILES
    )
    checked_paths.extend(
        (f"tests repo canonical {path.name}", path)
        for path in TESTS_REPO_CANONICAL_FILES
    )
    checked_paths.extend(
        (f"tests graphrag canonical {path.name}", path)
        for path in TESTS_GRAPHRAG_CANONICAL_FILES
    )
    checked_paths.extend(
        (f"tests retrieval canonical {path.name}", path)
        for path in TESTS_RETRIEVAL_CANONICAL_FILES
    )
    checked_paths.append(("platform application init", PLATFORM_APPLICATION_INIT))
    checked_paths.append(("platform settings", PLATFORM_SETTINGS))

    for label, path in checked_paths:
        text = _read(path)
        for alias_import in alias_imports:
            if alias_import in text:
                errors.append(f"{label} still imports through legacy alias: {alias_import}")

    send_email_manifest = _read(SEND_EMAIL_MANIFEST)
    if "zuno.tools.send_email" in send_email_manifest or "src/backend/zuno/tools/send_email" in send_email_manifest:
        errors.append("send email manifest still points at legacy zuno.tools path")
    if "zuno.capability.tools.send_email.cli" not in send_email_manifest:
        errors.append("send email manifest missing canonical capability tool entry module")

    current = _read(CURRENT_PROGRAM)
    manifest = _read(MANIFEST)
    for label, text in [("current.md", current), ("program-manifest.yaml", manifest)]:
        if "current_phase: PHASE22" not in text:
            errors.append(f"{label} missing PHASE22 current phase")

    return errors


def main() -> int:
    errors = verify_phase22_cleanup_boundary()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE22 cleanup boundary verification failed.")
        return 1
    print("PHASE22 cleanup boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

COMPLETED_PROGRAM_NAME = "zuno-eight-deliverables-full-realization-v1"
COMPLETED_PROGRAM_ARCHIVE = f"docs/history/programs/{COMPLETED_PROGRAM_NAME}"
COMPLETED_PROGRAM_PHASE_FILES = [
    "PHASE01_program-boot-baseline.md",
    "PHASE02_workflow-self-maintenance-system.md",
    "PHASE03_architecture-docs-html-system.md",
    "PHASE04_query-router-mode-policy.md",
    "PHASE05_context-builder-memory-system.md",
    "PHASE06_capability-toolcard-mcp-system.md",
    "PHASE07_hooks-evidence-trace-artifact-system.md",
    "PHASE08_graphrag-knowledge-runtime-system.md",
    "PHASE09_runtime-upgrade-integration.md",
    "PHASE10_validation-release-closure.md",
]
MASTER_PROGRAM_NAME = "zuno-master-architecture-implementation-v1"
MASTER_PROGRAM_ARCHIVE = f"docs/history/programs/{MASTER_PROGRAM_NAME}"
MASTER_PROGRAM_PHASE_FILES = [
    "PHASE01_program-baseline-and-previous-closure.md",
    "PHASE02_project-folder-and-code-layout-cleanup.md",
    "PHASE03_enterprise-scenario-and-product-loop.md",
    "PHASE04_document-ingestion-parse-gateway.md",
    "PHASE05_agent-runtime-langgraph-harness.md",
    "PHASE06_context-memory-system.md",
    "PHASE07_tool-control-plane-mcp-approval.md",
    "PHASE08_rag-graphrag-evidence-citation.md",
    "PHASE09_security-governance-sandbox.md",
    "PHASE10_eval-observability-langsmith.md",
    "PHASE11_architecture-docs-html-refresh.md",
    "PHASE12_validation-release-closure.md",
]
RUNTIME_PROGRAM_NAME = "zuno-target-architecture-runtime-full-implementation-v1"
RUNTIME_PROGRAM_ARCHIVE = f"docs/history/programs/{RUNTIME_PROGRAM_NAME}"
RUNTIME_PROGRAM_PHASE_FILES = [
    "PHASE01_program-reopen-and-truth-source-freeze.md",
    "PHASE02_runtime-migration-map-and-repo-ownership-lock.md",
    "PHASE03_task-session-artifact-event-runtime.md",
    "PHASE04_document-ingestion-parse-runtime.md",
    "PHASE05_index-jobs-and-knowledge-space-runtime.md",
    "PHASE06_durable-single-controller-runtime.md",
    "PHASE07_memory-db-and-context-governance.md",
    "PHASE08_tool-control-plane-approval-and-sandbox-runtime.md",
    "PHASE09_agentic-retrieval-evidence-citation-runtime.md",
    "PHASE10_security-observability-and-online-eval.md",
    "PHASE11_web-desktop-surface-and-feedback-loop.md",
    "PHASE12_release-gate-full-e2e-closure.md",
]
RUNTIME_PROGRAM_FILES = [
    "README.md",
    "current.md",
]
ACTIVE_PROGRAM_NAME = "zuno-production-architecture-and-deliverables-completion-v1"
ACTIVE_PROGRAM_ARCHIVE = f"docs/history/programs/{ACTIVE_PROGRAM_NAME}"
ACTIVE_PROGRAM_PHASE_FILES = [
    "PHASE01_production-maturity-gap-audit.md",
    "PHASE02_program-truth-source-and-execution-system.md",
    "PHASE03_workflow-self-maintenance-automation.md",
    "PHASE04_documentation-dedup-architecture-clarity.md",
    "PHASE05_repo-ownership-and-compatibility-retirement.md",
    "PHASE06_product-surface-desktop-recovery-loop.md",
    "PHASE07_production-parse-and-index-platform.md",
    "PHASE08_durable-agent-runtime-persistence.md",
    "PHASE09_memory-context-production-governance.md",
    "PHASE10_tool-sandbox-vault-network-runtime.md",
    "PHASE11_production-graphrag-evidence-citation.md",
    "PHASE12_security-trace-eval-release-closure.md",
]
ACTIVE_PROGRAM_FILES = [
    "README.md",
    "current.md",
    "implementation-roadmap.md",
    "closure-checklist.md",
    "PHASE01_truth-source-and-merge-plan.md",
    "PHASE02_shared-contract-freeze.md",
    "PHASE03_enterprise-ingestion-async-infrastructure.md",
    "PHASE04_knowledge-retrieval-and-graphrag-profile.md",
    "PHASE05_memory-context-engine.md",
    "PHASE06_capability-skill-tool-mcp-layer.md",
    "PHASE07_security-governance-envelope.md",
    "PHASE08_model-gateway-cost-latency.md",
    "PHASE09_planning-contract-and-strategy-selector.md",
    "PHASE10_react-reflection-replan-reflexion-runtime.md",
    "PHASE11_workspace-product-api-frontend-sync.md",
    "PHASE12_end-to-end-product-runtime.md",
    "PHASE13_eval-trace-cost-benchmark.md",
    "PHASE14_docs-architecture-expansion.md",
    "PHASE15_verification-archive-closure.md",
]
PROGRAM3_ACTIVE_NAME = "zuno-launchable-enterprise-agentic-graphrag-full-closure-v1"
PROGRAM3_ACTIVE_PHASE_FILES = ACTIVE_PROGRAM_FILES[4:]
LATEST_COMPLETED_PROGRAM_NAME = "zuno-enterprise-document-ingestion-platform-v2"
LATEST_COMPLETED_PROGRAM_ARCHIVE = f"docs/history/programs/{LATEST_COMPLETED_PROGRAM_NAME}"
LATEST_COMPLETED_PROGRAM_PHASE_FILES = [
    "PHASE01_truth-source-and-gap-audit.md",
    "PHASE02_durable-storage-contract.md",
    "PHASE03_workspace-file-durable-input.md",
    "PHASE04_parse-document-persistence.md",
    "PHASE05_index-persistence-rehydrate.md",
    "PHASE06_workspace-product-durable-closure.md",
    "PHASE07_restart-recovery-end-to-end.md",
    "PHASE08_docs-verifier-closure.md",
]
CURRENT_ACTIVE_PROGRAM_NAME = "zuno-production-document-ingestion-and-thread-foundation-v1"
CURRENT_ACTIVE_PROGRAM_ARCHIVE = f"docs/history/programs/{CURRENT_ACTIVE_PROGRAM_NAME}"
CURRENT_ACTIVE_PROGRAM_PHASE_FILES = [
    "PHASE01_program-truth-source-and-parser-current-audit.md",
    "PHASE02_document-ir-and-parser-contract-freeze.md",
    "PHASE03_parser-worker-runtime-and-job-lifecycle.md",
    "PHASE04_native-text-and-structured-file-parsers.md",
    "PHASE05_pdf-office-ocr-adapter-boundaries.md",
    "PHASE06_index-handoff-provenance-and-fixtures.md",
    "PHASE07_program2-thread-prompts-and-branch-plan.md",
    "PHASE08_verification-doc-sync-and-closure.md",
]
QUEUED_PROGRAM_FILES = [
    "README.md",
    "PROGRAM04_runtime-subsystems-parallel.md",
    "PROGRAM05_agent-planning-integration.md",
    "PROGRAM06_enterprise-knowledge-eval-benchmark.md",
]
THREAD_PROMPT_FILES = [
    "THREAD_A_memory-context.md",
    "THREAD_B_tool-sandbox.md",
    "THREAD_C_security-governance.md",
    "THREAD_D_graphrag-index.md",
]


def _current_phase_name(content: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("current_phase:"):
            return line.split(":", 1)[1].strip().strip("`")
    return None


def _assert_archived_phase_state() -> None:
    archive_root = REPO_ROOT / ACTIVE_PROGRAM_ARCHIVE
    for phase_name in ACTIVE_PROGRAM_PHASE_FILES:
        phase_text = (archive_root / phase_name).read_text(encoding="utf-8")
        assert "status: completed" in phase_text


def test_required_current_paths_exist() -> None:
    required_paths = [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/references/README.md",
        ".agent/references/project-map.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/references/docs-map.md",
        ".agent/references/architecture-docs-map.md",
        ".agent/references/documentation-governance.md",
        ".agent/references/architecture-update-policy.md",
        ".agent/references/diagram-inventory.md",
        ".agent/references/current-target-future-rules.md",
        ".agent/references/workflow-governance.md",
        ".agent/references/workflow-update-policy.md",
        ".agent/references/workflow-requirements.md",
        ".agent/references/workflow-change-log.md",
        ".agent/references/workflow-maintenance-checklist.md",
        ".agent/templates/architecture-doc-template.md",
        ".agent/templates/mermaid-diagram-template.md",
        ".agent/templates/architecture-change-note-template.md",
        ".agent/templates/verification-report-template.md",
        ".agent/templates/workflow-change-note-template.md",
        ".agent/programs/current.md",
        ".agent/programs/README.md",
        ".agent/programs/implementation-roadmap.md",
        ".agent/programs/closure-checklist.md",
        f"{ACTIVE_PROGRAM_ARCHIVE}/README.md",
        f"{ACTIVE_PROGRAM_ARCHIVE}/current.md",
        f"{ACTIVE_PROGRAM_ARCHIVE}/implementation-roadmap.md",
        f"{ACTIVE_PROGRAM_ARCHIVE}/closure-checklist.md",
        f"{ACTIVE_PROGRAM_ARCHIVE}/closure-summary.md",
        *[f"{ACTIVE_PROGRAM_ARCHIVE}/{phase_name}" for phase_name in ACTIVE_PROGRAM_PHASE_FILES],
        ".agent/architecture/README.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "apps/desktop",
        "apps/web",
        "docs/README.md",
        "docs/architecture/README.md",
        "docs/architecture/architecture.md",
        "docs/architecture/production-readiness.md",
        "docs/architecture/document-ingestion-foundation.md",
        "docs/architecture/architecture.html",
        "docs/architecture/repo-ownership-matrix.md",
        "docs/architecture/assets/zuno-agentic-rag-graphrag-ideal-architecture.pdf",
        "docs/history/architecture-surface-cleanup-2026-06-30/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/current-architecture.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/target-architecture.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/roadmap.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/deliverables.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/00-architecture-index.md",
        "docs/evidence/public-demo.md",
        "docs/reference/terminology.md",
        "docs/history/README.md",
        "docs/history/phases/README.md",
        "docs/history/plans/README.md",
        "docs/history/programs/README.md",
        "docs/history/development/README.md",
        "docs/history/reference/migration.md",
        "docs/history/audits",
        "docs/history/specs",
        "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml",
        "src/backend/zuno/main.py",
        "src/backend/zuno/knowledge/ingestion/README.md",
        "src/backend/zuno/platform/observability/README.md",
        "src/backend/zuno/platform/security/README.md",
        "src/backend/zuno/platform/vendor/README.md",
        "tools/agent/render_architecture.py",
        "tools/evals/zuno",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing required path: {relative_path}"


def test_repo_structure_verifier_pins_current_front_path() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    required_paths = set(verifier.REQUIRED_PATHS)
    for relative_path in [
        "AGENTS.md",
        ".agent/references/project-map.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/references/architecture-docs-map.md",
        ".agent/references/workflow-governance.md",
        "docs/README.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "docs/architecture/README.md",
        "docs/architecture/architecture.md",
        "docs/architecture/production-readiness.md",
        "docs/architecture/document-ingestion-foundation.md",
        "docs/architecture/architecture.html",
        "docs/architecture/repo-ownership-matrix.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/current-architecture.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/target-architecture.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/roadmap.md",
        "docs/evidence/public-demo.md",
        "docs/reference/terminology.md",
        "docs/history/audits",
        "docs/history/specs",
        "docs/history/development/README.md",
    ]:
        assert relative_path in required_paths


def test_repo_structure_verifier_pins_first_class_directory_responsibilities() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.TOP_LEVEL_RESPONSIBILITY_DIRECTORIES == {
        "tools": "维护脚本、验证器、eval、launcher、migration 和架构渲染工具",
        "tests": "自动化测试源和仓库边界 guardrails",
        "examples": "可运行示例和示例输入，不存放运行输出",
        "infra": "数据库、Docker 和本地基础设施配置，不存放运行态 volume/cache",
    }
    assert verifier.ALLOWED_RESPONSIBILITY_SUBDIRS == {
        "tools": ["agent", "cli", "evals", "launchers", "migrations", "scripts"],
        "tests": [
            "agent",
            "agent_system",
            "api",
            "capability",
            "evals",
            "fixtures",
            "frontend",
            "graphrag",
            "knowledge",
            "legacy_guards",
            "memory",
            "repo",
            "retrieval",
            "security",
            "storage",
            "tools",
        ],
        "examples": ["graphrag-projects"],
        "infra": ["db", "docker"],
    }


def test_repo_structure_verifier_pins_backend_zuno_directory_classifications() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS == {
        "api": "target-layer",
        "agent": "target-layer",
        "memory": "target-layer",
        "capability": "target-layer",
        "knowledge": "target-layer",
        "platform": "target-layer",
    }


def test_repo_structure_verifier_pins_backend_layer_internal_surfaces() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.BACKEND_LAYER_INTERNAL_SURFACES == {
        "api": {
            "directories": ["dto", "errcode", "services", "v1"],
            "files": ["JWT.py", "README.md", "__init__.py", "router.py"],
        },
        "agent": {
            "directories": ["core"],
            "files": [
                "README.md",
                "__init__.py",
                "context.py",
                "durable_runtime.py",
                "harness.py",
                "post_turn.py",
                "runtime.py",
                "state.py",
                "streaming.py",
                "tool_bridge.py",
            ],
        },
        "memory": {
            "directories": [],
            "files": [
                "README.md",
                "__init__.py",
                "contracts.py",
                "engine.py",
                "policy.py",
                "rendering.py",
                "retrieval.py",
                "review.py",
                "store.py",
            ],
        },
        "capability": {
            "directories": ["mcp", "tools"],
            "files": [
                "README.md",
                "__init__.py",
                "contracts.py",
                "execution.py",
                "control_plane.py",
                "policy.py",
                "registry.py",
                "retrieval.py",
                "runtime.py",
                "selector.py",
                "trace.py",
            ],
        },
        "knowledge": {
            "directories": ["fusion", "graphrag", "indexing", "ingestion", "retrieval"],
            "files": [
                "README.md",
                "__init__.py",
                "agentic_graphrag.py",
                "citation.py",
                "contracts.py",
                "evidence.py",
                "query_service.py",
                "trace.py",
            ],
        },
        "platform": {
            "directories": [
                "common",
                "compatibility",
                "config",
                "database",
                "middleware",
                "observability",
                "resources",
                "security",
                "services",
                "storage",
                "vendor",
            ],
            "files": ["README.md", "__init__.py", "model_gateway.py", "settings.py"],
        },
    }


def test_backend_owner_docs_do_not_reference_retired_physical_paths() -> None:
    api_readme = (REPO_ROOT / "src/backend/zuno/api/README.md").read_text(
        encoding="utf-8"
    )
    runtime_call_chain = (REPO_ROOT / ".agent/references/runtime-call-chain.md").read_text(
        encoding="utf-8"
    )
    verifier_source = (REPO_ROOT / "tools/scripts/verify_repo_structure.py").read_text(
        encoding="utf-8"
    )

    assert "src/backend/zuno/schema/" not in api_readme
    assert "src/backend/zuno/services/application/capabilities/" not in runtime_call_chain
    assert "src/backend/zuno/api/dto/" in api_readme
    assert "src/backend/zuno/platform/services/application/capabilities/" in runtime_call_chain
    assert "verify_backend_owner_docs_do_not_reference_retired_physical_paths" in verifier_source


def test_repo_structure_verifier_pins_phase02_ownership_contract() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.BACKEND_OWNERSHIP_MATRIX_PATH == "docs/architecture/repo-ownership-matrix.md"
    assert verifier.BACKEND_OWNERSHIP_MATRIX_REQUIRED_COLUMNS == [
        "current_path",
        "current_role",
        "target_owner",
        "target_path",
        "compat_path",
        "migration_risk",
        "tests",
        "verifier",
        "status",
    ]
    assert verifier.PHASE02_LEGACY_ALIAS_MATRIX_ROWS == {
        "zuno.schema.*": ("api/dto", "src/backend/zuno/api/dto", "legacy-alias-current"),
        "zuno.database.*": (
            "platform/database",
            "src/backend/zuno/platform/database",
            "legacy-alias-current",
        ),
        "zuno.services.*": (
            "platform/services",
            "src/backend/zuno/platform/services",
            "legacy-alias-current",
        ),
    }
    assert verifier.PHASE02_RUNTIME_DOMAIN_MATRIX_REQUIREMENTS == {
        "parser": [
            "src/backend/zuno/knowledge/ingestion",
            "src/backend/zuno/platform/services/convert_files",
            "src/backend/zuno/platform/services/pipeline",
        ],
        "retrieval": [
            "src/backend/zuno/knowledge",
            "src/backend/zuno/platform/services/rag",
            "src/backend/zuno/platform/services/retrieval",
            "src/backend/zuno/platform/services/deepsearch",
            "src/backend/zuno/platform/services/rewrite",
        ],
        "graphrag": [
            "src/backend/zuno/knowledge",
            "src/backend/zuno/platform/services/graphrag",
        ],
        "memory": [
            "src/backend/zuno/memory",
            "src/backend/zuno/platform/services/memory",
        ],
        "tool": [
            "src/backend/zuno/capability",
            "src/backend/zuno/platform/services/mcp",
            "src/backend/zuno/platform/services/mcp_openai",
            "src/backend/zuno/platform/services/sandbox",
        ],
        "database": [
            "src/backend/zuno/platform/database",
            "zuno.database.*",
        ],
        "workspace": [
            "src/backend/zuno/api",
            "src/backend/zuno/platform/services/workspace",
        ],
        "storage": [
            "src/backend/zuno/platform/storage",
            "src/backend/zuno/platform/services/storage",
        ],
        "queue": [
            "src/backend/zuno/platform/services/queue",
        ],
        "sandbox": [
            "src/backend/zuno/platform/security",
            "src/backend/zuno/platform/services/sandbox",
        ],
    }
    assert verifier.PHASE02_RESERVED_IMPORT_GUARD_PATHS == [
        "src/backend/zuno/platform/observability",
        "src/backend/zuno/platform/security",
        "src/backend/zuno/platform/vendor",
    ]


def test_repo_structure_verifier_pins_platform_services_target_owners() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.PLATFORM_SERVICES_TARGET_OWNERS == {
        "application": "api / knowledge / workspace",
        "autobuild": "capability / platform",
        "convert_files": "knowledge/ingestion",
        "deepsearch": "knowledge/retrieval",
        "embedding": "knowledge/retrieval / platform/model_gateway",
        "graphrag": "knowledge/graphrag",
        "lingseek": "capability/tools",
        "llm": "platform/model_gateway",
        "mcp": "capability/mcp",
        "mcp_openai": "capability/mcp",
        "memory": "memory",
        "pipeline": "knowledge/ingestion / platform/jobs",
        "queue": "platform/jobs",
        "rag": "knowledge/retrieval",
        "retrieval": "knowledge/retrieval",
        "rewrite": "knowledge/retrieval",
        "sandbox": "platform/security",
        "storage": "platform/storage",
        "workspace": "agent / platform/workspace",
    }


def test_repo_structure_verifier_pins_capability_provider_classifications() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.CAPABILITY_TOOL_PROVIDER_CLASSIFICATIONS == {
        "arxiv": "builtin-provider",
        "cli_tool": "executor-adapter",
        "convert_to_docx": "builtin-converter",
        "convert_to_pdf": "builtin-converter",
        "crawl_web": "builtin-web-provider",
        "delivery": "builtin-delivery-provider",
        "get_weather": "builtin-provider",
        "image2text": "model-provider-adapter",
        "openapi_tool": "api-provider-adapter",
        "resume_optimizer": "builtin-domain-tool",
        "send_email": "provider-adapter",
        "text2image": "model-provider-adapter",
        "web_reader": "builtin-web-provider",
        "web_search": "provider-adapter",
    }
    assert verifier.CAPABILITY_MCP_SERVER_CLASSIFICATIONS == {
        "arxiv": "mcp-provider",
        "lark_mcp": "mcp-provider",
        "qa_echo": "mcp-smoke-server",
        "remote_proxy": "mcp-compat-proxy",
        "weather": "mcp-provider",
    }


def test_backend_zuno_classified_directories_have_boundary_readmes() -> None:
    classified_directories = [
        "api",
        "agent",
        "memory",
        "capability",
        "knowledge",
        "platform",
    ]

    for directory in classified_directories:
        readme = REPO_ROOT / "src" / "backend" / "zuno" / directory / "README.md"
        assert readme.exists(), f"missing backend zuno boundary README: {directory}"
        content = readme.read_text(encoding="utf-8")
        for phrase in ["当前角色", "Target role", "禁止事项", "Focused tests"]:
            assert phrase in content, f"{readme.relative_to(REPO_ROOT)} missing phrase: {phrase}"


def test_backend_zuno_top_level_directories_match_classification_map() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    actual_directories = sorted(
        path.name
        for path in (REPO_ROOT / "src/backend/zuno").iterdir()
        if path.is_dir() and path.name != "__pycache__"
    )

    assert actual_directories == sorted(verifier.BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS)


def test_repo_structure_verifier_pins_backend_legacy_import_aliases() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.BACKEND_LEGACY_IMPORT_ALIASES == {
        "zuno.compatibility": "legacy imports route through zuno.platform.compatibility",
        "zuno.config": "legacy imports route through zuno.platform.config",
        "zuno.core": "legacy imports route through zuno.agent.core",
        "zuno.database": "legacy imports route through zuno.platform.database",
        "zuno.mcp_servers": "legacy imports route through zuno.capability.mcp.servers",
        "zuno.middleware": "legacy imports route through zuno.platform.middleware",
        "zuno.evals": "legacy imports route through tools/evals/zuno",
        "zuno.resources": "legacy imports route through zuno.platform.resources",
        "zuno.schema": "legacy imports route through zuno.api.dto",
        "zuno.services": "legacy imports route through zuno.platform.services",
        "zuno.settings": "legacy imports route through zuno.platform.settings",
        "zuno.tools": "legacy imports route through zuno.capability.tools",
        "zuno.utils": "legacy imports route through zuno.platform.common",
    }
    assert (
        REPO_ROOT / "src/backend/zuno/platform/compatibility/legacy_aliases.py"
    ).exists()


def test_repo_structure_verifier_pins_root_local_artifact_directories() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.ROOT_LOCAL_ARTIFACT_DIRECTORIES == {
        ".agents": "旧 Agent 入口或本地执行残留；当前唯一入口是 AGENTS.md",
        ".local": "本地配置、eval 和运行态产物；可以存在于本机但不能挡住仓库根目录",
        ".test-tmp": "测试 scratch 目录；可再生成且必须保持本地 ignored",
        "__pycache__": "Python bytecode cache；可再生成且不属于仓库结构",
        ".pytest_cache": "pytest 本地缓存；可再生成且不属于仓库结构",
        "node_modules": "依赖安装产物；根目录不提交也不作为项目结构展示",
    }


def test_first_class_directory_subdirs_match_allowed_responsibilities() -> None:
    allowed_subdirs = {
        "tools": {"agent", "cli", "evals", "launchers", "migrations", "scripts"},
        "tests": {
            "agent",
            "agent_system",
            "api",
            "capability",
            "evals",
            "fixtures",
            "frontend",
            "graphrag",
            "knowledge",
            "legacy_guards",
            "memory",
            "repo",
            "retrieval",
            "security",
            "storage",
            "tools",
        },
        "examples": {"graphrag-projects"},
        "infra": {"db", "docker"},
    }
    allowed_files = {
        "tools": {"__init__.py"},
        "tests": {"README.md", "conftest.py"},
        "examples": set(),
        "infra": set(),
    }

    for directory, expected_subdirs in allowed_subdirs.items():
        actual_subdirs = {
            path.name
            for path in (REPO_ROOT / directory).iterdir()
            if path.is_dir() and not path.name.startswith("__pycache__")
        }
        actual_files = {
            path.name
            for path in (REPO_ROOT / directory).iterdir()
            if path.is_file()
        }
        assert actual_subdirs == expected_subdirs
        assert actual_files == allowed_files[directory]


def test_repo_structure_verifier_runs_first_class_directory_responsibility_check(monkeypatch) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinel = "first-class responsibility check was called"

    def fake_responsibility_check() -> list[str]:
        return [sentinel]

    monkeypatch.setattr(
        verifier,
        "verify_first_class_directory_responsibilities",
        fake_responsibility_check,
    )

    result = verifier.run_verification()

    assert sentinel in result.errors


def test_repo_structure_verifier_runs_backend_zuno_directory_classification_check(monkeypatch) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinel = "backend zuno directory classification check was called"

    def fake_backend_classification_check() -> list[str]:
        return [sentinel]

    monkeypatch.setattr(
        verifier,
        "verify_backend_zuno_directory_classifications",
        fake_backend_classification_check,
    )

    result = verifier.run_verification()

    assert sentinel in result.errors


def test_repo_structure_verifier_runs_backend_layer_internal_surface_check(monkeypatch) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinel = "backend layer internal surface check was called"

    def fake_backend_internal_surface_check() -> list[str]:
        return [sentinel]

    monkeypatch.setattr(
        verifier,
        "verify_backend_layer_internal_surfaces",
        fake_backend_internal_surface_check,
    )

    result = verifier.run_verification()

    assert sentinel in result.errors


def test_repo_structure_verifier_runs_phase02_ownership_checks(monkeypatch) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinels = {
        "phase02 ownership matrix check was called",
        "phase02 service owner check was called",
        "phase02 provider classification check was called",
        "phase02 compat vendor boundary check was called",
        "phase02 reserved import guard check was called",
    }

    monkeypatch.setattr(
        verifier,
        "verify_phase02_backend_ownership_matrix",
        lambda: ["phase02 ownership matrix check was called"],
    )
    monkeypatch.setattr(
        verifier,
        "verify_phase02_platform_services_owner_guard",
        lambda: ["phase02 service owner check was called"],
    )
    monkeypatch.setattr(
        verifier,
        "verify_phase02_capability_provider_guard",
        lambda: ["phase02 provider classification check was called"],
    )
    monkeypatch.setattr(
        verifier,
        "verify_phase02_compatibility_vendor_boundary",
        lambda: ["phase02 compat vendor boundary check was called"],
    )
    monkeypatch.setattr(
        verifier,
        "verify_phase02_reserved_import_guards",
        lambda: ["phase02 reserved import guard check was called"],
    )

    result = verifier.run_verification()

    assert sentinels.issubset(set(result.errors))


def test_repo_structure_verifier_runs_root_local_artifact_check(monkeypatch) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinel = "root local artifact check was called"

    def fake_root_local_artifact_check() -> list[str]:
        return [sentinel]

    monkeypatch.setattr(
        verifier,
        "verify_root_local_artifacts_are_absent",
        fake_root_local_artifact_check,
    )

    result = verifier.run_verification()

    assert sentinel in result.errors


def test_repo_structure_verifier_pins_retired_backend_top_level_paths() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    assert verifier.BACKEND_RETIRED_TOP_LEVEL_PATHS == {
        "src/backend/fastapi_jwt_auth": "public FastAPI JWT shell retired; runtime imports use zuno.compatibility.vendor.fastapi_jwt_auth",
        "src/backend/zuno/prompts": "runtime prompts moved to zuno/resources/prompts",
        "src/backend/zuno/fixtures": "runtime fixtures moved to zuno/resources/fixtures",
        "src/backend/zuno/system_skills": "runtime system skills moved to zuno/resources/system_skills",
        "src/backend/zuno/legacy": "legacy aliases moved to zuno/compatibility/legacy",
        "src/backend/zuno/vendor": "vendored dependencies moved to zuno/compatibility/vendor",
        "src/backend/zuno/mcp_servers": "MCP server compatibility directory retired; implementations live in zuno/capability/mcp/servers",
        "src/backend/zuno/middleware": "HTTP middleware compatibility directory retired; implementations live in zuno/platform/middleware",
        "src/backend/zuno/evals": "eval compatibility directory retired; implementations live in tools/evals/zuno",
        "src/backend/zuno/compatibility": "compatibility implementation moved to zuno/platform/compatibility; root alias file retired",
        "src/backend/zuno/config": "configuration resources moved to zuno/platform/config; root alias file retired",
        "src/backend/zuno/database": "database implementation moved to zuno/platform/database; root alias file retired",
        "src/backend/zuno/resources": "runtime resources moved to zuno/platform/resources; root alias file retired",
        "src/backend/zuno/schema": "DTO schema implementation moved to zuno/api/dto; root alias file retired",
        "src/backend/zuno/tools": "runtime tools moved to zuno/capability/tools; root alias file retired",
        "src/backend/zuno/services": "legacy service implementation moved to zuno/platform/services; root alias file retired",
        "src/backend/zuno/core": "legacy core implementation moved to zuno/agent/core; root alias file retired",
        "src/backend/zuno/utils": "legacy utils moved to zuno/platform/common; root alias file retired",
        "src/backend/zuno/compatibility.py": "legacy zuno.compatibility alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/config.py": "legacy zuno.config alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/core.py": "legacy zuno.core alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/database.py": "legacy zuno.database alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/evals.py": "legacy zuno.evals alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/mcp_servers.py": "legacy zuno.mcp_servers alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/middleware.py": "legacy zuno.middleware alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/resources.py": "legacy zuno.resources alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/schema.py": "legacy zuno.schema alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/services.py": "legacy zuno.services alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/settings.py": "legacy zuno.settings alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/tools.py": "legacy zuno.tools alias now registered by zuno.platform.compatibility.legacy_aliases",
        "src/backend/zuno/utils.py": "legacy zuno.utils alias now registered by zuno.platform.compatibility.legacy_aliases",
    }


def test_repo_structure_verifier_runs_retired_backend_top_level_path_check(
    monkeypatch,
) -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    sentinel = "retired backend path check was called"

    def fake_retired_backend_path_check() -> list[str]:
        return [sentinel]

    monkeypatch.setattr(
        verifier,
        "verify_backend_retired_top_level_paths_are_absent",
        fake_retired_backend_path_check,
    )

    result = verifier.run_verification()

    assert sentinel in result.errors


def test_retired_front_path_directories_are_not_current_paths() -> None:
    retired_paths = [
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
        "docs/reference/api.md",
        "docs/reference/core.md",
        "docs/reference/database.md",
        "docs/reference/service.md",
        "docs/reference/zuno.md",
        ".agent/skills",
        ".agent/workflows",
        ".agent/programs/context-memory-agent-runtime-v1",
        ".agent/programs/official-graphrag-cleanup-v1",
        ".agent/programs/zuno-target-runtime-v2",
        ".agent/programs/implementation-phases",
        "docs/superpowers",
        "src/frontend",
        "domain-packs",
        "tests/compat",
    ]

    for relative_path in retired_paths:
        assert not (REPO_ROOT / relative_path).exists(), f"retired path still current: {relative_path}"


def test_backend_visual_compatibility_shells_are_registered_not_root_files() -> None:
    backend_root = REPO_ROOT / "src" / "backend" / "zuno"

    for name in [
        "compatibility",
        "config",
        "core",
        "database",
        "evals",
        "mcp_servers",
        "middleware",
        "resources",
        "schema",
        "services",
        "settings",
        "tools",
        "utils",
    ]:
        assert not (backend_root / name).exists(), f"visual compatibility directory still exists: {name}"
        assert not (backend_root / f"{name}.py").exists(), f"root compatibility file still exists: {name}.py"

    assert (
        backend_root / "platform" / "compatibility" / "legacy_aliases.py"
    ).exists()


def test_backend_zuno_top_level_files_match_completion_allowlist() -> None:
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    verifier = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = verifier
    spec.loader.exec_module(verifier)

    actual_files = sorted(
        path.name
        for path in (REPO_ROOT / "src/backend/zuno").iterdir()
        if path.is_file()
    )

    assert actual_files == sorted(verifier.BACKEND_ZUNO_ALLOWED_TOP_LEVEL_FILES)


def test_front_path_docs_link_current_entrypoints() -> None:
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "architecture.md" in architecture_index
    assert "production-readiness.md" in architecture_index
    assert "document-ingestion-foundation.md" in architecture_index
    assert "architecture.html" in architecture_index
    assert ".agent/architecture/architecture.md" in architecture_index
    assert ".agent/architecture/architecture.html" in architecture_index
    assert "../evidence/public-demo.md" in architecture_index
    assert "./architecture/architecture.md" in docs_index
    assert "./architecture/production-readiness.md" in docs_index
    assert "./architecture/document-ingestion-foundation.md" in docs_index
    assert "./architecture/architecture.html" in docs_index
    assert "./docs/architecture/architecture.md" in readme
    assert "./docs/architecture/production-readiness.md" in readme
    assert "./docs/architecture/document-ingestion-foundation.md" in readme
    assert "./docs/architecture/architecture.html" in readme


def test_phase_completion_truth_is_historical() -> None:
    content = (REPO_ROOT / "docs" / "history" / "phases" / "README.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "Phase 0: Stable Runtime Recovery",
        "Phase 1: LangGraph Runtime Deepening",
        "Phase 2: GraphRAG Mainline Deepening",
        "Phase 3: Domain Pack Formalization",
        "Phase 4: Knowledge Config V2 + Local Eval Strengthening",
        "Phase 5: Docs And Public Explanation Sync",
        "Phase 6: Agent GraphRAG Pluginization / Future Platform Layer",
    ]:
        assert phrase in content


def test_readme_mentions_current_backend_start_and_focused_verification() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in [
        "python tools/scripts/verify_docs_entrypoints.py",
        "python tools/scripts/verify_repo_structure.py",
        "python .agent/scripts/verify_agent_system.py",
        "python .agent/scripts/verify_doc_boundaries.py",
        "pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py",
        "uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860",
        "zuno-master-architecture-implementation-v1",
        ".agent/programs/",
    ]:
        assert phrase in readme


def test_reference_migration_doc_is_archived_out_of_front_path() -> None:
    assert not (REPO_ROOT / "docs" / "reference" / "migration.md").exists()
    assert (REPO_ROOT / "docs" / "history" / "reference" / "migration.md").exists()


def test_active_program_and_archived_program_closures_are_consistent() -> None:
    active_files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent" / "programs").iterdir()
        if path.is_file()
    )

    assert active_files == sorted(ACTIVE_PROGRAM_FILES)
    assert not (REPO_ROOT / ".agent/programs/zuno-target-runtime-v2").exists()
    assert not (REPO_ROOT / ".agent/programs/implementation-phases").exists()
    assert (
        REPO_ROOT
        / "docs/history/programs/zuno-target-runtime-v2/implementation-phases/README.md"
    ).exists()

    current = (REPO_ROOT / ".agent/programs/current.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / ".agent/programs/README.md").read_text(encoding="utf-8")
    roadmap = (REPO_ROOT / ".agent/programs/implementation-roadmap.md").read_text(
        encoding="utf-8"
    )
    closure = (REPO_ROOT / ".agent/programs/closure-checklist.md").read_text(
        encoding="utf-8"
    )
    current_reference = (REPO_ROOT / ".agent/references/current-program.md").read_text(
        encoding="utf-8"
    )
    latest_archive = REPO_ROOT / LATEST_COMPLETED_PROGRAM_ARCHIVE
    latest_archive_text = (
        (latest_archive / "current.md").read_text(encoding="utf-8")
        + (latest_archive / "README.md").read_text(encoding="utf-8")
        + (latest_archive / "closure-summary.md").read_text(encoding="utf-8")
    )
    production_archive = REPO_ROOT / ACTIVE_PROGRAM_ARCHIVE
    production_archive_text = (
        (production_archive / "current.md").read_text(encoding="utf-8")
        + (production_archive / "README.md").read_text(encoding="utf-8")
        + (production_archive / "closure-summary.md").read_text(encoding="utf-8")
    )
    ingestion_archive = REPO_ROOT / CURRENT_ACTIVE_PROGRAM_ARCHIVE
    ingestion_archive_text = (
        (ingestion_archive / "current.md").read_text(encoding="utf-8")
        + (ingestion_archive / "README.md").read_text(encoding="utf-8")
        + (ingestion_archive / "closure-summary.md").read_text(encoding="utf-8")
    )
    runtime_archive = REPO_ROOT / RUNTIME_PROGRAM_ARCHIVE
    archive_text = (
        (runtime_archive / "current.md").read_text(encoding="utf-8")
        + (runtime_archive / "README.md").read_text(encoding="utf-8")
        + (runtime_archive / "closure-summary.md").read_text(encoding="utf-8")
    )
    for phrase in [
        ACTIVE_PROGRAM_NAME,
        "state: active",
        f"active_program: {PROGRAM3_ACTIVE_NAME}",
        "current_phase: PHASE14_docs-architecture-expansion.md",
        f"latest_completed_program: {LATEST_COMPLETED_PROGRAM_NAME}",
        PROGRAM3_ACTIVE_NAME,
        LATEST_COMPLETED_PROGRAM_NAME,
        LATEST_COMPLETED_PROGRAM_ARCHIVE,
        CURRENT_ACTIVE_PROGRAM_NAME,
        CURRENT_ACTIVE_PROGRAM_ARCHIVE,
        "zuno-enterprise-agentic-graphrag-production-suite-v1",
        "zuno-runtime-subsystems-parallel-v1",
        "zuno-agent-planning-integration-v1",
        "zuno-enterprise-knowledge-eval-benchmark-v1",
        ACTIVE_PROGRAM_ARCHIVE,
        "completed / archived",
        "PHASE01-PHASE08",
        "PHASE01-PHASE12",
        "PHASE01_truth-source-and-gap-audit",
        "PHASE08_docs-verifier-closure",
        "Product V1 local durable ingestion baseline",
        "一次性交付型成熟化 program",
        "成熟目标架构和四大总交付物完成",
        "工作流自洽与自我维护",
        "文档系统清晰无冗余",
        "文件夹和代码 ownership 清晰",
        "架构功能完整实现",
        RUNTIME_PROGRAM_NAME,
        RUNTIME_PROGRAM_ARCHIVE,
        "runtime-first / vertical-slice-first",
        "只写 contract、schema 或 README 不能关闭 runtime phase",
        "成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准",
        MASTER_PROGRAM_NAME,
        MASTER_PROGRAM_ARCHIVE,
    ]:
        assert phrase in current + readme + roadmap + closure + current_reference + latest_archive_text + ingestion_archive_text + production_archive_text + archive_text
    assert sorted(path.name for path in (REPO_ROOT / ".agent/programs").glob("PHASE*.md")) == sorted(PROGRAM3_ACTIVE_PHASE_FILES)
    for phase_name in PROGRAM3_ACTIVE_PHASE_FILES:
        phase_text = (REPO_ROOT / ".agent/programs" / phase_name).read_text(encoding="utf-8")
        assert f"program: {PROGRAM3_ACTIVE_NAME}" in phase_text
        if phase_name.startswith("PHASE01_") or phase_name.startswith("PHASE02_") or phase_name.startswith("PHASE03_") or phase_name.startswith("PHASE04_") or phase_name.startswith("PHASE05_") or phase_name.startswith("PHASE06_") or phase_name.startswith("PHASE07_") or phase_name.startswith("PHASE08_") or phase_name.startswith("PHASE09_") or phase_name.startswith("PHASE10_") or phase_name.startswith("PHASE11_") or phase_name.startswith("PHASE12_") or phase_name.startswith("PHASE13_"):
            expected_status = "status: completed"
        elif phase_name.startswith("PHASE14_"):
            expected_status = "status: active"
        else:
            expected_status = "status: pending"
        assert expected_status in phase_text
        for section in [
            "## 目标",
            "## 范围",
            "## 禁止范围",
            "## 验收闸门",
            "## 验证命令",
            "## 需要先读取",
            "## 需要修改的文件",
            "## 执行拆解",
            "## 多 agent 分工",
            "## 需要返回的证据",
            "## 停止条件",
        ]:
            assert section in phase_text
    assert not (REPO_ROOT / ".agent/programs/thread-prompts").exists()
    for phase in LATEST_COMPLETED_PROGRAM_PHASE_FILES:
        phase_path = latest_archive / phase
        phase_text = phase_path.read_text(encoding="utf-8")
        assert f"program: {LATEST_COMPLETED_PROGRAM_NAME}" in phase_text
        assert "status: completed" in phase_text
        for section in [
            "## 目标",
            "## 范围",
            "## 禁止范围",
            "## 验收闸门",
            "## 验证命令",
            "## 需要先读取",
            "## 需要修改的文件",
            "## 执行拆解",
            "## 多 agent 分工",
            "## 需要返回的证据",
            "## 停止条件",
        ]:
            assert section in phase_text
    for archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        assert (latest_archive / archive_file).exists()
    for phase in CURRENT_ACTIVE_PROGRAM_PHASE_FILES:
        phase_path = ingestion_archive / phase
        phase_text = phase_path.read_text(encoding="utf-8")
        assert "program: zuno-production-document-ingestion-and-thread-foundation-v1" in phase_text
        assert "status: completed" in phase_text
        for section in [
            "## 目标",
            "## 范围",
            "## 禁止范围",
            "## 验收闸门",
            "## 验证命令",
            "## 需要先读取",
            "## 需要修改的文件",
            "## 执行拆解",
            "## 多 agent 分工",
            "## 需要返回的证据",
            "## 停止条件",
        ]:
            assert section in phase_text
    for archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        assert (ingestion_archive / archive_file).exists()
    for file_name in THREAD_PROMPT_FILES:
        assert (ingestion_archive / "thread-prompts" / file_name).exists()
    assert sorted(path.name for path in (REPO_ROOT / ".agent/programs/queued-programs").glob("*.md")) == sorted(QUEUED_PROGRAM_FILES)
    for file_name in QUEUED_PROGRAM_FILES:
        text = (REPO_ROOT / ".agent/programs/queued-programs" / file_name).read_text(encoding="utf-8")
        if file_name != "README.md":
            assert "state: superseded" in text
            assert "merged_into: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1" in text
            assert "superseded_by: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1" in text
    _assert_archived_phase_state()
    for phase in ACTIVE_PROGRAM_PHASE_FILES:
        phase_path = production_archive / phase
        assert phase_path.exists()
        phase_text = phase_path.read_text(encoding="utf-8")
        assert "status: completed" in phase_text
        for section in [
            "## 目标",
            "## 范围",
            "## 禁止范围",
            "## 验收闸门",
            "## 验证命令",
            "## 需要先读取",
            "## 需要修改的文件",
            "## 执行拆解",
            "## 多 agent 分工",
            "## 需要返回的证据",
            "## 停止条件",
        ]:
            assert section in phase_text
    for archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        assert (production_archive / archive_file).exists()
    for index, phase in enumerate(RUNTIME_PROGRAM_PHASE_FILES, start=1):
        phase_path = runtime_archive / phase
        assert phase_path.exists()
        phase_text = phase_path.read_text(encoding="utf-8")
        assert "status: completed" in phase_text
    for archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        assert (runtime_archive / archive_file).exists()
    for phase in MASTER_PROGRAM_PHASE_FILES:
        assert (REPO_ROOT / MASTER_PROGRAM_ARCHIVE / phase).exists()
    for phase in COMPLETED_PROGRAM_PHASE_FILES:
        assert (REPO_ROOT / COMPLETED_PROGRAM_ARCHIVE / phase).exists()
    program3 = (
        REPO_ROOT / "docs/history/programs/zuno-repo-layout-cleanup-v1/README.md"
    ).read_text(encoding="utf-8")
    program4 = (
        REPO_ROOT / "docs/history/programs/zuno-six-layer-internalization-v1/README.md"
    ).read_text(encoding="utf-8")
    assert "completed / archived" in program4
    assert "Capability tools 不按 CLI / API 拆成两棵顶层目录" in program4
    for phase in [
        "PHASE01_six-layer-current-inventory.md",
        "PHASE02_memory-layer-foundation-surfaces.md",
        "PHASE03_capability-layer-foundation-surfaces.md",
        "PHASE04_knowledge-layer-foundation-surfaces.md",
        "PHASE05_agent-runtime-boundary-surfaces.md",
        "PHASE06_platform-boundary-hardening.md",
        "PHASE07_docs-verifier-and-closure.md",
    ]:
        assert (
            REPO_ROOT / "docs/history/programs/zuno-six-layer-internalization-v1" / phase
        ).exists()
    assert "Directory Surface Alignment V1" in program3
    assert "repo hygiene verifier" in program3
    assert "capability/mcp/servers" in program3
    assert "platform/middleware" in program3
    for phase in [
        "PHASE01_directory-closure-master-plan.md",
        "PHASE02_platform-foundation-directory-migration.md",
        "PHASE03_schema-tools-resources-directory-migration.md",
        "PHASE04_services-thinning-directory-migration.md",
        "PHASE05_core-agent-runtime-directory-migration.md",
        "PHASE06_final-six-layer-guard-and-closure.md",
        "PHASE06_backend-directory-clarity-audit.md",
        "PHASE07_fastapi-jwt-auth-compat-retirement-plan.md",
        "PHASE08_backend-physical-cleanup-slices.md",
        "PHASE09_target-layout-visual-compat-shell-retirement.md",
        "PHASE10_alias-inventory-and-target-contract.md",
        "PHASE11_import-smoke-and-compat-registry-design.md",
        "PHASE12_low-risk-alias-surface-cleanup.md",
        "PHASE13_medium-risk-alias-surface-cleanup.md",
        "PHASE14_high-risk-core-services-settings-cleanup.md",
        "PHASE15_final-root-surface-guard-and-closure.md",
    ]:
        assert (
            REPO_ROOT / "docs/history/programs/zuno-repo-layout-cleanup-v1" / phase
        ).exists()
    phase03 = (
        REPO_ROOT / "docs/history/programs/zuno-workflow-doc-system-v1/PHASE03_skill-template-program-system.md"
    ).read_text(encoding="utf-8")
    assert "本地 skill system" in phase03
    program2 = (
        REPO_ROOT / "docs/history/programs/zuno-target-architecture-refresh-v1/README.md"
    ).read_text(encoding="utf-8")
    assert "LLM extraction" in program2


def test_architecture_diagram_generation_paths_are_pinned() -> None:
    content = (REPO_ROOT / "tools/scripts/verify_repo_structure.py").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "docs/architecture/architecture.md",
        "docs/architecture/architecture.html",
        "00-architecture-index.md",
        "tools/agent/render_architecture.py",
        "verify_architecture_diagram_outputs",
    ]:
        assert phrase in content


def test_superseded_specs_are_archived_out_of_architecture_front_path() -> None:
    assert not (REPO_ROOT / "docs" / "architecture" / "specs").exists()
    for relative_path in [
        "deep-graphrag-v1-runtime.md",
        "domain-pack-langgraph-graphrag-architecture.md",
        "domain-pack-builder.md",
        "knowledge-product-boundary.md",
    ]:
        assert (REPO_ROOT / "docs" / "history" / "specs" / relative_path).exists()

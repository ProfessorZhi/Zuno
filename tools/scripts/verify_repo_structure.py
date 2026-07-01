from __future__ import annotations

from dataclasses import dataclass
import importlib
import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

COMPLETED_PROGRAM_NAME = "zuno-eight-deliverables-full-realization-v1"
COMPLETED_PROGRAM_ARCHIVE = f"docs/history/programs/{COMPLETED_PROGRAM_NAME}"
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
    "PHASE01_truth-source-and-gap-audit.md",
    "PHASE02_durable-storage-contract.md",
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
    "PROGRAM03_runtime-subsystems-parallel.md",
    "PROGRAM04_agent-planning-integration.md",
    "PROGRAM05_enterprise-knowledge-eval-benchmark.md",
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


def _verify_archived_phase_state() -> list[str]:
    errors: list[str] = []
    archive_root = REPO_ROOT / ACTIVE_PROGRAM_ARCHIVE
    for phase_name in ACTIVE_PROGRAM_PHASE_FILES:
        phase_path = archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"production completion program archive missing phase: {phase_name}")
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if "status: completed" not in phase_content:
            errors.append(f"production completion program archive phase missing completed status: {phase_name}")
    return errors
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


REQUIRED_PATHS = [
    "AGENTS.md",
    ".agent/README.md",
    ".agent/system.yaml",
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
    *[f".agent/programs/queued-programs/{file_name}" for file_name in QUEUED_PROGRAM_FILES],
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/README.md",
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/current.md",
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/implementation-roadmap.md",
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/closure-checklist.md",
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/closure-summary.md",
    *[f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/{phase_name}" for phase_name in CURRENT_ACTIVE_PROGRAM_PHASE_FILES],
    *[f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/thread-prompts/{file_name}" for file_name in THREAD_PROMPT_FILES],
    f"{ACTIVE_PROGRAM_ARCHIVE}/README.md",
    f"{ACTIVE_PROGRAM_ARCHIVE}/current.md",
    f"{ACTIVE_PROGRAM_ARCHIVE}/implementation-roadmap.md",
    f"{ACTIVE_PROGRAM_ARCHIVE}/closure-checklist.md",
    f"{ACTIVE_PROGRAM_ARCHIVE}/closure-summary.md",
    *[f"{ACTIVE_PROGRAM_ARCHIVE}/{phase_name}" for phase_name in ACTIVE_PROGRAM_PHASE_FILES],
    f"{RUNTIME_PROGRAM_ARCHIVE}/README.md",
    f"{RUNTIME_PROGRAM_ARCHIVE}/current.md",
    f"{RUNTIME_PROGRAM_ARCHIVE}/implementation-roadmap.md",
    f"{RUNTIME_PROGRAM_ARCHIVE}/closure-checklist.md",
    f"{RUNTIME_PROGRAM_ARCHIVE}/closure-summary.md",
    *[f"{RUNTIME_PROGRAM_ARCHIVE}/{phase_name}" for phase_name in RUNTIME_PROGRAM_PHASE_FILES],
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/README.md",
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/current.md",
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/closure-checklist.md",
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/closure-summary.md",
    "docs/history/research/README.md",
    "docs/history/research/chatgpt-research-mode-artifacts/README.md",
    "docs/history/research/chatgpt-research-mode-artifacts/zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.pdf",
    "docs/history/research/chatgpt-research-mode-artifacts/zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.md",
    "docs/history/research/chatgpt-research-mode-artifacts/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf",
    "docs/history/research/chatgpt-research-mode-artifacts/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.md",
    "docs/architecture/assets/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf",
    f"{COMPLETED_PROGRAM_ARCHIVE}/README.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/current.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/implementation-roadmap.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/closure-checklist.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/closure-summary.md",
    *[f"{COMPLETED_PROGRAM_ARCHIVE}/{phase_name}" for phase_name in COMPLETED_PROGRAM_PHASE_FILES],
    ".agent/architecture/README.md",
    ".agent/architecture/architecture.md",
    ".agent/architecture/architecture.html",
    ".agent/scripts/verify_agent_system.py",
    ".agent/scripts/verify_doc_boundaries.py",
    ".agent/scripts/verify_repo_hygiene.py",
    "apps/desktop",
    "apps/web",
    "apps/web/AGENTS.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/architecture.md",
    "docs/architecture/production-readiness.md",
    "docs/architecture/document-ingestion-foundation.md",
    "docs/architecture/architecture.html",
    "docs/architecture/repo-ownership-matrix.md",
    "docs/architecture/assets/zuno-agentic-rag-graphrag-ideal-architecture.pdf",
    "docs/architecture/decisions/README.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/README.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/current-architecture.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/target-architecture.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/roadmap.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/product-scenario-enterprise-kb.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/security-and-sandbox.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/deliverables.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/README.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/README.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/decisions/README.md",
    "docs/evidence/README.md",
    "docs/evidence/public-demo.md",
    "docs/evidence/eval-baselines.md",
    "docs/reference/terminology.md",
    "docs/history/README.md",
    "docs/history/phases/README.md",
    "docs/history/plans/README.md",
    "docs/history/programs/README.md",
    "docs/history/programs/zuno-target-architecture-migration-v1/README.md",
    "docs/history/programs/zuno-target-runtime-v2/README.md",
    "docs/history/programs/official-graphrag-cleanup-v1/README.md",
    "docs/history/programs/zuno-workflow-doc-system-v1/README.md",
    "docs/history/programs/zuno-target-architecture-refresh-v1/README.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/README.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE01_repo-layout-audit.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE02_root-docs-hygiene.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE03_backend-six-layer-migration-plan.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE04_small-boundary-cleanups.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE05_hygiene-verifier-closure.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE06_backend-directory-clarity-audit.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE07_fastapi-jwt-auth-compat-retirement-plan.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE08_backend-physical-cleanup-slices.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE09_target-layout-visual-compat-shell-retirement.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE10_alias-inventory-and-target-contract.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE11_import-smoke-and-compat-registry-design.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE12_low-risk-alias-surface-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE13_medium-risk-alias-surface-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE14_high-risk-core-services-settings-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE15_final-root-surface-guard-and-closure.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/README.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/current.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE01_six-layer-current-inventory.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE02_memory-layer-foundation-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE03_capability-layer-foundation-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE04_knowledge-layer-foundation-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE05_agent-runtime-boundary-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE06_platform-boundary-hardening.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE07_docs-verifier-and-closure.md",
    "docs/history/development/README.md",
    "docs/history/reference/migration.md",
    "docs/history/specs",
    "docs/history/audits",
    "examples/graphrag-projects/contract_review/settings.yaml",
    "examples/graphrag-projects/contract_review/schema.json",
    "examples/graphrag-projects/contract_review/retrieval_policy.yaml",
    "examples/graphrag-projects/contract_review/eval/eval_dataset.jsonl",
    "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml",
    "docs/history/domain-packs/root-contract-review/contract_review/schema.json",
    "infra/db",
    "infra/docker",
    "src/backend/zuno",
    "src/backend/zuno/main.py",
    "src/backend/zuno/knowledge/ingestion/README.md",
    "src/backend/zuno/platform/observability/README.md",
    "src/backend/zuno/platform/security/README.md",
    "src/backend/zuno/platform/vendor/README.md",
    "tests",
    "tools",
    "tools/agent/render_architecture.py",
    "tools/evals/zuno",
    "tools/evals/zuno/AGENTS.md",
]


FORBIDDEN_CURRENT_PATHS = [
    ".agent/skills",
    ".agent/workflows",
    ".agent/architecture/near-term",
    ".agent/architecture/future",
    ".agent/architecture/decisions",
    ".agent/architecture/00-architecture-index.md",
    ".agent/architecture/glossary.md",
    "docs/architecture/history",
    "docs/architecture/audits",
    "docs/architecture/specs",
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/architecture/product-scenario-enterprise-kb.md",
    "docs/architecture/security-and-sandbox.md",
    "docs/architecture/deliverables.md",
    "docs/architecture/overall-architecture.md",
    ".agent/architecture/overall-architecture.md",
    "docs/development",
    "docs/prototypes",
    "docs/ui-review",
    "docs/ui-gallery",
    "docs/reference/api.md",
    "docs/reference/core.md",
    "docs/reference/database.md",
    "docs/reference/service.md",
    "docs/reference/zuno.md",
    ".agent/programs/context-memory-agent-runtime-v1",
    ".agent/programs/official-graphrag-cleanup-v1",
    ".agent/programs/zuno-target-runtime-v2",
    ".agent/programs/implementation-phases",
    ".agent/programs/phase-05-memory-engine.md",
    ".agent/programs/phase-06-capability-tool-retrieval.md",
    ".agent/programs/phase-07-graphrag-llm-entity-extraction.md",
    ".agent/programs/phase-08-langgraph-runtime.md",
    ".agent/programs/phase-09-product-trace-eval-closure.md",
    "docs/superpowers",
    "src/frontend",
    "domain-packs",
    "tests/compat",
]


DOC_REQUIRED_PHRASES: dict[str, list[str]] = {
    "AGENTS.md": [
        "这是仓库唯一的 Agent 入口",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/system.yaml",
        ".agent/programs/",
        ".agent/architecture/",
        "前台文档默认中文",
    ],
    ".agent/README.md": [
        "Zuno Local Agent Skill System",
        "本地 Agent Skill System",
        "新写或重写的 Agent 文档默认使用中文",
    ],
    "docs/README.md": [
        "./architecture/architecture.md",
        "./architecture/production-readiness.md",
        "./architecture/document-ingestion-foundation.md",
        "./architecture/architecture.html",
        "./evidence/public-demo.md",
        "./history/README.md",
        "前台文档默认使用中文",
    ],
    "docs/architecture/README.md": [
        "architecture.md",
        "production-readiness.md",
        "document-ingestion-foundation.md",
        "architecture.html",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/",
        "../evidence/public-demo.md",
        "过时审计、旧规格、旧 phase、旧计划和旧 runbook",
    ],
    "docs/architecture/architecture.md": [
        "总架构文档",
        "本地优先的企业私有知识库与多功能 Agent 助手",
        "文字总架构文档",
        "架构 HTML",
        "docs/architecture/architecture.md",
        "docs/architecture/architecture.html",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "Document Ingestion / Parse Gateway",
        "Tool Control Plane",
        "LangSmith-compatible Trace / Eval",
        "docs/architecture/document-ingestion-foundation.md",
    ],
    "docs/architecture/document-ingestion-foundation.md": [
        "Document Ingestion Foundation",
        "企业知识库文档入口",
        "ParseGateway.submit_parse_job()",
        "CanonicalDocumentIR",
        "IndexJobManifest",
        "document_version_id",
        "parse_idempotency_key",
        "index_idempotency_key",
        "workspace_text_runtime",
        "VLM enrichment adapter",
        "生产 DB、object store、queue / outbox、worker lease、external OCR / VLM、external index platform",
    ],
}

TOP_LEVEL_RESPONSIBILITY_DIRECTORIES = {
    "tools": "维护脚本、验证器、eval、launcher、migration 和架构渲染工具",
    "tests": "自动化测试源和仓库边界 guardrails",
    "examples": "可运行示例和示例输入，不存放运行输出",
    "infra": "数据库、Docker 和本地基础设施配置，不存放运行态 volume/cache",
}

ALLOWED_RESPONSIBILITY_SUBDIRS = {
    "tools": ["agent", "cli", "evals", "launchers", "migrations", "scripts"],
    "tests": [
        "agent",
        "agent_system",
        "api",
        "evals",
        "fixtures",
        "frontend",
        "graphrag",
        "knowledge",
        "legacy_guards",
        "repo",
        "retrieval",
        "security",
        "storage",
        "tools",
    ],
    "examples": ["graphrag-projects"],
    "infra": ["db", "docker"],
}

ALLOWED_RESPONSIBILITY_FILES = {
    "tools": ["__init__.py"],
    "tests": ["README.md", "conftest.py"],
    "examples": [],
    "infra": [],
}

BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS = {
    "api": "target-layer",
    "agent": "target-layer",
    "memory": "target-layer",
    "capability": "target-layer",
    "knowledge": "target-layer",
    "platform": "target-layer",
}

BACKEND_LAYER_INTERNAL_SURFACES = {
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

BACKEND_OWNERSHIP_MATRIX_PATH = "docs/architecture/repo-ownership-matrix.md"
BACKEND_OWNERSHIP_MATRIX_REQUIRED_COLUMNS = [
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

PHASE02_RUNTIME_DOMAIN_MATRIX_REQUIREMENTS = {
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

PHASE02_LEGACY_ALIAS_MATRIX_ROWS = {
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

PLATFORM_SERVICES_TARGET_OWNERS = {
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

CAPABILITY_TOOL_PROVIDER_CLASSIFICATIONS = {
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

CAPABILITY_MCP_SERVER_CLASSIFICATIONS = {
    "arxiv": "mcp-provider",
    "lark_mcp": "mcp-provider",
    "qa_echo": "mcp-smoke-server",
    "remote_proxy": "mcp-compat-proxy",
    "weather": "mcp-provider",
}

PHASE02_RESERVED_IMPORT_GUARD_PATHS = [
    "src/backend/zuno/platform/observability",
    "src/backend/zuno/platform/security",
    "src/backend/zuno/platform/vendor",
]

PHASE02_RESERVED_IMPORT_MODULES = {
    "src/backend/zuno/platform/observability": "zuno.platform.observability",
    "src/backend/zuno/platform/security": "zuno.platform.security",
    "src/backend/zuno/platform/vendor": "zuno.platform.vendor",
}

BACKEND_LEGACY_IMPORT_ALIASES = {
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

BACKEND_ZUNO_ALLOWED_TOP_LEVEL_FILES = {
    "__init__.py": "package marker",
    "main.py": "FastAPI application entrypoint",
}

BACKEND_RETIRED_TOP_LEVEL_PATHS = {
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

ROOT_LOCAL_ARTIFACT_DIRECTORIES = {
    ".agents": "旧 Agent 入口或本地执行残留；当前唯一入口是 AGENTS.md",
    ".local": "本地配置、eval 和运行态产物；可以存在于本机但不能挡住仓库根目录",
    ".test-tmp": "测试 scratch 目录；可再生成且必须保持本地 ignored",
    "__pycache__": "Python bytecode cache；可再生成且不属于仓库结构",
    ".pytest_cache": "pytest 本地缓存；可再生成且不属于仓库结构",
    "node_modules": "依赖安装产物；根目录不提交也不作为项目结构展示",
}


@dataclass
class VerificationResult:
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def verify_required_paths() -> list[str]:
    return [
        f"missing required path: {relative_path}"
        for relative_path in REQUIRED_PATHS
        if not (REPO_ROOT / relative_path).exists()
    ]


def verify_forbidden_current_paths() -> list[str]:
    return [
        f"retired current-path still exists: {relative_path}"
        for relative_path in FORBIDDEN_CURRENT_PATHS
        if (REPO_ROOT / relative_path).exists()
    ]


def verify_doc_phrases() -> list[str]:
    errors: list[str] = []
    for relative_path, phrases in DOC_REQUIRED_PHRASES.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing required doc: {relative_path}")
            continue
        content = _read_text(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing phrase: {phrase}")
    return errors


def verify_first_class_directory_responsibilities() -> list[str]:
    errors: list[str] = []
    for directory, role in TOP_LEVEL_RESPONSIBILITY_DIRECTORIES.items():
        root = REPO_ROOT / directory
        if not root.exists():
            errors.append(f"missing first-class responsibility directory: {directory}")
            continue
        if not role:
            errors.append(f"first-class responsibility directory missing role: {directory}")
        actual_subdirs = sorted(
            path.name
            for path in root.iterdir()
            if path.is_dir() and not path.name.startswith("__pycache__")
        )
        actual_files = sorted(path.name for path in root.iterdir() if path.is_file())
        expected_subdirs = ALLOWED_RESPONSIBILITY_SUBDIRS[directory]
        expected_files = ALLOWED_RESPONSIBILITY_FILES[directory]
        if actual_subdirs != expected_subdirs:
            errors.append(
                f"{directory}/ subdirectories drifted from responsibility allowlist: "
                f"expected {expected_subdirs}, got {actual_subdirs}"
            )
        if actual_files != expected_files:
            errors.append(
                f"{directory}/ files drifted from responsibility allowlist: "
                f"expected {expected_files}, got {actual_files}"
            )
    return errors


def verify_backend_zuno_directory_classifications() -> list[str]:
    errors: list[str] = []
    backend_root = REPO_ROOT / "src" / "backend" / "zuno"
    actual_directories = sorted(
        path.name
        for path in backend_root.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    )
    expected_directories = sorted(BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS)
    if actual_directories != expected_directories:
        errors.append(
            "backend zuno top-level directories drifted from classification map: "
            f"expected {expected_directories}, got {actual_directories}"
        )
    for directory, classification in BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS.items():
        path = backend_root / directory
        if not path.is_dir():
            errors.append(f"missing backend zuno classified directory: {directory}")
            continue
        readme = path / "README.md"
        if not readme.exists():
            errors.append(f"missing backend zuno boundary README: {directory}")
            continue
        content = readme.read_text(encoding="utf-8")
        for phrase in [
            f"分类：`{classification}`",
            "当前角色",
            "Target role",
            "禁止事项",
            "Focused tests",
        ]:
            if phrase not in content:
                errors.append(
                    f"{readme.relative_to(REPO_ROOT).as_posix()} missing phrase: {phrase}"
                )
    actual_files = sorted(
        path.name
        for path in backend_root.iterdir()
        if path.is_file()
    )
    expected_files = sorted(BACKEND_ZUNO_ALLOWED_TOP_LEVEL_FILES)
    if actual_files != expected_files:
        errors.append(
            "backend zuno top-level files drifted from completion allowlist: "
            f"expected {expected_files}, got {actual_files}"
        )
    return errors


def verify_backend_layer_internal_surfaces() -> list[str]:
    errors: list[str] = []
    backend_root = REPO_ROOT / "src" / "backend" / "zuno"
    for layer_name, surface in BACKEND_LAYER_INTERNAL_SURFACES.items():
        layer_root = backend_root / layer_name
        if not layer_root.is_dir():
            errors.append(f"missing backend layer directory: {layer_name}")
            continue

        for directory_name in surface["directories"]:
            if not (layer_root / directory_name).is_dir():
                errors.append(
                    f"missing backend layer internal directory: {layer_name}/{directory_name}"
                )

        for file_name in surface["files"]:
            if not (layer_root / file_name).is_file():
                errors.append(
                    f"missing backend layer internal file: {layer_name}/{file_name}"
                )
    return errors


def verify_backend_owner_docs_do_not_reference_retired_physical_paths() -> list[str]:
    errors: list[str] = []
    api_readme = _read_text("src/backend/zuno/api/README.md")
    runtime_call_chain = _read_text(".agent/references/runtime-call-chain.md")

    if "src/backend/zuno/schema/" in api_readme:
        errors.append("src/backend/zuno/api/README.md references retired physical schema directory")
    if "src/backend/zuno/api/dto/" not in api_readme:
        errors.append("src/backend/zuno/api/README.md must point to api/dto as DTO owner")
    if "src/backend/zuno/services/application/capabilities/" in runtime_call_chain:
        errors.append(".agent/references/runtime-call-chain.md references retired root services capability path")
    if "src/backend/zuno/platform/services/application/capabilities/" not in runtime_call_chain:
        errors.append(".agent/references/runtime-call-chain.md must point to platform/services/application/capabilities")
    return errors


def _split_markdown_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_markdown_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(cell and set(cell) <= {"-", ":"} for cell in cells)


def _parse_markdown_table(relative_path: str) -> tuple[list[str], list[dict[str, str]]]:
    table_lines = [
        line.strip()
        for line in _read_text(relative_path).splitlines()
        if line.strip().startswith("|") and line.strip().endswith("|")
    ]
    for index, line in enumerate(table_lines):
        headers = _split_markdown_table_row(line)
        if not set(BACKEND_OWNERSHIP_MATRIX_REQUIRED_COLUMNS).issubset(headers):
            continue
        rows: list[dict[str, str]] = []
        for row_line in table_lines[index + 1 :]:
            cells = _split_markdown_table_row(row_line)
            if _is_markdown_separator_row(cells):
                continue
            if len(cells) != len(headers):
                continue
            rows.append(dict(zip(headers, cells)))
        return headers, rows
    raise ValueError("missing markdown table with backend ownership matrix columns")


def _directory_names(relative_path: str) -> list[str]:
    root = REPO_ROOT / relative_path
    if not root.is_dir():
        return []
    return sorted(
        path.name
        for path in root.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    )


def verify_phase02_backend_ownership_matrix() -> list[str]:
    errors: list[str] = []
    matrix_path = REPO_ROOT / BACKEND_OWNERSHIP_MATRIX_PATH
    if not matrix_path.exists():
        return [f"missing backend ownership matrix: {BACKEND_OWNERSHIP_MATRIX_PATH}"]
    try:
        headers, rows = _parse_markdown_table(BACKEND_OWNERSHIP_MATRIX_PATH)
    except ValueError as exc:
        return [f"{BACKEND_OWNERSHIP_MATRIX_PATH}: {exc}"]

    for column in BACKEND_OWNERSHIP_MATRIX_REQUIRED_COLUMNS:
        if column not in headers:
            errors.append(f"{BACKEND_OWNERSHIP_MATRIX_PATH} missing column: {column}")

    rows_by_path: dict[str, dict[str, str]] = {}
    for row in rows:
        current_path = row.get("current_path", "")
        if not current_path:
            errors.append(f"{BACKEND_OWNERSHIP_MATRIX_PATH} row missing current_path")
            continue
        if current_path in rows_by_path:
            errors.append(f"{BACKEND_OWNERSHIP_MATRIX_PATH} duplicate row: {current_path}")
        rows_by_path[current_path] = row

    required_top_layer_paths = [
        f"src/backend/zuno/{directory}"
        for directory in BACKEND_ZUNO_DIRECTORY_CLASSIFICATIONS
    ]
    required_service_paths = [
        f"src/backend/zuno/platform/services/{service_name}"
        for service_name in PLATFORM_SERVICES_TARGET_OWNERS
    ]
    required_tool_paths = [
        f"src/backend/zuno/capability/tools/{tool_name}"
        for tool_name in CAPABILITY_TOOL_PROVIDER_CLASSIFICATIONS
    ]
    required_mcp_paths = [
        f"src/backend/zuno/capability/mcp/servers/{server_name}"
        for server_name in CAPABILITY_MCP_SERVER_CLASSIFICATIONS
    ]
    required_boundary_paths = [
        "src/backend/zuno/api/dto",
        "src/backend/zuno/platform/database",
        "src/backend/zuno/platform/compatibility/legacy_aliases.py",
        "src/backend/zuno/platform/compatibility/vendor/fastapi_jwt_auth",
        "src/backend/zuno/platform/vendor",
        *PHASE02_LEGACY_ALIAS_MATRIX_ROWS,
    ]
    for current_path in [
        *required_top_layer_paths,
        *required_service_paths,
        *required_tool_paths,
        *required_mcp_paths,
        *required_boundary_paths,
    ]:
        row = rows_by_path.get(current_path)
        if row is None:
            errors.append(f"{BACKEND_OWNERSHIP_MATRIX_PATH} missing row: {current_path}")
            continue
        for column in ["target_owner", "target_path", "migration_risk", "tests", "verifier", "status"]:
            if not row.get(column):
                errors.append(
                    f"{BACKEND_OWNERSHIP_MATRIX_PATH} row {current_path} missing {column}"
                )

    for service_name, target_owner in PLATFORM_SERVICES_TARGET_OWNERS.items():
        current_path = f"src/backend/zuno/platform/services/{service_name}"
        row = rows_by_path.get(current_path, {})
        if row.get("target_owner") != target_owner:
            errors.append(
                f"{BACKEND_OWNERSHIP_MATRIX_PATH} service owner drift: "
                f"{current_path} expected {target_owner}, got {row.get('target_owner')}"
            )

    for tool_name, classification in CAPABILITY_TOOL_PROVIDER_CLASSIFICATIONS.items():
        current_path = f"src/backend/zuno/capability/tools/{tool_name}"
        row = rows_by_path.get(current_path, {})
        if row.get("current_role") != classification:
            errors.append(
                f"{BACKEND_OWNERSHIP_MATRIX_PATH} tool classification drift: "
                f"{current_path} expected {classification}, got {row.get('current_role')}"
            )
        if row.get("target_owner") != "capability":
            errors.append(f"{BACKEND_OWNERSHIP_MATRIX_PATH} tool owner drift: {current_path}")

    for server_name, classification in CAPABILITY_MCP_SERVER_CLASSIFICATIONS.items():
        current_path = f"src/backend/zuno/capability/mcp/servers/{server_name}"
        row = rows_by_path.get(current_path, {})
        if row.get("current_role") != classification:
            errors.append(
                f"{BACKEND_OWNERSHIP_MATRIX_PATH} MCP classification drift: "
                f"{current_path} expected {classification}, got {row.get('current_role')}"
            )
        if row.get("target_owner") != "capability/mcp":
            errors.append(f"{BACKEND_OWNERSHIP_MATRIX_PATH} MCP owner drift: {current_path}")

    boundary_expectations = {
        "src/backend/zuno/platform/compatibility/legacy_aliases.py": (
            "legacy-import-registry",
            "platform/compatibility",
        ),
        "src/backend/zuno/platform/compatibility/vendor/fastapi_jwt_auth": (
            "vendor-shim-current-compat-path",
            "platform/vendor",
        ),
        "src/backend/zuno/platform/vendor": (
            "target-vendor-owner",
            "platform/vendor",
        ),
    }
    for current_path, (current_role, target_owner) in boundary_expectations.items():
        row = rows_by_path.get(current_path, {})
        if row.get("current_role") != current_role:
            errors.append(f"{BACKEND_OWNERSHIP_MATRIX_PATH} boundary role drift: {current_path}")
        if row.get("target_owner") != target_owner:
            errors.append(f"{BACKEND_OWNERSHIP_MATRIX_PATH} boundary owner drift: {current_path}")

    for current_path, (target_owner, target_path, status) in PHASE02_LEGACY_ALIAS_MATRIX_ROWS.items():
        row = rows_by_path.get(current_path, {})
        if row.get("target_owner") != target_owner:
            errors.append(
                f"{BACKEND_OWNERSHIP_MATRIX_PATH} legacy alias owner drift: {current_path}"
            )
        if row.get("target_path") != target_path:
            errors.append(
                f"{BACKEND_OWNERSHIP_MATRIX_PATH} legacy alias target path drift: {current_path}"
            )
        if row.get("status") != status:
            errors.append(
                f"{BACKEND_OWNERSHIP_MATRIX_PATH} legacy alias status drift: {current_path}"
            )

    for domain, required_paths in PHASE02_RUNTIME_DOMAIN_MATRIX_REQUIREMENTS.items():
        missing_paths = [path for path in required_paths if path not in rows_by_path]
        if missing_paths:
            errors.append(
                f"{BACKEND_OWNERSHIP_MATRIX_PATH} missing PHASE02 runtime domain {domain}: "
                f"{missing_paths}"
            )

    return errors


def verify_phase02_platform_services_owner_guard() -> list[str]:
    actual_services = _directory_names("src/backend/zuno/platform/services")
    expected_services = sorted(PLATFORM_SERVICES_TARGET_OWNERS)
    if actual_services != expected_services:
        return [
            "platform/services directories drifted from PHASE02 ownership map: "
            f"expected {expected_services}, got {actual_services}"
        ]
    return []


def verify_phase02_capability_provider_guard() -> list[str]:
    errors: list[str] = []
    actual_tools = _directory_names("src/backend/zuno/capability/tools")
    expected_tools = sorted(CAPABILITY_TOOL_PROVIDER_CLASSIFICATIONS)
    if actual_tools != expected_tools:
        errors.append(
            "capability/tools directories drifted from PHASE02 provider map: "
            f"expected {expected_tools}, got {actual_tools}"
        )
    actual_servers = _directory_names("src/backend/zuno/capability/mcp/servers")
    expected_servers = sorted(CAPABILITY_MCP_SERVER_CLASSIFICATIONS)
    if actual_servers != expected_servers:
        errors.append(
            "capability/mcp/servers directories drifted from PHASE02 provider map: "
            f"expected {expected_servers}, got {actual_servers}"
        )
    return errors


def verify_phase02_compatibility_vendor_boundary() -> list[str]:
    errors: list[str] = []
    compatibility_root = REPO_ROOT / "src/backend/zuno/platform/compatibility"
    if not compatibility_root.is_dir():
        return ["missing platform compatibility boundary"]
    actual_compat_dirs = sorted(
        path.name
        for path in compatibility_root.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    )
    if actual_compat_dirs != ["legacy", "vendor"]:
        errors.append(
            "platform/compatibility may only contain legacy registry and current vendor compat dirs: "
            f"{actual_compat_dirs}"
        )
    actual_compat_files = sorted(path.name for path in compatibility_root.iterdir() if path.is_file())
    if actual_compat_files != ["README.md", "__init__.py", "legacy_aliases.py"]:
        errors.append(
            "platform/compatibility files drifted from registry allowlist: "
            f"{actual_compat_files}"
        )

    compatibility_vendor_root = compatibility_root / "vendor"
    actual_current_vendor_dirs = sorted(
        path.name
        for path in compatibility_vendor_root.iterdir()
        if path.is_dir() and path.name != "__pycache__"
    )
    if actual_current_vendor_dirs != ["fastapi_jwt_auth"]:
        errors.append(
            "compatibility/vendor is only allowed to hold the current fastapi_jwt_auth compat shim: "
            f"{actual_current_vendor_dirs}"
        )

    target_vendor_root = REPO_ROOT / "src/backend/zuno/platform/vendor"
    if not target_vendor_root.is_dir():
        errors.append("missing target platform/vendor owner directory")
    else:
        actual_target_vendor_dirs = sorted(
            path.name
            for path in target_vendor_root.iterdir()
            if path.is_dir() and path.name != "__pycache__"
        )
        actual_target_vendor_files = sorted(
            path.name for path in target_vendor_root.iterdir() if path.is_file()
        )
        if actual_target_vendor_dirs:
            errors.append(
                "platform/vendor target owner must not receive runtime shims before compat tests move: "
                f"{actual_target_vendor_dirs}"
            )
        if actual_target_vendor_files != ["README.md", "__init__.py"]:
            errors.append(
                "platform/vendor target owner must stay as README/import guard in PHASE02: "
                f"{actual_target_vendor_files}"
            )

    compatibility_readme = compatibility_root / "README.md"
    if compatibility_readme.exists():
        content = compatibility_readme.read_text(encoding="utf-8")
        for phrase in [
            "legacy import registry only",
            "platform/vendor",
            "禁止把新的 vendor shim 写入 compatibility",
        ]:
            if phrase not in content:
                errors.append(f"platform/compatibility README missing PHASE02 phrase: {phrase}")
    return errors


def verify_phase02_reserved_import_guards() -> list[str]:
    errors: list[str] = []
    backend_path = str(REPO_ROOT / "src/backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    for relative_path in PHASE02_RESERVED_IMPORT_GUARD_PATHS:
        path = REPO_ROOT / relative_path
        readme = path / "README.md"
        init_file = path / "__init__.py"
        if not readme.is_file():
            errors.append(f"missing PHASE02 reserved README: {relative_path}/README.md")
            continue
        if not init_file.is_file():
            errors.append(f"missing PHASE02 import guard: {relative_path}/__init__.py")
            continue
        content = readme.read_text(encoding="utf-8")
        phase_phrase = "PHASE09" if relative_path == "src/backend/zuno/platform/security" else "PHASE02"
        for phrase in [phase_phrase, "当前角色", "Target role", "禁止事项", "Focused tests"]:
            if phrase not in content:
                errors.append(f"{relative_path}/README.md missing phrase: {phrase}")
        module_name = PHASE02_RESERVED_IMPORT_MODULES[relative_path]
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            errors.append(f"PHASE02 reserved import guard failed: {module_name}: {exc}")
    return errors


def verify_backend_legacy_import_aliases() -> list[str]:
    errors: list[str] = []
    registry = REPO_ROOT / "src/backend/zuno/platform/compatibility/legacy_aliases.py"
    if not registry.is_file():
        errors.append("missing backend legacy alias registry: src/backend/zuno/platform/compatibility/legacy_aliases.py")
        return errors
    for module_name, reason in BACKEND_LEGACY_IMPORT_ALIASES.items():
        try:
            module = importlib.import_module(module_name)
        except Exception as exc:
            errors.append(f"legacy backend import alias failed: {module_name} ({reason}): {exc}")
            continue
        if module_name != "zuno.settings" and not hasattr(module, "__path__"):
            errors.append(f"legacy backend import alias is not package-like: {module_name}")
    return errors


def verify_backend_retired_top_level_paths_are_absent() -> list[str]:
    errors: list[str] = []
    for relative_path, reason in BACKEND_RETIRED_TOP_LEVEL_PATHS.items():
        path = REPO_ROOT / relative_path
        if path.exists():
            errors.append(
                f"retired backend top-level path still exists: {relative_path} ({reason})"
            )
    return errors


def verify_root_local_artifacts_are_absent() -> list[str]:
    errors: list[str] = []
    for relative_path, reason in ROOT_LOCAL_ARTIFACT_DIRECTORIES.items():
        path = REPO_ROOT / relative_path
        if path.exists():
            errors.append(
                f"root local artifact must not remain visible: {relative_path} ({reason})"
            )
    return errors


def verify_architecture_surface_cleanup_archive() -> list[str]:
    errors: list[str] = []
    current_agent_files = sorted(
        path.name for path in (REPO_ROOT / ".agent/architecture").iterdir() if path.is_file()
    )
    if current_agent_files != ["README.md", "architecture.html", "architecture.md"]:
        errors.append(f".agent/architecture current files are not slim: {current_agent_files}")
    archive_root = REPO_ROOT / "docs/history/architecture-surface-cleanup-2026-06-30"
    for relative_path in [
        "agent-architecture/near-term/00-architecture-index.md",
        "agent-architecture/future/README.md",
        "agent-architecture/decisions/README.md",
        "docs-architecture/current-architecture.md",
        "docs-architecture/target-architecture.md",
        "docs-architecture/roadmap.md",
        "docs-architecture/deliverables.md",
    ]:
        if not (archive_root / relative_path).exists():
            errors.append(f"missing architecture cleanup archive path: {relative_path}")
    return errors


def verify_completed_architecture_surface_phase_plan() -> list[str]:
    errors: list[str] = []
    programs_root = REPO_ROOT / ".agent/programs"
    program_files = sorted(path.name for path in programs_root.iterdir() if path.is_file())
    if program_files != sorted(ACTIVE_PROGRAM_FILES):
        errors.append(f".agent/programs active files drifted: {program_files}")
    current_path = programs_root / "current.md"
    readme_path = programs_root / "README.md"
    roadmap_path = programs_root / "implementation-roadmap.md"
    closure_path = programs_root / "closure-checklist.md"
    current_program_reference = REPO_ROOT / ".agent/references/current-program.md"
    production_archive_root = REPO_ROOT / ACTIVE_PROGRAM_ARCHIVE
    production_archive_text = (
        (production_archive_root / "current.md").read_text(encoding="utf-8")
        + (production_archive_root / "README.md").read_text(encoding="utf-8")
        + (production_archive_root / "closure-summary.md").read_text(encoding="utf-8")
    )
    ingestion_archive_root = REPO_ROOT / CURRENT_ACTIVE_PROGRAM_ARCHIVE
    ingestion_archive_text = (
        (ingestion_archive_root / "current.md").read_text(encoding="utf-8")
        + (ingestion_archive_root / "README.md").read_text(encoding="utf-8")
        + (ingestion_archive_root / "closure-summary.md").read_text(encoding="utf-8")
    )
    runtime_archive_root = REPO_ROOT / RUNTIME_PROGRAM_ARCHIVE
    current_readme = (
        current_path.read_text(encoding="utf-8")
        + readme_path.read_text(encoding="utf-8")
        + roadmap_path.read_text(encoding="utf-8")
        + closure_path.read_text(encoding="utf-8")
        + current_program_reference.read_text(encoding="utf-8")
        + (runtime_archive_root / "current.md").read_text(encoding="utf-8")
        + (runtime_archive_root / "README.md").read_text(encoding="utf-8")
        + (runtime_archive_root / "closure-summary.md").read_text(encoding="utf-8")
    )
    for phrase in [
        "state: active",
        "active_program: zuno-enterprise-document-ingestion-platform-v2",
        "current_phase: PHASE02_durable-storage-contract",
        f"latest_completed_program: {CURRENT_ACTIVE_PROGRAM_NAME}",
        CURRENT_ACTIVE_PROGRAM_NAME,
        CURRENT_ACTIVE_PROGRAM_ARCHIVE,
        "zuno-enterprise-agentic-graphrag-production-suite-v1",
        "zuno-enterprise-document-ingestion-platform-v2",
        "zuno-runtime-subsystems-parallel-v1",
        "zuno-agent-planning-integration-v1",
        "zuno-enterprise-knowledge-eval-benchmark-v1",
        ACTIVE_PROGRAM_NAME,
        ACTIVE_PROGRAM_ARCHIVE,
        "completed / archived",
        "PHASE01-PHASE12",
        "PHASE01_truth-source-and-gap-audit",
        "PHASE02_durable-storage-contract",
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
        "上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback",
        MASTER_PROGRAM_NAME,
        MASTER_PROGRAM_ARCHIVE,
    ]:
        if phrase not in current_readme + ingestion_archive_text + production_archive_text:
            errors.append(f".agent/programs active surface missing phrase: {phrase}")
    phase03_path = REPO_ROOT / "docs/history/programs/zuno-workflow-doc-system-v1/PHASE03_skill-template-program-system.md"
    if not phase03_path.exists():
        errors.append("missing archived Program 1 PHASE03 Skill / Template / Program plan")
    else:
        phase03 = phase03_path.read_text(encoding="utf-8")
        for phrase in [
            "本地 skill system",
            "skill / lesson / playbook",
            "queued program",
        ]:
            if phrase not in phase03:
                errors.append(f"archived Program 1 PHASE03 Skill / Template / Program plan missing phrase: {phrase}")
    active_phase_names = sorted(path.name for path in programs_root.glob("PHASE*.md"))
    if active_phase_names != [
        "PHASE01_truth-source-and-gap-audit.md",
        "PHASE02_durable-storage-contract.md",
    ]:
        errors.append(".agent/programs active phase files drifted: " + ", ".join(active_phase_names))
    if (programs_root / "thread-prompts").exists():
        errors.append(".agent/programs/thread-prompts must stay archived until Program 3 starts")
    for phase_name in CURRENT_ACTIVE_PROGRAM_PHASE_FILES:
        phase_path = ingestion_archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"completed ingestion program archive missing phase: {phase_name}")
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if "program: zuno-production-document-ingestion-and-thread-foundation-v1" not in phase_content:
            errors.append(f"completed ingestion program phase missing program id: {phase_name}")
        if "status: completed" not in phase_content:
            errors.append(f"completed ingestion program phase missing completed status: {phase_name}")
        for required in [
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
            if required not in phase_content:
                errors.append(f"completed ingestion program phase missing section {required}: {phase_name}")
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (ingestion_archive_root / required_archive_file).exists():
            errors.append(f"completed ingestion program archive missing file: {required_archive_file}")
    for file_name in THREAD_PROMPT_FILES:
        if not (ingestion_archive_root / "thread-prompts" / file_name).exists():
            errors.append(f"completed ingestion program thread prompt missing file: {file_name}")
    queued_root = programs_root / "queued-programs"
    queued_files = sorted(path.name for path in queued_root.glob("*.md")) if queued_root.exists() else []
    if queued_files != sorted(QUEUED_PROGRAM_FILES):
        errors.append(".agent/programs queued program files drifted: " + ", ".join(queued_files))
    for file_name in QUEUED_PROGRAM_FILES:
        queued_path = queued_root / file_name
        if not queued_path.exists():
            errors.append(f"queued program missing file: {file_name}")
            continue
        content = queued_path.read_text(encoding="utf-8")
        if file_name != "README.md" and "state: queued" not in content:
            errors.append(f"queued program file missing queued state: {file_name}")
    errors.extend(_verify_archived_phase_state())
    for phase_name in ACTIVE_PROGRAM_PHASE_FILES:
        phase_path = production_archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"production completion program archive missing phase: {phase_name}")
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if "status: completed" not in phase_content:
            errors.append(f"production completion program archive phase missing completed status: {phase_name}")
        for required in [
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
            if required not in phase_content:
                errors.append(f"production completion program archive phase missing section {required}: {phase_name}")
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (production_archive_root / required_archive_file).exists():
            errors.append(f"production completion program archive missing file: {required_archive_file}")
    for phase_index, phase_name in enumerate(RUNTIME_PROGRAM_PHASE_FILES, start=1):
        phase_path = runtime_archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"runtime program archive missing phase: {phase_name}")
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if "status: completed" not in phase_content:
            errors.append(f"runtime program archive phase status drifted: {phase_name}")
        for required in ["## 目标", "## 范围", "## 禁止范围", "## 验收闸门", "## 验证命令"]:
            if required not in phase_content:
                errors.append(f"runtime program archive phase missing section {required}: {phase_name}")
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (runtime_archive_root / required_archive_file).exists():
            errors.append(f"runtime program archive missing file: {required_archive_file}")
    master_archive_root = REPO_ROOT / MASTER_PROGRAM_ARCHIVE
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (master_archive_root / required_archive_file).exists():
            errors.append(f"master program archive missing file: {required_archive_file}")
    for phase_name in MASTER_PROGRAM_PHASE_FILES:
        phase_path = master_archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"master program archive missing phase: {phase_name}")
            continue
        if "status: completed" not in phase_path.read_text(encoding="utf-8"):
            errors.append(f"master program archive phase missing completed status: {phase_name}")
    archive_root = REPO_ROOT / COMPLETED_PROGRAM_ARCHIVE
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (archive_root / required_archive_file).exists():
            errors.append(f"completed program archive missing file: {required_archive_file}")
    for phase_name in COMPLETED_PROGRAM_PHASE_FILES:
        phase_path = archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"completed program archive missing phase: {phase_name}")
            continue
        if "status: completed" not in phase_path.read_text(encoding="utf-8"):
            errors.append(f"completed program archive phase missing completed status: {phase_name}")
    archived_program4 = REPO_ROOT / "docs/history/programs/zuno-six-layer-internalization-v1/README.md"
    if not archived_program4.exists():
        errors.append("missing archived Program 4 README")
    else:
        archived_text = archived_program4.read_text(encoding="utf-8")
        for phrase in [
            "completed / archived",
            "Capability tools 不按 CLI / API 拆成两棵顶层目录",
            "PHASE01-07",
        ]:
            if phrase not in archived_text:
                errors.append(f"archived Program 4 README missing phrase: {phrase}")
    for phase_name in [
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
        if not (REPO_ROOT / "docs/history/programs/zuno-repo-layout-cleanup-v1" / phase_name).exists():
            errors.append(f"missing archived Program 3 continuation phase: {phase_name}")
    archived_program3 = REPO_ROOT / "docs/history/programs/zuno-repo-layout-cleanup-v1/README.md"
    if not archived_program3.exists():
        errors.append("missing archived Program 3 README")
    else:
        archived_text = archived_program3.read_text(encoding="utf-8")
        for phrase in [
            "root/docs hygiene",
            "backend 六层迁移计划",
            "repo hygiene verifier",
            "Directory Surface Alignment V1",
        ]:
            if phrase not in archived_text:
                errors.append(f"archived Program 3 README missing phrase: {phrase}")
    archived_future_programs = (
        REPO_ROOT
        / "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/programs"
    )
    if not archived_future_programs.exists():
        errors.append("missing archived future architecture programs")
    system_yaml_path = REPO_ROOT / ".agent/system.yaml"
    if not system_yaml_path.exists():
        errors.append("missing .agent/system.yaml")
    else:
        system_yaml = system_yaml_path.read_text(encoding="utf-8")
        for phrase in [
            "new_program_first_phase: \"PHASE01\"",
            "skill_routes:",
            ".agent/references/workflow.md",
        ]:
            if phrase not in system_yaml:
                errors.append(f".agent/system.yaml missing phrase: {phrase}")
    return errors


def verify_architecture_diagram_outputs() -> list[str]:
    errors: list[str] = []
    architecture_source = _read_text("docs/architecture/architecture.md")
    for phrase in [
        "Zuno 架构总览",
        "python tools/agent/render_architecture.py --check",
        "#f7f8fb",
        "#ffffff",
        "#b8c2cc",
        "#16202a",
        "#52616f",
    ]:
        if phrase not in architecture_source:
            errors.append(f"docs/architecture/architecture.md missing diagram sync phrase: {phrase}")

    for stale_path in [
        "docs/architecture.md",
        "docs/architecture.html",
        "docs/architecture/overview.html",
        ".agent/architecture/blueprint.html",
    ]:
        if (REPO_ROOT / stale_path).exists():
            errors.append(f"stale architecture HTML must not remain: {stale_path}")

    for relative_path in ["docs/architecture/architecture.html", ".agent/architecture/architecture.html"]:
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing architecture diagram HTML: {relative_path}")
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in [
            "docs/architecture/architecture.md",
            "tools/agent/render_architecture.py",
            "4+1 View Model",
            "Component-and-Connector View",
            "Deployment View",
            "Quality View",
            "Scenarios View",
            "Process View",
            "V&amp;B Logical View",
            "V&amp;B Deployment View",
            "Agent Loop View",
            "#f7f8fb",
            "#ffffff",
            "#b8c2cc",
            "#16202a",
            "#52616f",
        ]:
            if phrase not in content:
                errors.append(f"{relative_path} missing diagram HTML phrase: {phrase}")
    script_path = REPO_ROOT / "tools/agent/render_architecture.py"
    if script_path.exists():
        spec = importlib.util.spec_from_file_location("render_architecture", script_path)
        if spec is None or spec.loader is None:
            errors.append("cannot load tools/agent/render_architecture.py")
        else:
            render_architecture = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = render_architecture
            spec.loader.exec_module(render_architecture)
            rendered = render_architecture.build_html()
            for relative_path in ["docs/architecture/architecture.html"]:
                path = REPO_ROOT / relative_path
                if path.exists() and path.read_text(encoding="utf-8") != rendered:
                    errors.append(f"generated architecture HTML is stale: {relative_path}")
            agent_source_path = REPO_ROOT / ".agent/architecture/architecture.md"
            docs_source_path = REPO_ROOT / "docs/architecture/architecture.md"
            if agent_source_path.exists() and agent_source_path.read_bytes() != docs_source_path.read_bytes():
                errors.append(".agent/architecture/architecture.md is stale")
            for relative_path in [".agent/architecture/architecture.html"]:
                path = REPO_ROOT / relative_path
                if path.exists() and path.read_text(encoding="utf-8") != rendered:
                    errors.append(f"generated architecture HTML is stale: {relative_path}")
    return errors


def run_verification() -> VerificationResult:
    return VerificationResult(
        errors=[
            *verify_required_paths(),
            *verify_forbidden_current_paths(),
            *verify_doc_phrases(),
            *verify_root_local_artifacts_are_absent(),
            *verify_first_class_directory_responsibilities(),
            *verify_backend_zuno_directory_classifications(),
            *verify_backend_layer_internal_surfaces(),
            *verify_backend_owner_docs_do_not_reference_retired_physical_paths(),
            *verify_phase02_backend_ownership_matrix(),
            *verify_phase02_platform_services_owner_guard(),
            *verify_phase02_capability_provider_guard(),
            *verify_phase02_compatibility_vendor_boundary(),
            *verify_phase02_reserved_import_guards(),
            *verify_backend_legacy_import_aliases(),
            *verify_backend_retired_top_level_paths_are_absent(),
            *verify_architecture_surface_cleanup_archive(),
            *verify_completed_architecture_surface_phase_plan(),
            *verify_architecture_diagram_outputs(),
        ]
    )


def main() -> int:
    result = run_verification()
    if result.ok:
        print("Repository structure verification passed.")
        return 0

    for error in result.errors:
        print(f"ERROR: {error}")
    print("Repository structure verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

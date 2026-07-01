Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$failures = New-Object System.Collections.Generic.List[string]

function Require-Path($Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        $failures.Add("Missing path: $Path")
    }
}

function Require-NoPath($Path) {
    if (Test-Path -LiteralPath $Path) {
        $failures.Add("Unexpected path: $Path")
    }
}

Require-Path "AGENTS.md"
$legacyAgentEntrypoint = "agent" + ".md"
Require-NoPath $legacyAgentEntrypoint
Require-Path ".agent\README.md"
Require-Path ".agent\references\README.md"
Require-Path ".agent\references\current-program.md"
Require-Path ".agent\references\docs-map.md"
Require-Path ".agent\references\code-map.md"
Require-Path ".agent\references\task-routing.md"
Require-Path ".agent\references\workflow.md"
Require-Path ".agent\references\verification-map.md"
Require-Path ".agent\system.yaml"
Require-Path ".agent\architecture\README.md"
Require-Path ".agent\architecture\architecture.md"
Require-Path ".agent\architecture\architecture.html"
Require-Path "docs\architecture\README.md"
Require-Path "docs\architecture\architecture.md"
Require-Path "docs\architecture\architecture.html"
Require-Path ".agent\programs\current.md"
Require-Path ".agent\programs\README.md"
Require-Path ".agent\programs\implementation-roadmap.md"
Require-Path ".agent\programs\closure-checklist.md"
Require-Path ".agent\programs\PHASE01_truth-source-and-merge-plan.md"
Require-Path ".agent\programs\PHASE02_shared-contract-freeze.md"
Require-Path ".agent\programs\PHASE03_enterprise-ingestion-async-infrastructure.md"
Require-Path ".agent\programs\PHASE04_knowledge-retrieval-and-graphrag-profile.md"
Require-Path ".agent\programs\PHASE05_memory-context-engine.md"
Require-Path ".agent\programs\PHASE06_capability-skill-tool-mcp-layer.md"
Require-Path ".agent\programs\PHASE07_security-governance-envelope.md"
Require-Path ".agent\programs\PHASE08_model-gateway-cost-latency.md"
Require-Path ".agent\programs\PHASE09_planning-contract-and-strategy-selector.md"
Require-Path ".agent\programs\PHASE10_react-reflection-replan-reflexion-runtime.md"
Require-Path ".agent\programs\PHASE11_workspace-product-api-frontend-sync.md"
Require-Path ".agent\programs\PHASE12_end-to-end-product-runtime.md"
Require-Path ".agent\programs\PHASE13_eval-trace-cost-benchmark.md"
Require-Path ".agent\programs\PHASE14_docs-architecture-expansion.md"
Require-Path ".agent\programs\PHASE15_verification-archive-closure.md"
Require-NoPath ".agent\programs\PHASE01_truth-source-and-gap-audit.md"
Require-NoPath ".agent\programs\PHASE02_durable-storage-contract.md"
Require-NoPath ".agent\programs\PHASE01_program-truth-source-and-parser-current-audit.md"
Require-NoPath ".agent\programs\PHASE02_document-ir-and-parser-contract-freeze.md"
Require-NoPath ".agent\programs\PHASE03_parser-worker-runtime-and-job-lifecycle.md"
Require-NoPath ".agent\programs\PHASE04_native-text-and-structured-file-parsers.md"
Require-NoPath ".agent\programs\PHASE05_pdf-office-ocr-adapter-boundaries.md"
Require-NoPath ".agent\programs\PHASE06_index-handoff-provenance-and-fixtures.md"
Require-NoPath ".agent\programs\PHASE07_program2-thread-prompts-and-branch-plan.md"
Require-NoPath ".agent\programs\PHASE08_verification-doc-sync-and-closure.md"
Require-NoPath ".agent\programs\thread-prompts"
Require-Path ".agent\programs\queued-programs\README.md"
Require-Path ".agent\programs\queued-programs\PROGRAM04_runtime-subsystems-parallel.md"
Require-Path ".agent\programs\queued-programs\PROGRAM05_agent-planning-integration.md"
Require-Path ".agent\programs\queued-programs\PROGRAM06_enterprise-knowledge-eval-benchmark.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\README.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\current.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\implementation-roadmap.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\closure-checklist.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\closure-summary.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\PHASE01_truth-source-and-gap-audit.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\PHASE02_durable-storage-contract.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\PHASE03_workspace-file-durable-input.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\PHASE04_parse-document-persistence.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\PHASE05_index-persistence-rehydrate.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\PHASE06_workspace-product-durable-closure.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\PHASE07_restart-recovery-end-to-end.md"
Require-Path "docs\history\programs\zuno-enterprise-document-ingestion-platform-v2\PHASE08_docs-verifier-closure.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\README.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\current.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\implementation-roadmap.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\closure-checklist.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\closure-summary.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\PHASE01_program-truth-source-and-parser-current-audit.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\PHASE02_document-ir-and-parser-contract-freeze.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\PHASE03_parser-worker-runtime-and-job-lifecycle.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\PHASE04_native-text-and-structured-file-parsers.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\PHASE05_pdf-office-ocr-adapter-boundaries.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\PHASE06_index-handoff-provenance-and-fixtures.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\PHASE07_program2-thread-prompts-and-branch-plan.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\PHASE08_verification-doc-sync-and-closure.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\thread-prompts\THREAD_A_memory-context.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\thread-prompts\THREAD_B_tool-sandbox.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\thread-prompts\THREAD_C_security-governance.md"
Require-Path "docs\history\programs\zuno-production-document-ingestion-and-thread-foundation-v1\thread-prompts\THREAD_D_graphrag-index.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\README.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\current.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\implementation-roadmap.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\closure-checklist.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\closure-summary.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE01_production-maturity-gap-audit.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE02_program-truth-source-and-execution-system.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE03_workflow-self-maintenance-automation.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE04_documentation-dedup-architecture-clarity.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE05_repo-ownership-and-compatibility-retirement.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE06_product-surface-desktop-recovery-loop.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE07_production-parse-and-index-platform.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE08_durable-agent-runtime-persistence.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE09_memory-context-production-governance.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE10_tool-sandbox-vault-network-runtime.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE11_production-graphrag-evidence-citation.md"
Require-Path "docs\history\programs\zuno-production-architecture-and-deliverables-completion-v1\PHASE12_security-trace-eval-release-closure.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\implementation-roadmap.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\closure-checklist.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\closure-summary.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE01_program-reopen-and-truth-source-freeze.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE02_runtime-migration-map-and-repo-ownership-lock.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE03_task-session-artifact-event-runtime.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE04_document-ingestion-parse-runtime.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE05_index-jobs-and-knowledge-space-runtime.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE06_durable-single-controller-runtime.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE07_memory-db-and-context-governance.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE08_tool-control-plane-approval-and-sandbox-runtime.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE09_agentic-retrieval-evidence-citation-runtime.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE10_security-observability-and-online-eval.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE11_web-desktop-surface-and-feedback-loop.md"
Require-Path "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\PHASE12_release-gate-full-e2e-closure.md"
Require-NoPath ".agent\programs\PHASE01_program-baseline-and-previous-closure.md"
Require-NoPath ".agent\programs\PHASE02_project-folder-and-code-layout-cleanup.md"
Require-NoPath ".agent\programs\PHASE03_enterprise-scenario-and-product-loop.md"
Require-NoPath ".agent\programs\PHASE04_document-ingestion-parse-gateway.md"
Require-NoPath ".agent\programs\PHASE05_agent-runtime-langgraph-harness.md"
Require-NoPath ".agent\programs\PHASE06_context-memory-system.md"
Require-NoPath ".agent\programs\PHASE07_tool-control-plane-mcp-approval.md"
Require-NoPath ".agent\programs\PHASE08_rag-graphrag-evidence-citation.md"
Require-NoPath ".agent\programs\PHASE09_security-governance-sandbox.md"
Require-NoPath ".agent\programs\PHASE10_eval-observability-langsmith.md"
Require-NoPath ".agent\programs\PHASE11_architecture-docs-html-refresh.md"
Require-NoPath ".agent\programs\PHASE12_validation-release-closure.md"
Require-NoPath ".agent\programs\PHASE01_program-boot-baseline.md"
Require-NoPath ".agent\programs\PHASE02_workflow-self-maintenance-system.md"
Require-NoPath ".agent\programs\PHASE03_architecture-docs-html-system.md"
Require-NoPath ".agent\programs\PHASE04_query-router-mode-policy.md"
Require-NoPath ".agent\programs\PHASE05_context-builder-memory-system.md"
Require-NoPath ".agent\programs\PHASE06_capability-toolcard-mcp-system.md"
Require-NoPath ".agent\programs\PHASE07_hooks-evidence-trace-artifact-system.md"
Require-NoPath ".agent\programs\PHASE08_graphrag-knowledge-runtime-system.md"
Require-NoPath ".agent\programs\PHASE09_runtime-upgrade-integration.md"
Require-NoPath ".agent\programs\PHASE10_validation-release-closure.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\README.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\current.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\implementation-roadmap.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\closure-checklist.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\closure-summary.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE01_program-baseline-and-previous-closure.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE02_project-folder-and-code-layout-cleanup.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE03_enterprise-scenario-and-product-loop.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE04_document-ingestion-parse-gateway.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE05_agent-runtime-langgraph-harness.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE06_context-memory-system.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE07_tool-control-plane-mcp-approval.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE08_rag-graphrag-evidence-citation.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE09_security-governance-sandbox.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE10_eval-observability-langsmith.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE11_architecture-docs-html-refresh.md"
Require-Path "docs\history\programs\zuno-master-architecture-implementation-v1\PHASE12_validation-release-closure.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\README.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\current.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\implementation-roadmap.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\closure-checklist.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\closure-summary.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE01_program-boot-baseline.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE02_workflow-self-maintenance-system.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE03_architecture-docs-html-system.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE04_query-router-mode-policy.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE05_context-builder-memory-system.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE06_capability-toolcard-mcp-system.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE07_hooks-evidence-trace-artifact-system.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE08_graphrag-knowledge-runtime-system.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE09_runtime-upgrade-integration.md"
Require-Path "docs\history\programs\zuno-eight-deliverables-full-realization-v1\PHASE10_validation-release-closure.md"
Require-Path "docs\history\programs\zuno-architecture-detail-and-execution-plan-v1\README.md"
Require-Path "docs\history\programs\zuno-architecture-detail-and-execution-plan-v1\current.md"
Require-Path "docs\history\programs\zuno-architecture-detail-and-execution-plan-v1\implementation-roadmap.md"
Require-Path "docs\history\programs\zuno-architecture-detail-and-execution-plan-v1\closure-checklist.md"
Require-Path "docs\history\programs\zuno-architecture-detail-and-execution-plan-v1\closure-summary.md"
Require-Path "docs\history\research\README.md"
Require-Path "docs\history\research\chatgpt-research-mode-artifacts\README.md"
Require-Path "docs\history\research\chatgpt-research-mode-artifacts\zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.pdf"
Require-Path "docs\history\research\chatgpt-research-mode-artifacts\zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.md"
Require-Path "docs\history\research\chatgpt-research-mode-artifacts\zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf"
Require-Path "docs\history\research\chatgpt-research-mode-artifacts\zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.md"
Require-Path "docs\architecture\assets\zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf"
Require-Path "docs\history\architecture-surface-cleanup-2026-06-30\README.md"
Require-Path "docs\history\architecture-surface-cleanup-2026-06-30\docs-architecture\current-architecture.md"
Require-Path "docs\history\architecture-surface-cleanup-2026-06-30\docs-architecture\target-architecture.md"
Require-Path "docs\history\architecture-surface-cleanup-2026-06-30\docs-architecture\roadmap.md"
Require-Path "docs\history\architecture-surface-cleanup-2026-06-30\docs-architecture\deliverables.md"
Require-Path "docs\history\architecture-surface-cleanup-2026-06-30\agent-architecture\future\programs\README.md"
Require-Path "docs\history\architecture-surface-cleanup-2026-06-30\agent-architecture\near-term\00-architecture-index.md"
Require-NoPath ".agent\programs\thread-prompts\THREAD_D_resources-compatibility-physical-migration-prompt.md"
Require-NoPath ".agent\programs\thread-prompts\THREAD_E_target-layer-physical-migration-prompt.md"
Require-NoPath ".agent\programs\PHASE01_workflow-doc-audit.md"
Require-NoPath ".agent\programs\PHASE02_agent-bootloader-routing.md"
Require-NoPath ".agent\programs\PHASE03_skill-template-program-system.md"
Require-NoPath ".agent\programs\PHASE04_workflow-verifiers-drift-tests.md"
Require-NoPath ".agent\programs\PHASE05_closure-history-archive.md"
Require-NoPath ".agent\programs\PHASE06_backend-directory-clarity-audit.md"
Require-NoPath ".agent\programs\PHASE07_fastapi-jwt-auth-compat-retirement-plan.md"
Require-NoPath ".agent\programs\PHASE08_backend-physical-cleanup-slices.md"
Require-NoPath ".agent\programs\PHASE09_target-layout-visual-compat-shell-retirement.md"
Require-NoPath ".agent\programs\PHASE01_alias-inventory-and-target-contract.md"
Require-NoPath ".agent\programs\PHASE02_import-smoke-and-compat-registry-design.md"
Require-NoPath ".agent\programs\PHASE03_low-risk-alias-surface-cleanup.md"
Require-NoPath ".agent\programs\PHASE04_medium-risk-alias-surface-cleanup.md"
Require-NoPath ".agent\programs\PHASE05_high-risk-core-services-settings-cleanup.md"
Require-NoPath ".agent\programs\PHASE06_final-root-surface-guard-and-closure.md"
Require-NoPath ".agent\architecture\future\programs\zuno-target-architecture-refresh-v1"
Require-NoPath ".agent\architecture\future\programs\zuno-repo-layout-cleanup-v1"
Require-NoPath ".agent\architecture\future"
Require-NoPath ".agent\architecture\near-term"
Require-NoPath ".agent\architecture\decisions"
Require-NoPath "docs\architecture\current-architecture.md"
Require-NoPath "docs\architecture\target-architecture.md"
Require-NoPath "docs\architecture\roadmap.md"
Require-NoPath "docs\architecture\deliverables.md"
Require-NoPath "docs\architecture\overall-architecture.md"
Require-NoPath ".agent\architecture\overall-architecture.md"
Require-NoPath ".agent\programs\zuno-target-runtime-v2"
Require-NoPath ".agent\programs\phase-05-memory-engine.md"
Require-NoPath ".agent\programs\phase-06-capability-tool-retrieval.md"
Require-NoPath ".agent\programs\phase-07-graphrag-llm-entity-extraction.md"
Require-NoPath ".agent\programs\phase-08-langgraph-runtime.md"
Require-NoPath ".agent\programs\phase-09-product-trace-eval-closure.md"
Require-NoPath ".agent\workflows"
Require-NoPath ".agent\skills"
Require-Path ".agent\templates\requirement-intake.md"
Require-Path ".agent\scripts\verify-docs.ps1"
Require-Path ".agent\scripts\verify_agent_system.py"
Require-Path ".agent\scripts\verify_doc_boundaries.py"
Require-Path ".agent\scripts\verify_repo_hygiene.py"
Require-Path ".agent\scripts\grep-legacy.ps1"
Require-Path ".agent\scripts\grep-domain-pack.ps1"
Require-Path "docs\history\programs\zuno-target-architecture-migration-v1\README.md"
Require-Path "docs\history\programs\official-graphrag-cleanup-v1\README.md"
Require-Path "docs\history\programs\context-memory-agent-runtime-v1\README.md"
Require-Path "docs\history\programs\zuno-workflow-doc-system-v1\README.md"
Require-Path "docs\history\programs\zuno-target-architecture-refresh-v1\README.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\README.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\implementation-roadmap.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE01_repo-layout-audit.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE05_hygiene-verifier-closure.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE06_backend-directory-clarity-audit.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE07_fastapi-jwt-auth-compat-retirement-plan.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE08_backend-physical-cleanup-slices.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE09_target-layout-visual-compat-shell-retirement.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE10_alias-inventory-and-target-contract.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE11_import-smoke-and-compat-registry-design.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE12_low-risk-alias-surface-cleanup.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE13_medium-risk-alias-surface-cleanup.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE14_high-risk-core-services-settings-cleanup.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE15_final-root-surface-guard-and-closure.md"
Require-Path "docs\history\README.md"
Require-Path "apps\web\AGENTS.md"
Require-Path "tools\evals\zuno\AGENTS.md"

$gitignore = Get-Content -LiteralPath ".gitignore" -Raw -Encoding UTF8
if ($gitignore -match "(?m)^\.agent/?$") {
    $failures.Add(".gitignore must not ignore the whole .agent directory")
}
foreach ($ignored in @(".agent/local/*", ".agent/local/notes/", ".agent/local/tmp/", ".agent/local/logs/", ".agent/local/secrets/")) {
    if ($gitignore -notmatch [regex]::Escape($ignored)) {
        $failures.Add(".gitignore missing $ignored")
    }
}

if ($gitignore -match "(?m)^apps/web/AGENTS\.md$") {
    $failures.Add(".gitignore must not ignore apps/web/AGENTS.md")
}

$agentText = Get-Content -LiteralPath "AGENTS.md" -Raw -Encoding UTF8
foreach ($required in @("docs/", "AGENTS.md", ".agent/", "docs/history/", ".agent/references/task-routing.md", ".agent/references/workflow.md")) {
    if ($agentText -notmatch [regex]::Escape($required)) {
        $failures.Add("AGENTS.md missing required text: $required")
    }
}

$currentProgram = Get-Content -LiteralPath ".agent\references\current-program.md" -Raw -Encoding UTF8
if ($currentProgram -notmatch "zuno-enterprise-document-ingestion-platform-v2" -or $currentProgram -notmatch "state: active" -or $currentProgram -notmatch "active_program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1" -or $currentProgram -notmatch "current_phase: PHASE03_enterprise-ingestion-async-infrastructure.md" -or $currentProgram -notmatch "latest_completed_program: zuno-enterprise-document-ingestion-platform-v2") {
    $failures.Add("current-program.md must declare active Program 3 Mega state and latest completed Program 2")
}
if ($currentProgram -notmatch "zuno-production-document-ingestion-and-thread-foundation-v1" -or $currentProgram -notmatch "zuno-enterprise-agentic-graphrag-production-suite-v1" -or $currentProgram -notmatch "zuno-launchable-enterprise-agentic-graphrag-full-closure-v1" -or $currentProgram -notmatch "zuno-enterprise-ingestion-async-infrastructure-v1" -or $currentProgram -notmatch "zuno-runtime-subsystems-parallel-v1" -or $currentProgram -notmatch "zuno-agent-planning-integration-v1" -or $currentProgram -notmatch "zuno-enterprise-knowledge-eval-benchmark-v1") {
    $failures.Add("current-program.md missing Program 1-3 mega suite map")
}
if ($currentProgram -notmatch "docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/" -or $currentProgram -notmatch "Product V1 local durable ingestion baseline") {
    $failures.Add("current-program.md missing latest Program 2 archive and durable baseline summary")
}
if ($currentProgram -notmatch "docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/") {
    $failures.Add("current-program.md must keep latest production completion archive")
}
if ($currentProgram -notmatch "zuno-target-architecture-runtime-full-implementation-v1" -or $currentProgram -notmatch "docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/") {
    $failures.Add("current-program.md must keep latest runtime full implementation archive")
}
if ($currentProgram -notmatch "runtime-first / vertical-slice-first" -or $currentProgram -notmatch "只写 contract、schema 或 README 不能关闭 runtime phase") {
    $failures.Add("current-program.md missing runtime-first closure guard")
}
if ($currentProgram -notmatch "一次性交付型成熟化 program" -or $currentProgram -notmatch "成熟目标架构和四大总交付物完成") {
    $failures.Add("current-program.md missing production completion program goal")
}
if ($currentProgram -notmatch "zuno-master-architecture-implementation-v1") {
    $failures.Add("current-program.md must keep the archived master architecture implementation program visible")
}
if ($currentProgram -notmatch "zuno-eight-deliverables-full-realization-v1") {
    $failures.Add("current-program.md must keep the completed eight deliverables program visible")
}
if ($currentProgram -notmatch "PHASE01-PHASE10" -or $currentProgram -notmatch "docs/history/programs/zuno-eight-deliverables-full-realization-v1/") {
    $failures.Add("current-program.md missing completed archive boundaries")
}
if ($currentProgram -notmatch "PHASE01-PHASE12" -or $currentProgram -notmatch "docs/history/programs/zuno-master-architecture-implementation-v1/") {
    $failures.Add("current-program.md missing latest archived master program boundary")
}
if ($currentProgram -notmatch "zuno-six-layer-internalization-v1" -or $currentProgram -notmatch "docs/history/programs/zuno-six-layer-internalization-v1/") {
    $failures.Add("current-program.md missing archived six-layer internalization program facts")
}
if ($currentProgram -notmatch "\.agent/programs/") {
    $failures.Add("current-program.md does not point to the flat program directory")
}
if ($currentProgram -notmatch "zuno-repo-layout-cleanup-v1") {
    $failures.Add("current-program.md missing completed repo layout cleanup program id")
}
if ($currentProgram -notmatch "zuno-runtime-architecture-upgrade-v1" -or $currentProgram -notmatch "zuno-architecture-visuals-v1") {
    $failures.Add("current-program.md missing future reference draft ids")
}
if ($currentProgram -notmatch "final alias surface closure" -or $currentProgram -notmatch "legacy_aliases.py") {
    $failures.Add("current-program.md missing historical Program 3 final alias closure completion facts")
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

python .agent\scripts\verify_agent_system.py
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

python .agent\scripts\verify_doc_boundaries.py
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

python .agent\scripts\verify_repo_hygiene.py
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Workflow verification passed."

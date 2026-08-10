from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

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
COMPLETED_PROGRAM_NAME = "zuno-eight-deliverables-full-realization-v1"
COMPLETED_PROGRAM_ARCHIVE = f"docs/history/programs/{COMPLETED_PROGRAM_NAME}"
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
]
EVIDENCE_SPAN_PROGRAM_NAME = "zuno-evidence-span-agentic-graphrag-hardening-v1"
EVIDENCE_SPAN_PROGRAM_ARCHIVE = f"docs/history/programs/{EVIDENCE_SPAN_PROGRAM_NAME}"
EVIDENCE_SPAN_PROGRAM_PHASE_FILES = [
    "PHASE01_eval-truth-source-and-gap-buckets.md",
    "PHASE02_source-span-provenance-contract.md",
    "PHASE03_citation-sized-chunk-index.md",
    "PHASE04_lexical-phrase-evidence-retriever.md",
    "PHASE05_entity-chunk-bidirectional-graph-index.md",
    "PHASE06_evidence-aware-reranker.md",
    "PHASE07_claim-level-citation-binder.md",
    "PHASE08_hard-negative-eval-and-release-gate.md",
]
UNIFIED_RUNTIME_PROGRAM_NAME = "zuno-unified-agent-runtime-closure-v1"
UNIFIED_RUNTIME_PROGRAM_ARCHIVE = f"docs/history/programs/{UNIFIED_RUNTIME_PROGRAM_NAME}"
UNIFIED_RUNTIME_CURRENT_PHASE = "PHASE13_paired-benchmark-release-gate-and-program-closure"
UNIFIED_RUNTIME_PHASE_FILES = [
    "PHASE01_truth-source-baseline-and-program-activation.md",
    "PHASE02_unified-runtime-contracts-and-state.md",
    "PHASE03_model-gateway-closure.md",
    "PHASE04_durable-store-trace-and-idempotency.md",
    "PHASE05_unified-langgraph-runtime-skeleton.md",
    "PHASE06_strategy-plan-and-react-step-execution.md",
    "PHASE07_tool-control-plane-and-approval-integration.md",
    "PHASE08_corrective-agentic-graphrag-and-evidence-ledger.md",
    "PHASE09_reflection-replan-grounded-synthesis.md",
    "PHASE10_four-layer-memory-and-reflexion-reuse.md",
    "PHASE11_product-api-sse-ui-and-recovery-cutover.md",
    "PHASE12_real-pdf-source-span-vertical-slice.md",
    "PHASE13_paired-benchmark-release-gate-and-program-closure.md",
]
UNIFIED_RUNTIME_PROGRAM_FILES = [
    *ACTIVE_PROGRAM_FILES,
    "baseline-manifest.md",
    "program-decisions.md",
    "code-architecture-map.md",
    "powershell-runbook.md",
    "test-matrix.md",
    *UNIFIED_RUNTIME_PHASE_FILES,
]
CURRENT_FRONT_PROGRAM_FILES = [
    *ACTIVE_PROGRAM_FILES,
]
PROGRAM3_ACTIVE_NAME = "zuno-launchable-enterprise-agentic-graphrag-full-closure-v1"
PROGRAM3_ACTIVE_ARCHIVE = f"docs/history/programs/{PROGRAM3_ACTIVE_NAME}"
PROGRAM3_ACTIVE_PHASE_FILES = [
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
    "PROGRAM01_real-unified-runtime-cutover.md",
]
PROGRAM3_MERGED_QUEUED_FILES = [
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


def test_agent_architecture_and_module_mirrors_are_removed() -> None:
    assert not (REPO_ROOT / ".agent/architecture").exists()
    assert not (REPO_ROOT / ".agent/modules").exists()


def test_archived_agent_architecture_worksets_are_reachable() -> None:
    for relative_path in [
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/00-architecture-index.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/programs/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/decisions/README.md",
    ]:
        assert (REPO_ROOT / relative_path).exists(), f"missing archived workset: {relative_path}"


def test_agent_entrypoint_records_current_architecture_sync_and_work_modes() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for phrase in [
        "这是仓库唯一的 Agent 入口",
        "Architecture Documentation Governance",
        "Agent Workflow Self-Maintenance",
        "docs/architecture/architecture.md",
        "docs/architecture/architecture.html",
        ".agent/architecture/",
        "总架构 Markdown 必须比 HTML 更充实",
        "python tools/agent/render_architecture.py --write",
        "## 工作模式",
        "### 挂机模式",
        "### 多线程模式",
        "Single Controller 主线",
        "docs/status/production-readiness.md",
    ]:
        assert phrase in agents


def test_agent_references_keep_canonical_set() -> None:
    reference_files = sorted(
        path.name for path in (REPO_ROOT / ".agent/references").iterdir() if path.is_file()
    )
    expected_references = sorted(
        [
            "README.md",
            "agentchat-knowledge-lifecycle-implementation-plan.md",
            "agentchat-knowledge-profile-alignment.md",
            "agentic-retrieval-dashboard-observability-plan.md",
            "project-map.md",
            "current-program.md",
            "docs-map.md",
            "architecture-docs-map.md",
            "documentation-governance.md",
            "architecture-update-policy.md",
            "diagram-inventory.md",
            "current-target-future-rules.md",
            "workflow-governance.md",
            "workflow-update-policy.md",
            "workflow-requirements.md",
            "workflow-change-log.md",
            "workflow-maintenance-checklist.md",
            "code-map.md",
            "runtime-call-chain.md",
            "verification-map.md",
            "command-catalog.md",
            "known-pitfalls.md",
            "zuno-repo-hygiene.md",
            "task-routing.md",
            "workflow.md",
        ]
    )
    assert reference_files == expected_references


def test_agent_architecture_docs_map_explains_single_formal_source() -> None:
    content = (REPO_ROOT / ".agent/references/architecture-docs-map.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "docs/architecture/architecture.md",
        "docs/architecture/architecture.html",
        ".agent/",
        "Markdown 是重文字架构设计，HTML 是重图展示",
        "python tools/agent/render_architecture.py --write",
        "不恢复简化 offline SVG renderer",
        "不恢复拆分的 current/target/roadmap 前台文档",
    ]:
        assert phrase in content


def test_agent_program_surface_records_no_active_runtime_program() -> None:
    program_files = sorted(
        path.name for path in (REPO_ROOT / ".agent/programs").iterdir() if path.is_file()
    )
    required_files = {
        "README.md",
        "current.md",
        "implementation-roadmap.md",
        "closure-checklist.md",
    }
    assert set(program_files) == required_files
    current_program = (REPO_ROOT / ".agent/programs/current.md").read_text(encoding="utf-8")
    current_reference = (REPO_ROOT / ".agent/references/current-program.md").read_text(encoding="utf-8")
    phase22 = (REPO_ROOT / "docs/history/programs/zuno-canonical-architecture-runtime-realization-v1/PHASE22_fixed-benchmark-production-readiness-and-closure.md").read_text(encoding="utf-8")
    for phrase in [
        "state: no-active",
        "active_program: none",
        "current_phase: none",
        "phase_count: 22",
    ]:
        assert phrase in current_program + current_reference
    assert "phase_id: PHASE22" in phase22
    assert "status: completed" in phase22
    assert "Fixed Benchmark" in phase22
    assert (REPO_ROOT / "docs/history/programs/zuno-canonical-architecture-runtime-realization-v1/thread-prompts").is_dir()
    assert list((REPO_ROOT / "docs/history/programs/zuno-canonical-architecture-runtime-realization-v1").glob("PHASE*.md"))


def test_program2_thread_prompts_are_target_mode_ready_and_guarded() -> None:
    prompt_root = REPO_ROOT / CURRENT_ACTIVE_PROGRAM_ARCHIVE / "thread-prompts"
    prompt_files = sorted(path.name for path in prompt_root.glob("*.md"))
    assert prompt_files == sorted(THREAD_PROMPT_FILES)

    verifier = (REPO_ROOT / ".agent/scripts/verify_agent_system.py").read_text(
        encoding="utf-8"
    )
    assert "verify_architecture_directory_contract" in verifier
    assert "verify_mirrors" not in verifier

    required_phrases = [
        "## UI Mode",
        "Codex UI 目标模式",
        "## Goal",
        "## Safety Gate",
        "git fetch --prune",
        "git status --short --branch",
        "git log --oneline -5 --decorate",
        "## Program 1 Shared Facts",
        "Document IR",
        "citation_lineage",
        "target-blocked",
        "## Allowed Paths",
        "## Forbidden Paths",
        "## Focused Tests",
        "## Stop Conditions",
        "Commit hash",
        "Push status",
    ]
    branch_by_file = {
        "THREAD_A_memory-context.md": "codex/zuno-p2-memory-context",
        "THREAD_B_tool-sandbox.md": "codex/zuno-p2-tool-sandbox",
        "THREAD_C_security-governance.md": "codex/zuno-p2-security-governance",
        "THREAD_D_graphrag-index.md": "codex/zuno-p2-graphrag-index",
    }
    ownership_by_file = {
        "THREAD_A_memory-context.md": "src/backend/zuno/memory/**",
        "THREAD_B_tool-sandbox.md": "src/backend/zuno/capability/**",
        "THREAD_C_security-governance.md": "src/backend/zuno/platform/security/**",
        "THREAD_D_graphrag-index.md": "src/backend/zuno/knowledge/**",
    }
    for file_name in THREAD_PROMPT_FILES:
        text = (prompt_root / file_name).read_text(encoding="utf-8")
        for phrase in required_phrases:
            assert phrase in text
        assert branch_by_file[file_name] in text
        assert ownership_by_file[file_name] in text
        assert "AGENTS.md" in text
        assert "docs/**" in text
        assert ".agent/**" in text


def test_closure_checklist_keeps_self_maintenance_gate() -> None:
    content = (
        REPO_ROOT / MASTER_PROGRAM_ARCHIVE / "closure-checklist.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "## Program Closure 自维护审查",
        "completed program 已归档到 `docs/history/programs/`",
        "如果用户提醒“以后注意”，不能只留在对话里",
        "verifier / tests 是否覆盖新规则",
    ]:
        assert phrase in content


def test_agent_verifier_enforces_workflow_self_maintenance_contracts() -> None:
    content = (REPO_ROOT / ".agent" / "scripts" / "verify_agent_system.py").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "verify_required_paths",
        "verify_architecture_directory_contract",
        "retired Agent documentation mirror must not exist",
        "verify_entrypoints",
        "verify_module_contracts",
        "verify_no_tracked_local_workspace",
    ]:
        assert phrase in content


def test_workflow_update_policy_requires_classification_and_writeback_evidence() -> None:
    content = (REPO_ROOT / ".agent/references/workflow-update-policy.md").read_text(
        encoding="utf-8"
    )
    template = (REPO_ROOT / ".agent/templates/workflow-change-note-template.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "规则分类证据",
        "写回路径证据",
        "one-time instruction",
        "reusable project rule",
        "architecture governance rule",
        "Codex execution rule",
        "documentation template rule",
        "long-term workflow rule",
    ]:
        assert phrase in content + template


def test_phase_closure_template_self_maintenance_review_is_not_duplicate() -> None:
    content = (REPO_ROOT / ".agent/templates/phase-closure-report.md").read_text(
        encoding="utf-8"
    )
    self_review = content.split("## 自维护审查", 1)[1].split("## 剩余风险", 1)[0]

    checklist_items = [
        line.strip()
        for line in self_review.splitlines()
        if line.strip().startswith("- ")
    ]
    assert len(checklist_items) == len(set(checklist_items))
    for phrase in [
        "`AGENTS.md`",
        "`.agent/system.yaml`",
        "`.agent/references/`",
        "`.agent/templates/`",
        "`.agent/programs/`",
        "`docs/history/programs/`",
        "`docs/architecture/architecture.md`",
        "`docs/architecture/architecture.html`",
        "verifier / tests",
    ]:
        assert phrase in self_review


def test_system_yaml_tracks_current_architecture_docs_sync() -> None:
    content = (REPO_ROOT / ".agent/system.yaml").read_text(encoding="utf-8")

    for phrase in [
        "Zuno Local Agent Skill System",
        "new_program_first_phase: \"PHASE01\"",
        "skill_routes:",
        "docs_sync:",
        "docs/status/production-readiness.md",
        "verify:",
        ".agent/references/workflow.md",
        ".agent/references/architecture-docs-map.md",
        "python tools/agent/render_architecture.py --check",
        "python tools/scripts/verify_docs_entrypoints.py",
        "python .agent/scripts/verify_agent_system.py",
    ]:
        assert phrase in content

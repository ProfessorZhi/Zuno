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
    "closure-checklist.md",
    "current.md",
    "implementation-roadmap.md",
    *RUNTIME_PROGRAM_PHASE_FILES,
]


def test_agent_architecture_folder_is_slim_mirror() -> None:
    files = {
        path.name for path in (REPO_ROOT / ".agent" / "architecture").iterdir() if path.is_file()
    }
    assert files == {"README.md", "architecture.md", "architecture.html"}
    assert (REPO_ROOT / ".agent/architecture/architecture.md").read_bytes() == (
        REPO_ROOT / "docs/architecture/architecture.md"
    ).read_bytes()
    assert (REPO_ROOT / ".agent/architecture/architecture.html").read_text(
        encoding="utf-8"
    ) == (REPO_ROOT / "docs/architecture/architecture.html").read_text(encoding="utf-8")


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
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "Markdown 内容必须比架构 HTML 更充实",
        "python tools/agent/render_architecture.py --write",
        "## 工作模式",
        "### 挂机模式",
        "### 多线程模式",
        "Single GeneralAgent",
        "## Program Closure 自维护审查",
        "如果用户提醒“以后注意”，不能只留在对话里",
    ]:
        assert phrase in agents


def test_agent_references_keep_canonical_set() -> None:
    reference_files = sorted(
        path.name for path in (REPO_ROOT / ".agent/references").iterdir() if path.is_file()
    )
    expected_references = sorted(
        [
            "README.md",
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


def test_agent_architecture_docs_map_explains_dual_mirror_rule() -> None:
    content = (REPO_ROOT / ".agent/references/architecture-docs-map.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "docs/architecture/architecture.md",
        "docs/architecture/architecture.html",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "Markdown 是主文档，HTML 是展示页",
        "python tools/agent/render_architecture.py --write",
        "不要恢复 `current-architecture.md`",
        "不要恢复旧 near-term / future / decisions 工作集",
    ]:
        assert phrase in content


def test_agent_program_surface_records_active_runtime_program() -> None:
    program_files = sorted(
        path.name for path in (REPO_ROOT / ".agent/programs").iterdir() if path.is_file()
    )
    assert program_files == sorted(RUNTIME_PROGRAM_FILES)

    current_program = (REPO_ROOT / ".agent/programs/current.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / ".agent/programs/README.md").read_text(encoding="utf-8")
    roadmap = (REPO_ROOT / ".agent/programs/implementation-roadmap.md").read_text(encoding="utf-8")
    current_reference = (REPO_ROOT / ".agent/references/current-program.md").read_text(
        encoding="utf-8"
    )
    for phrase in [
        "state: active",
        f"active_program: {RUNTIME_PROGRAM_NAME}",
        "current_phase: PHASE10_security-observability-and-online-eval",
        "runtime-first / vertical-slice-first",
        "只写 contract、schema 或 README 不能关闭 runtime phase",
        "上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback",
        MASTER_PROGRAM_NAME,
        MASTER_PROGRAM_ARCHIVE,
    ]:
        assert phrase in current_program + readme + roadmap + current_reference
    for index, phase in enumerate(RUNTIME_PROGRAM_PHASE_FILES, start=1):
        phase_path = REPO_ROOT / ".agent/programs" / phase
        assert phase_path.exists()
        phase_text = phase_path.read_text(encoding="utf-8")
        expected_status = {
            1: "status: completed",
            2: "status: completed",
            3: "status: completed",
            4: "status: completed",
            5: "status: completed",
            6: "status: completed",
            7: "status: completed",
            8: "status: completed",
            9: "status: completed",
            10: "status: active",
        }.get(index, "status: pending")
        assert expected_status in phase_text
        for section in ["## 目标", "## 范围", "## 禁止范围", "## 验收闸门", "## 验证命令"]:
            assert section in phase_text
    for archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        assert (REPO_ROOT / MASTER_PROGRAM_ARCHIVE / archive_file).exists()
    for phase in MASTER_PROGRAM_PHASE_FILES:
        phase_path = REPO_ROOT / MASTER_PROGRAM_ARCHIVE / phase
        assert phase_path.exists()
        assert "status: completed" in phase_path.read_text(encoding="utf-8")


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
        "verify_workflow_rule_writeback_route",
        "verify_templates_are_skeletons",
        "verify_program_lifecycle_surfaces",
        "verify_workflow_change_log_entries",
        "docs-agent-system-history",
        "verification-report-template.md",
        "workflow-change-log.md",
        "docs/history/programs",
        "## 自维护审查",
        "verify_architecture_mirror",
    ]:
        assert phrase in content


def test_system_yaml_tracks_current_architecture_docs_sync() -> None:
    content = (REPO_ROOT / ".agent/system.yaml").read_text(encoding="utf-8")

    for phrase in [
        "Zuno Local Agent Skill System",
        "new_program_first_phase: \"PHASE01\"",
        "skill_routes:",
        "docs_sync:",
        "verify:",
        ".agent/references/workflow.md",
        ".agent/references/architecture-docs-map.md",
        "python tools/agent/render_architecture.py --check",
        "python .agent/scripts/verify_agent_system.py",
    ]:
        assert phrase in content

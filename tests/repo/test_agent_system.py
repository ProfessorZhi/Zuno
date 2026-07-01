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
    *ACTIVE_PROGRAM_PHASE_FILES,
]


def _current_phase_name(content: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("current_phase:"):
            return line.split(":", 1)[1].strip().strip("`")
    return None


def _assert_active_phase_state(current: str) -> None:
    current_phase = _current_phase_name(current)
    phase_stems = [Path(name).stem for name in ACTIVE_PROGRAM_PHASE_FILES]
    assert current_phase in phase_stems

    active_index = phase_stems.index(current_phase)
    for index, phase_name in enumerate(ACTIVE_PROGRAM_PHASE_FILES):
        phase_text = (REPO_ROOT / ".agent/programs" / phase_name).read_text(encoding="utf-8")
        expected_status = "completed" if index < active_index else "active" if index == active_index else "pending"
        assert f"status: {expected_status}" in phase_text


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
        "当前前台采用 runtime-first 口径",
        "成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准",
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
    assert program_files == sorted(ACTIVE_PROGRAM_FILES)

    current_program = (REPO_ROOT / ".agent/programs/current.md").read_text(encoding="utf-8")
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
    runtime_archive = REPO_ROOT / RUNTIME_PROGRAM_ARCHIVE
    archive_text = (
        (runtime_archive / "current.md").read_text(encoding="utf-8")
        + (runtime_archive / "README.md").read_text(encoding="utf-8")
        + (runtime_archive / "closure-summary.md").read_text(encoding="utf-8")
    )
    for phrase in [
        "state: active",
        f"active_program: {ACTIVE_PROGRAM_NAME}",
        "current_phase:",
        ACTIVE_PROGRAM_NAME,
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
        assert phrase in current_program + readme + roadmap + closure + current_reference + archive_text
    assert sorted(path.name for path in (REPO_ROOT / ".agent/programs").glob("PHASE*.md")) == sorted(ACTIVE_PROGRAM_PHASE_FILES)
    _assert_active_phase_state(current_program)
    current_phase = _current_phase_name(current_program)
    assert current_phase in readme
    assert current_phase in roadmap
    assert current_phase in current_reference
    for phase in ACTIVE_PROGRAM_PHASE_FILES:
        phase_path = REPO_ROOT / ".agent/programs" / phase
        assert phase_path.exists()
        phase_text = phase_path.read_text(encoding="utf-8")
        assert "status:" in phase_text
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
    for index, phase in enumerate(RUNTIME_PROGRAM_PHASE_FILES, start=1):
        phase_path = runtime_archive / phase
        assert phase_path.exists()
        phase_text = phase_path.read_text(encoding="utf-8")
        assert "status: completed" in phase_text
        for section in ["## 目标", "## 范围", "## 禁止范围", "## 验收闸门", "## 验证命令"]:
            assert section in phase_text
    for archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        assert (runtime_archive / archive_file).exists()
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
        "docs/architecture/production-readiness.md",
        "verify:",
        ".agent/references/workflow.md",
        ".agent/references/architecture-docs-map.md",
        "python tools/agent/render_architecture.py --check",
        "python tools/scripts/verify_docs_entrypoints.py",
        "python .agent/scripts/verify_agent_system.py",
    ]:
        assert phrase in content

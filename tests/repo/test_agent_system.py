from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ACTIVE_PROGRAM_NAME = "zuno-eight-deliverables-full-realization-v1"
ACTIVE_CURRENT_PHASE = "PHASE07_hooks-evidence-trace-artifact-system.md"
COMPLETED_PROGRAM_PHASE_FILES = [
    "PHASE01_program-boot-baseline.md",
    "PHASE02_workflow-self-maintenance-system.md",
    "PHASE03_architecture-docs-html-system.md",
    "PHASE04_query-router-mode-policy.md",
    "PHASE05_context-builder-memory-system.md",
    "PHASE06_capability-toolcard-mcp-system.md",
]
ACTIVE_PROGRAM_PHASE_FILES = [
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


def test_agent_system_required_paths_exist() -> None:
    required_paths = [
        "apps/web/AGENTS.md",
        "tools/evals/zuno/AGENTS.md",
        ".agent/references/project-map.md",
        ".agent/references/code-map.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
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
        ".agent/references/verification-map.md",
        ".agent/references/zuno-repo-hygiene.md",
        ".agent/templates/architecture-doc-template.md",
        ".agent/templates/mermaid-diagram-template.md",
        ".agent/templates/architecture-change-note-template.md",
        ".agent/templates/verification-report-template.md",
        ".agent/templates/workflow-change-note-template.md",
        ".agent/architecture/README.md",
        ".agent/architecture/near-term/00-architecture-index.md",
        ".agent/architecture/near-term/01-target-runtime-architecture.md",
        ".agent/architecture/near-term/02-context-memory-architecture.md",
        ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
        ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
        ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
        ".agent/scripts/verify_module_boundaries.py",
        ".agent/system.yaml",
        ".agent/programs/README.md",
        ".agent/programs/current.md",
        ".agent/programs/implementation-roadmap.md",
        ".agent/programs/closure-checklist.md",
        ".agent/architecture/future/programs/README.md",
        ".agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md",
        ".agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md",
        "docs/history/programs/zuno-workflow-doc-system-v1/README.md",
        "docs/history/programs/zuno-workflow-doc-system-v1/PHASE03_skill-template-program-system.md",
        "docs/history/programs/zuno-target-architecture-refresh-v1/README.md",
        "docs/history/programs/zuno-target-architecture-refresh-v1/PHASE03_graphrag-llm-entity-knowledge-config.md",
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
        "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE01_directory-closure-master-plan.md",
        "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE02_platform-foundation-directory-migration.md",
        "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE03_schema-tools-resources-directory-migration.md",
        "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE04_services-thinning-directory-migration.md",
        "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE05_core-agent-runtime-directory-migration.md",
        "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE06_final-six-layer-guard-and-closure.md",
        "docs/history/programs/zuno-repo-layout-cleanup-v1/thread-prompts/THREAD_A_root-docs-agent-hygiene-prompt.md",
        "docs/history/programs/zuno-repo-layout-cleanup-v1/thread-prompts/THREAD_B_backend-six-layer-audit-prompt.md",
        "docs/history/programs/zuno-repo-layout-cleanup-v1/thread-prompts/THREAD_C_tools-tests-generated-artifacts-prompt.md",
        "docs/history/programs/zuno-target-runtime-v2/README.md",
        "docs/history/programs/zuno-target-architecture-migration-v1/README.md",
        "docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
        "docs/history/programs/zuno-target-architecture-migration-v1/implementation-phases/README.md",
        "docs/history/programs/context-memory-agent-runtime-v1/README.md",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing Agent path: {relative_path}"


def test_retired_agent_skill_and_workflow_dirs_are_collapsed() -> None:
    assert not (REPO_ROOT / ".agent" / "skills").exists()
    assert not (REPO_ROOT / ".agent" / "workflows").exists()


def test_near_term_architecture_index_is_canonical_and_referenced() -> None:
    index_path = (
        REPO_ROOT
        / ".agent"
        / "architecture"
        / "near-term"
        / "00-architecture-index.md"
    )
    content = index_path.read_text(encoding="utf-8")
    for phrase in [
        "目标架构设计工作集索引",
        "Native BM25",
        "RRF",
        "Summary Compression",
        "Structured Extraction",
        "ToolCard",
        "docs/architecture.md",
        "docs/architecture.html",
        "00-architecture-index.md",
    ]:
        assert phrase in content

    assert not (
        REPO_ROOT
        / ".agent"
        / "architecture"
        / "near-term"
        / "zuno-ideal-architecture-and-repo-layout.html"
    ).exists()

    required_files = [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/architecture/README.md",
        ".agent/architecture/near-term/README.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
    ]
    for relative_path in required_files:
        file_content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "00-architecture-index.md" in file_content
        assert "zuno-ideal-architecture-and-repo-layout.html" not in file_content


def test_root_agents_routes_to_module_agents_and_references() -> None:
    content = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    required_phrases = [
        "## 任务路由",
        "apps/web/AGENTS.md",
        ".agent/references/code-map.md",
        "tools/evals/zuno/AGENTS.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/programs/",
        "前台文档默认中文",
        "## 工作模式",
        "### 挂机模式",
        "### 多线程模式",
        "提示词里写“目标模式”不等于 UI 目标模式",
        "粗粒度",
        "用户在 UI 里手动创建目标模式线程",
        "线程内开启多 agent 模式",
        "主线程先盘点可复用 Codex 线程和 git worktree",
        "主线程必须在生成、改写或投递线程提示词之前完成线程盘点",
        "不能先写一堆提示词再回头找线程",
        "不能在主对话里直接粘贴完整子线程提示词",
        "有合适可复用线程就复用；没有合适线程才创建新线程",
        "复用或新建线程后必须改线程标题",
        "子线程目标模式提示词默认要求线程内开启多 agent 模式",
        "Single GeneralAgent",
        "## Program Closure 自维护审查",
        "如果用户提醒“以后注意”，不能只留在对话里",
        "verifier / tests 是否覆盖新规则",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing root routing phrase: {phrase}"

    assert "src/backend/zuno/AGENTS.md" not in content


def test_agent_readme_documents_workflow_library_boundaries() -> None:
    content = (REPO_ROOT / ".agent" / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        ".agent/references/",
        ".agent/programs/",
        ".agent/architecture/",
        "Zuno Local Agent Skill System",
        "本地 Agent Skill System",
        "新写或重写的 Agent 文档默认使用中文",
        "挂机模式由主线程",
        "多线程模式由主线程",
        "提示词目标模式不等于 Codex UI 目标模式",
        "粗粒度",
        "用户在 UI 里手动创建真正的目标模式子线程",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing workflow-library phrase: {phrase}"


def test_agent_system_yaml_routes_to_skills_templates_docs_sync_and_verify() -> None:
    content = (REPO_ROOT / ".agent" / "system.yaml").read_text(encoding="utf-8")

    required_phrases = [
        "Zuno Local Agent Skill System",
        "system_identity:",
        "local_skills_root: \".agent/references\"",
        "template_root: \".agent/templates\"",
        "skill_file_contract:",
        "template_rules:",
        "skill_routes:",
        "docs_sync:",
        "verify:",
        "work_modes:",
        "hangup_mode:",
        "multi_thread_mode:",
        "main_thread_goal_mode: true",
        "persistent_thread_slots: true",
        "task_isolation_unit: \"worktree + codex branch, not thread title\"",
        "main_thread_can_self_execute: true",
        "main_thread_can_delegate: true",
        "child_threads_are_reusable_slots: true",
        "require_fresh_or_confirmed_worktree_branch_per_task: true",
        "prefer_reuse_existing_thread_slots: true",
        "create_new_threads_when_no_reusable_slot: true",
        "rename_thread_after_assignment: true",
        "child_prompt_must_default_multi_agent: true",
        "thread_prompt_root: \".agent/programs/thread-prompts\"",
        "thread_prompts_separate_from_phase_files: true",
        "thread_prompts_replace_on_next_plan: true",
        "cleanup_old_thread_prompts_by_default: true",
        "archive_thread_prompts_only_when_requested: true",
        "temporary_thread_execution_plans_default_cleanup: true",
        "coarse_grained_child_tasks: true",
        "child_threads_allow_multi_agent: true",
        "prompt_only_is_not_goal_mode: true",
        "提示词目标模式不等于 Codex UI 目标模式",
        "require_disjoint_write_scope: true",
        "runtime target remains Single GeneralAgent",
        ".agent/references/task-routing.md",
        ".agent/templates/phase-closure-report.md",
        "python .agent/scripts/verify_agent_system.py",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing system route phrase: {phrase}"


def test_agent_references_are_local_skills_not_plain_indexes() -> None:
    references_readme = (REPO_ROOT / ".agent" / "references" / "README.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "本地项目 skill library",
        "skills、lessons、playbooks",
        "一次性调查流水账",
        ".agent/templates/",
    ]:
        assert phrase in references_readme

    required_sections = [
        "When To Use",
        "Mental Model",
        "Current Truth",
        "Target Direction",
        "Must Preserve",
        "Before Editing",
        "Allowed Changes",
        "Forbidden Changes",
        "Common Failure Patterns",
        "Debug Playbooks",
        "Focused Tests",
        "Docs Sync",
        "Lessons Learned",
    ]
    skill_files = [
        "task-routing.md",
        "workflow.md",
        "docs-map.md",
        "verification-map.md",
        "known-pitfalls.md",
        "zuno-repo-hygiene.md",
    ]

    for file_name in skill_files:
        content = (REPO_ROOT / ".agent" / "references" / file_name).read_text(
            encoding="utf-8"
        )
        for section in required_sections:
            assert section in content, f"{file_name} missing skill section: {section}"


def test_workflow_documents_goal_work_modes_contract() -> None:
    content = (REPO_ROOT / ".agent" / "references" / "workflow.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "挂机模式由主线程作为真正的 Codex UI 目标模式",
        "线程可以常驻",
        "每轮任务必须重新确认或切换独立 worktree 和独立 `codex/` 分支",
        "粗粒度",
        "用户在 UI 里手动创建目标模式线程",
        "提示词目标模式不等于 Codex UI 目标模式",
        "主线程先盘点可复用 Codex 线程和 git worktree",
        "主线程必须在生成、改写或投递线程提示词之前完成线程盘点",
        "主线程不能在主对话里直接粘贴完整子线程提示词",
        "有合适可复用线程就复用；没有合适线程才创建新线程",
        "复用或新建线程后必须改线程标题",
        "子线程目标模式提示词默认要求线程内开启多 agent 模式",
        "不把执行工作流里的多 agent 写成 Zuno runtime 的当前架构",
        "### 挂机模式",
        "### 多线程模式",
        "### Program Closure 自维护审查",
        "如果用户提醒“以后注意”，不能只留在对话里",
        "能机器检查的规则是否已进入脚本或 repo tests",
    ]:
        assert phrase in content, f"missing parallel workflow phrase: {phrase}"


def test_program_closure_checklist_requires_self_review() -> None:
    content = (REPO_ROOT / ".agent" / "programs" / "closure-checklist.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "## Program Closure 自维护审查",
        "completed program 是否已归档到 `docs/history/programs/`",
        "如果用户提醒“以后注意”，不能只留在对话里",
        "verifier / tests 是否覆盖新规则",
        "docs/architecture/roadmap.md",
    ]:
        assert phrase in content, f"missing program closure self-review phrase: {phrase}"


def test_agent_templates_keep_execution_skeleton_boundary() -> None:
    content = (REPO_ROOT / ".agent" / "templates" / "README.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "只保存 skill 执行模板和报告骨架",
        "不保存项目知识",
        "Allowed Content",
        "Forbidden Content",
        "Lessons Learned",
        "architecture-doc-template.md",
        "verification-report-template.md",
        "workflow-change-note-template.md",
    ]:
        assert phrase in content, f"missing template boundary phrase: {phrase}"


def test_verification_report_template_exists_and_stays_a_skeleton() -> None:
    content = (
        REPO_ROOT / ".agent" / "templates" / "verification-report-template.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "## Scope",
        "## Commands",
        "## Results",
        "## Failure Analysis",
        "## Evidence",
        "## Remaining Risk",
    ]:
        assert phrase in content
    assert "Zuno current =" not in content
    assert "GraphRAGProjectSnapshot" not in content


def test_phase_closure_template_requires_program_self_review() -> None:
    content = (
        REPO_ROOT / ".agent" / "templates" / "phase-closure-report.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "## 自维护审查",
        "AGENTS.md",
        "`.agent/system.yaml`",
        "`.agent/references/`",
        "`.agent/templates/`",
        "`.agent/programs/`",
        "`docs/history/programs/`",
        "`docs/architecture/current-architecture.md`",
        "`docs/architecture/target-architecture.md`",
        "`docs/architecture/roadmap.md`",
        "verifier / tests",
    ]:
        assert phrase in content, f"missing phase closure self-review item: {phrase}"


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
    ]:
        assert phrase in content, f"missing verifier self-maintenance guard: {phrase}"


def test_docs_agent_system_history_route_references_all_front_templates() -> None:
    system_yaml = (REPO_ROOT / ".agent" / "system.yaml").read_text(encoding="utf-8")

    for file_name in [
        "requirement-intake.md",
        "readonly-audit-prompt.md",
        "phase-plan.md",
        "phase-closure-report.md",
        "goal-mode-prompt.md",
        "target-mode-prompt.md",
        "codex-batch-prompt.md",
        "spec-coding-checklist.md",
        "architecture-doc-template.md",
        "mermaid-diagram-template.md",
        "architecture-change-note-template.md",
        "verification-report-template.md",
        "workflow-change-note-template.md",
    ]:
        assert file_name in system_yaml, f"template not routed in system.yaml: {file_name}"


def test_current_program_declares_active_eight_deliverables_program() -> None:
    current = (REPO_ROOT / ".agent" / "programs" / "current.md").read_text(encoding="utf-8")
    programs_index = (REPO_ROOT / ".agent" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )
    history_index = (REPO_ROOT / "docs" / "history" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )

    active_phase_files = sorted(
        path.name for path in (REPO_ROOT / ".agent" / "programs").glob("PHASE*.md")
    )

    assert ACTIVE_PROGRAM_NAME in current
    assert "state: active" in current
    assert ACTIVE_CURRENT_PHASE in current
    assert active_phase_files == ACTIVE_PROGRAM_PHASE_FILES
    assert "八个交付物" in current
    assert "默认开启线程内多 agent" in current
    assert "不是多线程模式" in current
    assert "zuno-six-layer-internalization-v1" in current
    assert "Program 3 / `zuno-repo-layout-cleanup-v1` 已完成" in current
    assert "api / agent / memory / capability / knowledge / platform" in current
    assert "GeneralAgent 主循环" in current
    assert ACTIVE_PROGRAM_NAME in programs_index
    assert "zuno-target-architecture-migration-v1/README.md" not in programs_index
    assert "zuno-target-architecture-migration-v1/" in history_index
    assert "context-memory-agent-runtime-v1" not in programs_index
    assert "context-memory-agent-runtime-v1" in history_index
    assert "zuno-workflow-doc-system-v1/" in history_index
    assert "zuno-target-architecture-refresh-v1/" in history_index
    assert "zuno-repo-layout-cleanup-v1/" in history_index
    assert "zuno-six-layer-internalization-v1/" in history_index


def test_active_program_phase_status_lifecycle_is_machine_checkable() -> None:
    phase_statuses = {
        path.name: path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / ".agent" / "programs").glob("PHASE*.md")
    }
    current = (REPO_ROOT / ".agent" / "programs" / "current.md").read_text(
        encoding="utf-8"
    )

    assert f"current_phase: `{ACTIVE_CURRENT_PHASE}`" in current
    for phase_name in COMPLETED_PROGRAM_PHASE_FILES:
        assert "status: completed" in phase_statuses[phase_name]
    assert "status: active" in phase_statuses[ACTIVE_CURRENT_PHASE]
    for phase_name in ACTIVE_PROGRAM_PHASE_FILES[7:]:
        assert "status: planned" in phase_statuses[phase_name], phase_name


def test_phase05_context_memory_focused_stack_is_routed() -> None:
    system_yaml = (REPO_ROOT / ".agent" / "system.yaml").read_text(encoding="utf-8")
    verification_map = (REPO_ROOT / ".agent" / "references" / "verification-map.md").read_text(
        encoding="utf-8"
    )
    required_tests = [
        "tests/agent/test_context_contracts.py",
        "tests/agent/test_context_orchestrator.py",
        "tests/agent/test_memory_layers.py",
        "tests/agent/test_memory_layer_surfaces.py",
        "tests/agent/test_generalagent_context_memory_runtime.py",
        "tests/repo/test_backend_facade_layers.py",
        "tests/repo/test_static_target_layer_imports.py",
    ]

    for relative_path in required_tests:
        assert relative_path in system_yaml
        assert relative_path in verification_map
        assert (REPO_ROOT / relative_path).exists()


def test_phase06_capability_toolcard_focused_stack_is_routed() -> None:
    system_yaml = (REPO_ROOT / ".agent" / "system.yaml").read_text(encoding="utf-8")
    verification_map = (REPO_ROOT / ".agent" / "references" / "verification-map.md").read_text(
        encoding="utf-8"
    )
    required_tests = [
        "tests/agent/test_capability_system.py",
        "tests/agent/test_capability_registry.py",
        "tests/agent/test_capability_layer_surfaces.py",
        "tests/agent/test_generalagent_context_memory_runtime.py",
        "tests/repo/test_backend_facade_layers.py",
        "tests/repo/test_static_target_layer_imports.py",
    ]

    for relative_path in required_tests:
        assert relative_path in system_yaml
        assert relative_path in verification_map
        assert (REPO_ROOT / relative_path).exists()


def test_multi_agent_status_text_keeps_codex_execution_boundary() -> None:
    for relative_path in [
        ".agent/programs/current.md",
        ".agent/references/current-program.md",
        "docs/architecture/roadmap.md",
    ]:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "Codex 执行协作" in content, relative_path
        assert "不是 Zuno runtime 架构" in content, relative_path


def test_status_surfaces_do_not_keep_stale_no_active_or_program4_queue_claims() -> None:
    future_programs = (
        REPO_ROOT / ".agent" / "architecture" / "future" / "programs" / "README.md"
    ).read_text(encoding="utf-8")
    repo_hygiene = (REPO_ROOT / ".agent" / "references" / "zuno-repo-hygiene.md").read_text(
        encoding="utf-8"
    )

    assert ACTIVE_PROGRAM_NAME in future_programs
    assert "参考输入" in future_programs
    assert "当前没有 active program" not in future_programs
    assert "Program 4 runtime architecture upgrade 保持 queued / not active" not in repo_hygiene
    assert "zuno-six-layer-internalization-v1" in repo_hygiene
    assert "runtime architecture upgrade" in repo_hygiene


def test_near_term_architecture_uses_canonical_five_doc_set() -> None:
    files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent" / "architecture" / "near-term").iterdir()
        if path.is_file()
    )

    assert files == sorted(
        [
            "README.md",
            "00-architecture-index.md",
            "01-target-runtime-architecture.md",
            "02-context-memory-architecture.md",
            "03-capability-tool-retrieval-architecture.md",
            "04-knowledge-graphrag-retrieval-fusion.md",
            "05-repository-boundaries-and-acceptance-gates.md",
        ]
    )


def test_agent_references_are_governance_navigation_set() -> None:
    files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent" / "references").iterdir()
        if path.is_file()
    )

    assert files == sorted(
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


def test_gitignore_allows_module_agents() -> None:
    content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "apps/web/AGENTS.md" not in content
    assert ".agent/local/*" in content


def test_domain_pack_grep_helper_tracks_all_phase11c_legacy_patterns() -> None:
    content = (REPO_ROOT / ".agent/scripts/grep-domain-pack.ps1").read_text(encoding="utf-8")

    for pattern in [
        "Domain Pack",
        "domain_pack",
        "DomainQAGraph",
        "MultiAgentSupervisorGraph",
        "domain-packs",
    ]:
        assert pattern in content

    assert "rg" in content
    assert "docs/history/**" in content

    verification_map = (REPO_ROOT / ".agent/references/verification-map.md").read_text(
        encoding="utf-8"
    )

    assert ".agent/scripts/grep-domain-pack.ps1" in verification_map


def test_six_layer_internalization_is_archived_and_active_program_is_open() -> None:
    roadmap = (REPO_ROOT / ".agent" / "programs" / "implementation-roadmap.md").read_text(
        encoding="utf-8"
    )
    phase03 = (
        REPO_ROOT
        / "docs"
        / "history"
        / "programs"
        / "zuno-workflow-doc-system-v1"
        / "PHASE03_skill-template-program-system.md"
    ).read_text(encoding="utf-8")
    program2 = (
        REPO_ROOT
        / "docs"
        / "history"
        / "programs"
        / "zuno-target-architecture-refresh-v1"
        / "README.md"
    ).read_text(encoding="utf-8")
    program3 = (
        REPO_ROOT
        / "docs"
        / "history"
        / "programs"
        / "zuno-repo-layout-cleanup-v1"
        / "README.md"
    ).read_text(encoding="utf-8")
    program4 = (
        REPO_ROOT
        / "docs"
        / "history"
        / "programs"
        / "zuno-six-layer-internalization-v1"
        / "README.md"
    ).read_text(encoding="utf-8")
    active_phase_files = sorted(
        path.name for path in (REPO_ROOT / ".agent" / "programs").glob("PHASE*.md")
    )

    for phrase in [
        ACTIVE_PROGRAM_NAME,
        "state: active",
        "zuno-six-layer-internalization-v1",
        "每次新 program 都从 `PHASE01` 开始编号",
        "zuno-repo-layout-cleanup-v1",
        "zuno-runtime-architecture-upgrade-v1",
        "zuno-architecture-visuals-v1",
    ]:
        assert phrase in roadmap

    assert active_phase_files == ACTIVE_PROGRAM_PHASE_FILES
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
            REPO_ROOT
            / "docs"
            / "history"
            / "programs"
            / "zuno-six-layer-internalization-v1"
            / phase
        ).exists()
    assert "completed / archived" in program4
    assert "Capability tools 不按 CLI / API 拆成两棵顶层目录" in program4
    for prompt in [
        "PROGRAM3_DIRECTORY_CLOSURE_TARGET_MODE_PROMPT.md",
    ]:
        assert (
            REPO_ROOT
            / "docs"
            / "history"
            / "programs"
            / "zuno-repo-layout-cleanup-v1"
            / "thread-prompts"
            / prompt
        ).exists()
    assert "本地 skill system" in phase03
    assert "skill / lesson / playbook" in phase03
    assert "queued program" in phase03
    assert "LLM extraction" in program2
    assert "知识库支持多套 extractor / config 选择" in program2
    assert "repo hygiene verifier" in program3
    assert "capability/mcp/servers" in program3
    assert "platform/middleware" in program3
    for phase in [
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
            REPO_ROOT
            / "docs"
            / "history"
            / "programs"
            / "zuno-repo-layout-cleanup-v1"
            / phase
        ).exists()


def test_queued_program_files_are_marked_not_active() -> None:
    queued_files = sorted((REPO_ROOT / ".agent" / "architecture" / "future" / "programs").glob("*/*.md"))
    assert queued_files
    assert not (
        REPO_ROOT / ".agent" / "architecture" / "future" / "programs" / "zuno-target-architecture-refresh-v1"
    ).exists()
    assert not (
        REPO_ROOT / ".agent" / "architecture" / "future" / "programs" / "zuno-repo-layout-cleanup-v1"
    ).exists()
    for path in queued_files:
        content = path.read_text(encoding="utf-8")
        assert "queued draft / not active" in content, f"{path} missing queued banner"

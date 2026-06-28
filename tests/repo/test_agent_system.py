from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_agent_system_required_paths_exist() -> None:
    required_paths = [
        "apps/web/AGENTS.md",
        "src/backend/zuno/AGENTS.md",
        "tools/evals/zuno/AGENTS.md",
        ".agent/references/code-map.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/references/verification-map.md",
        ".agent/architecture/README.md",
        ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
        ".agent/architecture/near-term/01-target-runtime-architecture.md",
        ".agent/architecture/near-term/02-context-memory-architecture.md",
        ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
        ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
        ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
        ".agent/scripts/verify_module_boundaries.py",
        ".agent/system.yaml",
        ".agent/programs/README.md",
        ".agent/programs/implementation-roadmap.md",
        ".agent/programs/closure-checklist.md",
        ".agent/programs/PHASE01_repo-layout-audit.md",
        ".agent/programs/PHASE02_root-docs-hygiene.md",
        ".agent/programs/PHASE03_backend-six-layer-migration-plan.md",
        ".agent/programs/PHASE04_small-boundary-cleanups.md",
        ".agent/programs/PHASE05_hygiene-verifier-closure.md",
        ".agent/programs/thread-prompts/THREAD_A_root-docs-agent-hygiene-prompt.md",
        ".agent/programs/thread-prompts/THREAD_B_backend-six-layer-audit-prompt.md",
        ".agent/programs/thread-prompts/THREAD_C_tools-tests-generated-artifacts-prompt.md",
        ".agent/architecture/future/programs/README.md",
        ".agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md",
        ".agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md",
        "docs/history/programs/zuno-workflow-doc-system-v1/README.md",
        "docs/history/programs/zuno-workflow-doc-system-v1/PHASE03_skill-template-program-system.md",
        "docs/history/programs/zuno-target-architecture-refresh-v1/README.md",
        "docs/history/programs/zuno-target-architecture-refresh-v1/PHASE03_graphrag-llm-entity-knowledge-config.md",
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


def test_target_architecture_html_is_canonical_and_referenced() -> None:
    html_path = (
        REPO_ROOT
        / ".agent"
        / "architecture"
        / "near-term"
        / "zuno-ideal-architecture-and-repo-layout.html"
    )
    html = html_path.read_text(encoding="utf-8")
    assert "<html" in html.lower()
    assert "Zuno" in html
    for phrase in [
        "Target / Proposed",
        "Native BM25",
        "RRF",
        "Summary Compression",
        "Structured Extraction",
        "ToolCard",
        "Phase 05",
        "Phase 09",
        "Execution Contract",
        "Query Journey",
        "产品入口层",
        "RAG / GraphRAG 层",
    ]:
        assert phrase in html

    tracked_html = [
        path.replace("\\", "/")
        for path in subprocess.run(
            ["git", "ls-files", "*.html"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=True,
        ).stdout.splitlines()
        if "zuno-ideal-architecture" in path
    ]
    assert tracked_html == [
        ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html"
    ]

    required_files = [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/architecture/README.md",
        ".agent/architecture/near-term/README.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
    ]
    for relative_path in required_files:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert "zuno-ideal-architecture-and-repo-layout.html" in content


def test_root_agents_routes_to_module_agents_and_references() -> None:
    content = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    required_phrases = [
        "## 任务路由",
        "apps/web/AGENTS.md",
        "src/backend/zuno/AGENTS.md",
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
    ]:
        assert phrase in content, f"missing template boundary phrase: {phrase}"


def test_current_program_points_to_active_repo_layout_program_and_archives_old_candidate() -> None:
    current = (REPO_ROOT / ".agent" / "programs" / "current.md").read_text(encoding="utf-8")
    programs_index = (REPO_ROOT / ".agent" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )
    history_index = (REPO_ROOT / "docs" / "history" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "当前 active program" in current
    assert "zuno-workflow-doc-system-v1" in current
    assert "zuno-target-architecture-refresh-v1" in current
    assert "zuno-repo-layout-cleanup-v1" in current
    assert "PHASE01_repo-layout-audit.md" in current
    assert "zuno-target-architecture-migration-v1/README.md" not in programs_index
    assert "zuno-target-architecture-migration-v1/" in history_index
    assert "context-memory-agent-runtime-v1" not in programs_index
    assert "context-memory-agent-runtime-v1" in history_index
    assert "zuno-workflow-doc-system-v1/" in history_index
    assert "zuno-target-architecture-refresh-v1/" in history_index


def test_near_term_architecture_uses_canonical_five_doc_set() -> None:
    files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent" / "architecture" / "near-term").iterdir()
        if path.is_file()
    )

    assert files == sorted(
        [
            "README.md",
            "zuno-ideal-architecture-and-repo-layout.html",
            "01-target-runtime-architecture.md",
            "02-context-memory-architecture.md",
            "03-capability-tool-retrieval-architecture.md",
            "04-knowledge-graphrag-retrieval-fusion.md",
            "05-repository-boundaries-and-acceptance-gates.md",
        ]
    )


def test_agent_references_are_slim_navigation_set() -> None:
    files = sorted(
        path.name
        for path in (REPO_ROOT / ".agent" / "references").iterdir()
        if path.is_file()
    )

    assert files == sorted(
        [
            "README.md",
            "current-program.md",
            "docs-map.md",
            "code-map.md",
            "runtime-call-chain.md",
            "verification-map.md",
            "command-catalog.md",
            "known-pitfalls.md",
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


def test_program3_active_state_archives_completed_programs_and_keeps_next_queue() -> None:
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
    active_phase_files = sorted(
        path.name for path in (REPO_ROOT / ".agent" / "programs").glob("PHASE*.md")
    )

    for phrase in [
        "状态：active",
        "必要目录 + 清晰职责 + 可验证边界",
        "src/backend",
        "zuno-workflow-doc-system-v1",
        "每次新 program 都从 `PHASE01` 开始编号",
        "zuno-target-architecture-refresh-v1",
        "zuno-repo-layout-cleanup-v1",
    ]:
        assert phrase in roadmap

    assert active_phase_files == [
        "PHASE01_repo-layout-audit.md",
        "PHASE02_root-docs-hygiene.md",
        "PHASE03_backend-six-layer-migration-plan.md",
        "PHASE04_small-boundary-cleanups.md",
        "PHASE05_hygiene-verifier-closure.md",
    ]
    for prompt in [
        "THREAD_A_root-docs-agent-hygiene-prompt.md",
        "THREAD_B_backend-six-layer-audit-prompt.md",
        "THREAD_C_tools-tests-generated-artifacts-prompt.md",
    ]:
        assert (REPO_ROOT / ".agent" / "programs" / "thread-prompts" / prompt).exists()
    assert "本地 skill system" in phase03
    assert "skill / lesson / playbook" in phase03
    assert "queued program" in phase03
    assert "LLM extraction" in program2
    assert "知识库支持多套 extractor / config 选择" in program2


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

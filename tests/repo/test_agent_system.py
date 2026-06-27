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
        ".agent/programs/PHASE01_public-architecture-surface.md",
        ".agent/programs/PHASE02_local-agent-skill-system.md",
        ".agent/programs/PHASE03_tools-tests-guardrails.md",
        ".agent/programs/PHASE04_backend-facade-layers.md",
        ".agent/programs/PHASE05_large-file-light-split.md",
        ".agent/programs/PHASE06_architecture-diagrams-html.md",
        ".agent/programs/closure-checklist.md",
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
        "## 并行执行规则",
        "默认优先考虑多线程 / 多 agent 协作",
        "每个线程都必须是目标模式",
        "优先打开 Codex UI 的目标模式",
        "线程内开启多 agent 模式",
        "Single GeneralAgent",
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
        "默认优先考虑多线程 / 多 agent 协作",
        "每个线程都必须带目标、范围、禁止范围、验收闸门和验证命令",
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
        "parallel_execution:",
        "require_target_mode: true",
        "prefer_codex_ui_goal_mode: true",
        "allow_multi_agent_inside_thread: true",
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


def test_workflow_documents_parallel_target_mode_contract() -> None:
    content = (REPO_ROOT / ".agent" / "references" / "workflow.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "复杂任务默认优先考虑多线程 / 多 agent 协作",
        "每个线程使用独立 `codex/` 分支",
        "每个线程都必须是目标模式",
        "线程内可以按范围开启多 agent 模式",
        "不把执行工作流里的多 agent 写成 Zuno runtime 的当前架构",
        "### 多线程目标模式",
    ]:
        assert phrase in content, f"missing parallel workflow phrase: {phrase}"


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


def test_current_program_points_to_architecture_surface_and_archives_old_candidate() -> None:
    current = (REPO_ROOT / ".agent" / "programs" / "current.md").read_text(encoding="utf-8")
    programs_index = (REPO_ROOT / ".agent" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )
    history_index = (REPO_ROOT / "docs" / "history" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "当前 active program 就是 `.agent/programs/` 根目录这一层" in current
    assert "zuno-architecture-surface-cleanup-v1" in current
    assert "PHASE01" in current
    assert "zuno-target-architecture-migration-v1/README.md" not in programs_index
    assert "zuno-target-architecture-migration-v1/" in history_index
    assert "context-memory-agent-runtime-v1" not in programs_index
    assert "context-memory-agent-runtime-v1" in history_index


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


def test_active_program_starts_from_phase01_and_has_surface_cleanup_plan() -> None:
    roadmap = (REPO_ROOT / ".agent" / "programs" / "implementation-roadmap.md").read_text(
        encoding="utf-8"
    )
    phase01 = (
        REPO_ROOT / ".agent" / "programs" / "PHASE01_public-architecture-surface.md"
    ).read_text(encoding="utf-8")
    phase02 = (
        REPO_ROOT / ".agent" / "programs" / "PHASE02_local-agent-skill-system.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "zuno-architecture-surface-cleanup-v1",
        "PHASE01：公开封面与架构叙事收口",
        "PHASE02：本地 Agent Skill System 收口",
        "PHASE03：tools / tests 工作流防回归",
        "PHASE04：后端六层 facade 分层",
        "PHASE05：大文件轻拆",
        "PHASE06：架构图与 HTML 展示页",
        "每次新 program 都从 `PHASE01` 开始编号",
    ]:
        assert phrase in roadmap

    assert "README" in phase01
    assert "Zuno Local Agent Skill System" in phase02
    assert "Lessons Learned" in phase02

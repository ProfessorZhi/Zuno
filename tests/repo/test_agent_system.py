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
        ".agent/programs/zuno-target-runtime-v2/README.md",
        ".agent/programs/zuno-target-runtime-v2/implementation-roadmap.md",
        ".agent/programs/zuno-target-runtime-v2/current-phase.md",
        ".agent/programs/zuno-target-runtime-v2/closure-checklist.md",
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
        ".agent/programs/zuno-target-runtime-v2/",
        "前台文档默认中文",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing root routing phrase: {phrase}"


def test_agent_readme_documents_workflow_library_boundaries() -> None:
    content = (REPO_ROOT / ".agent" / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        ".agent/references/",
        ".agent/programs/",
        ".agent/architecture/",
        "类似 skill 的任务路由",
        "新写或重写的 Agent 文档默认使用中文",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing workflow-library phrase: {phrase}"


def test_current_program_points_to_active_v2_and_archives_old_candidate() -> None:
    current = (REPO_ROOT / ".agent" / "programs" / "current.md").read_text(encoding="utf-8")
    programs_index = (REPO_ROOT / ".agent" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )
    history_index = (REPO_ROOT / "docs" / "history" / "programs" / "README.md").read_text(
        encoding="utf-8"
    )

    assert "zuno-target-runtime-v2/" in current
    assert "受控的首个实现切片" in current
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


def test_active_v2_program_has_phase_execution_plan() -> None:
    roadmap = (
        REPO_ROOT / ".agent" / "programs" / "zuno-target-runtime-v2" / "implementation-roadmap.md"
    ).read_text(encoding="utf-8")
    current_phase = (
        REPO_ROOT / ".agent" / "programs" / "zuno-target-runtime-v2" / "current-phase.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "Phase 05：记忆引擎",
        "Phase 06：能力与工具检索",
        "Phase 07：知识检索与融合",
        "Phase 08：GeneralAgent LangGraph 运行时",
        "Phase 09：产品边界、Trace 与 Eval 收口",
    ]:
        assert phrase in roadmap

    assert "Phase 05：记忆引擎" in current_phase
    assert "不要在 Phase 05 没有聚焦测试" in current_phase

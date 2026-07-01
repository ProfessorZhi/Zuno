import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_readme_exposes_current_architecture_entrypoints() -> None:
    content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in [
        "./docs/architecture/architecture.md",
        "./docs/architecture/production-readiness.md",
        "./docs/architecture/architecture.html",
        "./docs/evidence/public-demo.md",
        "Single Controller Agent 是目标架构角色",
        "当前实现主线是 `GeneralAgent` single loop",
        "Completion API -> CompletionService -> GeneralAgent single loop",
        "企业私有知识库与多功能 Agent 助手",
        "普通 RAG 问答",
    ]:
        assert phrase in content


def test_docs_architecture_front_path_is_small_and_synced() -> None:
    docs_files = {
        path.name for path in (REPO_ROOT / "docs" / "architecture").iterdir() if path.is_file()
    }
    agent_files = {
        path.name for path in (REPO_ROOT / ".agent" / "architecture").iterdir() if path.is_file()
    }

    assert docs_files == {
        "README.md",
        "architecture.md",
        "production-readiness.md",
        "architecture.html",
        "repo-ownership-matrix.md",
    }
    assert agent_files == {"README.md", "architecture.md", "architecture.html"}
    assert (REPO_ROOT / "docs/architecture/architecture.md").read_bytes() == (
        REPO_ROOT / ".agent/architecture/architecture.md"
    ).read_bytes()
    assert (REPO_ROOT / "docs/architecture/architecture.html").read_text(encoding="utf-8") == (
        REPO_ROOT / ".agent/architecture/architecture.html"
    ).read_text(encoding="utf-8")


def test_docs_front_path_readmes_explain_architecture_contract() -> None:
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    architecture_index = (REPO_ROOT / "docs" / "architecture" / "README.md").read_text(
        encoding="utf-8"
    )
    agent_architecture_index = (
        REPO_ROOT / ".agent" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "Zuno 文档入口",
        "./architecture/architecture.md",
        "./architecture/production-readiness.md",
        "./architecture/architecture.html",
        "./evidence/public-demo.md",
        "./history/README.md",
        "前台文档默认使用中文",
    ]:
        assert phrase in docs_index

    for phrase in [
        "架构文档",
        "architecture.md",
        "production-readiness.md",
        "architecture.html",
        "repo-ownership-matrix.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/",
        "过时审计、旧规格、旧 phase、旧计划和旧 runbook",
    ]:
        assert phrase in architecture_index

    for phrase in [
        "Agent 架构工作区",
        "architecture.md",
        "architecture.html",
        "必须与正式人类文档 `docs/architecture/architecture.md` 完全一致",
        "python tools/agent/render_architecture.py --write",
    ]:
        assert phrase in agent_architecture_index


def test_architecture_markdown_is_text_first_and_contains_diagram_source() -> None:
    docs_architecture = (REPO_ROOT / "docs" / "architecture" / "architecture.md").read_text(
        encoding="utf-8"
    )
    production_readiness = (
        REPO_ROOT / "docs" / "architecture" / "production-readiness.md"
    ).read_text(encoding="utf-8")
    agent_architecture = (
        REPO_ROOT / ".agent" / "architecture" / "architecture.md"
    ).read_text(encoding="utf-8")

    assert docs_architecture == agent_architecture
    for phrase in [
        "总架构文档",
        "本地优先的企业私有知识库与多功能 Agent 助手",
        "文字总架构文档",
        "架构 HTML",
        "Current",
        "Target",
        "Document Ingestion / Parse Gateway",
        "Tool Control Plane",
        "LangSmith-compatible Trace / Eval",
        "文档一致性规则",
        "架构图视图集",
        "python tools/agent/render_architecture.py --write",
    ]:
        assert phrase in docs_architecture
    assert docs_architecture.count("```mermaid") == 10
    for phrase in [
        "第一版 runtime-first vertical slice",
        "唯一成熟度与 runtime-first 交付物口径事实源",
        "当前 runtime-first 八类交付物",
        "历史治理交付物只保留在 History",
        "Production Target",
        "zuno-target-architecture-runtime-full-implementation-v1",
        "zuno-eight-deliverables-full-realization-v1",
        "不要恢复已退休的拆分架构文档",
    ]:
        assert phrase in production_readiness


def test_front_path_summaries_do_not_duplicate_program_phase_or_target_catalogs() -> None:
    summary_paths = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "docs" / "README.md",
        REPO_ROOT / "docs" / "architecture" / "README.md",
        REPO_ROOT / ".agent" / "programs" / "current.md",
        REPO_ROOT / ".agent" / "references" / "current-program.md",
    ]

    forbidden_summary_details = [
        "PHASE03 已完成",
        "PHASE04 已完成",
        "PHASE05 已完成",
        "PHASE06 已完成",
        "PHASE07 已完成",
        "PHASE08 已完成",
        "PHASE09 已完成",
        "PHASE10 已完成",
        "PHASE11 已把",
        "PHASE12 已完成 release gate",
        "production-grade parser platform",
        "durable LangGraph-compatible runtime",
        "rootless / gVisor / Firecracker sandbox",
    ]

    for path in summary_paths:
        content = path.read_text(encoding="utf-8")
        assert "production-readiness.md" in content
        for phrase in forbidden_summary_details:
            assert phrase not in content, f"{path.relative_to(REPO_ROOT)} duplicates detail: {phrase}"


def test_architecture_surface_cleanup_archive_keeps_old_materials() -> None:
    for relative_path in [
        "docs/history/architecture-surface-cleanup-2026-06-30/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/current-architecture.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/target-architecture.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/roadmap.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/product-scenario-enterprise-kb.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/security-and-sandbox.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/deliverables.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/00-architecture-index.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/decisions/README.md",
    ]:
        assert (REPO_ROOT / relative_path).exists(), f"missing archive path: {relative_path}"


def test_active_entrypoints_do_not_restore_retired_front_path() -> None:
    files = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "README.md",
        REPO_ROOT / "docs" / "architecture" / "README.md",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".agent" / "README.md",
        REPO_ROOT / ".agent" / "architecture" / "README.md",
    ]
    forbidden = [
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/architecture/deliverables.md",
        "docs/architecture/overall-architecture.md",
        ".agent/architecture/overall-architecture.md",
        ".agent/architecture/near-term/",
        ".agent/architecture/future/",
        ".agent/architecture/decisions/",
        "docs/architecture/phases/",
        "docs/architecture/plans/",
        "docs/architecture/programs/",
        "docs/architecture/audits/",
        "docs/architecture/specs/",
        "docs/architecture/history/",
        "docs/development/",
        "docs/prototypes/",
        "docs/ui-review/",
    ]

    for path in files:
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in content, f"{path} contains retired front-path text: {phrase}"


def test_agent_entrypoint_records_dual_architecture_sync_rule() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    for phrase in [
        "这是仓库唯一的 Agent 入口",
        "Architecture Documentation Governance",
        "docs/architecture/architecture.md",
        "docs/architecture/architecture.html",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "Markdown 内容必须比架构 HTML 更充实",
        "python tools/agent/render_architecture.py --write",
    ]:
        assert phrase in agents


def test_verify_docs_entrypoints_script_tracks_current_surface() -> None:
    content = (REPO_ROOT / "tools" / "scripts" / "verify_docs_entrypoints.py").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "documentation entrypoint verification passed.",
        "verify_front_path_shape",
        "verify_front_path_summary_boundaries",
        "verify_no_retired_front_path_links",
        "docs/architecture/architecture.md",
        "docs/architecture/production-readiness.md",
        "docs/architecture/repo-ownership-matrix.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "architecture.html",
    ]:
        assert phrase in content


def test_architecture_html_is_generated_from_mermaid_source() -> None:
    for stale_path in [
        "docs/architecture.md",
        "docs/architecture.html",
        "docs/architecture/overview.html",
        ".agent/architecture/blueprint.html",
        "docs/architecture/overall-architecture.md",
        ".agent/architecture/overall-architecture.md",
    ]:
        assert not (REPO_ROOT / stale_path).exists()

    for relative_path in [
        "docs/architecture/architecture.html",
        ".agent/architecture/architecture.html",
    ]:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        for phrase in [
            "docs/architecture/architecture.md",
            ".agent/architecture/architecture.md",
            "tools/agent/render_architecture.py",
            "4+1 View Model",
            "Component-and-Connector View",
            "Deployment View",
            "Quality View",
            "Scenarios View",
            "Process View",
            "View &amp; Beyond",
            "V&amp;B Logical View",
            "V&amp;B Deployment View",
            "Agent Loop View",
            "展开全屏查看",
            "diagram-dialog",
        ]:
            assert phrase in content


def test_architecture_view_contract_is_shared_across_docs_and_renderer() -> None:
    expected = [
        (1, "Logical View", "4+1 Logical"),
        (2, "Development View", "4+1 Development"),
        (3, "Process View", "4+1 Process"),
        (4, "Physical View", "4+1 Physical"),
        (5, "Scenarios View", "4+1 Scenarios"),
        (6, "V&B Logical View", "View & Beyond Logical"),
        (7, "Component-and-Connector View", "View & Beyond C&C"),
        (8, "V&B Deployment View", "View & Beyond Deployment"),
        (9, "Quality View", "View & Beyond Quality"),
        (10, "Agent Loop View", "Zuno 专题图"),
    ]
    module_path = REPO_ROOT / "tools" / "agent" / "render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", module_path)
    assert spec is not None
    assert spec.loader is not None
    render_architecture = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = render_architecture
    spec.loader.exec_module(render_architecture)

    assert render_architecture.EXPECTED_DIAGRAMS == [title for _, title, _ in expected]

    architecture_source = (REPO_ROOT / "docs" / "architecture" / "architecture.md").read_text(
        encoding="utf-8"
    )
    architecture_html = (
        REPO_ROOT / "docs" / "architecture" / "architecture.html"
    ).read_text(encoding="utf-8")

    for index, title, _theory in expected:
        assert f"### {title}" in architecture_source
        html_title = title.replace("&", "&amp;")
        assert f"<h3>{index}. {html_title}</h3>" in architecture_html

    assert architecture_html.count('class="diagram-section"') == 10
    assert architecture_html.count('<div class="mermaid">') == 10
    assert architecture_html.count("<summary>Mermaid source</summary>") == 10


def test_architecture_html_matches_rendered_mermaid_source() -> None:
    module_path = REPO_ROOT / "tools" / "agent" / "render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", module_path)
    assert spec is not None
    assert spec.loader is not None
    render_architecture = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = render_architecture
    spec.loader.exec_module(render_architecture)

    expected = render_architecture.build_html()
    for relative_path in [
        "docs/architecture/architecture.html",
        ".agent/architecture/architecture.html",
    ]:
        assert (REPO_ROOT / relative_path).read_bytes() == expected.encode("utf-8")

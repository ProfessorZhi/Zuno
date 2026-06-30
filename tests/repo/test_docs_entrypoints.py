import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_readme_exposes_short_first_reader_path() -> None:
    content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in [
        "./docs/architecture/current-architecture.md",
        "./docs/architecture/target-architecture.md",
        "./docs/architecture/roadmap.md",
        "./docs/architecture.md",
        "./docs/architecture.html",
        "./docs/evidence/public-demo.md",
        "受限历史兼容",
        "Phase 11A",
        "Phase 11B",
        "Single Controller Agent 是目标架构角色",
        "当前实现主线是 `GeneralAgent` single loop",
        "Completion API -> CompletionService -> GeneralAgent single loop",
    ]:
        assert phrase in content


def test_docs_front_path_is_small_and_chinese() -> None:
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    architecture_index = (REPO_ROOT / "docs" / "architecture" / "README.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "Zuno 文档入口",
        "./architecture/current-architecture.md",
        "./architecture/target-architecture.md",
        "./architecture/roadmap.md",
        "./deliverables.md",
        "./evidence/public-demo.md",
        "./history/README.md",
        "前台文档默认使用中文",
    ]:
        assert phrase in docs_index

    for phrase in [
        "架构文档",
        "current-architecture.md",
        "target-architecture.md",
        "roadmap.md",
        "../architecture.md",
        "../architecture.html",
        "../evidence/public-demo.md",
        "docs/history/programs/official-graphrag-cleanup-v1/",
        "docs/history/programs/zuno-target-architecture-migration-v1/",
        "过时审计、旧规格、旧 phase、旧计划和旧 runbook",
    ]:
        assert phrase in architecture_index


def test_evidence_page_links_archived_public_demo_material() -> None:
    content = (REPO_ROOT / "docs" / "evidence" / "public-demo.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "../history/development/public-demo-evidence.md",
        "../history/development/public-demo-runbook.md",
        "../history/development/public-demo-acceptance.md",
    ]:
        assert phrase in content


def test_agent_entrypoint_and_agent_folder_form_one_workflow() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    agent_readme = (REPO_ROOT / ".agent" / "README.md").read_text(encoding="utf-8")
    routing = (REPO_ROOT / ".agent" / "references" / "task-routing.md").read_text(
        encoding="utf-8"
    )
    workflow = (REPO_ROOT / ".agent" / "references" / "workflow.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "这是仓库唯一的 Agent 入口",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/references/architecture-docs-map.md",
        ".agent/references/workflow-governance.md",
        ".agent/references",
        "Architecture Documentation Governance",
        "Agent Workflow Self-Maintenance",
        "前台文档默认中文",
    ]:
        assert phrase in agents

    assert "Zuno Local Agent Skill System" in agent_readme
    assert "本地 Agent Skill System" in agent_readme
    assert "任务路由层" in routing
    assert "具体执行步骤、停止条件、验证和收尾规则" in workflow


def test_verify_docs_entrypoints_script_tracks_current_surface() -> None:
    content = (REPO_ROOT / "tools" / "scripts" / "verify_docs_entrypoints.py").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "documentation entrypoint verification passed.",
        "verify_front_path_shape",
        "verify_active_docs_do_not_link_retired_paths",
        "docs/architecture/audits",
        "docs/development",
        "前台文档默认使用中文",
        "zuno-workflow-doc-system-v1",
        "zuno-target-architecture-refresh-v1",
        "zuno-repo-layout-cleanup-v1",
        "zuno-architecture-visuals-v1",
        "docs/architecture.md",
    ]:
        assert phrase in content


def test_active_entrypoints_do_not_restore_retired_front_path() -> None:
    files = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "README.md",
        REPO_ROOT / "docs" / "architecture" / "README.md",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / ".agent" / "README.md",
    ]
    forbidden = [
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


def test_front_path_directories_are_archived() -> None:
    for relative_path in [
        "docs/architecture/history",
        "docs/architecture/audits",
        "docs/architecture/specs",
        "docs/development",
        "docs/prototypes",
        "docs/ui-review",
        "docs/ui-gallery",
        "docs/reference/api.md",
        "docs/reference/core.md",
        "docs/reference/database.md",
        "docs/reference/service.md",
        "docs/reference/zuno.md",
    ]:
        assert not (REPO_ROOT / relative_path).exists(), f"retired front path still exists: {relative_path}"

    for relative_path in [
        "docs/history/audits",
        "docs/history/specs",
        "docs/history/development",
        "docs/history/prototypes",
        "docs/history/ui-review",
        "docs/history/reference/api.md",
    ]:
        assert (REPO_ROOT / relative_path).exists(), f"missing archive path: {relative_path}"


def test_current_target_and_roadmap_keep_current_target_boundary() -> None:
    current = (REPO_ROOT / "docs" / "architecture" / "current-architecture.md").read_text(
        encoding="utf-8"
    )
    target = (REPO_ROOT / "docs" / "architecture" / "target-architecture.md").read_text(
        encoding="utf-8"
    )
    roadmap = (REPO_ROOT / "docs" / "architecture" / "roadmap.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "当前架构",
        "以下仍是 Target，不是当前成熟事实",
        "Memory layer foundation contracts",
        "docs/history/domain-packs/root-contract-review/",
        "上面的调用链是当前 runtime 事实。目标架构图见",
    ]:
        assert phrase in current

    for phrase in [
        "目标架构",
        "Summary Compression",
        "Structured Extraction",
        "Native BM25",
        "ToolCard",
        "RRF",
        "`auto` 是 router",
        "GraphRAG 实体抽取默认主路径是 LLM 抽取",
        "六个主层",
        "新增或重写的前台文档使用中文",
    ]:
        assert phrase in target

    for phrase in [
        "Phase 11A：已完成",
        "Phase 11B：已完成",
        "Phase 11C：active runtime cleanup 已完成",
        "Phase 12：已通过 target migration closure evidence 关闭",
        "受限历史兼容",
        "zuno-workflow-doc-system-v1",
        "zuno-target-architecture-refresh-v1",
        "zuno-repo-layout-cleanup-v1",
        "zuno-architecture-visuals-v1",
        "PHASE03 completed",
        "视觉 QA",
    ]:
        assert phrase in roadmap


def test_doc_boundary_verifier_guards_future_only_terms() -> None:
    content = (
        REPO_ROOT / ".agent" / "scripts" / "verify_doc_boundaries.py"
    ).read_text(encoding="utf-8")

    for phrase in [
        "verify_future_only_terms",
        "Java",
        "microservice",
        "event-driven worker",
        "product-level multi-agent",
        "Coding Agent",
        "不属于 Current",
        "非近期目标",
        "当前不是什么",
    ]:
        assert phrase in content


def test_architecture_diagrams_expose_multi_view_target_architecture() -> None:
    content = (REPO_ROOT / "docs" / "architecture.md").read_text(encoding="utf-8")

    for phrase in [
        "Logical View",
        "Development View",
        "Process View",
        "Physical View",
        "Scenarios View",
        "V&B Logical View",
        "V&B Deployment View",
        "Quality View",
        "Agent Loop View",
        "Component-and-Connector View",
        "```mermaid",
        "Zuno 架构总览",
        "python tools/agent/render_architecture.py --write",
        "#f7f8fb",
        "#ffffff",
        "#b8c2cc",
        "#16202a",
        "#52616f",
        "4+1 View Model",
        "Component-and-Connector View",
        "Deployment View",
        "Quality View",
        "Agentic RAG",
        "GraphRAG",
        "Raw Event Log",
        "Memory Read Policy",
        "Memory Review Gate",
        "structured memory candidate",
        "write-manage-read",
        "Domain Pack 只允许作为历史或兼容语境出现",
    ]:
        assert phrase in content


def test_architecture_html_is_generated_from_mermaid_source() -> None:
    for stale_path in [
        "docs/architecture/architecture.html",
        "docs/architecture/overview.html",
        ".agent/architecture/blueprint.html",
    ]:
        assert not (REPO_ROOT / stale_path).exists()

    for relative_path in ["docs/architecture.html"]:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        for phrase in [
            "docs/architecture.md",
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
            "#f7f8fb",
            "#ffffff",
            "#b8c2cc",
            "#16202a",
            "#52616f",
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

    inventory = (REPO_ROOT / ".agent" / "references" / "diagram-inventory.md").read_text(
        encoding="utf-8"
    )
    deliverables = (REPO_ROOT / "docs" / "deliverables.md").read_text(encoding="utf-8")
    target = (
        REPO_ROOT / "docs" / "architecture" / "target-architecture.md"
    ).read_text(encoding="utf-8")
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    architecture_html = (REPO_ROOT / "docs" / "architecture.html").read_text(
        encoding="utf-8"
    )

    for index, title, theory in expected:
        assert f"| {index} | {title} | {theory} |" in inventory
        assert f"| {index} | {title} | {theory} |" in deliverables
        assert f"| {title} | {theory} |" in target
        assert f"{index}. `{title}`" in architecture_index
        html_title = title.replace("&", "&amp;")
        assert f"<h3>{index}. {html_title}</h3>" in architecture_html

    assert "absorbed reference programs / roadmap reference inputs" in deliverables
    assert architecture_html.count('class="diagram-section"') == 10
    assert architecture_html.count('<div class="mermaid">') == 10
    assert architecture_html.count("<summary>Mermaid source</summary>") == 10
    for phrase in [
        "overflow-x: auto",
        "min-width: 760px",
        "securityLevel: \"strict\"",
        "useMaxWidth: false",
    ]:
        assert phrase in architecture_html


def test_architecture_html_matches_rendered_mermaid_source() -> None:
    module_path = REPO_ROOT / "tools/agent/render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", module_path)
    assert spec is not None
    assert spec.loader is not None
    render_architecture = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = render_architecture
    spec.loader.exec_module(render_architecture)

    expected = render_architecture.build_html()
    for relative_path in ["docs/architecture.html"]:
        assert (REPO_ROOT / relative_path).read_bytes() == expected.encode("utf-8")


def test_repository_docs_do_not_keep_local_download_reference() -> None:
    for path in [*REPO_ROOT.glob("docs/**/*.md"), *REPO_ROOT.glob(".agent/**/*.md")]:
        content = path.read_text(encoding="utf-8")
        assert "C:\\Users\\Administrator\\Downloads" not in content


def test_architecture_decisions_do_not_keep_domain_pack_binding_as_active_mainline() -> None:
    active_decision = REPO_ROOT / "docs/architecture/decisions/0001-domain-pack-binding.md"
    history_decision = REPO_ROOT / "docs/history/decisions/0001-domain-pack-binding.md"
    decisions_index = (REPO_ROOT / "docs/architecture/decisions/README.md").read_text(
        encoding="utf-8"
    )

    assert not active_decision.exists()
    assert history_decision.exists()
    assert "0001-domain-pack-binding.md" not in decisions_index
    assert "ADR 0002" in decisions_index

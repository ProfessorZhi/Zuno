import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def _current_phase_name(content: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("current_phase:"):
            return line.split(":", 1)[1].strip().strip("`")
    return None


def _load_render_architecture():
    module_path = REPO_ROOT / "tools" / "agent" / "render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", module_path)
    assert spec is not None
    assert spec.loader is not None
    render_architecture = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = render_architecture
    spec.loader.exec_module(render_architecture)
    return render_architecture


def test_readme_exposes_lean_complete_positioning() -> None:
    content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    for phrase in [
        "Lean Complete Agentic GraphRAG Product",
        "./docs/architecture/architecture.md",
        "./docs/architecture/architecture.html",
        "./docs/architecture/production-readiness.md",
        "./docs/evidence/public-demo.md",
        "implementation available",
        "measurement blocked",
        "quality not yet proven",
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
            "document-ingestion-foundation.md",
            "agent-core-runtime.md",
            "memory-and-context.md",
            "capability-and-skill-layer.md",
        "agentic-retrieval-planner.md",
        "eval-observability-and-cost.md",
        "input-layer-and-document-processing.md",
        "knowledge-space-product-configuration.md",
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


def test_docs_front_path_readmes_explain_current_contract() -> None:
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
        "./architecture/architecture.html",
        "./architecture/production-readiness.md",
        "./history/README.md",
        "前台文档默认使用中文",
    ]:
        assert phrase in docs_index

    for phrase in [
        "架构文档",
        "architecture.md",
        "architecture.html",
        "production-readiness.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "python tools/agent/render_architecture.py --write",
    ]:
        assert phrase in architecture_index

    for phrase in [
        "Agent 架构工作区",
        "Lean Complete Agentic GraphRAG Product",
        "收缩的是近期目标规模，不是文档精度",
        "python tools/agent/render_architecture.py --write",
    ]:
        assert phrase in agent_architecture_index


def test_architecture_markdown_is_detailed_lean_blueprint() -> None:
    docs_architecture = (REPO_ROOT / "docs" / "architecture" / "architecture.md").read_text(
        encoding="utf-8"
    )
    production_readiness = (
        REPO_ROOT / "docs" / "architecture" / "production-readiness.md"
    ).read_text(encoding="utf-8")
    current_program = (REPO_ROOT / ".agent" / "programs" / "current.md").read_text(
        encoding="utf-8"
    )
    assert _current_phase_name(current_program) in {
        "none",
        "PHASE01_truth-source-baseline-and-program-activation",
        "PHASE03_four-diagram-html-and-guardrails",
        "PHASE04_docs-sync-verification-and-closure",
    }

    for phrase in [
        "Zuno Lean Complete Product Architecture",
        "Lean Complete Agentic GraphRAG Product",
        "十一逻辑能力层",
        "六物理运行域",
        "Agent Core / Planning & Control",
        "Capability 是能力目录、选择器和权限策略",
        "Four-layer governed Memory",
        "Corrective Agentic GraphRAG",
        "EvidenceLedger",
        "Product & API",
        "Input & Knowledge",
        "Agent Core",
        "Capability & Tool",
        "Governance & Observability",
        "Local Infrastructure",
        "代码 Ownership Matrix",
        "配置化与禁止写死契约",
        "数据与状态模型",
        "Runtime 完成与质量完成",
        "Agentic Recall@5 >= standard_rag",
        "unavailable_due_to_missing_trace_fields",
        "Future Optional Extensions",
    ]:
        assert phrase in docs_architecture
    assert docs_architecture.count("```mermaid") >= 10

    for phrase in [
        "Short-term Closure Gap",
        "Measurement Blocked",
        "Future Optional",
        "Agentic GraphRAG fixed benchmark 跑通并达到 baseline gate",
        "所有真实模型调用统一进入 Model Runtime / Gateway",
        "统一 Agent Core 真实闭环",
        "EvidenceLedger",
        "Agent run trace 持久化并可查看",
    ]:
        assert phrase in production_readiness


def test_topic_docs_follow_six_runtime_domains() -> None:
    expected = {
        "document-ingestion-foundation.md": ["Input & Knowledge", "SourceObject", "CitationLineage"],
        "agent-core-runtime.md": ["Agent Core", "Model Runtime / Gateway", "Single Controller", "统一 Agent Core 真实闭环"],
        "memory-and-context.md": ["Sensory Memory", "Short-term Memory", "Long-term Memory", "Entity Memory", "ContextPack read view"],
        "capability-and-skill-layer.md": ["Capability & Tool", "Function Calling", "SkillMetadata", "ToolRequest"],
        "agentic-retrieval-planner.md": ["Agentic Retrieval Planner", "Failure Buckets", "EvidenceLedger", "RetrievalQualityVerdict"],
        "eval-observability-and-cost.md": ["Governance & Observability", "agent_run", "Measurement Semantics", "Retrieval", "Generation"],
        "input-layer-and-document-processing.md": ["Product & API", "Input & Knowledge", "parser blocked"],
        "knowledge-space-product-configuration.md": ["Knowledge Space", "ModelSlotBinding", "RetrievalProfile"],
    }
    for file_name, phrases in expected.items():
        content = (REPO_ROOT / "docs" / "architecture" / file_name).read_text(encoding="utf-8")
        for phrase in phrases:
            assert phrase in content


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
        "verify_docs_map_has_unique_architecture_source_roles",
        "verify_no_retired_front_path_links",
        "ARCHITECTURE_VIEW_CONTRACT",
        "Logical View (4+1)",
        "Development View (4+1)",
        "Process View (4+1)",
        "Physical View (4+1)",
        "Scenarios View (4+1)",
        "Module View (Views & Beyond)",
        "Component-and-Connector View (Views & Beyond)",
        "Data View (Views & Beyond)",
        "Quality View (Views & Beyond)",
        "Agentic GraphRAG Evidence and Agent Loop (Zuno)",
    ]:
        assert phrase in content


def test_architecture_html_is_generated_from_ten_mermaid_sections() -> None:
    render_architecture = _load_render_architecture()
    expected = [
        "Logical View (4+1)",
        "Development View (4+1)",
        "Process View (4+1)",
        "Physical View (4+1)",
        "Scenarios View (4+1)",
        "Module View (Views & Beyond)",
        "Component-and-Connector View (Views & Beyond)",
        "Data View (Views & Beyond)",
        "Quality View (Views & Beyond)",
        "Agentic GraphRAG Evidence and Agent Loop (Zuno)",
    ]
    assert render_architecture.EXPECTED_DIAGRAMS == expected

    architecture_source = (REPO_ROOT / "docs" / "architecture" / "architecture.md").read_text(
        encoding="utf-8"
    )
    architecture_html = (
        REPO_ROOT / "docs" / "architecture" / "architecture.html"
    ).read_text(encoding="utf-8")

    for index, title in enumerate(expected, start=1):
        assert f"### {title}" in architecture_source
        html_title = title.replace("&", "&amp;")
        assert f"<h3>{index}. {html_title}</h3>" in architecture_html

    assert architecture_html.count('class="diagram-section') == 10
    assert architecture_html.count('class="diagram-card"') >= 10
    assert architecture_html.count("<summary>Mermaid source</summary>") >= 10
    assert architecture_html.count('class="offline-svg"') >= 10
    assert architecture_html.count('class="svg-edge-label"') >= 5
    assert "diagram-dialog" in architecture_html
    assert "https://cdn.jsdelivr.net" not in architecture_html
    assert "import mermaid" not in architecture_html
    assert "_status_class_for_label" not in (
        REPO_ROOT / "tools" / "agent" / "render_architecture.py"
    ).read_text(encoding="utf-8")


def test_architecture_html_matches_rendered_mermaid_source() -> None:
    render_architecture = _load_render_architecture()
    expected = render_architecture.build_html()
    for relative_path in [
        "docs/architecture/architecture.html",
        ".agent/architecture/architecture.html",
    ]:
        assert (REPO_ROOT / relative_path).read_bytes() == expected.encode("utf-8")


def test_offline_architecture_renderer_preserves_key_topology_and_labels() -> None:
    render_architecture = _load_render_architecture()
    source = (REPO_ROOT / "docs" / "architecture" / "architecture.md").read_text(
        encoding="utf-8"
    )
    diagrams = {diagram.title: diagram for diagram in render_architecture.extract_diagrams(source)}

    logical_mermaid = diagrams["Logical View (4+1)"].subdiagrams[0].mermaid
    _nodes, logical_edges = render_architecture._extract_mermaid_graph(logical_mermaid)
    logical_pairs = {(edge.source, edge.target) for edge in logical_edges}
    assert ("Product", "Agent") in logical_pairs
    assert ("Product", "Input") in logical_pairs
    assert ("Input", "Knowledge") in logical_pairs
    assert ("Agent", "Capability") in logical_pairs
    assert ("Capability", "Tool") in logical_pairs

    process_internal = next(
        subdiagram
        for subdiagram in diagrams["Process View (4+1)"].subdiagrams
        if subdiagram.title == "Planning and Control Internal View"
    )
    _nodes, process_edges = render_architecture._extract_mermaid_graph(process_internal.mermaid)
    process_pairs = {(edge.source, edge.target) for edge in process_edges}
    process_labels = {(edge.source, edge.target): edge.label for edge in process_edges}
    assert ("Reflection", "Replan") in process_pairs
    assert ("Replan", "Executor") in process_pairs
    assert ("Final", "Reflexion") in process_pairs
    assert ("Reflexion", "Memory") in process_pairs
    assert process_labels[("Reflection", "Revise")] == "REWRITE_ANSWER"
    assert process_labels[("Reflection", "Replan")] == "RETRIEVE_MORE / failure"

    rag_mermaid = diagrams["Agentic GraphRAG Evidence and Agent Loop (Zuno)"].subdiagrams[
        0
    ].mermaid
    _nodes, rag_edges = render_architecture._extract_mermaid_graph(rag_mermaid)
    rag_pairs = {(edge.source, edge.target) for edge in rag_edges}
    assert ("Query", "BM25") in rag_pairs
    assert ("Query", "Vector") in rag_pairs
    assert ("Query", "Graph") in rag_pairs
    assert ("Quality", "Correct") in rag_pairs
    assert ("Correct", "Query") in rag_pairs


def test_offline_architecture_renderer_rejects_silent_truncation() -> None:
    render_architecture = _load_render_architecture()
    mermaid = "flowchart LR\n" + "\n".join(
        f'  N{index}["Node {index}"]' for index in range(render_architecture.MAX_OFFLINE_NODES + 1)
    )
    with pytest.raises(ValueError, match="supports .* nodes"):
        render_architecture._extract_mermaid_graph(mermaid)

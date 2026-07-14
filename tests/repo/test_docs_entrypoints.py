import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_VIEWS = [
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

CANONICAL_ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
}


def _load_render_architecture():
    module_path = REPO_ROOT / "tools" / "agent" / "render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_readme_exposes_lean_complete_positioning() -> None:
    content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    for phrase in [
        "Lean Complete Agentic GraphRAG Product",
        "./docs/architecture/architecture.md",
        "./docs/architecture/architecture.html",
        "./docs/modules/README.md",
        "./docs/status/production-readiness.md",
        "./docs/modules/06-agent-core-planning-control.md",
        "implementation available",
        "measurement blocked",
        "quality not yet proven",
    ]:
        assert phrase in content


def test_architecture_directories_only_contain_canonical_files() -> None:
    docs_root = REPO_ROOT / "docs" / "architecture"
    agent_root = REPO_ROOT / ".agent" / "architecture"

    docs_files = {path.name for path in docs_root.iterdir() if path.is_file()}
    agent_files = {path.name for path in agent_root.iterdir() if path.is_file()}

    assert docs_files == CANONICAL_ARCHITECTURE_FILES
    assert agent_files == CANONICAL_ARCHITECTURE_FILES
    assert not [path for path in docs_root.iterdir() if path.is_dir()]
    assert not [path for path in agent_root.iterdir() if path.is_dir()]


def test_architecture_and_agent_mirrors_match() -> None:
    for file_name in ["architecture.md", "architecture-views.md", "architecture.html"]:
        assert (REPO_ROOT / "docs/architecture" / file_name).read_text(encoding="utf-8") == (
            REPO_ROOT / ".agent/architecture" / file_name
        ).read_text(encoding="utf-8")

    for file_name in [
        "05-memory-context.md",
        "06-agent-core-planning-control.md",
    ]:
        assert (REPO_ROOT / "docs/modules" / file_name).read_bytes() == (
            REPO_ROOT / ".agent/modules" / file_name
        ).read_bytes()


def test_docs_front_path_readmes_explain_current_contract() -> None:
    docs_index = (REPO_ROOT / "docs/README.md").read_text(encoding="utf-8")
    architecture_index = (REPO_ROOT / "docs/architecture/README.md").read_text(
        encoding="utf-8"
    )
    modules_index = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    agent_architecture_index = (REPO_ROOT / ".agent/architecture/README.md").read_text(
        encoding="utf-8"
    )

    for phrase in [
        "Zuno 文档入口",
        "./architecture/architecture.md",
        "./architecture/architecture.html",
        "./modules/README.md",
        "./status/production-readiness.md",
        "./decisions/README.md",
        "./governance/repo-ownership-matrix.md",
    ]:
        assert phrase in docs_index

    for phrase in [
        "架构文档",
        "architecture.md",
        "architecture-views.md",
        "architecture.html",
        "docs/modules/",
        "docs/status/",
        "python tools/agent/render_architecture.py --write",
    ]:
        assert phrase in architecture_index

    for phrase in [
        "Zuno 逻辑模块设计文档",
        "02-input-document-ingestion.md",
        "03-knowledge-agentic-graphrag.md",
        "05-memory-context.md",
        "06-agent-core-planning-control.md",
        "07-capability-skill.md",
        "10-observability-eval.md",
        "verify_memory_context_target_protocols.py",
    ]:
        assert phrase in modules_index

    for phrase in [
        "架构文档",
        "docs/modules/06-agent-core-planning-control.md",
        "docs/status/production-readiness.md",
    ]:
        assert phrase in agent_architecture_index


def test_architecture_markdown_is_text_first_target_design() -> None:
    render_architecture = _load_render_architecture()
    design = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")

    assert render_architecture.validate_design(design) == []
    assert 2 <= design.count("```mermaid") <= 8

    for phrase in [
        "Zuno Target Architecture Atlas",
        "项目定位与架构目标",
        "十一逻辑模块",
        "六个物理运行域",
        "Single Controller Agent Runtime",
        "AgentRunGraph",
        "Plan DAG",
        "StepExecutionGraph",
        "TaskContract",
        "FinalCandidate",
        "Publication",
        "EvidenceLedger",
        "implementation available",
        "measurement blocked",
        "quality not yet proven",
    ]:
        assert phrase in design


def test_architecture_views_contains_ten_categories_and_thirty_diagrams() -> None:
    render_architecture = _load_render_architecture()
    views = (REPO_ROOT / "docs/architecture/architecture-views.md").read_text(
        encoding="utf-8"
    )

    assert render_architecture.EXPECTED_VIEWS == EXPECTED_VIEWS
    assert render_architecture.EXPECTED_DIAGRAMS == EXPECTED_VIEWS
    assert render_architecture.validate_source(views) == []
    assert views.count("```mermaid") >= 30

    for title in EXPECTED_VIEWS:
        section = render_architecture._section(views, title)
        assert section
        assert "#### Overall" in section
        assert section.count("#### Local") >= 2
        assert "```mermaid" in section


def test_architecture_html_uses_true_mermaid_rendering() -> None:
    render_architecture = _load_render_architecture()
    html = (REPO_ROOT / "docs/architecture/architecture.html").read_text(encoding="utf-8")

    assert render_architecture.validate_html(html) == []
    for title in EXPECTED_VIEWS:
        assert title in html

    for phrase in [
        "Zuno Target Architecture Atlas",
        '<script type="module">',
        'fetch("/docs/architecture/architecture-views.md"',
        "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs",
        'className = "mermaid"',
        "diagram-dialog",
        "Mermaid source",
        'diagram.subtitle.startsWith("Overall")',
        "${kind} Diagram",
        "阅读文字总架构",
    ]:
        assert phrase in html

    assert "offline-svg" not in html
    assert "offline-diagram" not in html


def test_architecture_renderer_sync_contract() -> None:
    render_architecture = _load_render_architecture()
    assert render_architecture.check_outputs() == []
    expected_html = (REPO_ROOT / "docs/architecture/architecture.html").read_text(
        encoding="utf-8"
    )
    assert render_architecture.build_html() == expected_html


def test_module_docs_follow_logical_module_boundaries() -> None:
    expected = {
        "02-input-document-ingestion.md": [
            "Input / Document Ingestion",
            "SourceObject",
            "CanonicalDocumentIR",
            "IndexableDocumentSnapshot",
        ],
        "03-knowledge-agentic-graphrag.md": [
            "Knowledge / Agentic GraphRAG",
            "EvidenceLedger",
            "RetrievalQualityVerdict",
            "KnowledgeSnapshot",
        ],
        "05-memory-context.md": [
            "Working Memory",
            "Session Memory",
            "Long-term Memory",
            "Episodic Memory",
            "Semantic Memory",
            "Procedural Memory",
            "C0 Deterministic Lossless",
            "C3 Reasoning Consolidation",
            "ContextPack read view",
        ],
        "06-agent-core-planning-control.md": [
            "Agent Core / Planning & Control",
            "Single Controller Agent Runtime",
            "Plan DAG",
            "TaskContract",
            "pending_interrupt_refs",
            "prepare_publication",
            "PostgreSQL",
        ],
        "07-capability-skill.md": [
            "Capability / Skill",
            "Function Calling",
            "SkillMetadata",
            "ToolRequest",
        ],
        "10-observability-eval.md": [
            "Observability & Eval",
            "agent_run",
            "Measurement Semantics",
        ],
    }

    for file_name, phrases in expected.items():
        content = (REPO_ROOT / "docs/modules" / file_name).read_text(encoding="utf-8")
        for phrase in phrases:
            assert phrase in content


def test_status_decision_and_governance_entries_exist() -> None:
    expected = {
        "docs/status/production-readiness.md": [
            "Short-term Closure Gap",
            "Measurement Blocked",
            "Future Optional",
        ],
        "docs/decisions/README.md": ["架构决策记录"],
        "docs/decisions/0002-retire-compat-namespace.md": ["Accepted"],
        "docs/governance/repo-ownership-matrix.md": ["Repository Ownership Matrix"],
    }

    for relative_path, phrases in expected.items():
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
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
    ]:
        assert (REPO_ROOT / relative_path).exists(), f"missing archive path: {relative_path}"


def test_active_updated_entrypoints_do_not_reference_migrated_architecture_docs() -> None:
    files = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs/README.md",
        REPO_ROOT / "docs/architecture/README.md",
        REPO_ROOT / "docs/modules/README.md",
        REPO_ROOT / ".agent/README.md",
        REPO_ROOT / ".agent/architecture/README.md",
        REPO_ROOT / ".agent/modules/README.md",
        REPO_ROOT / ".agent/references/docs-map.md",
        REPO_ROOT / ".agent/references/architecture-docs-map.md",
    ]

    forbidden = [
        "docs/architecture/production-readiness.md",
        "docs/architecture/document-ingestion-foundation.md",
        "docs/architecture/agent-core-runtime.md",
        "docs/architecture/memory-and-context.md",
        "docs/architecture/capability-and-skill-layer.md",
        "docs/architecture/agentic-retrieval-planner.md",
        "docs/architecture/eval-observability-and-cost.md",
        "docs/architecture/input-layer-and-document-processing.md",
        "docs/architecture/knowledge-space-product-configuration.md",
        "docs/architecture/repo-ownership-matrix.md",
        "docs/architecture/decisions/",
        ".agent/architecture/agent-core-runtime.md",
    ]

    for path in files:
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in content, f"{path} contains migrated path: {phrase}"

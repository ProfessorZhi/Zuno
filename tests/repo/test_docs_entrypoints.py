from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VIEWS = ['Logical View (4+1)', 'Development View (4+1)', 'Process View (4+1)', 'Physical View (4+1)', 'Scenarios View (4+1)', 'Module View (Views & Beyond)', 'Component-and-Connector View (Views & Beyond)', 'Data View (Views & Beyond)', 'Quality View (Views & Beyond)', 'Agentic GraphRAG Evidence and Agent Loop (Zuno)']
MODULE_DOCS = ['01-product-surface.md', '02-input-document-ingestion.md', '03-knowledge-agentic-graphrag.md', '04-model-gateway.md', '05-memory-context.md', '06-agent-core-planning-control.md', '07-capability-skill.md', '08-tool-runtime.md', '09-security.md', '10-observability-eval.md', '11-infrastructure.md']
CANONICAL_ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}


def _load_render_architecture():
    path = REPO_ROOT / "tools/agent/render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_architecture_directories_only_contain_support_files() -> None:
    for root in [REPO_ROOT / "docs/architecture", REPO_ROOT / ".agent/architecture"]:
        assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_ARCHITECTURE_FILES
        assert not [p for p in root.iterdir() if p.is_dir()]


def test_formal_architecture_set_is_eleven_plus_two() -> None:
    assert sorted(p.name for p in (REPO_ROOT / "docs/modules").glob("[0-9][0-9]-*.md")) == MODULE_DOCS
    assert (REPO_ROOT / "docs/architecture/architecture.md").exists()
    assert (REPO_ROOT / "docs/architecture/architecture.html").exists()


def test_all_module_and_architecture_mirrors_match() -> None:
    for file_name in MODULE_DOCS:
        assert (REPO_ROOT / "docs/modules" / file_name).read_bytes() == (REPO_ROOT / ".agent/modules" / file_name).read_bytes()
    for file_name in ["architecture.md", "architecture-views.md", "architecture.html"]:
        assert (REPO_ROOT / "docs/architecture" / file_name).read_bytes() == (REPO_ROOT / ".agent/architecture" / file_name).read_bytes()


def test_architecture_markdown_is_integration_first() -> None:
    renderer = _load_render_architecture()
    design = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    assert renderer.validate_design(design) == []
    assert 3 <= design.count("```mermaid") <= 8
    for file_name in MODULE_DOCS:
        assert f"docs/modules/{file_name}" in design


def test_visual_source_keeps_ten_views_and_thirty_diagrams() -> None:
    renderer = _load_render_architecture()
    views = (REPO_ROOT / "docs/architecture/architecture-views.md").read_text(encoding="utf-8")
    assert renderer.EXPECTED_VIEWS == EXPECTED_VIEWS
    assert renderer.validate_source(views) == []
    assert views.count("```mermaid") == 30


def test_architecture_html_routes_to_text_modules_and_status() -> None:
    renderer = _load_render_architecture()
    html = (REPO_ROOT / "docs/architecture/architecture.html").read_text(encoding="utf-8")
    assert renderer.validate_html(html) == []
    for phrase in ["./architecture.md", "../modules/README.md", "../status/production-readiness.md", "./architecture-views.md"]:
        assert phrase in html


def test_renderer_and_mirrors_are_synchronized() -> None:
    assert _load_render_architecture().check_outputs() == []


def test_active_architecture_surfaces_do_not_reference_retired_split_docs() -> None:
    retired = [
        "04-model-gateway-contract-freeze.md",
        "04-model-gateway-operations-conformance.md",
        "10-observability-eval-rag-agent-evaluation.md",
        "11-infrastructure-data-services.md",
        "11-infrastructure-consistency-lifecycle.md",
    ]
    active = [
        REPO_ROOT / "docs/modules/README.md",
        REPO_ROOT / ".agent/modules/README.md",
        REPO_ROOT / "docs/architecture/README.md",
        REPO_ROOT / "docs/architecture/architecture.md",
        REPO_ROOT / "docs/architecture/architecture-views.md",
        REPO_ROOT / "docs/architecture/architecture.html",
    ]
    for path in active:
        content = path.read_text(encoding="utf-8")
        for phrase in retired:
            assert phrase not in content, f"{path} references retired {phrase}"

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VIEWS = [
    "Product Context View", "Business Flow View", "Logical Capability View", "Provider Boundary View",
    "Domain State View", "Staleness and Review View", "Agent Runtime View", "Runtime and Domain State View",
    "Microservice View", "Deployment Profiles View", "Data Ownership View", "Failure and Recovery View",
    "A/B/C Eval View", "Security Verification View",
]
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
    for root in [REPO_ROOT / "docs/project/architecture"]:
        assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_ARCHITECTURE_FILES
        assert not [p for p in root.iterdir() if p.is_dir()]


def test_legacy_modules_are_explicitly_superseded() -> None:
    assert sorted(p.name for p in (REPO_ROOT / "docs/project/modules").glob("[0-9][0-9]-*.md")) == MODULE_DOCS
    assert all("status: superseded-legacy-reference" in p.read_text(encoding="utf-8") for p in (REPO_ROOT / "docs/project/modules").glob("[0-9][0-9]-*.md"))
    assert (REPO_ROOT / "docs/project/architecture/architecture.md").exists()
    assert (REPO_ROOT / "docs/project/architecture/architecture.html").exists()


def test_agent_architecture_and_module_mirrors_are_absent() -> None:
    assert not (REPO_ROOT / ".agent/architecture").exists()
    assert not (REPO_ROOT / ".agent/modules").exists()


def test_architecture_markdown_is_integration_first() -> None:
    renderer = _load_render_architecture()
    design = (REPO_ROOT / "docs/project/architecture/architecture.md").read_text(encoding="utf-8")
    assert renderer.validate_design(design) == []
    assert design.count("```mermaid") == 0
    for marker in ["product-architecture.md", "legal-domain-model.md", "service-architecture.md", "microservice-deployment.md"]:
        assert marker in design


def test_visual_source_matches_new_architecture_taxonomy() -> None:
    renderer = _load_render_architecture()
    views = (REPO_ROOT / "docs/project/architecture/architecture-views.md").read_text(encoding="utf-8")
    assert renderer.EXPECTED_VIEWS == EXPECTED_VIEWS
    assert renderer.validate_source(views) == []
    assert views.count("```mermaid") == len(EXPECTED_VIEWS)


def test_architecture_html_routes_to_text_taxonomy_and_status() -> None:
    renderer = _load_render_architecture()
    html = (REPO_ROOT / "docs/project/architecture/architecture.html").read_text(encoding="utf-8")
    assert renderer.validate_html(html) == []
    for phrase in ["./architecture.md", "../product/product-architecture.md", "../services/service-architecture.md", "../../status/production-readiness.md", "./architecture-views.md"]:
        assert phrase in html


def test_renderer_checks_formal_architecture_surface() -> None:
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
        REPO_ROOT / "docs/project/modules/README.md",
        REPO_ROOT / "docs/project/architecture/README.md",
        REPO_ROOT / "docs/project/architecture/architecture.md",
        REPO_ROOT / "docs/project/architecture/architecture-views.md",
        REPO_ROOT / "docs/project/architecture/architecture.html",
    ]
    for path in active:
        content = path.read_text(encoding="utf-8")
        for phrase in retired:
            assert phrase not in content, f"{path} references retired {phrase}"

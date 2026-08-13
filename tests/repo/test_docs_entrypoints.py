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
    for root in [REPO_ROOT / "docs/architecture"]:
        assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_ARCHITECTURE_FILES
        assert not [p for p in root.iterdir() if p.is_dir()]


def test_legacy_documents_are_archived_and_not_active() -> None:
    assert (REPO_ROOT / "docs/facts/project-context.md").exists()
    assert (REPO_ROOT / "docs/facts/current-state.md").exists()
    assert (REPO_ROOT / "docs/modules/README.md").exists()
    assert (REPO_ROOT / "docs/history/superseded-document-taxonomy/README.md").exists()
    assert (REPO_ROOT / "docs/architecture/architecture.md").exists()
    assert (REPO_ROOT / "docs/architecture/architecture.html").exists()


def test_agent_architecture_and_module_mirrors_are_absent() -> None:
    assert not (REPO_ROOT / ".agent/architecture").exists()
    assert not (REPO_ROOT / ".agent/modules").exists()


def test_architecture_markdown_is_integration_first() -> None:
    renderer = _load_render_architecture()
    design = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    assert renderer.validate_design(design) == []
    assert design.count("```mermaid") == 0
    for marker in ["docs/history/", "docs/facts/", "Part A — Architecture Narrative", "Part B — Detailed Architecture Specification"]:
        assert marker in design


def test_visual_source_matches_new_architecture_taxonomy() -> None:
    renderer = _load_render_architecture()
    views = (REPO_ROOT / "docs/architecture/architecture-views.md").read_text(encoding="utf-8")
    assert renderer.EXPECTED_VIEWS == EXPECTED_VIEWS
    assert renderer.validate_source(views) == []
    assert views.count("```mermaid") == len(EXPECTED_VIEWS)


def test_architecture_html_routes_to_text_taxonomy_and_status() -> None:
    renderer = _load_render_architecture()
    html = (REPO_ROOT / "docs/architecture/architecture.html").read_text(encoding="utf-8")
    assert renderer.validate_html(html) == []
    for phrase in ["./architecture.md", "../history/README.md", "./architecture.md#target-status-boundary", "../evidence/README.md", "../facts/current-state.md", "./architecture-views.md"]:
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
        REPO_ROOT / "docs/architecture/README.md",
        REPO_ROOT / "docs/architecture/architecture.md",
        REPO_ROOT / "docs/architecture/architecture-views.md",
        REPO_ROOT / "docs/architecture/architecture.html",
    ]
    for path in active:
        content = path.read_text(encoding="utf-8")
        for phrase in retired:
            assert phrase not in content, f"{path} references retired {phrase}"

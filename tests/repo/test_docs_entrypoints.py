from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VIEWS = [
    "Product Context View", "Business Flow View", "Logical Capability View", "Provider Boundary View",
    "Domain State View", "Staleness and Review View", "Agent Runtime View", "Runtime and Domain State View",
    "Physical Deployment Decision View", "Deployment Profiles View", "Data Ownership View", "Failure and Recovery View",
    "A/B/C Eval View", "Security Verification View",
]
CANONICAL_ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}
CANONICAL_MODULE_FILES = {
    "README.md",
    "01-application-integration.md",
    "02-legal-domain-work-product.md",
    "03-knowledge-evidence.md",
    "04-agent-runtime-control.md",
    "05-capability-skill.md",
    "06-tool-runtime-effects.md",
    "07-model-gateway.md",
    "08-security-governance.md",
    "09-observability-evaluation.md",
}
MODULE_BASELINE_HEADINGS = [
    "### B1 Scope / Global Invariants",
    "### B2 Responsibility / Ownership",
    "### B3 Upstream / Downstream",
    "### B4 Authoritative Facts / Core Objects",
    "### B5 Cross-boundary Contracts",
    "### B6 Normal Flow",
    "### B7 State / Lifecycle",
    "### B8 Failure Taxonomy",
    "### B9 Retry / Replan / Reconcile / Recovery / Idempotency",
    "### B10 Security / Approval / Audit",
    "### B11 Persistence / Transaction Boundaries",
    "### B12 Observability / Evaluation",
    "### B13 Current / Target / Gap / Evidence",
    "### B14 Code / Database / Migration Constraints",
]


def _load_render_architecture():
    path = REPO_ROOT / "tools/agent/render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_project_documentation_is_canonical() -> None:
    assert (REPO_ROOT / "docs/project/project-background.md").exists()
    assert (REPO_ROOT / "docs/project/development-process.md").exists()
    assert not (REPO_ROOT / "docs/facts").exists()
    assert (REPO_ROOT / "docs/history/red-blue/README.md").exists()
    assert (REPO_ROOT / "docs/history/red-blue/manual-round-01-overall-architecture.md").exists()


def test_architecture_directories_only_contain_support_files() -> None:
    root = REPO_ROOT / "docs/architecture"
    assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_ARCHITECTURE_FILES
    assert not [p for p in root.iterdir() if p.is_dir()]


def test_module_design_baseline_is_canonical_human_first_and_complete() -> None:
    root = REPO_ROOT / "docs/modules"
    assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_MODULE_FILES
    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "module_design_baseline: AVAILABLE_V1" in readme
    assert "implementation_authorization: NO" in readme
    assert "简单问答" in readme and "复杂法律分析" in readme and "现实副作用" in readme

    for name in sorted(CANONICAL_MODULE_FILES - {"README.md"}):
        content = (root / name).read_text(encoding="utf-8")
        assert content.startswith("# ")
        assert "status: design-baseline-v1" in content
        assert "implementation: not-authorized" in content
        assert "## Part A — Human Narrative" in content
        assert "## Part B — Engineering / Agent Reference" in content
        for heading in MODULE_BASELINE_HEADINGS:
            assert heading in content, f"{name} missing {heading}"
        assert "Current" in content and "Target" in content and "Gap" in content


def test_architecture_markdown_is_integration_first() -> None:
    renderer = _load_render_architecture()
    design = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    assert renderer.validate_design(design) == []
    assert design.count("```mermaid") <= 6
    for marker in ["docs/history/", "docs/project/", "Part A — Architecture Narrative", "Part B — Detailed Architecture Specification"]:
        assert marker in design


def test_visual_source_matches_canonical_architecture_views() -> None:
    renderer = _load_render_architecture()
    views = (REPO_ROOT / "docs/architecture/architecture-views.md").read_text(encoding="utf-8")
    assert renderer.EXPECTED_VIEWS == EXPECTED_VIEWS
    assert renderer.validate_source(views) == []
    assert views.count("```mermaid") == len(EXPECTED_VIEWS)


def test_architecture_html_routes_to_current_project_and_history() -> None:
    renderer = _load_render_architecture()
    html = (REPO_ROOT / "docs/architecture/architecture.html").read_text(encoding="utf-8")
    assert renderer.validate_html(html) == []
    for phrase in ["./architecture.md", "../project/project-background.md", "../history/README.md", "./architecture.md#target-status-boundary", "../evidence/README.md", "./architecture-views.md"]:
        assert phrase in html


def test_renderer_checks_formal_architecture_surface() -> None:
    assert _load_render_architecture().check_outputs() == []


def test_active_architecture_surfaces_do_not_reference_retired_split_docs() -> None:
    retired = [
        "04-model-gateway-contract-freeze.md", "04-model-gateway-operations-conformance.md",
        "10-observability-eval-rag-agent-evaluation.md", "11-infrastructure-data-services.md",
        "11-infrastructure-consistency-lifecycle.md",
    ]
    active = [REPO_ROOT / "docs/architecture" / name for name in CANONICAL_ARCHITECTURE_FILES]
    for path in active:
        content = path.read_text(encoding="utf-8")
        for phrase in retired:
            assert phrase not in content, f"{path} references retired {phrase}"

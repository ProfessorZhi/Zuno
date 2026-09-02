from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VIEWS = [
    "Case Timeline View",
    "Fact Authority View",
    "Boundary Transition View",
    "Responsibility View",
    "Recovery View",
    "Deployment and Evolution View",
]
CANONICAL_ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}
CANONICAL_PROJECT_FILES = {"README.md", "project.md"}
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
CANONICAL_RED_BLUE_FILES = {
    "README.md", "current.md", "protocol.md", "attack-model.md", "judge.md",
    "templates/round.md", "templates/turn.md",
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
MODULE_CONSISTENCY_HEADINGS = [
    "## Part C — Cross-Module Consistency（跨模块一致性）",
    "### C1 Completion Proof / Non-proof（完成证明与非证明）",
    "### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）",
    "### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）",
    "### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）",
]
DETAIL_CANDIDATE_HEADINGS = [
    f"#### B14.{number} Detail Freeze Candidate" for number in range(1, 9)
]


def _load_render_architecture():
    path = REPO_ROOT / "tools/agent/render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _has_candidate_status(content: str) -> bool:
    return "detail_design: candidate-v1" in content or "detail-design: candidate-v1" in content


def test_project_documentation_is_consolidated_and_canonical() -> None:
    root = REPO_ROOT / "docs/project"
    assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_PROJECT_FILES
    assert not (REPO_ROOT / "docs/facts").exists()
    assert (REPO_ROOT / "docs/maintenance/history/red-blue/README.md").exists()
    assert (REPO_ROOT / "docs/maintenance/history/red-blue/manual-round-01-overall-architecture.md").exists()

    readme = (root / "README.md").read_text(encoding="utf-8")
    assert "project.md" in readme
    assert "project-fact-provenance.md" in readme

    project = (root / "project.md").read_text(encoding="utf-8")
    for marker in (
        "为什么会有这个项目",
        "为什么不直接用 Dify、Coze",
        "项目是怎样发展到今天的",
        "团队是什么形态，我在里面做了什么",
        "相比通用方案，我们今天到底证明了什么",
    ):
        assert marker in project
    assert "通用宿主" in project and "Zuno Legal Backend" in project
    assert "Current" in project and "Target" in project and "Unknown" in project


def test_red_blue_harness_is_dedicated_and_closed_book() -> None:
    root = REPO_ROOT / ".agent/red-blue"
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    assert actual == CANONICAL_RED_BLUE_FILES

    current = (root / "current.md").read_text(encoding="utf-8")
    assert "state: `no-active`" in current
    assert "active_round: `none`" in current

    protocol = (root / "protocol.md").read_text(encoding="utf-8")
    for marker in ("Context Firewall", "ChatGPT Duel", "Autonomous Agent", "Closed-book"):
        assert marker in protocol

    attack = (root / "attack-model.md").read_text(encoding="utf-8")
    for marker in ("Ownership Claim", "Build / Buy", "面经校准", "一次只"):
        assert marker in attack

    judge = (root / "judge.md").read_text(encoding="utf-8")
    for marker in ("UNSUPPORTED_CLAIM", "NARRATIVE_GAP", "ARCHITECTURE_GAP", "OWNERSHIP_GAP"):
        assert marker in judge

    workflow = (REPO_ROOT / "docs/maintenance/red-blue/README.md").read_text(encoding="utf-8")
    for marker in (
        "ProfessorZhi/internship-work", "ProfessorZhi/interview-notes", "Part A",
        "Closed-book", "ChatGPT Red / Blue 对攻", "Autonomous Agent",
    ):
        assert marker in workflow


def test_architecture_directories_only_contain_support_files() -> None:
    root = REPO_ROOT / "docs/architecture"
    assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_ARCHITECTURE_FILES
    assert not [p for p in root.iterdir() if p.is_dir()]


def test_module_design_is_human_first_complete_and_detail_candidate_9_of_9() -> None:
    root = REPO_ROOT / "docs/modules"
    assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_MODULE_FILES
    readme = (root / "README.md").read_text(encoding="utf-8")
    for marker in (
        "module_design_baseline: AVAILABLE_V1",
        "module_deep_design: AVAILABLE_V2",
        "module_deep_design_coverage: 9/9",
        "cross_module_consistency: AVAILABLE_V1",
        "module_detail_design_candidate: AVAILABLE_V1",
        "module_detail_design_candidate_coverage: 9/9",
        "module_detail_freeze: NOT_YET",
        "implementation_authorization: NO",
        "Module Detail Freeze Review",
    ):
        assert marker in readme
    assert "简单法律问答" in readme and "复杂法律分析" in readme and "现实副作用" in readme

    for name in sorted(CANONICAL_MODULE_FILES - {"README.md"}):
        content = (root / name).read_text(encoding="utf-8")
        assert content.startswith("# ")
        assert "status: design-baseline-v1" in content
        assert "implementation: not-authorized" in content
        assert "deepening: cross-module-consistency-v2" in content
        assert _has_candidate_status(content)
        assert "## Part A — Human Narrative" in content
        assert "## Part B — Engineering / Agent Reference" in content
        for heading in MODULE_BASELINE_HEADINGS + DETAIL_CANDIDATE_HEADINGS + MODULE_CONSISTENCY_HEADINGS:
            assert heading in content, f"{name} missing {heading}"
        assert "Current" in content and "Target" in content and "Gap" in content
        assert "Failure Injection / Freeze Evidence" in content


def test_architecture_markdown_is_conceptual_target_design() -> None:
    renderer = _load_render_architecture()
    design = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    assert renderer.validate_design(design) == []
    assert design.count("```mermaid") <= 2
    for marker in [
        "# Zuno 目标架构",
        "## 2. 一件案件里的五种事实",
        "## 3. 四次跨边界决定系统是否可信",
        "## 4. 九个责任域如何从这些边界产生",
        "## 5. 故障以后，先找事实再恢复控制",
        "## 6. 研究成果怎样变成工程能力",
        "docs/modules/",
        "docs/decisions/",
        "docs/evidence/",
        "docs/research/",
    ]:
        assert marker in design
    assert "## Part B" not in design


def test_visual_source_matches_canonical_architecture_views() -> None:
    renderer = _load_render_architecture()
    views = (REPO_ROOT / "docs/architecture/architecture-views.md").read_text(encoding="utf-8")
    assert renderer.EXPECTED_VIEWS == EXPECTED_VIEWS
    assert renderer.validate_source(views) == []
    assert views.count("```mermaid") == len(EXPECTED_VIEWS)


def test_architecture_html_routes_to_current_architecture_sources() -> None:
    renderer = _load_render_architecture()
    html = (REPO_ROOT / "docs/architecture/architecture.html").read_text(encoding="utf-8")
    assert renderer.validate_html(html) == []
    for phrase in [
        "./architecture.md", "../project/project.md", "../maintenance/history/README.md",
        "../evidence/README.md", "./architecture-views.md",
    ]:
        assert phrase in html
    assert "./architecture.md#target-status-boundary" not in html


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

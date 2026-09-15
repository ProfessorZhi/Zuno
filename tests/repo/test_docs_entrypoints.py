from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VIEWS = [
    "System Context View",
    "Case Timeline View",
    "State / Persistence / Consistency View",
    "Recovery View",
    "Deployment / Scale / Backpressure View",
    "Deployment Evolution View",
]
CANONICAL_ARCHITECTURE_FILES = {
    "README.md", "architecture.md", "architecture-views.md", "architecture.html", "reference.md"
}
CANONICAL_PROJECT_FILES = {"README.md", "reference.md"}
MODULE_DIRS = (
    "application",
    "domain",
    "knowledge",
    "runtime",
    "capability",
    "effects",
    "model-gateway",
    "security",
    "evaluation",
)
CANONICAL_MODULE_FILES = {
    "README.md",
    "reference.md",
    *{
        f"{directory}/{filename}"
        for directory in MODULE_DIRS
        for filename in ("README.md", "reference.md")
    },
}
CANONICAL_RED_BLUE_FILES = {
    "README.md", "current.md", "protocol.md", "attack-model.md", "defense-model.md", "judge.md",
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
    assert not (root / "project.md").exists()
    assert not (REPO_ROOT / "docs/facts").exists()
    assert not (REPO_ROOT / "docs/maintenance").exists()
    assert (REPO_ROOT / "docs/red-blue/archive/legacy/README.md").exists()
    assert (REPO_ROOT / "docs/red-blue/archive/legacy/manual-round-01-overall-architecture.md").exists()

    project = (root / "README.md").read_text(encoding="utf-8")
    for marker in ("project-fact-provenance.md", "Pilot Validation", "Production", "Current", "Target", "Unknown"):
        assert marker in project

    reference = (root / "reference.md").read_text(encoding="utf-8")
    assert "human_source: docs/project/README.md" in reference
    assert "project-fact-provenance.md" in reference


def test_red_blue_harness_is_resume_first_two_wave_batch_and_archivable() -> None:
    root = REPO_ROOT / ".agent/red-blue"
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    assert actual == CANONICAL_RED_BLUE_FILES

    current = (root / "current.md").read_text(encoding="utf-8")
    assert "state: `no-active`" in current
    assert "active_round: `none`" in current
    for marker in (
        "execution_mode: `BATCH_DUEL`",
        "red_wave_1_question_target: `100`",
        "blue_wave_1_answer_target: `100`",
        "red_wave_2_question_target: `100`",
        "blue_wave_2_answer_target: `100`",
        "batch_checkpoint_policy: `LINK_ONLY_PAUSE`",
        "red_wave_1_status:",
        "blue_wave_1_status:",
        "red_wave_2_status:",
        "blue_wave_2_status:",
        "improvement_ledger_status:",
        "round_report_status:",
        "next_resume_candidate_status:",
    ):
        assert marker in current

    protocol = (root / "protocol.md").read_text(encoding="utf-8")
    for marker in (
        "Context Firewall", "CHATGPT_AUTO", "AGENT_AUTO", "Resume Builder",
        "BUILD_SIMULATED_RESUME", "RED_WAVE_1", "BLUE_WAVE_1", "RED_WAVE_2", "BLUE_WAVE_2",
        "BATCH_CHECKPOINT_RED_1", "BATCH_CHECKPOINT_BLUE_1", "BATCH_CHECKPOINT_RED_2", "BATCH_CHECKPOINT_BLUE_2",
        "RED_EVALUATION", "BLUE_ARCHITECTURE_REFLECTION", "WORKFLOW_RETROSPECTIVE",
        "IMPROVEMENT_SYNTHESIS", "ROUND_REPORT", "USER_IMPROVEMENT_REVIEW", "BUILD_NEXT_RESUME_CANDIDATE",
        "03_blue_architecture_notes.md", "04_red_wave2_review_and_questions.md",
        "04_blue_wave2_answers.md", "04_blue_wave2_architecture_notes.md", "09_round_report.md",
        "Exactly 100 Targeted Follow-ups", "NEXT_ROUND_ONLY", "LIVE_INTERVIEW",
    ):
        assert marker.lower() in protocol.lower()

    attack = (root / "attack-model.md").read_text(encoding="utf-8")
    for marker in (
        "精品思维", "全链路追踪", "Ownership", "Build / Buy",
        "每一波固定 100 问", "一问一个主要意图", "Red Wave 2：评价 + 追杀",
        "Answer-driven handles", "Multi-Agent 不是正确答案",
        "Red Final Evaluation", "Red 自我质量检查", "Skill 也必须接受审判",
    ):
        assert marker in attack

    defense = (root / "defense-model.md").read_text(encoding="utf-8")
    for marker in (
        "Candidate Mode", "Architecture Reviewer Mode", "HISTORICAL_OWNERSHIP",
        "CURRENT_SYSTEM", "TARGET_DESIGN", "OPEN_DESIGN", "FUNDAMENTAL",
        "Ownership", "Evidence", "Unknown 与边界", "Failure / Recovery",
        "Build / Buy / Delete", "Multi-Agent 的回答框架", "Final Architecture Reflection",
    ):
        assert marker in defense

    judge = (root / "judge.md").read_text(encoding="utf-8")
    for marker in (
        "Red Wave 2 Blind Review", "Red Final Evaluation", "Blue Architecture Reflection",
        "Workflow Retrospective", "Red Thinking Framework", "Blue Thinking Framework",
        "Harness", "Improvement Classification", "Round Report",
        "RED_SKILL_GAP", "BLUE_SKILL_GAP", "HARNESS_GAP", "ARCHITECTURE_GAP",
        "FUNDAMENTAL_GAP", "NEXT_ROUND_ONLY",
    ):
        assert marker in judge

    workflow = (REPO_ROOT / "docs/red-blue/README.md").read_text(encoding="utf-8")
    for marker in (
        "Resume-first", "Red Interview Skill", "Blue Wave 1", "Red Wave 2", "Blue Wave 2",
        "Red Evaluation", "Blue Architecture Reflection", "Workflow Retrospective",
        "Improvement Ledger", "Round Report", "10_next_resume_candidate.md",
    ):
        assert marker in workflow

    workspace = (REPO_ROOT / "docs/red-blue/workspace/README.md").read_text(encoding="utf-8")
    for marker in (
        "Active Workspace", "BATCH_DUEL", "Red Wave 1", "Blue Wave 1", "Red Wave 2", "Blue Wave 2",
        "03_blue_architecture_notes.md", "04_red_wave2_review_and_questions.md",
        "04_blue_wave2_answers.md", "04_blue_wave2_architecture_notes.md",
        "09_improvement_ledger.md", "09_round_report.md", "10_next_resume_candidate.md",
        "NEXT_ROUND_ONLY",
    ):
        assert marker in workspace

    rounds = (REPO_ROOT / "docs/red-blue/rounds/README.md").read_text(encoding="utf-8")
    assert "INVALID / calibration Round" in rounds
    assert "counts_as_formal_round: false" in rounds


def test_architecture_directories_only_contain_support_files() -> None:
    root = REPO_ROOT / "docs/architecture"
    assert {p.name for p in root.iterdir() if p.is_file()} == CANONICAL_ARCHITECTURE_FILES
    assert not [p for p in root.iterdir() if p.is_dir()]
    assert (root / "architecture.md").exists()
    reference = (root / "reference.md").read_text(encoding="utf-8")
    assert "human_source: docs/architecture/architecture.md" in reference
    assert "module_router: docs/modules/reference.md" in reference


def test_module_design_is_human_first_complete_and_detail_candidate_9_of_9() -> None:
    root = REPO_ROOT / "docs/modules"
    assert {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()} == CANONICAL_MODULE_FILES
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

    router = (root / "reference.md").read_text(encoding="utf-8")
    assert "application/README.md" in router
    assert "application/reference.md" in router
    assert "evaluation/README.md" in router
    assert "evaluation/reference.md" in router

    for directory in MODULE_DIRS:
        human = (root / directory / "README.md").read_text(encoding="utf-8")
        reference = (root / directory / "reference.md").read_text(encoding="utf-8")

        assert human.startswith("# ")
        assert "status: design-baseline-v1" in human
        assert "implementation: not-authorized" in human
        assert "deepening: cross-module-consistency-v2" in human
        assert _has_candidate_status(human)
        assert "## Part A — Human Narrative" in human
        assert "## Part B — Engineering / Agent Reference" not in human
        assert "## Part C — Cross-Module Consistency" not in human
        assert "reference.md" in human

        assert reference.startswith("# ")
        assert "## Part B — Engineering / Agent Reference" in reference
        for heading in MODULE_BASELINE_HEADINGS + DETAIL_CANDIDATE_HEADINGS + MODULE_CONSISTENCY_HEADINGS:
            assert heading in reference, f"{directory}/reference.md missing {heading}"
        assert "Current" in reference and "Target" in reference and "Gap" in reference
        assert "Failure Injection / Freeze Evidence" in reference


def test_architecture_markdown_has_coordinated_human_and_agent_views() -> None:
    renderer = _load_render_architecture()
    human = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    reference = (REPO_ROOT / "docs/architecture/reference.md").read_text(encoding="utf-8")
    combined = human + "\n" + reference
    assert renderer.validate_design(human, reference) == []
    assert human.count("```mermaid") <= 2

    for marker in [
        "# Zuno 目标架构",
        "## Part A — Human Narrative（人类技术叙事）",
        "reference.md",
    ]:
        assert marker in human
    assert "## Part B — Engineering / Agent Reference（工程 / Agent 参考）" not in human

    for marker in [
        "## Part B — Engineering / Agent Reference（工程 / Agent 参考）",
        "### B2. Authority / Ownership Matrix",
        "### B3. Cross-boundary Contract Map",
        "### B6. Completion Proof / Non-proof",
        "### B7. Failure Taxonomy / Recovery Order",
        "### B14. Machine Navigation / Source Precedence",
    ]:
        assert marker in reference

    for route in ("docs/modules/", "docs/decisions/", "docs/evidence/", "docs/research/"):
        assert route in combined


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
        "./architecture.md", "../project/README.md", "../evidence/README.md", "./architecture-views.md",
    ]:
        assert phrase in html
    assert "../maintenance/" not in html
    assert "./README.md#target-status-boundary" not in html


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

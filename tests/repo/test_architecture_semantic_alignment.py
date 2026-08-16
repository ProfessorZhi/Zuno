from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load():
    path = REPO_ROOT / "tools/scripts/verify_architecture_semantic_alignment.py"
    spec = importlib.util.spec_from_file_location("verify_architecture_semantic_alignment", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_architecture_semantics_follow_canonical_module_designs() -> None:
    assert _load().verify() == []


def test_active_architecture_has_no_pre_baseline_status_claims() -> None:
    architecture = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    assert "module_design_baseline: AVAILABLE_V1" in architecture
    assert "module_detail_freeze: NOT_YET" in architecture
    assert "implementation_authorization: NO" in architecture
    for stale in (
        "仍等待 Main Architecture Freeze Review",
        "不等于模块正文已经建立",
        "docs/modules/ 仍只有 README",
        "模块正文现在可以在独立的 Module Design 任务中逐个建立",
        "UPLOADED → PROCESSING → READY",
    ):
        assert stale not in architecture


def test_domain_and_knowledge_authority_is_consistent_across_human_and_engineering_docs() -> None:
    architecture = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    modules_readme = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    domain = (REPO_ROOT / "docs/modules/02-legal-domain-work-product.md").read_text(encoding="utf-8")
    knowledge = (REPO_ROOT / "docs/modules/03-knowledge-evidence.md").read_text(encoding="utf-8")
    terminology = (REPO_ROOT / "docs/terminology.md").read_text(encoding="utf-8")

    for text in (architecture, modules_readme, domain, knowledge, terminology):
        assert "EvidenceCandidate" in text
        assert "Evidence" in text
        assert "CitationLineage" in text
        assert "WorkProductCitationBinding" in text
        assert "KnowledgeGeneration" in text
        assert "ReadinessDecision" in text

    assert "EvidenceCandidate != Evidence" in architecture
    assert "CitationLineage != WorkProductCitationBinding" in architecture
    assert "KnowledgeGeneration lifecycle != task-level ReadinessDecision" in architecture

    assert "EvidenceCandidate / CitationLineage 归 03；正式 Evidence 归 02" in domain
    assert "DocumentVersion canonical identity 归 02" in knowledge
    assert "stale KnowledgeGeneration 归 03；stale Finding / WorkProduct 归 02" in knowledge


def test_all_nine_modules_have_human_first_b1_b14_deep_design() -> None:
    modules = {
        "01": "01-application-integration.md",
        "02": "02-legal-domain-work-product.md",
        "03": "03-knowledge-evidence.md",
        "04": "04-agent-runtime-control.md",
        "05": "05-capability-skill.md",
        "06": "06-tool-runtime-effects.md",
        "07": "07-model-gateway.md",
        "08": "08-security-governance.md",
        "09": "09-observability-evaluation.md",
    }
    b_sections = (
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
    )
    for number, filename in modules.items():
        text = (REPO_ROOT / "docs/modules" / filename).read_text(encoding="utf-8")
        assert "## Part A — Human Narrative" in text, number
        assert "## Part B — Engineering / Agent Reference" in text, number
        assert "implementation: not-authorized" in text, number
        for marker in b_sections:
            assert marker in text, f"{number}: {marker}"

    for number in ("01", "04", "05", "06", "07", "08", "09"):
        text = (REPO_ROOT / "docs/modules" / modules[number]).read_text(encoding="utf-8")
        assert "deepening: all-modules-v1" in text, number

    readme = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    assert "module_deep_design: AVAILABLE_V1" in readme
    assert "module_deep_design_coverage: 9/9" in readme
    assert "module_detail_freeze: NOT_YET" in readme
    assert "implementation_authorization: NO" in readme


def test_cross_module_authority_invariants_are_explicit() -> None:
    modules_readme = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    assert "EvidenceCandidate != Evidence" in modules_readme
    assert "CitationLineage != WorkProductCitationBinding" in modules_readme
    assert "KnowledgeGeneration lifecycle != task-level ReadinessDecision" in modules_readme
    assert "Checkpoint completed\n!=\nDomain committed" in modules_readme
    assert "Capability Proposal\n!=\nPreparedAction\n!=\nToolAttempt\n!=\nEffectReceipt" in modules_readme
    assert "AuthorizationDecision\n!=\nApprovalDecision\n!=\nHumanDecision" in modules_readme
    assert "Telemetry / Trace\n!=\nDurable Audit\n!=\nBusiness Truth" in modules_readme


def test_human_first_governance_matches_current_module_b1_b14_template() -> None:
    governance = (REPO_ROOT / "docs/governance/human-first-documentation-standard.md").read_text(encoding="utf-8")
    for marker in (
        "B1  Scope / Global Invariants",
        "B2  Responsibility / Ownership",
        "B3  Upstream / Downstream",
        "B4  Authoritative Facts / Core Objects",
        "B5  Cross-boundary Contracts",
        "B6  Normal Flow",
        "B7  State / Lifecycle",
        "B8  Failure Taxonomy",
        "B9  Retry / Replan / Reconcile / Recovery / Idempotency",
        "B10 Security / Approval / Audit",
        "B11 Persistence / Transaction Boundaries",
        "B12 Observability / Evaluation",
        "B13 Current / Target / Gap / Evidence",
        "B14 Code / Database / Migration Constraints",
    ):
        assert marker in governance
    assert "中文优先规则" in governance


def test_adr_precedence_is_explicit_for_round02_refinements() -> None:
    decisions = (REPO_ROOT / "docs/decisions/README.md").read_text(encoding="utf-8")
    adr0008 = (REPO_ROOT / "docs/decisions/0008-legal-domain-kernel-and-host-boundary.md").read_text(encoding="utf-8")
    adr0013 = (REPO_ROOT / "docs/decisions/0013-round-02-responsibility-taxonomy.md").read_text(encoding="utf-8")
    assert "supersede / refine（取代 / 细化）" in decisions
    assert "ADR-0008" in decisions and "ADR-0013" in decisions and "ADR-0014" in decisions
    assert "阅读说明：本 ADR 与后续 ADR 的关系" in adr0008
    assert "clarification（澄清）而不是新决策" in adr0008
    assert "Round 02 后续已经完成 Overall Architecture Freeze" in adr0013
    assert "Gap：Main Architecture Freeze Review 尚未完成" not in adr0013

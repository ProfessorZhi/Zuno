from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULES = {
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

B_SECTIONS = (
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

C_SECTIONS = (
    "## Part C — Cross-Module Consistency（跨模块一致性）",
    "### C1 Completion Proof / Non-proof（完成证明与非证明）",
    "### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）",
    "### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）",
    "### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）",
)

DETAIL_CANDIDATE_MARKERS = (
    "detail_design: candidate-v1",
    "#### B14.1 Detail Freeze Candidate",
    "#### B14.2 Detail Freeze Candidate",
    "#### B14.3 Detail Freeze Candidate",
    "#### B14.4 Detail Freeze Candidate",
    "#### B14.5 Detail Freeze Candidate",
    "#### B14.6 Detail Freeze Candidate",
    "#### B14.7 Detail Freeze Candidate",
    "#### B14.8 Detail Freeze Candidate",
)


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
        for marker in (
            "EvidenceCandidate",
            "Evidence",
            "CitationLineage",
            "WorkProductCitationBinding",
            "KnowledgeGeneration",
            "ReadinessDecision",
        ):
            assert marker in text

    assert "EvidenceCandidate != Evidence" in architecture
    assert "CitationLineage != WorkProductCitationBinding" in architecture
    assert "KnowledgeGeneration lifecycle != task-level ReadinessDecision" in architecture
    assert "EvidenceCandidate / CitationLineage 归 03；正式 Evidence 归 02" in domain
    assert "DocumentVersion canonical identity 归 02" in knowledge
    assert "stale KnowledgeGeneration 归 03；stale Finding / WorkProduct 归 02" in knowledge


def test_all_nine_modules_have_human_first_b1_b14_and_part_c_v2() -> None:
    for number, filename in MODULES.items():
        text = (REPO_ROOT / "docs/modules" / filename).read_text(encoding="utf-8")
        assert "## Part A — Human Narrative" in text, number
        assert "## Part B — Engineering / Agent Reference" in text, number
        assert "implementation: not-authorized" in text, number
        assert "deepening: cross-module-consistency-v2" in text, number
        for marker in B_SECTIONS + C_SECTIONS:
            assert marker in text, f"{number}: {marker}"

    readme = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    assert "module_design_baseline: AVAILABLE_V1" in readme
    assert "module_deep_design: AVAILABLE_V2" in readme
    assert "module_deep_design_coverage: 9/9" in readme
    assert "cross_module_consistency: AVAILABLE_V1" in readme
    assert "module_detail_design_candidate: AVAILABLE_V1" in readme
    assert "module_detail_design_candidate_coverage: 2/9" in readme
    assert "module_detail_freeze: NOT_YET" in readme
    assert "implementation_authorization: NO" in readme


def test_domain_and_knowledge_have_detail_freeze_candidate_v1_only() -> None:
    docs = {
        number: (REPO_ROOT / "docs/modules" / filename).read_text(encoding="utf-8")
        for number, filename in MODULES.items()
    }
    for number in ("02", "03"):
        for marker in DETAIL_CANDIDATE_MARKERS:
            assert marker in docs[number], f"{number}: {marker}"

    for number in ("01", "04", "05", "06", "07", "08", "09"):
        assert "detail_design: candidate-v1" not in docs[number], number

    domain = docs["02"]
    for marker in (
        "AdmissionCommand candidate",
        "AdmissionReceipt candidate",
        "Matter-level serialized admission",
        "expected_activation_version",
    ):
        if marker == "expected_activation_version":
            continue
        assert marker in domain
    assert "Crash Window 与恢复矩阵" in domain
    assert "Failure Injection / Freeze Evidence" in domain

    knowledge = docs["03"]
    for marker in (
        "KnowledgeGeneration / ProcessingSpec / Manifest 字段组",
        "ServingPointer candidate",
        "expected_activation_version",
        "Worker、Backpressure、Cache 与并发规则",
        "Failure Injection / Freeze Evidence",
    ):
        assert marker in knowledge


def test_cross_module_authority_invariants_are_explicit() -> None:
    readme = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    for marker in (
        "EvidenceCandidate != Evidence",
        "CitationLineage != WorkProductCitationBinding",
        "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
        "Checkpoint completed != Domain committed",
        "Capability Proposal != PreparedAction != ToolAttempt != EffectReceipt",
        "AuthorizationDecision != ApprovalDecision != HumanDecision",
        "Telemetry / Trace != Durable Audit != Business Truth",
        "Cancel requested\n!= external operation cancelled\n!= Domain fact rolled back",
        "Late result arrived\n!= late result still eligible for current Plan / Domain",
        "Same correlation id\n!= same idempotency namespace",
    ):
        assert marker in readme


def test_cross_module_cancellation_and_recovery_semantics_are_specialized_per_owner() -> None:
    docs = {
        number: (REPO_ROOT / "docs/modules" / filename).read_text(encoding="utf-8")
        for number, filename in MODULES.items()
    }
    assert "取消入口请求或 Runtime Run" in docs["01"]
    assert "Run / request cancellation 不撤销已经提交的 Domain transaction" in docs["02"]
    assert "取消 ingestion / rebuild" in docs["03"]
    assert "AgentRun=CANCELLED" in docs["04"]
    assert "Capability invocation 被取消" in docs["05"]
    assert "取消 Runtime / request 后" in docs["06"]
    assert "CANCEL_REQUESTED" in docs["07"]
    assert "旧 SecurityEpoch 的 allow" in docs["08"]
    assert "OpenTelemetry Baggage" in docs["09"]

    assert "matching AdmissionReceipt" in docs["04"]
    assert "EffectReceipt / ReconciliationReceipt" in docs["06"]
    assert "恢复时先找 Owner Fact，再修复 Projection" in (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")


def test_idempotency_and_correlation_boundaries_do_not_collapse() -> None:
    readme = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    assert "Idempotency（幂等）不是一个全局 key" in readme
    assert "request / invocation idempotency" in readme
    assert "formal admission idempotency" in readme
    assert "prepared action / external effect" in readme
    assert "publication / delivery identity" in readme
    assert "opaque identity（不透明身份）" in readme

    observability = (REPO_ROOT / "docs/modules/09-observability-evaluation.md").read_text(encoding="utf-8")
    assert "Baggage" in observability
    assert "Secret、tenant / matter 名称、用户 PII" in observability
    assert "opaque ref" in observability


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

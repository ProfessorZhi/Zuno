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

DETAIL_CANDIDATE_MARKERS = tuple(
    f"#### B14.{number} Detail Freeze Candidate" for number in range(1, 9)
)


def _load():
    path = REPO_ROOT / "tools/scripts/verify_architecture_semantic_alignment.py"
    spec = importlib.util.spec_from_file_location("verify_architecture_semantic_alignment", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _docs() -> dict[str, str]:
    return {
        number: (REPO_ROOT / "docs/modules" / filename).read_text(encoding="utf-8")
        for number, filename in MODULES.items()
    }


def _has_candidate_status(text: str) -> bool:
    return "detail_design: candidate-v1" in text or "detail-design: candidate-v1" in text


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


def test_domain_and_knowledge_authority_is_consistent_across_docs() -> None:
    architecture = (REPO_ROOT / "docs/architecture/architecture.md").read_text(encoding="utf-8")
    modules_readme = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    domain = (REPO_ROOT / "docs/modules/02-legal-domain-work-product.md").read_text(encoding="utf-8")
    knowledge = (REPO_ROOT / "docs/modules/03-knowledge-evidence.md").read_text(encoding="utf-8")
    terminology = (REPO_ROOT / "docs/terminology.md").read_text(encoding="utf-8")

    for text in (architecture, modules_readme, domain, knowledge, terminology):
        for marker in (
            "EvidenceCandidate", "Evidence", "CitationLineage",
            "WorkProductCitationBinding", "KnowledgeGeneration", "ReadinessDecision",
        ):
            assert marker in text

    assert "EvidenceCandidate != Evidence" in architecture
    assert "CitationLineage != WorkProductCitationBinding" in architecture
    assert "KnowledgeGeneration lifecycle != task-level ReadinessDecision" in architecture
    assert "EvidenceCandidate / CitationLineage 归 03；正式 Evidence 归 02" in domain
    assert "DocumentVersion canonical identity 归 02" in knowledge
    assert "stale KnowledgeGeneration 归 03；stale Finding / WorkProduct 归 02" in knowledge


def test_all_nine_modules_have_human_first_b1_b14_part_c_and_detail_candidate() -> None:
    docs = _docs()
    for number, text in docs.items():
        assert "## Part A — Human Narrative" in text, number
        assert "## Part B — Engineering / Agent Reference" in text, number
        assert "implementation: not-authorized" in text, number
        assert "deepening: cross-module-consistency-v2" in text, number
        assert _has_candidate_status(text), number
        for marker in B_SECTIONS + C_SECTIONS + DETAIL_CANDIDATE_MARKERS:
            assert marker in text, f"{number}: {marker}"

    readme = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
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


def test_each_detail_candidate_has_owner_specific_freeze_semantics() -> None:
    docs = _docs()
    required = {
        "01": ("ExternalRequest / TaskScope 字段组", "Publication 字段组", "Outbox / Crash / Idempotency"),
        "02": ("正式准入输入与回执字段组", "Matter-level serialized admission", "Crash Window 与恢复矩阵"),
        "03": ("KnowledgeGeneration / ProcessingSpec / Manifest 字段组", "ServingPointer", "Worker、Backpressure、Cache"),
        "04": ("AgentRun / PlanVersion 字段组", "Ready / Parallel / Join Guard", "Checkpoint / Interrupt / Resume"),
        "05": ("CapabilityVersion 字段组", "ProviderBinding / Conformance", "Eligibility 字段组与 Guard"),
        "06": ("PreparedAction 字段组", "EffectClass / RetrySafety", "Send Boundary / Transaction Candidate"),
        "07": ("ModelRequest / Routing 字段组", "Usage / Cost / Budget Settlement", "Qualification / Role Guard"),
        "08": ("Authorization / Approval 字段组", "Secret / Credential / Lease", "生命周期与 per-store enforcement"),
        "09": ("TelemetryEnvelope / Correlation 字段组", "EvalDataset / EvalCase 字段组", "Release / Experiment Guard"),
    }
    for number, markers in required.items():
        for marker in markers:
            assert marker in docs[number], f"{number}: {marker}"
        assert "Failure Injection / Freeze Evidence" in docs[number]


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


def test_retry_replan_reconcile_and_cancel_do_not_collapse() -> None:
    docs = _docs()
    assert "Retry != Replan != Reconcile" in docs["04"]
    assert "Replan Barrier" in docs["04"]
    assert "Outcome Unknown（结果未知）不得映射为普通 Failed" in docs["06"]
    assert "ReconciliationReceipt" in docs["06"]
    assert "cancel" in docs["01"].lower()
    assert "cancel" in docs["04"].lower()
    assert "cancel" in docs["06"].lower()
    assert "CANCEL_REQUESTED" in docs["07"]
    assert "matching AdmissionReceipt" in docs["04"]


def test_idempotency_and_correlation_boundaries_do_not_collapse() -> None:
    readme = (REPO_ROOT / "docs/modules/README.md").read_text(encoding="utf-8")
    assert "Idempotency（幂等）不是一个全局 key" in readme
    for marker in (
        "request / invocation idempotency",
        "formal admission idempotency",
        "prepared action / external effect",
        "publication / delivery identity",
    ):
        assert marker in readme

    observability = (REPO_ROOT / "docs/modules/09-observability-evaluation.md").read_text(encoding="utf-8")
    assert "OpenTelemetry Baggage" in observability
    assert "Secret NEVER EXPORT" in observability
    assert "opaque ref" in observability


def test_owner_completion_proofs_remain_separate() -> None:
    docs = _docs()
    assert "Run completed\n!=\nDomain admitted\n!=\nAnswer publishable\n!=\nConsumer displayed" in docs["01"]
    assert "DomainVersion + matching AdmissionReceipt" in docs["02"]
    assert "index write success" in docs["03"]
    assert "Runtime Checkpoint != Domain Commit != Tool Effect != Publication truth" in docs["04"]
    assert "Provider Conformance != task quality" in docs["05"]
    assert "Transport Success 不等于 Effect Success" in docs["06"]
    assert "Gateway 调用成功 != Runtime Step accepted != Domain admitted != Answer published" in docs["07"]
    assert "Retention != Recall Eligibility != Physical Purge Completion" in docs["08"]
    assert "Telemetry != Durable Audit != Business Truth" in docs["09"]


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

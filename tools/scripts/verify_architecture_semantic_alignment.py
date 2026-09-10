from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH_HUMAN = ROOT / "docs/architecture/architecture.md"
ARCH_REFERENCE = ROOT / "docs/architecture/reference.md"
VIEWS = ROOT / "docs/architecture/architecture-views.md"
HTML = ROOT / "docs/architecture/architecture.html"
PROJECT = ROOT / "docs/project/README.md"
MODULES = ROOT / "docs/modules"
DECISIONS = ROOT / "docs/decisions"
TERMINOLOGY = ROOT / "docs/governance/terminology.md"

MODULE_DIRS = {
    "01": "application",
    "02": "domain",
    "03": "knowledge",
    "04": "runtime",
    "05": "capability",
    "06": "effects",
    "07": "model-gateway",
    "08": "security",
    "09": "evaluation",
}

B1_B14_MARKERS = (
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

PART_C_MARKERS = (
    "## Part C — Cross-Module Consistency（跨模块一致性）",
    "### C1 Completion Proof / Non-proof（完成证明与非证明）",
    "### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）",
    "### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）",
    "### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）",
)

DETAIL_CANDIDATE_MARKERS = tuple(f"#### B14.{number} Detail Freeze Candidate" for number in range(1, 9))


def _require(errors: list[str], label: str, text: str, markers: tuple[str, ...]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        errors.append(f"{label} missing: {', '.join(missing)}")


def _has_detail_candidate_status(text: str) -> bool:
    return "detail_design: candidate-v1" in text or "detail-design: candidate-v1" in text


def _module_docs() -> tuple[dict[str, str], dict[str, str]]:
    human = {
        number: (MODULES / directory / "README.md").read_text(encoding="utf-8")
        for number, directory in MODULE_DIRS.items()
    }
    reference = {
        number: (MODULES / directory / "reference.md").read_text(encoding="utf-8")
        for number, directory in MODULE_DIRS.items()
    }
    return human, reference


def verify() -> list[str]:
    errors: list[str] = []
    architecture_human = ARCH_HUMAN.read_text(encoding="utf-8")
    architecture_reference = ARCH_REFERENCE.read_text(encoding="utf-8")
    architecture_all = architecture_human + "\n" + architecture_reference
    project = PROJECT.read_text(encoding="utf-8")
    views = VIEWS.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    modules_readme = (MODULES / "README.md").read_text(encoding="utf-8")
    modules_reference = (MODULES / "reference.md").read_text(encoding="utf-8")
    module_human, module_reference = _module_docs()
    terminology = TERMINOLOGY.read_text(encoding="utf-8")

    _require(
        errors,
        "project narrative",
        project,
        (
            "project-fact-provenance.md",
            "Pilot Validation",
            "Production",
            "Current",
            "Target",
            "Unknown",
        ),
    )

    _require(
        errors,
        "overall architecture human narrative",
        architecture_human,
        (
            "# Zuno 目标架构",
            "## Part A — Human Narrative（人类技术叙事）",
            "overall_architecture_state: ROUND_02_FROZEN",
            "target_logical_module_count: 9",
            "module_design_baseline: AVAILABLE_V1",
            "module_deep_design: AVAILABLE_V2",
            "module_deep_design_coverage: 9/9",
            "cross_module_consistency: AVAILABLE_V1",
            "module_detail_freeze: NOT_YET",
            "implementation_authorization: NO",
            "reference.md",
        ),
    )
    if "## Part B — Engineering / Agent Reference（工程 / Agent 参考）" in architecture_human:
        errors.append("overall architecture human document must not retain Part B")
    _require(
        errors,
        "overall architecture split views",
        architecture_all,
        ("Single Controller", "docs/modules/", "docs/decisions/", "docs/evidence/", "docs/research/"),
    )

    _require(
        errors,
        "overall architecture engineering reference",
        architecture_reference,
        (
            "## Part B — Engineering / Agent Reference（工程 / Agent 参考）",
            "### B1. Scope / Global Invariants",
            "### B2. Authority / Ownership Matrix",
            "### B3. Cross-boundary Contract Map",
            "### B4. Canonical Execution Profiles",
            "### B5. State / Lifecycle Families",
            "### B6. Completion Proof / Non-proof",
            "### B7. Failure Taxonomy / Recovery Order",
            "### B8. Retry / Replan / Reconcile / Idempotency",
            "### B9. Version / Freshness / Causation Bindings",
            "### B10. Security / Approval / Human Authority",
            "### B11. Persistence / Transaction Boundaries",
            "### B12. Build / Buy / Extend / Delete Conditions",
            "### B13. Current / Target / Evidence / Unknown",
            "### B14. Machine Navigation / Source Precedence",
            "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
            "EvidenceCandidate != Evidence",
            "CitationLineage != WorkProductCitationBinding",
            "Retry != Replan != Reconcile",
            "AdmissionReceipt",
            "PreparedAction",
            "EffectReceipt",
            "Runtime Checkpoint != Domain Commit != Tool Effect != Publication truth",
            "AuthorizationDecision、ApprovalDecision、HumanDecision",
        ),
    )

    responsibility_markers = (
        "01 Application & Integration",
        "02 Legal Domain & Work Product",
        "03 Knowledge & Evidence",
        "04 Agent Runtime & Control",
        "05 Capability & Skill",
        "06 Tool Runtime & Effects",
        "07 Model Gateway",
        "08 Security & Governance",
        "09 Observability & Evaluation",
    )
    positions = [architecture_reference.find(marker) for marker in responsibility_markers]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        errors.append("architecture engineering reference must preserve canonical 01-09 responsibility order")

    for marker in (
        "02 Legal Domain & Work Product | Matter / DocumentVersion canonical identity",
        "03 Knowledge & Evidence | KnowledgeGeneration",
        "Domain commit + matching `AdmissionReceipt`",
        "`EffectReceipt` or conclusive `ReconciliationReceipt`",
        "current matching Authorization/Approval/Audit/egress/secret facts",
        "Current Code / Test / Runtime Evidence",
        "> canonical docs/architecture + docs/modules",
    ):
        if marker not in architecture_reference:
            errors.append(f"overall architecture Part B missing cross-module reference invariant: {marker}")

    for number in MODULE_DIRS:
        human = module_human[number]
        reference = module_reference[number]
        combined = human + "\n" + reference

        _require(
            errors,
            f"module {number} human layer",
            human,
            (
                "## Part A — Human Narrative",
                "implementation: not-authorized",
                "deepening: cross-module-consistency-v2",
                "reference.md",
            ),
        )
        if "## Part B — Engineering / Agent Reference" in human:
            errors.append(f"module {number} README must not retain Part B")
        if not _has_detail_candidate_status(human):
            errors.append(f"module {number} missing detail design candidate-v1 status marker")

        _require(
            errors,
            f"module {number} engineering template",
            reference,
            ("## Part B — Engineering / Agent Reference",) + B1_B14_MARKERS + PART_C_MARKERS,
        )
        _require(errors, f"module {number} detail candidate", reference, DETAIL_CANDIDATE_MARKERS)
        if not reference.index("## Part B — Engineering / Agent Reference") < reference.index("## Part C — Cross-Module Consistency"):
            errors.append(f"module {number} reference must keep Part B before Part C")

        if not all(marker in combined for marker in ("Current", "Target", "Gap")):
            errors.append(f"module {number} split views must preserve Current / Target / Gap")

    # Semantic gates should be anchored in the combined Human + Engineering views. Part A is
    # free to explain the concept in natural prose; exact ownership/failure wording belongs in
    # the Engineering Reference when the human story no longer benefits from symbolic slogans.
    module_invariants = {
        "01": ("负责组合，不负责重新发明事实", "RunOutcome != Domain Admission != AnswerPublication != Consumer Display", "Agent Version = 产品能力 / 配置版本"),
        "02": (
            "EvidenceCandidate（证据候选）\n    ≠\nEvidence（正式证据）",
            "DomainVersion + matching AdmissionReceipt",
            "WorkProductCitationBinding",
            "| HumanDecision | 保存正式人工业务决定",
            "08 Security & Governance | AuthorizationDecision、ApprovalDecision / policy refs",
        ),
        "03": ("KnowledgeGeneration lifecycle != task-level ReadinessDecision", "EvidenceCandidate != formal Evidence", "CitationLineage != WorkProductCitationBinding", "stale KnowledgeGeneration 归 03；stale Finding / WorkProduct 归 02"),
        "04": ("Single Controller", "Fixed AgentRunGraph + dynamic Plan DAG + fixed StepExecutionGraph", "PlanVersion immutable after activation", "Retry != Replan != Reconcile", "Replan Barrier"),
        "05": (
            "Capability = 稳定专业语义",
            "Provider Conformance != task quality",
            "Provider transient failure 可 Retry；semantic / schema / applicability drift 触发 re-resolution / Replan",
        ),
        "06": ("Outcome Unknown（结果未知）不得映射为普通 Failed", "Transport Success 不等于 Effect Success", "same key + different action hash 必须拒绝"),
        "07": ("Model Role 与具体 Provider / Model 解耦", "Provider technically available != currently permitted != quality qualified", "Gateway 调用成功 != Runtime Step accepted != Domain admitted != Answer published"),
        "08": ("Continuous Authorization（持续授权）", "AuthorizationDecision、ApprovalDecision、HumanDecision 三者 Owner 与语义不同", "Retention != Recall Eligibility != Physical Purge Completion", "MANDATORY_BEFORE_EFFECT"),
        "09": ("Telemetry != Durable Audit != Business Truth", "MEASUREMENT_BLOCKED", "Secret NEVER EXPORT", "OpenTelemetry Baggage"),
    }
    for number, markers in module_invariants.items():
        _require(errors, f"module {number} invariant", module_human[number] + "\n" + module_reference[number], markers)

    _require(
        errors,
        "modules README state",
        modules_readme,
        (
            "module_design_baseline: AVAILABLE_V1",
            "module_deep_design: AVAILABLE_V2",
            "module_deep_design_coverage: 9/9",
            "cross_module_consistency: AVAILABLE_V1",
            "module_detail_design_candidate: AVAILABLE_V1",
            "module_detail_design_candidate_coverage: 9/9",
            "module_detail_freeze: NOT_YET",
            "implementation_authorization: NO",
            "reference.md",
        ),
    )
    _require(
        errors,
        "modules engineering reference",
        modules_reference,
        (
            "Cancellation（取消）是停止未来工作，不是全局回滚",
            "Idempotency（幂等）不是一个全局 key",
            "恢复时先找 Owner Fact，再修复 Projection",
            "DETAIL DESIGN CANDIDATE V1 AVAILABLE",
            "Module Detail Freeze Review",
        ),
    )

    _require(
        errors,
        "terminology authority",
        terminology,
        (
            "DocumentVersion（材料版本）",
            "EvidenceCandidate（证据候选）",
            "Evidence（正式证据）",
            "CitationLineage（检索引用链）",
            "WorkProductCitationBinding（工作成果历史引用绑定）",
            "KnowledgeGeneration（知识生成版本）",
            "ReadinessDecision（知识就绪判断）",
            "AdmissionReceipt（正式准入回执）",
        ),
    )

    decisions_readme = (DECISIONS / "README.md").read_text(encoding="utf-8")
    _require(errors, "ADR precedence", decisions_readme, ("supersede / refine（取代 / 细化）", "ADR-0008", "ADR-0013", "ADR-0014", "Architecture Gap"))
    for name in (
        "0008-legal-domain-kernel-and-host-boundary.md",
        "0012-evidence-gated-physical-service-split.md",
        "0013-round-02-responsibility-taxonomy.md",
        "0014-round-02-cross-boundary-authority-and-recovery.md",
    ):
        if not (DECISIONS / name).exists():
            errors.append(f"active architecture decision is missing: {name}")

    for forbidden in (
        "Product Surface & Agent Portfolio",
        "Agent Runtime & Multi-Agent Orchestration",
        "NEW_10_MODULE_SET",
        "ROUND_02_REVISED_PENDING_FREEZE_REVIEW",
        "final_module_count: NOT_FROZEN",
        "module_decomposition_gate: NOT_OPEN",
        "docs/modules/ 仍只有 README",
    ):
        if forbidden in architecture_all or forbidden in views:
            errors.append(f"active architecture retains superseded semantics: {forbidden}")

    if views.count("```mermaid") != 6:
        errors.append("architecture-views.md must contain exactly 6 conceptual diagrams")
    if 'fetch("./architecture-views.md")' not in html:
        errors.append("architecture.html must render canonical Mermaid source")
    if "../project/README.md" not in html or "./architecture.md" not in html:
        errors.append("architecture.html must expose current canonical entrypoints")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("architecture semantic alignment verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

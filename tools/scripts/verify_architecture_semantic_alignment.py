from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture/architecture.md"
VIEWS = ROOT / "docs/architecture/architecture-views.md"
HTML = ROOT / "docs/architecture/architecture.html"
PROJECT = ROOT / "docs/project/project.md"
MODULES = ROOT / "docs/modules"
DECISIONS = ROOT / "docs/decisions"
GOVERNANCE = ROOT / "docs/governance/human-first-documentation-standard.md"
TERMINOLOGY = ROOT / "docs/terminology.md"

MODULE_FILES = {
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

DETAIL_CANDIDATE_MARKERS = tuple(
    f"#### B14.{number} Detail Freeze Candidate" for number in range(1, 9)
)


def _require(errors: list[str], label: str, text: str, markers: tuple[str, ...]) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        errors.append(f"{label} missing: {', '.join(missing)}")


def _has_detail_candidate_status(text: str) -> bool:
    return "detail_design: candidate-v1" in text or "detail-design: candidate-v1" in text


def verify() -> list[str]:
    errors: list[str] = []
    architecture = ARCH.read_text(encoding="utf-8")
    project = PROJECT.read_text(encoding="utf-8")
    views = VIEWS.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    modules_readme = (MODULES / "README.md").read_text(encoding="utf-8")
    modules = {
        number: (MODULES / filename).read_text(encoding="utf-8")
        for number, filename in MODULE_FILES.items()
    }
    terminology = TERMINOLOGY.read_text(encoding="utf-8")
    governance = GOVERNANCE.read_text(encoding="utf-8")

    _require(
        errors,
        "project narrative",
        project,
        (
            "为什么会有这个项目",
            "为什么不直接用 Dify、Coze",
            "项目是怎样发展到今天的",
            "团队是什么形态，我在里面做了什么",
            "相比通用方案，我们今天到底证明了什么",
            "Pilot Validation",
            "Production",
            "Current",
            "Target",
            "Unknown",
        ),
    )

    _require(
        errors,
        "overall architecture",
        architecture,
        (
            "## Part A — Architecture Narrative",
            "## Part B — Detailed Architecture Specification",
            "overall_architecture_state: ROUND_02_FROZEN",
            "target_logical_module_count: 9",
            "module_design_baseline: AVAILABLE_V1",
            "module_deep_design: AVAILABLE_V2",
            "module_deep_design_coverage: 9/9",
            "cross_module_consistency: AVAILABLE_V1",
            "module_detail_freeze: NOT_YET",
            "implementation_authorization: NO",
            "EvidenceCandidate != Evidence",
            "CitationLineage != WorkProductCitationBinding",
            "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
            "Retry != Replan != Reconcile",
            "AdmissionReceipt",
            "PreparedAction",
            "EffectReceipt",
            "AuditPersistenceReceipt",
            "Single Controller",
            "按事实权威划分责任",
            "九个逻辑责任域",
            "复杂度的退出机制",
            "docs/project/project.md",
        ),
    )

    # Preserve the canonical 01-09 responsibility order without freezing a particular
    # Markdown heading level. Textbook prose may present these responsibilities as
    # headings, bold terms, or another readable form as long as all nine remain ordered.
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
    positions = [architecture.find(marker) for marker in responsibility_markers]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        errors.append("architecture responsibilities must exist in canonical 01-09 order")

    for number, text in modules.items():
        _require(errors, f"module {number} template", text, B1_B14_MARKERS + PART_C_MARKERS)
        _require(
            errors,
            f"module {number} layers",
            text,
            (
                "## Part A — Human Narrative",
                "## Part B — Engineering / Agent Reference",
                "implementation: not-authorized",
                "deepening: cross-module-consistency-v2",
                "### 当前、目标与缺口",
            ),
        )
        if not _has_detail_candidate_status(text):
            errors.append(f"module {number} missing detail design candidate-v1 status marker")
        _require(errors, f"module {number} detail candidate", text, DETAIL_CANDIDATE_MARKERS)

    module_invariants = {
        "01": (
            "负责组合，不负责重新发明事实",
            "Run completed\n!=\nDomain admitted\n!=\nAnswer publishable\n!=\nConsumer displayed",
            "Agent Version = 产品能力 / 配置版本",
        ),
        "02": (
            "EvidenceCandidate（证据候选）\n    ≠\nEvidence（正式证据）",
            "DomainVersion + matching AdmissionReceipt",
            "WorkProductCitationBinding",
            "HumanDecision（人工业务决定）和 ApprovalDecision（安全审批决定）",
        ),
        "03": (
            "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
            "EvidenceCandidate != formal Evidence",
            "CitationLineage != WorkProductCitationBinding",
            "stale KnowledgeGeneration 归 03；stale Finding / WorkProduct 归 02",
        ),
        "04": (
            "Single Controller",
            "Fixed AgentRunGraph + dynamic Plan DAG + fixed StepExecutionGraph",
            "PlanVersion immutable after activation",
            "Retry != Replan != Reconcile",
            "Replan Barrier",
        ),
        "05": (
            "Capability = 稳定专业语义",
            "Provider Conformance != task quality",
            "provider execution failure\n!=\ncapability semantic drift",
        ),
        "06": (
            "Outcome Unknown（结果未知）不得映射为普通 Failed",
            "Transport Success 不等于 Effect Success",
            "same key + different action hash 必须拒绝",
        ),
        "07": (
            "Model Role 与具体 Provider / Model 解耦",
            "Provider technically available != currently permitted != quality qualified",
            "Gateway 调用成功 != Runtime Step accepted != Domain admitted != Answer published",
        ),
        "08": (
            "Continuous Authorization（持续授权）",
            "AuthorizationDecision、ApprovalDecision、HumanDecision 三者 Owner 与语义不同",
            "Retention != Recall Eligibility != Physical Purge Completion",
            "MANDATORY_BEFORE_EFFECT",
        ),
        "09": (
            "Telemetry != Durable Audit != Business Truth",
            "MEASUREMENT_BLOCKED",
            "Secret NEVER EXPORT",
            "OpenTelemetry Baggage",
        ),
    }
    for number, markers in module_invariants.items():
        _require(errors, f"module {number} invariant", modules[number], markers)

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

    _require(
        errors,
        "human-first governance",
        governance,
        (
            "中文优先规则",
            "B1  Scope / Global Invariants",
            "B5  Cross-boundary Contracts",
            "B14 Code / Database / Migration Constraints",
            "如果 Part A 和 Part B 无法保持一致",
        ),
    )

    decisions_readme = (DECISIONS / "README.md").read_text(encoding="utf-8")
    _require(
        errors,
        "ADR precedence",
        decisions_readme,
        ("supersede / refine（取代 / 细化）", "ADR-0008", "ADR-0013", "ADR-0014", "Architecture Gap"),
    )
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
        if forbidden in architecture or forbidden in views:
            errors.append(f"active architecture retains superseded semantics: {forbidden}")

    if views.count("```mermaid") != 14:
        errors.append("architecture-views.md must contain exactly 14 canonical diagrams")
    if 'fetch("./architecture-views.md")' not in html:
        errors.append("architecture.html must render canonical Mermaid source")
    if "../project/project.md" not in html or "./architecture.md#target-status-boundary" not in html:
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

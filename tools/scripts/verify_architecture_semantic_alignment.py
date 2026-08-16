from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture/architecture.md"
VIEWS = ROOT / "docs/architecture/architecture-views.md"
HTML = ROOT / "docs/architecture/architecture.html"
MODULES = ROOT / "docs/modules"
DECISIONS = ROOT / "docs/decisions"
GOVERNANCE = ROOT / "docs/governance/human-first-documentation-standard.md"
TERMINOLOGY = ROOT / "docs/terminology.md"


def _missing(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def _require(errors: list[str], label: str, text: str, markers: tuple[str, ...]) -> None:
    missing = _missing(text, markers)
    if missing:
        errors.append(f"{label} missing: {', '.join(missing)}")


def verify() -> list[str]:
    errors: list[str] = []
    architecture = ARCH.read_text(encoding="utf-8")
    views = VIEWS.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    modules_readme = (MODULES / "README.md").read_text(encoding="utf-8")
    domain = (MODULES / "02-legal-domain-work-product.md").read_text(encoding="utf-8")
    knowledge = (MODULES / "03-knowledge-evidence.md").read_text(encoding="utf-8")
    governance = GOVERNANCE.read_text(encoding="utf-8")
    terminology = TERMINOLOGY.read_text(encoding="utf-8")
    decisions_readme = (DECISIONS / "README.md").read_text(encoding="utf-8")
    adr0008 = (DECISIONS / "0008-legal-domain-kernel-and-host-boundary.md").read_text(encoding="utf-8")

    # Check the actual responsibility section order, not arbitrary earlier mentions.
    responsibility_headings = (
        "#### 01 Application & Integration（应用与集成）",
        "#### 02 Legal Domain & Work Product（法律领域与工作成果）",
        "#### 03 Knowledge & Evidence（知识与证据）",
        "#### 04 Agent Runtime & Control（智能体运行与控制）",
        "#### 05 Capability & Skill（专业能力与技能）",
        "#### 06 Tool Runtime & Effects（工具运行与外部效果）",
        "#### 07 Model Gateway（模型网关）",
        "#### 08 Security & Governance（安全与治理）",
        "#### 09 Observability & Evaluation（可观测性与评测）",
    )
    positions = [architecture.find(marker) for marker in responsibility_headings]
    if any(position < 0 for position in positions):
        errors.append("architecture is missing one or more canonical responsibility headings")
    elif positions != sorted(positions):
        errors.append("canonical responsibility headings are not ordered 01 through 09")

    part_a_marker = "## Part A — Architecture Narrative"
    part_b_marker = "## Part B — Detailed Architecture Specification"
    if part_a_marker not in architecture or part_b_marker not in architecture:
        errors.append("architecture must contain both Part A and Part B")
        part_a = architecture
        part_b = architecture
    else:
        part_a = architecture.split(part_a_marker, 1)[1].split(part_b_marker, 1)[0]
        part_b = architecture.split(part_b_marker, 1)[1]

    part_a_groups = {
        "simple qa": ("简单问答", "材料范围", "Generic Host（通用 Agent 宿主）"),
        "complex legal flow": ("一次复杂法律任务怎样完整运行", "EvidenceCandidate（证据候选）", "正式准入"),
        "domain knowledge boundary": (
            "KnowledgeGeneration 生命周期",
            "ReadinessDecision（知识就绪判断）",
            "EvidenceCandidate != Evidence",
            "CitationLineage != WorkProductCitationBinding",
        ),
        "controlled effect": ("外部动作为什么需要另一套处理方式", "EffectReceipt（效果回执）", "Reconciliation（对账恢复）"),
        "responsibility taxonomy": ("谁来负责这些不同事实", "九个冻结的 Logical Responsibility", "可选上下文边界"),
        "admission recovery": ("AdmissionReceipt（正式准入回执）", "Checkpoint（检查点）", "修复运行状态"),
        "build buy": ("哪些能力应该自己建设，哪些能力应该复用", "为什么必须独立服务", "不是库或 Worker"),
        "status boundary": ("Design Baseline V1（设计基线 V1）", "Module Detail Freeze", "implementation available"),
    }
    for name, markers in part_a_groups.items():
        _require(errors, f"Part A {name}", part_a, markers)

    part_b_groups = {
        "global invariants": (
            "### B1 Scope and Global Invariants",
            "Retry != Replan != Reconcile",
            "EvidenceCandidate != Evidence",
            "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
        ),
        "ownership": (
            "### B2 Responsibility / Ownership Map",
            "Formal Admission、AdmissionReceipt、WorkProductCitationBinding、Domain invalidation truth",
            "KnowledgeGeneration、processing / manifest / serving semantics",
            "AuthorizationDecision、SecurityEpoch、ApprovalDecision、EffectiveLifecycleDecision、Audit Requirement",
        ),
        "contracts": (
            "### B3 Cross-boundary Contracts",
            "#### ReadinessDecision",
            "#### EvidenceCandidate / CitationLineage",
            "#### WorkProductCitationBinding",
            "#### AdmissionReceipt",
            "#### WorkProductInvalidationFact / InvalidationDeliveryFact / ConsumerAcknowledgementObservation",
            "#### AuthorizationDecision / ApprovalDecision / EffectiveLifecycleDecision",
            "#### PreparedAction / ToolAttempt / EffectReceipt / ReconciliationReceipt",
            "#### AuditPersistenceReceipt",
        ),
        "state": (
            "### B5 State Machines",
            "#### KnowledgeGeneration Lifecycle",
            "#### Task-level ReadinessDecision",
            "#### Agent Runtime",
            "#### External Effect",
        ),
        "recovery": (
            "### B9 Recovery and Idempotency",
            "Domain Commit + AdmissionReceipt success；Checkpoint fail",
            "Knowledge generation partial write",
            "External Effect unknown",
        ),
        "persistence": (
            "### B10 Persistence Boundaries",
            "one Domain transactional durability boundary",
            "跨 Store 2PC",
        ),
        "status": (
            "### B12 Current / Target / Gap",
            "9 Module Design Baseline V1",
            "Module Detail Freeze",
            "NOT ESTABLISHED",
        ),
    }
    for name, markers in part_b_groups.items():
        _require(errors, f"Part B {name}", part_b, markers)

    stale_active_phrases = (
        "仍等待 Main Architecture Freeze Review",
        "不等于模块正文已经建立",
        "docs/modules/ 仍只有 README",
        "模块正文现在可以在独立的 Module Design 任务中逐个建立",
        "UPLOADED → PROCESSING → READY",
    )
    for phrase in stale_active_phrases:
        if phrase in architecture:
            errors.append(f"active architecture retains stale pre-baseline phrase: {phrase}")

    # 02/03 authority is checked by ownership, not by forcing every document to repeat every identifier.
    _require(
        errors,
        "architecture domain/knowledge authority",
        architecture,
        (
            "EvidenceCandidate != Evidence",
            "CitationLineage != WorkProductCitationBinding",
            "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
            "WorkProductCitationBinding",
            "AdmissionReceipt",
        ),
    )
    _require(
        errors,
        "modules README domain/knowledge authority",
        modules_readme,
        (
            "EvidenceCandidate != Evidence",
            "CitationLineage != WorkProductCitationBinding",
            "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
            "DocumentVersion",
            "AdmissionReceipt",
        ),
    )
    _require(
        errors,
        "module 02 authority",
        domain,
        (
            "Matter / DocumentVersion identity",
            "EvidenceCandidate / CitationLineage 归 03；正式 Evidence 归 02",
            "DomainVersion + matching AdmissionReceipt",
            "WorkProductCitationBinding",
            "Domain invalidation truth",
            "ReadinessDecision",
        ),
    )
    _require(
        errors,
        "module 03 authority",
        knowledge,
        (
            "DocumentVersion canonical identity 归 02",
            "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
            "EvidenceCandidate != formal Evidence",
            "CitationLineage != WorkProductCitationBinding",
            "stale KnowledgeGeneration 归 03；stale Finding / WorkProduct 归 02",
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
            "B1  Scope / Global Invariants",
            "B5  Cross-boundary Contracts",
            "B14 Code / Database / Migration Constraints",
            "中文优先规则",
            "如果 Part A 和 Part B 无法保持一致",
            "EvidenceCandidate   owner = 03 Knowledge & Evidence",
            "Evidence            owner = 02 Legal Domain & Work Product",
            "KnowledgeGeneration lifecycle",
        ),
    )

    _require(
        errors,
        "ADR precedence",
        decisions_readme,
        ("supersede / refine（取代 / 细化）", "ADR-0008", "ADR-0013", "ADR-0014", "Architecture Gap"),
    )
    _require(
        errors,
        "ADR-0008 clarification",
        adr0008,
        (
            "阅读说明：本 ADR 与后续 ADR 的关系",
            "clarification（澄清）而不是新决策",
            "08 Security & Governance 是 Authorization、Approval",
            "KnowledgeGeneration、task-level ReadinessDecision、EvidenceCandidate 和 CitationLineage",
        ),
    )

    for marker in (
        "FastAPI",
        "LangGraph",
        "PostgreSQL",
        "Checkpoint",
        "Reconciliation",
        "target_logical_module_count: 9",
        "Current",
        "Target",
        "History",
        "A/B/C",
        "architecture_revision: COMPLETED",
        "overall_architecture_state: ROUND_02_FROZEN",
        "module_decomposition_gate: OPEN",
        "module_design_baseline: AVAILABLE_V1",
        "module_detail_freeze: NOT_YET",
        "implementation_authorization: NO",
    ):
        if marker not in architecture:
            errors.append(f"architecture integration semantics missing: {marker}")

    for marker in (
        "Product Context View",
        "Logical Capability View",
        "Provider Boundary View",
        "Domain State View",
        "Agent Runtime View",
        "Physical Deployment Decision View",
        "Data Ownership View",
        "Failure and Recovery View",
        "A/B/C Eval View",
        "Security Verification View",
        "EffectReceipt",
        "Evidence Gate",
        "Modular Python Backend + Workers",
        "Optional Context Provider",
    ):
        if marker not in views:
            errors.append(f"architecture visual semantics missing: {marker}")

    for forbidden in (
        "Product Surface & Agent Portfolio",
        "Agent Runtime & Multi-Agent Orchestration",
        "Capability / Skill & Tool Runtime",
        "NEW_10_MODULE_SET",
        "REFINED_BASELINE_READY_FOR_FREEZE_REVIEW",
        "TARGET_HYPOTHESIS_PENDING_RED_TEAM",
        "ROUND_02_REVISED_PENDING_FREEZE_REVIEW",
        "final_module_count: NOT_FROZEN",
        "module_decomposition_gate: NOT_OPEN",
    ):
        if forbidden in architecture or forbidden in views:
            errors.append(f"active architecture retains superseded taxonomy: {forbidden}")

    if (DECISIONS / "0010-microservice-target-and-service-boundaries.md").exists():
        errors.append("ADR-0010 must be superseded out of the active decisions tree")
    for name in (
        "0012-evidence-gated-physical-service-split.md",
        "0013-round-02-responsibility-taxonomy.md",
        "0014-round-02-cross-boundary-authority-and-recovery.md",
    ):
        if not (DECISIONS / name).exists():
            errors.append(f"active architecture decision is missing: {name}")

    if 'fetch("./architecture-views.md")' not in html:
        errors.append("architecture.html must render canonical Mermaid source")
    if "../project/project-background.md" not in html or "./architecture.md#target-status-boundary" not in html:
        errors.append("architecture.html must expose canonical taxonomy entrypoints")
    if views.count("```mermaid") != 14:
        errors.append("architecture-views.md must contain exactly 14 canonical diagrams")

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

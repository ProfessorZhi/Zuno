from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture/architecture.md"
VIEWS = ROOT / "docs/architecture/architecture-views.md"
HTML = ROOT / "docs/architecture/architecture.html"
DECISIONS = ROOT / "docs/decisions"


def _missing(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def verify() -> list[str]:
    errors: list[str] = []
    architecture = ARCH.read_text(encoding="utf-8")
    views = VIEWS.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")

    responsibility_order = (
        "Application & Integration",
        "Legal Domain & Work Product",
        "Knowledge & Evidence",
        "Agent Runtime & Control",
        "Capability & Skill",
        "Tool Runtime & Effects",
        "Model Gateway",
        "Security & Governance",
        "Observability & Evaluation",
    )
    positions = [architecture.find(marker) for marker in responsibility_order]
    if any(position < 0 for position in positions):
        errors.append("architecture is missing one or more canonical responsibility domains")
    elif positions != sorted(positions):
        errors.append("canonical responsibility domains are not ordered 01 through 09")

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
        "simple qa": ("一个简单问题怎样完成", "Simple QA", "Generic Host 完成"),
        "complex legal flow": ("一个复杂法律分析怎样完成", "Finding Proposal", "WorkProduct"),
        "controlled effect": ("外部动作必须单独处理", "Effect Receipt", "Reconciliation"),
        "responsibility taxonomy": ("九个逻辑责任域", "Platform / Infrastructure Responsibility Layer", "Optional Context Provider"),
        "admission recovery": ("任务失败以后怎样恢复", "AdmissionReceipt", "Checkpoint"),
        "build buy": ("Build / Buy / Reuse", "Why service?", "Why not library?"),
    }
    for name, markers in part_a_groups.items():
        missing = _missing(part_a, markers)
        if missing:
            errors.append(f"Part A {name} missing: {', '.join(missing)}")

    part_b_groups = {
        "global invariants": ("B1 Scope and Global Invariants", "Retry != Replan != Reconcile", "Formal Admission"),
        "ownership": ("B2 Responsibility / Ownership Map", "Historical WorkProduct Citation Binding", "Security & Governance"),
        "contracts": ("B3 Cross-boundary Contracts", "InvocationDecision", "AnswerPublicationDecision", "AdmissionReceipt", "EffectiveLifecycleDecision"),
        "invalidation": ("WorkProductInvalidationFact", "InvalidationDeliveryFact", "ConsumerAcknowledgementObservation"),
        "recovery": ("B9 Recovery and Idempotency", "Domain Commit", "AdmissionReceipt", "Checkpoint"),
        "persistence": ("B10 Persistence Boundaries", "transactional durability boundary", "2PC"),
    }
    for name, markers in part_b_groups.items():
        missing = _missing(part_b, markers)
        if missing:
            errors.append(f"Part B {name} missing: {', '.join(missing)}")

    for marker in (
        "FastAPI", "LangGraph", "PostgreSQL", "Checkpoint", "Reconciliation",
        "target_logical_module_count: 9", "Current", "Target", "History",
        "A/B/C", "ROUND_02_REVISION_IMPLEMENTED", "MODULE_DECOMPOSITION_GATE",
    ):
        if marker not in architecture:
            errors.append(f"architecture integration semantics missing: {marker}")

    for marker in (
        "Product Context View", "Logical Capability View", "Provider Boundary View",
        "Domain State View", "Agent Runtime View", "Physical Deployment Decision View",
        "Data Ownership View", "Failure and Recovery View", "A/B/C Eval View",
        "Security Verification View", "EffectReceipt", "Evidence Gate",
        "Modular Python Backend + Workers", "Optional Context Provider",
    ):
        if marker not in views:
            errors.append(f"architecture visual semantics missing: {marker}")

    for forbidden in (
        "Product Surface & Agent Portfolio",
        "Agent Runtime & Multi-Agent Orchestration",
        "Capability / Skill & Tool Runtime",
        "Memory & Context",
        "Infrastructure & Persistence",
        "NEW_10_MODULE_SET",
        "REFINED_BASELINE_READY_FOR_FREEZE_REVIEW",
        "TARGET_HYPOTHESIS_PENDING_RED_TEAM",
    ):
        if forbidden in architecture or forbidden in views:
            errors.append(f"active architecture retains superseded taxonomy: {forbidden}")

    if (DECISIONS / "0010-microservice-target-and-service-boundaries.md").exists():
        errors.append("ADR-0010 must be superseded out of the active decisions tree")
    for name in ("0012-evidence-gated-physical-service-split.md", "0013-round-02-responsibility-taxonomy.md", "0014-round-02-cross-boundary-authority-and-recovery.md"):
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

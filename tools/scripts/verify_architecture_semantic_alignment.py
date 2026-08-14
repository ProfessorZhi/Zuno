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
        "Legal Work Surface",
        "Legal Domain & Intelligence",
        "Agentic Knowledge & Context",
        "Agent Runtime & Execution",
        "Trust & Platform Engineering",
    )
    positions = [architecture.find(marker) for marker in responsibility_order]
    for marker, position in zip(responsibility_order, positions):
        if position < 0:
            errors.append(f"architecture responsibility layer missing: {marker}")
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        errors.append("architecture responsibility layers are not ordered Work Surface → Domain → Knowledge → Runtime → Trust")

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
        "complete runtime flow": ("User / Generic Host submits task", "Knowledge Readiness Gate", "Canonical Domain Commit"),
        "knowledge readiness": ("Document Uploaded != Knowledge Ready", "Partial Knowledge View", "Full Scope Formal Result"),
        "result eligibility": ("Result Is Eligible for Formal Business Use", "review_required", "Abstain / Reject"),
        "continuous authorization": ("Run Start Authorization", "Run Lifetime Permanent Lease", "Model Egress"),
        "capability drift": ("Capability Assumption", "Capability Re-resolution", "Retry", "Replan"),
        "evidence-gated deployment": ("EVIDENCE-GATED DEPLOYMENT REFINEMENT", "Modular Python Backend", "Why service? Why not library? Why not worker?"),
    }
    for name, markers in part_a_groups.items():
        missing = _missing(part_a, markers)
        if missing:
            errors.append(f"Part A {name} missing: {', '.join(missing)}")

    part_b_groups = {
        "knowledge view contract": ("Declared Scope", "Document Version Set", "Knowledge View / Generation", "Readiness Receipt", "PARTIAL", "STALE", "MISSING_REQUIRED_SOURCE", "VERSION_MISMATCH"),
        "result eligibility contract": ("Degradation Context", "Evidence Sufficiency", "Quality Evaluation", "Security Decision", "Human Review Requirement", "Canonical Version"),
        "continuous authorization contract": ("Policy Epoch", "Current Authorization", "Resume、Retry、Replan", "Security Owner"),
        "capability compatibility contract": ("Retry != Replan", "Capability Assumption", "External Effect Outcome Unknown", "Stop / Human Review"),
        "physical deployment gate": ("Physical Deployment Gate", "Logical Responsibility 不等于 Physical Service", "Service Count", "Database-per-service"),
    }
    for name, markers in part_b_groups.items():
        missing = _missing(part_b, markers)
        if missing:
            errors.append(f"Part B {name} missing: {', '.join(missing)}")

    for marker in (
        "FastAPI", "LangGraph", "PostgreSQL", "Checkpoint", "Reconciliation",
        "FINAL_MODULE_COUNT: NOT_DECIDED", "Target", "不是 Current", "A/B/C Kill Test",
    ):
        if marker not in architecture:
            errors.append(f"architecture integration semantics missing: {marker}")

    for marker in (
        "Product Context View", "Logical Capability View", "Domain State View",
        "Agent Runtime View", "Physical Deployment Decision View", "Data Ownership View",
        "Failure and Recovery View", "A/B/C Eval View", "Security Verification View",
        "EvidenceRequirement", "ConflictProposal", "EffectReceipt", "PostgreSQL",
        "Evidence Gate", "Modular Backend + Independent Workers", "Split specific boundary",
    ):
        if marker not in views:
            errors.append(f"architecture visual semantics missing: {marker}")

    for forbidden in (
        "### Microservice View",
        "Microservice Direction | `ACCEPTED_TARGET`",
        "Microservice Architecture = accepted-target",
        "edge-api",
        "platform-domain-service",
        "agent-runtime-service",
        "knowledge-service",
        "tool-sandbox-service",
    ):
        if forbidden in architecture or forbidden in views:
            errors.append(f"active architecture retains superseded service semantics: {forbidden}")

    if (DECISIONS / "0010-microservice-target-and-service-boundaries.md").exists():
        errors.append("ADR-0010 must be superseded out of the active decisions tree")
    adr_0012 = DECISIONS / "0012-evidence-gated-physical-service-split.md"
    if not adr_0012.exists():
        errors.append("active evidence-gated physical service split ADR is missing")
    elif "EVIDENCE-GATED DEPLOYMENT REFINEMENT" not in adr_0012.read_text(encoding="utf-8"):
        errors.append("ADR-0012 does not define evidence-gated deployment refinement")

    if 'fetch("./architecture-views.md")' not in html:
        errors.append("architecture.html must render canonical Mermaid source")
    if "../facts/README.md" not in html or "./architecture.md#target-status-boundary" not in html:
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

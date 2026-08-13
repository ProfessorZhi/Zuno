from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/project/architecture/architecture.md"
VIEWS = ROOT / "docs/project/architecture/architecture-views.md"
HTML = ROOT / "docs/project/architecture/architecture.html"


def verify() -> list[str]:
    errors: list[str] = []
    architecture = ARCH.read_text(encoding="utf-8")
    views = VIEWS.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")

    precedence = [
        "Product / Domain",
        "Logical Capability Architecture",
        "Physical Service / Deployment Architecture",
        "History 只保存",
    ]
    positions = [architecture.find(marker) for marker in precedence]
    for marker, position in zip(precedence, positions):
        if position < 0:
            errors.append(f"architecture precedence missing: {marker}")
    if all(position >= 0 for position in positions) and positions != sorted(positions):
        errors.append("architecture layers are not ordered Product/Domain → Logical → Physical → status")

    for marker in [
        "Python-only", "Microservice", "FastAPI", "LangGraph", "PostgreSQL",
        "Checkpoint", "Reconciliation", "edge-api", "platform-domain-service",
        "agent-runtime-service", "knowledge-service", "tool-sandbox-service",
        "Target", "不是 Current",
    ]:
        if marker not in architecture and not (marker == "not Current" and "不是 Current" in architecture):
            errors.append(f"architecture integration semantics missing: {marker}")

    for marker in [
        "Product Context View", "Logical Capability View", "Domain State View",
        "Agent Runtime View", "Microservice View", "Data Ownership View",
        "Failure and Recovery View", "A/B/C Eval View", "Security Verification View",
        "EvidenceRequirement", "ConflictProposal", "EffectReceipt", "PostgreSQL",
    ]:
        if marker not in views:
            errors.append(f"architecture visual semantics missing: {marker}")
    for forbidden in ("PROP --> PLAN", "Graph checkpoint = Domain Fact", "GraphRAG always wins"):
        if forbidden in views or forbidden in architecture:
            errors.append(f"architecture retains forbidden shortcut: {forbidden}")
    if 'fetch("./architecture-views.md")' not in html:
        errors.append("architecture.html must render canonical Mermaid source")
    if "../history/README.md" not in html or "../status/target-status.md" not in html:
        errors.append("architecture.html must expose new taxonomy entrypoints")
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

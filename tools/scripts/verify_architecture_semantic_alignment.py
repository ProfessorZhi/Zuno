from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCH = ROOT / "docs/architecture/architecture.md"
VIEWS = ROOT / "docs/architecture/architecture-views.md"
HTML = ROOT / "docs/architecture/architecture.html"
MODULES = ROOT / "docs/modules"


def verify() -> list[str]:
    errors: list[str] = []
    architecture = ARCH.read_text(encoding="utf-8")
    views = VIEWS.read_text(encoding="utf-8")
    html = HTML.read_text(encoding="utf-8")
    modules = {
        name: (MODULES / name).read_text(encoding="utf-8")
        for name in [
            "01-product-surface.md",
            "02-input-document-ingestion.md",
            "03-knowledge-agentic-graphrag.md",
            "04-model-gateway.md",
            "05-memory-context.md",
            "06-agent-core-planning-control.md",
            "07-capability-skill.md",
            "08-tool-runtime.md",
            "09-security.md",
            "10-observability-eval.md",
            "11-infrastructure.md",
        ]
    }

    precedence = [
        "Canonical Owner 的十一份模块 Target 文档",
        "architecture.md 跨模块集成架构",
        "architecture-views.md 说明性 Mermaid",
        "architecture.html 渲染与导航",
    ]
    last = -1
    for marker in precedence:
        pos = architecture.find(marker)
        if pos < 0:
            errors.append(f"architecture precedence missing: {marker}")
        elif pos <= last:
            errors.append(f"architecture precedence out of order: {marker}")
        last = max(last, pos)

    required_arch = [
        "TaskContract",
        "GoalVersion",
        "ExecutionContextSnapshot",
        "Controller Loop",
        "DispatchGroup",
        "BranchResultRef",
        "Join Evaluation",
        "Replan Barrier",
        "KnowledgeControlProposal",
        "CorrectiveRetrieval",
        "TelemetryEnvelopeV1",
        "accepted immutable AuditEvent",
        "UNAVAILABLE",
        "INCOMPARABLE",
        "BudgetSettlement",
    ]
    for marker in required_arch:
        if marker not in architecture:
            errors.append(f"architecture integration semantics missing: {marker}")

    required_views = [
        "TaskContract / GoalVersion",
        "Dispatch commit before Send",
        "BranchResultRef",
        "Replan Barrier + new PlanVersion",
        "KnowledgeControlProposal",
        "Agent Core ControlDecision",
        "CorrectiveRetrievalDecision",
        "TelemetryEnvelopeV1",
        "Append-only Ingest",
        "Accepted immutable AuditEvent",
        "BenchmarkComparison",
        "UNAVAILABLE",
        "INCOMPARABLE",
    ]
    for marker in required_views:
        if marker not in views:
            errors.append(f"architecture visual semantics missing: {marker}")

    forbidden_views = [
        "PROP --> PLAN",
        "Reflection / Replan Barrier] --> C[Query Normalize",
        "KnowledgeControlProposal] --> PLAN",
    ]
    for marker in forbidden_views:
        if marker in views:
            errors.append(f"architecture view retains stale control shortcut: {marker}")

    if "03-agentic-graphrag-cross-module-coordination.md" in modules["03-knowledge-agentic-graphrag.md"]:
        errors.append("Knowledge module still references retired temporary coordination document")
    if "Source Object、ParseRun、Chunk 和摄取状态" in modules["04-model-gateway.md"]:
        errors.append("Model Gateway still assigns Chunk ownership to Input")
    if "ExecutionAttempt、EffectReceipt" in modules["10-observability-eval.md"]:
        errors.append("Observability still uses retired Tool ExecutionAttempt terminology")

    for name in ["03-knowledge-agentic-graphrag.md", "05-memory-context.md", "06-agent-core-planning-control.md"]:
        content = modules[name]
        adr = content.find("已接受 ADR")
        module = content.find("本模块 Target")
        if adr < 0 or module < 0 or adr > module:
            errors.append(f"module precedence does not place accepted ADR before module contract: {name}")

    if 'fetch("./architecture-views.md")' not in html:
        errors.append("architecture.html must render the canonical Mermaid source")
    if "模块 Owner 文档是领域规范源" not in html:
        errors.append("architecture.html does not disclose module-first precedence")

    if views.count("```mermaid") != 30:
        errors.append("architecture-views.md must retain exactly 30 canonical diagrams")

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

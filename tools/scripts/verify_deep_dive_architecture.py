from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

COMMON_CASE = "审查合同 A 的责任限制条款"

DOCUMENT_REQUIREMENTS = {
    "docs/project/architecture/architecture.md": (
        "PlanVersion",
        "EvidenceRequirement",
        "PreparedToolAction",
        "ContextPackVersion",
        "EffectReconciliation",
        "Security",
        "Observability",
        "Infrastructure",
    ),
    "docs/project/modules/03-knowledge-agentic-graphrag.md": (
        "EvidenceRequirement",
        "EvidenceCandidate",
        "EvidenceLedger",
        "RetrievalRound",
        "Corrective Retrieval",
        "KnowledgeSnapshot",
    ),
    "docs/project/modules/05-memory-context.md": (
        "MemoryCandidate",
        "MemoryVersion",
        "SessionSummaryVersion",
        "ContextPackVersion",
        "StructuredObservation",
        "MemoryWriteDecision",
        "Memory Provenance",
    ),
    "docs/project/modules/06-agent-core-planning-control.md": (
        "PlanVersion",
        "StepRun",
        "ActionProposal",
        "Reflection",
        "Replan",
        "Reflexion",
        "TaskUnderstandingSnapshot",
    ),
    "docs/project/modules/08-tool-runtime.md": (
        "PreparedToolAction",
        "ToolAttempt",
        "ToolObservation",
        "ToolExecutionReceipt",
        "EffectReceipt",
        "EffectReconciliation",
        "McpCapabilitySnapshot",
    ),
    "docs/project/modules/09-security.md": (
        "SecurityApprovalDecision",
        "EffectiveSecurityEpoch",
        "PreparedToolAction",
        "McpCapabilitySnapshot",
        "Effective Memory Scope",
        "Memory Poisoning",
    ),
}


def verify() -> list[str]:
    errors: list[str] = []
    for relative_path, required_tokens in DOCUMENT_REQUIREMENTS.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing deep-dive document: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        if COMMON_CASE not in text:
            errors.append(f"{relative_path} missing unified case: {COMMON_CASE}")
        if "Target" not in text and "TARGET" not in text:
            errors.append(f"{relative_path} must retain an explicit Target boundary")
        for token in required_tokens:
            if token not in text:
                errors.append(f"{relative_path} missing deep-dive contract token: {token}")
    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("deep dive architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

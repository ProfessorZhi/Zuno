from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OLD_VERIFIER = '''RAG_PROCESS_TERMS = [
    "Query Normalize / Rewrite / Decompose",
    "Route and Profile Decision",
    "Retrieval Plan + Budget + Security Scope",
    "Vector / Dense",
    "Lexical / BM25",
    "Local Graph Search",
    "Global Community Search",
    "DRIFT / Follow-up Expansion",
    "Entity / Relation / Path / Community Expansion",
    "Graph-to-Text Source Grounding",
    "Fusion / Dedup",
    "Rerank",
    "Evidence Assembly / Compression",
    "Claim Extraction / Citation Binding",
    "Reflection / Replan Barrier",
    "basic | local | global | drift",
    "standard_rag | local_graphrag | deep_graphrag | agentic_graphrag",
]'''

NEW_VERIFIER = '''RAG_PROCESS_TERMS = [
    "Agent Core Task Analysis",
    "RetrievalNeedDecision / EvidenceRequirement",
    "KnowledgeQueryRequest + Budget + Authorized Scope",
    "Fixed KnowledgeRetrievalGraph",
    "RetrievalPlan / RetrievalRound",
    "Parallel BM25 / Vector / Graph / Structured Retrievers",
    "Normalize / Ground / Fusion / Rerank",
    "EvidenceLedger / EvidenceFrontier",
    "RetrievalQualityVerdict",
    "CorrectiveRetrievalDecision + new RetrievalRound",
    "SelectedEvidenceBundle / KnowledgeRetrievalOutcome",
    "KnowledgeControlProposal",
    "Agent Core Step Acceptance",
    "Agent Core ControlDecision",
    "Replan Barrier + new PlanVersion",
    "Interrupt or terminal control",
    "Final Synthesis / Claim and Citation Binding / Final Gate",
    "Publication / RunOutcome / BudgetSettlement / Eval",
    "basic | local | global | drift",
    "standard_rag | local_graphrag | deep_graphrag | agentic_graphrag",
]'''

OLD_TEST = '''    for term in [
        "Query Normalize / Rewrite / Decompose",
        "Route and Profile Decision",
        "Retrieval Plan + Budget + Security Scope",
        "Vector / Dense",
        "Lexical / BM25",
        "Local Graph Search",
        "Global Community Search",
        "DRIFT / Follow-up Expansion",
        "Entity / Relation / Path / Community Expansion",
        "Graph-to-Text Source Grounding",
        "Fusion / Dedup",
        "Rerank",
        "Evidence Assembly / Compression",
        "Claim Extraction / Citation Binding",
        "Reflection / Replan Barrier",
        "AgenticGraphRAGTrace",
        "RetrievalCandidateTrace",
        "GraphTraversalRecord",
        "AgentLoopObservation",
    ]:'''

NEW_TEST = '''    for term in [
        "Agent Core Task Analysis",
        "RetrievalNeedDecision / EvidenceRequirement",
        "KnowledgeQueryRequest + Budget + Authorized Scope",
        "Fixed KnowledgeRetrievalGraph",
        "RetrievalPlan / RetrievalRound",
        "Parallel BM25 / Vector / Graph / Structured Retrievers",
        "Normalize / Ground / Fusion / Rerank",
        "EvidenceLedger / EvidenceFrontier",
        "RetrievalQualityVerdict",
        "CorrectiveRetrievalDecision + new RetrievalRound",
        "SelectedEvidenceBundle / KnowledgeRetrievalOutcome",
        "KnowledgeControlProposal",
        "Agent Core Step Acceptance",
        "Agent Core ControlDecision",
        "Replan Barrier + new PlanVersion",
        "Interrupt or terminal control",
        "Final Synthesis / Claim and Citation Binding / Final Gate",
        "Publication / RunOutcome / BudgetSettlement / Eval",
        "AgenticGraphRAGTrace",
        "RetrievalCandidateTrace",
        "GraphTraversalRecord",
        "AgentLoopObservation",
    ]:'''


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected legacy assertion block not found: {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def main() -> None:
    replace_exact(
        ROOT / "tools/scripts/verify_observability_eval_target_protocols.py",
        OLD_VERIFIER,
        NEW_VERIFIER,
    )
    replace_exact(
        ROOT / "tests/repo/test_observability_eval_target_protocols.py",
        OLD_TEST,
        NEW_TEST,
    )
    Path(__file__).unlink(missing_ok=True)


if __name__ == "__main__":
    main()

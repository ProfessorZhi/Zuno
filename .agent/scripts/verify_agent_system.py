from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

CANONICAL_ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
}

MEMORY_CONTEXT_DOC = "05-memory-context.md"
AGENT_CORE_DOC = "06-agent-core-planning-control.md"

REQUIRED_PATHS = [
    "AGENTS.md",
    "README.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/architecture.md",
    "docs/architecture/architecture-views.md",
    "docs/architecture/architecture.html",
    "docs/modules/README.md",
    "docs/modules/02-input-document-ingestion.md",
    "docs/modules/03-knowledge-agentic-graphrag.md",
    f"docs/modules/{MEMORY_CONTEXT_DOC}",
    f"docs/modules/{AGENT_CORE_DOC}",
    "docs/modules/07-capability-skill.md",
    "docs/modules/10-observability-eval.md",
    "docs/status/production-readiness.md",
    "docs/decisions/README.md",
    "docs/decisions/0002-retire-compat-namespace.md",
    "docs/governance/repo-ownership-matrix.md",
    ".agent/README.md",
    ".agent/system.yaml",
    ".agent/architecture/README.md",
    ".agent/architecture/architecture.md",
    ".agent/architecture/architecture-views.md",
    ".agent/architecture/architecture.html",
    ".agent/modules/README.md",
    f".agent/modules/{MEMORY_CONTEXT_DOC}",
    f".agent/modules/{AGENT_CORE_DOC}",
    ".agent/references/README.md",
    ".agent/references/project-map.md",
    ".agent/references/task-routing.md",
    ".agent/references/workflow.md",
    ".agent/references/code-map.md",
    ".agent/references/runtime-call-chain.md",
    ".agent/references/verification-map.md",
    ".agent/references/docs-map.md",
    ".agent/references/architecture-docs-map.md",
    ".agent/references/documentation-governance.md",
    ".agent/references/architecture-update-policy.md",
    ".agent/references/diagram-inventory.md",
    ".agent/references/current-target-future-rules.md",
    ".agent/references/workflow-governance.md",
    ".agent/references/workflow-update-policy.md",
    ".agent/references/workflow-requirements.md",
    ".agent/references/workflow-change-log.md",
    ".agent/references/workflow-maintenance-checklist.md",
    ".agent/templates/README.md",
    ".agent/templates/architecture-doc-template.md",
    ".agent/templates/mermaid-diagram-template.md",
    ".agent/templates/architecture-change-note-template.md",
    ".agent/templates/verification-report-template.md",
    ".agent/templates/workflow-change-note-template.md",
    ".agent/templates/phase-plan.md",
    ".agent/templates/phase-closure-report.md",
    ".agent/templates/requirement-intake.md",
    ".agent/templates/readonly-audit-prompt.md",
    ".agent/templates/goal-mode-prompt.md",
    ".agent/programs/README.md",
    ".agent/programs/current.md",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/closure-checklist.md",
    ".agent/programs/queued-programs/README.md",
    ".agent/programs/queued-programs/PROGRAM01_real-unified-runtime-cutover.md",
    "tools/scripts/verify_docs_entrypoints.py",
    "tools/scripts/verify_repo_structure.py",
    "tools/scripts/verify_current_program.py",
    "tools/scripts/verify_memory_context_target_protocols.py",
    "tools/scripts/verify_agent_core_target_protocols.py",
    "tests/repo/test_memory_context_target_protocols.py",
    ".github/workflows/memory-context-target-docs.yml",
]

FORBIDDEN_ACTIVE_PATHS = [
    "docs/architecture/production-readiness.md",
    "docs/architecture/document-ingestion-foundation.md",
    "docs/architecture/agent-core-runtime.md",
    "docs/architecture/memory-and-context.md",
    "docs/architecture/capability-and-skill-layer.md",
    "docs/architecture/agentic-retrieval-planner.md",
    "docs/architecture/eval-observability-and-cost.md",
    "docs/architecture/input-layer-and-document-processing.md",
    "docs/architecture/knowledge-space-product-configuration.md",
    "docs/architecture/repo-ownership-matrix.md",
    "docs/architecture/decisions",
    ".agent/architecture/agent-core-runtime.md",
    ".agent/architecture/near-term",
    ".agent/architecture/future",
    ".agent/architecture/decisions",
    ".agent/plans",
]

ENTRYPOINT_FILES = [
    "README.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/modules/README.md",
    ".agent/README.md",
    ".agent/architecture/README.md",
    ".agent/modules/README.md",
    ".agent/references/docs-map.md",
    ".agent/references/architecture-docs-map.md",
]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def verify_required_paths() -> list[str]:
    return [
        f"missing required Agent System path: {path}"
        for path in REQUIRED_PATHS
        if not (REPO_ROOT / path).exists()
    ]


def verify_architecture_directory_contract() -> list[str]:
    errors: list[str] = []
    for relative_root in ["docs/architecture", ".agent/architecture"]:
        root = REPO_ROOT / relative_root
        files = {path.name for path in root.iterdir() if path.is_file()}
        directories = [path.name for path in root.iterdir() if path.is_dir()]
        if files != CANONICAL_ARCHITECTURE_FILES:
            errors.append(
                f"{relative_root} must contain only {sorted(CANONICAL_ARCHITECTURE_FILES)}; "
                f"got {sorted(files)}"
            )
        if directories:
            errors.append(f"{relative_root} must not contain subdirectories: {sorted(directories)}")
    return errors


def verify_mirrors() -> list[str]:
    pairs = [
        ("docs/architecture/architecture.md", ".agent/architecture/architecture.md"),
        ("docs/architecture/architecture-views.md", ".agent/architecture/architecture-views.md"),
        ("docs/architecture/architecture.html", ".agent/architecture/architecture.html"),
        (f"docs/modules/{MEMORY_CONTEXT_DOC}", f".agent/modules/{MEMORY_CONTEXT_DOC}"),
        (f"docs/modules/{AGENT_CORE_DOC}", f".agent/modules/{AGENT_CORE_DOC}"),
    ]
    return [
        f"mirror mismatch: {mirror} must match {formal}"
        for formal, mirror in pairs
        if (REPO_ROOT / formal).read_bytes() != (REPO_ROOT / mirror).read_bytes()
    ]


def verify_entrypoint_boundaries() -> list[str]:
    errors: list[str] = []
    for relative_path in ENTRYPOINT_FILES:
        content = _read(relative_path)
        for forbidden in FORBIDDEN_ACTIVE_PATHS:
            if forbidden in content:
                errors.append(f"{relative_path} references migrated or forbidden path: {forbidden}")

    required_phrases = {
        "docs/README.md": [
            "./architecture/architecture.md",
            "./modules/README.md",
            "./status/production-readiness.md",
        ],
        "docs/architecture/README.md": [
            "docs/modules/",
            "docs/status/",
            "docs/decisions/",
            "docs/governance/",
        ],
        "docs/modules/README.md": [
            MEMORY_CONTEXT_DOC,
            AGENT_CORE_DOC,
            "docs/status/production-readiness.md",
            "verify_memory_context_target_protocols.py",
            "verify_agent_core_target_protocols.py",
        ],
        ".agent/modules/README.md": [
            MEMORY_CONTEXT_DOC,
            AGENT_CORE_DOC,
            "verify_memory_context_target_protocols.py",
            "verify_agent_core_target_protocols.py",
        ],
        ".agent/README.md": [".agent/architecture/", ".agent/modules/"],
    }
    for relative_path, phrases in required_phrases.items():
        content = _read(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing phrase: {phrase}")
    return errors


def verify_module_contracts() -> list[str]:
    required = {
        "docs/modules/02-input-document-ingestion.md": [
            "SourceObject",
            "CanonicalDocumentIR",
            "IndexableDocumentSnapshot",
        ],
        "docs/modules/03-knowledge-agentic-graphrag.md": [
            "EvidenceLedger",
            "RetrievalQualityVerdict",
            "KnowledgeSnapshot",
        ],
        f"docs/modules/{MEMORY_CONTEXT_DOC}": [
            "Working Memory",
            "Session Memory",
            "Long-term Memory",
            "Episodic Memory",
            "Semantic Memory",
            "Procedural Memory",
            "C0 Deterministic Lossless",
            "C3 Reasoning Consolidation",
            "ContextPack read view, not another memory layer",
            "ARCH-MEM-060",
        ],
        f"docs/modules/{AGENT_CORE_DOC}": [
            "Single Controller Agent Runtime",
            "Plan DAG",
            "TaskContract",
            "pending_interrupt_refs",
            "WAITING_CONDITION",
            "ActionProposal",
            "ActionExecutionBinding",
            "PreparedToolAction",
            "RecoveryWatermark",
            "ResultValidity",
            "RunOrphanReconciler",
            "prepare_publication",
            "EffectivePolicySnapshot",
            "ActionOutcome",
            "Requirement Enforcement Matrix",
            "LangGraph Adapter Contract",
            "ModelCapabilityProfile",
            "StepFeasibilityDecision",
            "RC-AG-080",
            "ARCH-AGENT-080",
            "PostgreSQL",
        ],
        "docs/modules/07-capability-skill.md": [
            "Function Calling",
            "SkillMetadata",
            "ToolRequest",
        ],
        "docs/modules/10-observability-eval.md": ["Measurement Semantics", "agent_run"],
    }

    errors: list[str] = []
    for relative_path, phrases in required.items():
        content = _read(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing module contract phrase: {phrase}")
    return errors


def verify_module_routing() -> list[str]:
    errors: list[str] = []
    agents = _read("AGENTS.md")
    system = _read(".agent/system.yaml")

    if MEMORY_CONTEXT_DOC not in agents and "Memory 模块文档" not in agents:
        errors.append("AGENTS.md does not route to the Memory & Context module document")
    if MEMORY_CONTEXT_DOC not in system:
        errors.append(f".agent/system.yaml does not route to module document: {MEMORY_CONTEXT_DOC}")

    for relative_path, content in [("AGENTS.md", agents), (".agent/system.yaml", system)]:
        if AGENT_CORE_DOC not in content:
            errors.append(f"{relative_path} does not route to module document: {AGENT_CORE_DOC}")
        if "verify_agent_core_target_protocols.py" not in content:
            errors.append(f"{relative_path} does not route to Agent Core verifier")

    if "Single GeneralAgent" in system:
        errors.append(".agent/system.yaml uses obsolete Single GeneralAgent terminology")
    if "Single Controller Agent Runtime" not in system:
        errors.append(".agent/system.yaml must declare Single Controller Agent Runtime")
    return errors


def verify_no_tracked_local_workspace() -> list[str]:
    errors: list[str] = []
    for relative_path in [
        ".agent/local",
        ".agent/local/notes",
        ".agent/local/tmp",
        ".agent/local/logs",
        ".agent/local/secrets",
    ]:
        path = REPO_ROOT / relative_path
        if path.exists() and any(path.iterdir()):
            errors.append(f"local-only Agent directory must not contain tracked files: {relative_path}")
    return errors


def main() -> int:
    checks = [
        verify_required_paths,
        verify_architecture_directory_contract,
        verify_mirrors,
        verify_entrypoint_boundaries,
        verify_module_contracts,
        verify_module_routing,
        verify_no_tracked_local_workspace,
    ]
    errors: list[str] = []
    for check in checks:
        errors.extend(check())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("agent system verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

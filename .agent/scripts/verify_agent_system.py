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

MODULE_DOCS = [
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

REQUIRED_PATHS = [
    "AGENTS.md",
    "README.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/architecture.md",
    "docs/architecture/architecture-views.md",
    "docs/architecture/architecture.html",
    "docs/modules/README.md",
    "docs/status/production-readiness.md",
    "docs/decisions/README.md",
    "docs/governance/repo-ownership-matrix.md",
    ".agent/README.md",
    ".agent/system.yaml",
    ".agent/architecture/README.md",
    ".agent/architecture/architecture.md",
    ".agent/architecture/architecture-views.md",
    ".agent/architecture/architecture.html",
    ".agent/modules/README.md",
    ".agent/references/docs-map.md",
    ".agent/references/task-routing.md",
    ".agent/references/workflow.md",
    ".agent/references/code-map.md",
    ".agent/references/verification-map.md",
    ".agent/programs/README.md",
    *[f"docs/modules/{name}" for name in MODULE_DOCS],
    *[f".agent/modules/{name}" for name in MODULE_DOCS],
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
    ".agent/architecture/agent-core-runtime.md",
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
                f"{relative_root} must contain only {sorted(CANONICAL_ARCHITECTURE_FILES)}; got {sorted(files)}"
            )
        if directories:
            errors.append(f"{relative_root} must not contain subdirectories: {sorted(directories)}")
    return errors


def verify_mirrors() -> list[str]:
    errors: list[str] = []
    pairs = [
        ("docs/architecture/architecture.md", ".agent/architecture/architecture.md"),
        ("docs/architecture/architecture-views.md", ".agent/architecture/architecture-views.md"),
        ("docs/architecture/architecture.html", ".agent/architecture/architecture.html"),
        *[(f"docs/modules/{name}", f".agent/modules/{name}") for name in MODULE_DOCS],
    ]
    for formal, mirror in pairs:
        if (REPO_ROOT / formal).read_bytes() != (REPO_ROOT / mirror).read_bytes():
            errors.append(f"mirror mismatch: {mirror} must match {formal}")
    return errors


def verify_entrypoints() -> list[str]:
    errors: list[str] = []
    entrypoint_files = [
        "AGENTS.md",
        "docs/README.md",
        "docs/architecture/README.md",
        "docs/modules/README.md",
        ".agent/README.md",
        ".agent/architecture/README.md",
        ".agent/modules/README.md",
        ".agent/references/docs-map.md",
        ".agent/system.yaml",
    ]
    for relative_path in entrypoint_files:
        content = _read(relative_path)
        for forbidden in FORBIDDEN_ACTIVE_PATHS:
            if forbidden in content:
                errors.append(f"{relative_path} references migrated or forbidden path: {forbidden}")

    for name in MODULE_DOCS:
        for relative_path in [
            "docs/modules/README.md",
            ".agent/modules/README.md",
            ".agent/references/docs-map.md",
            ".agent/system.yaml",
        ]:
            if name not in _read(relative_path):
                errors.append(f"{relative_path} does not route module document: {name}")

    agents = _read("AGENTS.md")
    for phrase in [
        "Single Controller",
        "docs/modules/",
        "docs/modules/06-agent-core-planning-control.md",
        "python tools/scripts/verify_agent_core_target_protocols.py",
    ]:
        if phrase not in agents:
            errors.append(f"AGENTS.md missing architecture route: {phrase}")

    system = _read(".agent/system.yaml")
    for phrase in [
        "Single Controller Agent Runtime",
        'formal: "docs/modules/04-model-gateway.md"',
        'mirror: ".agent/modules/04-model-gateway.md"',
        'verifier: "python tools/scripts/verify_model_gateway_target_protocols.py"',
        'formal: "docs/modules/08-tool-runtime.md"',
    ]:
        if phrase not in system:
            errors.append(f".agent/system.yaml missing architecture route: {phrase}")

    return errors


def verify_module_contracts() -> list[str]:
    required = {
        "01-product-surface.md": ["Product Surface", "AvailableAction", "ProductProjection"],
        "02-input-document-ingestion.md": ["SourceObject", "CanonicalDocumentIR", "IndexableDocumentSnapshot"],
        "03-knowledge-agentic-graphrag.md": ["EvidenceLedger", "RetrievalQualityVerdict", "KnowledgeSnapshot"],
        "04-model-gateway.md": ["ModelRoutingDecision", "ModelCallAttempt", "ModelUsageReceiptV1"],
        "05-memory-context.md": ["ContextPack", "MemoryCandidate", "MemoryVersion"],
        "06-agent-core-planning-control.md": ["Single Controller Agent Runtime", "Plan DAG", "ActionProposal"],
        "07-capability-skill.md": ["CapabilityDefinition", "SkillVersion", "ToolDefinitionRef"],
        "08-tool-runtime.md": ["PreparedToolAction", "ToolAttempt", "EffectReconciliation"],
        "09-security.md": ["EffectiveSecurityEpoch", "Approval", "InformationFlowDecision"],
        "10-observability-eval.md": ["MeasurementStatus", "ReleaseGateEvaluation", "AuditEvent"],
        "11-infrastructure.md": ["PostgreSQL", "RabbitMQ", "FencingToken"],
    }
    errors: list[str] = []
    for name, phrases in required.items():
        content = _read(f"docs/modules/{name}")
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"docs/modules/{name} missing module contract phrase: {phrase}")
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
        verify_entrypoints,
        verify_module_contracts,
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

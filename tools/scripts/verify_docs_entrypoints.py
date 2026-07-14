from __future__ import annotations

import importlib.util
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

RETIRED_MODULE_DOCS = [
    "04-model-gateway-contract-freeze.md",
    "04-model-gateway-operations-conformance.md",
    "10-observability-eval-rag-agent-evaluation.md",
    "11-infrastructure-data-services.md",
    "11-infrastructure-consistency-lifecycle.md",
]

REQUIRED_FRONT_PATHS = [
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
    ".agent/architecture/README.md",
    ".agent/architecture/architecture.md",
    ".agent/architecture/architecture-views.md",
    ".agent/architecture/architecture.html",
    ".agent/modules/README.md",
    ".agent/references/docs-map.md",
    ".agent/system.yaml",
    *[f"docs/modules/{name}" for name in MODULE_DOCS],
    *[f".agent/modules/{name}" for name in MODULE_DOCS],
]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _load_renderer():
    path = REPO_ROOT / "tools/agent/render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load tools/agent/render_architecture.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify() -> list[str]:
    errors: list[str] = []

    for relative_path in REQUIRED_FRONT_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing documentation entrypoint: {relative_path}")

    for root_name in ["docs/architecture", ".agent/architecture"]:
        root = REPO_ROOT / root_name
        files = {path.name for path in root.iterdir() if path.is_file()}
        directories = [path.name for path in root.iterdir() if path.is_dir()]
        if files != CANONICAL_ARCHITECTURE_FILES:
            errors.append(
                f"{root_name} must contain only {sorted(CANONICAL_ARCHITECTURE_FILES)}; got {sorted(files)}"
            )
        if directories:
            errors.append(f"{root_name} must not contain subdirectories: {sorted(directories)}")

    formal_modules = sorted(path.name for path in (REPO_ROOT / "docs/modules").glob("[0-9][0-9]-*.md"))
    mirror_modules = sorted(path.name for path in (REPO_ROOT / ".agent/modules").glob("[0-9][0-9]-*.md"))
    if formal_modules != MODULE_DOCS:
        errors.append(f"formal module document set mismatch: {formal_modules}")
    if mirror_modules != MODULE_DOCS:
        errors.append(f"Agent module mirror set mismatch: {mirror_modules}")

    for name in MODULE_DOCS:
        formal = REPO_ROOT / "docs/modules" / name
        mirror = REPO_ROOT / ".agent/modules" / name
        if formal.exists() and mirror.exists() and formal.read_bytes() != mirror.read_bytes():
            errors.append(f"module mirror mismatch: {name}")

    for name in RETIRED_MODULE_DOCS:
        if (REPO_ROOT / "docs/modules" / name).exists() or (REPO_ROOT / ".agent/modules" / name).exists():
            errors.append(f"retired split module document remains active: {name}")

    docs_index = _read("docs/modules/README.md")
    agent_index = _read(".agent/modules/README.md")
    docs_map = _read(".agent/references/docs-map.md")
    system = _read(".agent/system.yaml")
    architecture_index = _read("docs/architecture/README.md")
    agent_architecture_index = _read(".agent/architecture/README.md")

    for name in MODULE_DOCS:
        if name not in docs_index:
            errors.append(f"docs/modules/README.md does not route {name}")
        if name not in agent_index:
            errors.append(f".agent/modules/README.md does not route {name}")
        if name not in docs_map:
            errors.append(f".agent/references/docs-map.md does not route {name}")
        if name not in system:
            errors.append(f".agent/system.yaml does not route {name}")

    for phrase in ["docs/modules/", "docs/status/", "docs/decisions/", "docs/governance/"]:
        if phrase not in architecture_index:
            errors.append(f"docs/architecture/README.md missing phrase: {phrase}")
    for phrase in [".agent/modules/06-agent-core-planning-control.md", "docs/status/production-readiness.md"]:
        if phrase not in agent_architecture_index:
            errors.append(f".agent/architecture/README.md missing phrase: {phrase}")

    renderer = _load_renderer()
    design = _read("docs/architecture/architecture.md")
    views = _read("docs/architecture/architecture-views.md")
    html = _read("docs/architecture/architecture.html")
    errors.extend(renderer.validate_design(design))
    errors.extend(renderer.validate_source(views))
    errors.extend(renderer.validate_html(html))

    for formal, mirror in [
        ("docs/architecture/architecture.md", ".agent/architecture/architecture.md"),
        ("docs/architecture/architecture-views.md", ".agent/architecture/architecture-views.md"),
        ("docs/architecture/architecture.html", ".agent/architecture/architecture.html"),
    ]:
        if (REPO_ROOT / formal).read_bytes() != (REPO_ROOT / mirror).read_bytes():
            errors.append(f"architecture mirror mismatch: {mirror}")

    for phrase in [
        "十一模块",
        "Single Controller",
        "AgentRunGraph",
        "Plan DAG",
        "StepExecutionGraph",
        "CrossModuleEnvelope",
        "PreparedToolAction",
        "EffectReconciliation",
        "EvidenceLedger",
        "ContextPackVersion",
    ]:
        if phrase not in design:
            errors.append(f"docs/architecture/architecture.md missing integration phrase: {phrase}")

    for phrase in [
        "./architecture.md",
        "../modules/README.md",
        "../status/production-readiness.md",
        "./architecture-views.md",
        "mermaid@11",
        "diagram-dialog",
        "Mermaid source",
    ]:
        if phrase not in html:
            errors.append(f"docs/architecture/architecture.html missing marker: {phrase}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("documentation entrypoint verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

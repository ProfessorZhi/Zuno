from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ARCHITECTURE_VIEW_CONTRACT = [
    "Logical View (4+1)",
    "Development View (4+1)",
    "Process View (4+1)",
    "Physical View (4+1)",
    "Scenarios View (4+1)",
    "Module View (Views & Beyond)",
    "Component-and-Connector View (Views & Beyond)",
    "Data View (Views & Beyond)",
    "Quality View (Views & Beyond)",
    "Agentic GraphRAG Evidence and Agent Loop (Zuno)",
]

CANONICAL_ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
}

REQUIRED_MODULE_DOCS = {
    "README.md",
    "02-input-document-ingestion.md",
    "03-knowledge-agentic-graphrag.md",
    "05-memory-context.md",
    "06-agent-core-planning-control.md",
    "07-capability-skill.md",
    "10-observability-eval.md",
}

REQUIRED_FRONT_PATHS = [
    "README.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/architecture.md",
    "docs/architecture/architecture-views.md",
    "docs/architecture/architecture.html",
    "docs/modules/README.md",
    "docs/modules/06-agent-core-planning-control.md",
    "docs/status/production-readiness.md",
    "docs/decisions/README.md",
    "docs/governance/repo-ownership-matrix.md",
    ".agent/architecture/README.md",
    ".agent/architecture/architecture.md",
    ".agent/architecture/architecture-views.md",
    ".agent/architecture/architecture.html",
    ".agent/modules/README.md",
    ".agent/modules/06-agent-core-planning-control.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/README.md",
]

ARCHIVED_ARCHITECTURE_SPLIT_DOCS = [
    "current-architecture.md",
    "target-architecture.md",
    "roadmap.md",
    "product-scenario-enterprise-kb.md",
    "security-and-sandbox.md",
    "deliverables.md",
]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _load_render_architecture_module():
    module_path = REPO_ROOT / "tools" / "agent" / "render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load tools/agent/render_architecture.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify_front_path_shape() -> list[str]:
    errors: list[str] = []

    for relative_path in REQUIRED_FRONT_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing documentation entrypoint: {relative_path}")

    docs_architecture_files = {
        path.name
        for path in (REPO_ROOT / "docs" / "architecture").iterdir()
        if path.is_file()
    }
    if docs_architecture_files != CANONICAL_ARCHITECTURE_FILES:
        errors.append(
            "docs/architecture must contain only the four canonical files: "
            f"expected {sorted(CANONICAL_ARCHITECTURE_FILES)}, "
            f"got {sorted(docs_architecture_files)}"
        )

    docs_architecture_dirs = [
        path.name
        for path in (REPO_ROOT / "docs" / "architecture").iterdir()
        if path.is_dir()
    ]
    if docs_architecture_dirs:
        errors.append(
            "docs/architecture must not contain subdirectories: "
            f"{sorted(docs_architecture_dirs)}"
        )

    agent_architecture_files = {
        path.name
        for path in (REPO_ROOT / ".agent" / "architecture").iterdir()
        if path.is_file()
    }
    if agent_architecture_files != CANONICAL_ARCHITECTURE_FILES:
        errors.append(
            ".agent/architecture must contain only the four canonical files: "
            f"expected {sorted(CANONICAL_ARCHITECTURE_FILES)}, "
            f"got {sorted(agent_architecture_files)}"
        )

    agent_architecture_dirs = [
        path.name
        for path in (REPO_ROOT / ".agent" / "architecture").iterdir()
        if path.is_dir()
    ]
    if agent_architecture_dirs:
        errors.append(
            ".agent/architecture must not contain subdirectories: "
            f"{sorted(agent_architecture_dirs)}"
        )

    module_files = {
        path.name
        for path in (REPO_ROOT / "docs" / "modules").iterdir()
        if path.is_file()
    }
    missing_modules = REQUIRED_MODULE_DOCS - module_files
    if missing_modules:
        errors.append(f"docs/modules missing required module docs: {sorted(missing_modules)}")

    for name in ARCHIVED_ARCHITECTURE_SPLIT_DOCS:
        if (REPO_ROOT / "docs" / "architecture" / name).exists():
            errors.append(f"split architecture doc must stay archived: docs/architecture/{name}")
        archived = (
            REPO_ROOT
            / "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture"
            / name
        )
        if not archived.exists():
            errors.append(f"missing archived architecture split doc: {name}")

    return errors


def verify_entrypoint_text() -> list[str]:
    errors: list[str] = []

    contents = {
        "README.md": _read("README.md"),
        "docs/README.md": _read("docs/README.md"),
        "docs/architecture/README.md": _read("docs/architecture/README.md"),
        "docs/modules/README.md": _read("docs/modules/README.md"),
        ".agent/architecture/README.md": _read(".agent/architecture/README.md"),
        ".agent/modules/README.md": _read(".agent/modules/README.md"),
    }

    expected_by_file = {
        "docs/README.md": [
            "./architecture/architecture.md",
            "./architecture/architecture.html",
            "./modules/README.md",
            "./status/production-readiness.md",
            "./decisions/README.md",
            "./governance/repo-ownership-matrix.md",
        ],
        "docs/architecture/README.md": [
            "README.md",
            "architecture.md",
            "architecture-views.md",
            "architecture.html",
            "docs/modules/",
            "docs/status/",
            "docs/decisions/",
            "docs/governance/",
        ],
        "docs/modules/README.md": [
            "02-input-document-ingestion.md",
            "03-knowledge-agentic-graphrag.md",
            "05-memory-context.md",
            "06-agent-core-planning-control.md",
            "07-capability-skill.md",
            "10-observability-eval.md",
            "docs/status/production-readiness.md",
        ],
        ".agent/architecture/README.md": [
            ".agent/modules/06-agent-core-planning-control.md",
            "docs/status/production-readiness.md",
        ],
        ".agent/modules/README.md": [
            ".agent/modules/06-agent-core-planning-control.md",
            "docs/modules/06-agent-core-planning-control.md",
        ],
    }

    for path, phrases in expected_by_file.items():
        for phrase in phrases:
            if phrase not in contents[path]:
                errors.append(f"{path} missing phrase: {phrase}")

    architecture = _read("docs/architecture/architecture.md")
    for phrase in [
        "Zuno Target Architecture Atlas",
        "项目定位与架构目标",
        "十一逻辑模块",
        "六个物理运行域",
        "Single Controller Agent Runtime",
        "AgentRunGraph",
        "Plan DAG",
        "StepExecutionGraph",
        "TaskContract",
        "FinalCandidate",
        "Publication",
        "EvidenceLedger",
        "docs/status/production-readiness.md",
    ]:
        if phrase not in architecture:
            errors.append(f"docs/architecture/architecture.md missing phrase: {phrase}")

    production = _read("docs/status/production-readiness.md")
    for phrase in [
        "Short-term Closure Gap",
        "Measurement Blocked",
        "Future Optional",
        "EvidenceLedger",
        "Agent run trace 持久化并可查看",
    ]:
        if phrase not in production:
            errors.append(f"docs/status/production-readiness.md missing phrase: {phrase}")

    agent_core = _read("docs/modules/06-agent-core-planning-control.md")
    for phrase in [
        "Single Controller Agent Runtime",
        "Plan DAG",
        "TaskContract",
        "pending_interrupt_refs",
        "prepare_publication",
        "PostgreSQL",
    ]:
        if phrase not in agent_core:
            errors.append(f"Agent Core module doc missing phrase: {phrase}")

    return errors


def verify_architecture_view_contract() -> list[str]:
    errors: list[str] = []
    module = _load_render_architecture_module()

    if module.EXPECTED_VIEWS != ARCHITECTURE_VIEW_CONTRACT:
        errors.append(
            "render_architecture.EXPECTED_VIEWS drifted: "
            f"expected {ARCHITECTURE_VIEW_CONTRACT}, got {module.EXPECTED_VIEWS}"
        )

    architecture = _read("docs/architecture/architecture.md")
    views = _read("docs/architecture/architecture-views.md")
    html = _read("docs/architecture/architecture.html")

    errors.extend(module.validate_design(architecture))
    errors.extend(module.validate_source(views))
    errors.extend(module.validate_html(html))

    if architecture.count("```mermaid") > 8:
        errors.append("architecture.md must stay text-first; detailed diagrams belong in architecture-views.md")
    if views.count("```mermaid") < 30:
        errors.append("architecture-views.md must contain at least 30 Mermaid diagrams")

    for title in ARCHITECTURE_VIEW_CONTRACT:
        section = module._section(views, title)
        if "#### Overall" not in section:
            errors.append(f"architecture-views.md missing Overall diagram: {title}")
        if section.count("#### Local") < 2:
            errors.append(f"architecture-views.md needs two Local diagrams: {title}")
        if title not in html:
            errors.append(f"architecture.html missing canonical view title: {title}")

    if "mermaid@11" not in html or 'className = "mermaid"' not in html:
        errors.append("architecture.html must use the native Mermaid v11 browser runtime")
    if "offline-svg" in html or "offline-diagram" in html:
        errors.append("architecture.html must not use the retired simplified SVG renderer")
    if "diagram-dialog" not in html or "Mermaid source" not in html:
        errors.append("architecture.html must preserve fullscreen and source disclosure")
    if 'fetch("/docs/architecture/architecture-views.md"' not in html:
        errors.append("architecture.html must load the dedicated Mermaid source")

    return errors


def verify_architecture_mirrors() -> list[str]:
    errors: list[str] = []

    pairs = [
        ("docs/architecture/architecture.md", ".agent/architecture/architecture.md"),
        ("docs/architecture/architecture-views.md", ".agent/architecture/architecture-views.md"),
        ("docs/architecture/architecture.html", ".agent/architecture/architecture.html"),
        (
            "docs/modules/06-agent-core-planning-control.md",
            ".agent/modules/06-agent-core-planning-control.md",
        ),
        (
        ),
        (
        ),
    ]

    for formal, mirror in pairs:
        if _read(formal) != _read(mirror):
            errors.append(f"mirror mismatch: {mirror} must match {formal}")

    return errors


def verify_no_retired_front_path_links() -> list[str]:
    errors: list[str] = []
    files = [
        "README.md",
        "docs/README.md",
        "docs/architecture/README.md",
        "docs/modules/README.md",
        "AGENTS.md",
        ".agent/README.md",
        ".agent/architecture/README.md",
        ".agent/modules/README.md",
    ]

    forbidden = [
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
        "docs/architecture/decisions/",
        ".agent/architecture/agent-core-runtime.md",
        ".agent/architecture/near-term/",
        ".agent/architecture/future/",
        ".agent/architecture/decisions/",
        "docs/architecture/phases/",
        "docs/architecture/plans/",
        "docs/architecture/programs/",
    ]

    for relative_path in files:
        content = _read(relative_path)
        for phrase in forbidden:
            if phrase in content:
                errors.append(f"{relative_path} contains retired front-path text: {phrase}")

    return errors


def main() -> int:
    checks = [
        verify_front_path_shape,
        verify_entrypoint_text,
        verify_architecture_view_contract,
        verify_architecture_mirrors,
        verify_no_retired_front_path_links,
    ]

    errors: list[str] = []
    for check in checks:
        errors.extend(check())

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("documentation entrypoint verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

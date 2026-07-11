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

ACTIVE_DOCS_ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "production-readiness.md",
    "document-ingestion-foundation.md",
    "agent-core-runtime.md",
    "memory-and-context.md",
    "capability-and-skill-layer.md",
    "agentic-retrieval-planner.md",
    "eval-observability-and-cost.md",
    "input-layer-and-document-processing.md",
    "knowledge-space-product-configuration.md",
    "architecture.html",
    "repo-ownership-matrix.md",
}

ACTIVE_AGENT_ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture.html"}

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
    required = [
        "README.md",
        "docs/README.md",
        "docs/architecture/README.md",
        "docs/architecture/architecture.md",
        "docs/architecture/architecture-views.md",
        "docs/architecture/architecture.html",
        "docs/architecture/production-readiness.md",
        ".agent/architecture/README.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "docs/history/architecture-surface-cleanup-2026-06-30/README.md",
    ]
    for relative_path in required:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing documentation entrypoint: {relative_path}")

    docs_files = {
        path.name for path in (REPO_ROOT / "docs" / "architecture").iterdir() if path.is_file()
    }
    if docs_files != ACTIVE_DOCS_ARCHITECTURE_FILES:
        errors.append(
            "docs/architecture files changed unexpectedly: "
            f"expected {sorted(ACTIVE_DOCS_ARCHITECTURE_FILES)}, got {sorted(docs_files)}"
        )

    agent_files = {
        path.name for path in (REPO_ROOT / ".agent" / "architecture").iterdir() if path.is_file()
    }
    if agent_files != ACTIVE_AGENT_ARCHITECTURE_FILES:
        errors.append(
            ".agent/architecture files changed unexpectedly: "
            f"expected {sorted(ACTIVE_AGENT_ARCHITECTURE_FILES)}, got {sorted(agent_files)}"
        )

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
    readme = _read("README.md")
    docs_index = _read("docs/README.md")
    architecture_index = _read("docs/architecture/README.md")
    architecture = _read("docs/architecture/architecture.md")
    views = _read("docs/architecture/architecture-views.md")
    production = _read("docs/architecture/production-readiness.md")

    expected_by_file = {
        "README.md": [
            "Lean Complete Agentic GraphRAG Product",
            "./docs/architecture/architecture.md",
            "./docs/architecture/architecture.html",
            "implementation available",
            "measurement blocked",
            "quality not yet proven",
        ],
        "docs/README.md": [
            "Zuno 文档入口",
            "./architecture/architecture.md",
            "./architecture/architecture.html",
            "./architecture/production-readiness.md",
        ],
        "docs/architecture/README.md": [
            "架构文档",
            "architecture.md",
            "architecture-views.md",
            "architecture.html",
            "production-readiness.md",
            "python tools/agent/render_architecture.py --write",
        ],
    }
    contents = {
        "README.md": readme,
        "docs/README.md": docs_index,
        "docs/architecture/README.md": architecture_index,
    }
    for path, phrases in expected_by_file.items():
        for phrase in phrases:
            if phrase not in contents[path]:
                errors.append(f"{path} missing phrase: {phrase}")

    architecture_phrases = [
        "Zuno Target Architecture Atlas",
        "Text-first Design Document",
        "轻量实现，成熟设计",
        "十一逻辑能力模块",
        "六个物理运行域",
        "Agent Core / Planning & Control",
        "TaskQueuePort",
        "RabbitMQAdapter",
        "LangSmithTraceSink",
        "RuntimeRequest",
        "ModelCallRequest",
        "ContextPack",
        "RetrievalPlan",
        "EvidenceBundle",
        "ToolCallIntent",
        "NormalizedToolObservation",
        "GroundedAnswer",
        "EvidenceLedger",
        "implementation available",
        "measurement blocked",
        "quality not yet proven",
    ]
    for phrase in architecture_phrases:
        if phrase not in architecture:
            errors.append(f"docs/architecture/architecture.md missing phrase: {phrase}")

    view_phrases = [
        "Zuno Architecture Visual Atlas Source",
        "4+1 View Model",
        "Views & Beyond",
        "Zuno Product Core",
        "RuntimeRequest",
        "ModelCallRequest",
        "ContextPack",
        "RetrievalPlan",
        "EvidenceBundle",
        "ToolCallIntent",
        "NormalizedToolObservation",
        "GroundedAnswer",
        "EvidenceLedger",
        "TaskQueuePort",
        "RabbitMQ",
        "LangSmith",
    ]
    for phrase in view_phrases:
        if phrase not in views:
            errors.append(f"docs/architecture/architecture-views.md missing phrase: {phrase}")

    production_phrases = [
        "Short-term Closure Gap",
        "Measurement Blocked",
        "Future Optional",
        "EvidenceLedger",
        "Agent run trace 持久化并可查看",
    ]
    for phrase in production_phrases:
        if phrase not in production:
            errors.append(f"docs/architecture/production-readiness.md missing phrase: {phrase}")
    return errors


def verify_front_path_summary_boundaries() -> list[str]:
    errors: list[str] = []
    summary_paths = [
        "README.md",
        "docs/README.md",
        "docs/architecture/README.md",
        ".agent/architecture/README.md",
    ]
    forbidden = [
        "Kafka / RabbitMQ 集群",
        "Kubernetes",
        "Firecracker 沙箱",
        "Production Scale Target",
        "V&B Logical View",
    ]
    for relative_path in summary_paths:
        content = _read(relative_path)
        if "production-readiness.md" not in content:
            errors.append(f"{relative_path} must link production-readiness.md")
        for phrase in forbidden:
            if phrase in content:
                errors.append(f"{relative_path} contains over-scoped or retired phrase: {phrase}")
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
    docs_md = _read("docs/architecture/architecture.md")
    agent_md = _read(".agent/architecture/architecture.md")
    docs_html = _read("docs/architecture/architecture.html")
    agent_html = _read(".agent/architecture/architecture.html")
    if docs_md != agent_md:
        errors.append(".agent/architecture/architecture.md must match docs/architecture/architecture.md")
    if docs_html != agent_html:
        errors.append(".agent/architecture/architecture.html must match docs/architecture/architecture.html")
    return errors


def verify_docs_map_has_unique_architecture_source_roles() -> list[str]:
    errors: list[str] = []
    content = _read(".agent/references/docs-map.md")
    formal_entries = content.split("正式人类入口：", 1)[1].split("Agent 工作流入口：", 1)[0]
    if formal_entries.count("`docs/architecture/architecture.md`") != 1:
        errors.append("docs-map must list architecture.md exactly once in formal entries")
    for phrase in [
        "`docs/architecture/architecture-views.md`",
        "`docs/architecture/architecture.html`",
        "`docs/architecture/production-readiness.md`",
        "Lean Complete Agentic GraphRAG Product",
    ]:
        if phrase not in content:
            errors.append(f"docs-map missing phrase: {phrase}")
    return errors


def verify_no_retired_front_path_links() -> list[str]:
    errors: list[str] = []
    files = [
        "README.md",
        "docs/README.md",
        "docs/architecture/README.md",
        "AGENTS.md",
        ".agent/README.md",
        ".agent/architecture/README.md",
    ]
    forbidden = [
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/architecture/deliverables.md",
        "docs/architecture/overall-architecture.md",
        ".agent/architecture/overall-architecture.md",
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
        verify_front_path_summary_boundaries,
        verify_architecture_view_contract,
        verify_architecture_mirrors,
        verify_docs_map_has_unique_architecture_source_roles,
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

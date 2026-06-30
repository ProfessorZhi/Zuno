from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ARCHITECTURE_VIEW_CONTRACT = [
    (1, "Logical View", "4+1 Logical"),
    (2, "Development View", "4+1 Development"),
    (3, "Process View", "4+1 Process"),
    (4, "Physical View", "4+1 Physical"),
    (5, "Scenarios View", "4+1 Scenarios"),
    (6, "V&B Logical View", "View & Beyond Logical"),
    (7, "Component-and-Connector View", "View & Beyond C&C"),
    (8, "V&B Deployment View", "View & Beyond Deployment"),
    (9, "Quality View", "View & Beyond Quality"),
    (10, "Agent Loop View", "Zuno 专题图"),
]

ACTIVE_ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture.md",
    "architecture.html",
}

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

    for relative_path in [
        "README.md",
        "docs/README.md",
        "docs/architecture/README.md",
        "docs/architecture/architecture.md",
        "docs/architecture/architecture.html",
        ".agent/architecture/README.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "docs/history/architecture-surface-cleanup-2026-06-30/README.md",
    ]:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing documentation entrypoint: {relative_path}")

    current_docs_architecture_files = {
        path.name
        for path in (REPO_ROOT / "docs" / "architecture").iterdir()
        if path.is_file()
    }
    if current_docs_architecture_files != ACTIVE_ARCHITECTURE_FILES:
        errors.append(
            "docs/architecture files must stay slim: "
            f"expected {sorted(ACTIVE_ARCHITECTURE_FILES)}, got {sorted(current_docs_architecture_files)}"
        )

    current_agent_architecture_files = {
        path.name
        for path in (REPO_ROOT / ".agent" / "architecture").iterdir()
        if path.is_file()
    }
    if current_agent_architecture_files != ACTIVE_ARCHITECTURE_FILES:
        errors.append(
            ".agent/architecture files must stay slim: "
            f"expected {sorted(ACTIVE_ARCHITECTURE_FILES)}, got {sorted(current_agent_architecture_files)}"
        )

    for name in ARCHIVED_ARCHITECTURE_SPLIT_DOCS:
        if (REPO_ROOT / "docs" / "architecture" / name).exists():
            errors.append(f"split architecture doc must stay archived: docs/architecture/{name}")
        if not (
            REPO_ROOT
            / "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture"
            / name
        ).exists():
            errors.append(f"missing archived architecture split doc: {name}")

    for relative_path in [
        ".agent/architecture/near-term",
        ".agent/architecture/future",
        ".agent/architecture/decisions",
        ".agent/architecture/00-architecture-index.md",
        ".agent/architecture/glossary.md",
    ]:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"agent architecture workset must stay archived: {relative_path}")

    for relative_path in [
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/decisions/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/00-architecture-index.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/glossary.md",
    ]:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing archived agent architecture workset path: {relative_path}")

    return errors


def verify_entrypoint_text() -> list[str]:
    errors: list[str] = []
    readme = _read("README.md")
    docs_index = _read("docs/README.md")
    architecture_index = _read("docs/architecture/README.md")
    docs_architecture = _read("docs/architecture/architecture.md")
    agent_architecture = _read(".agent/architecture/architecture.md")

    for phrase in [
        "./docs/architecture/architecture.md",
        "./docs/architecture/architecture.html",
        "GeneralAgent` single loop",
        "zuno-document-ingestion-v1",
        "docs/history/architecture-surface-cleanup-2026-06-30/",
    ]:
        if phrase not in readme:
            errors.append(f"README.md missing phrase: {phrase}")

    for phrase in [
        "./architecture/architecture.md",
        "./architecture/architecture.html",
        "./history/README.md",
        "docs/history/architecture-surface-cleanup-2026-06-30/",
    ]:
        if phrase not in docs_index:
            errors.append(f"docs/README.md missing phrase: {phrase}")

    for phrase in [
        "architecture.md",
        "architecture.html",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/",
        "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/",
    ]:
        if phrase not in architecture_index:
            errors.append(f"docs/architecture/README.md missing phrase: {phrase}")

    shared_phrases = [
        "总架构文档",
        "本地优先的企业私有知识库与多功能 Agent 助手",
        "文字总架构文档",
        "架构 HTML",
        "docs/architecture/architecture.md",
        ".agent/architecture/architecture.md",
        "docs/architecture/architecture.html",
        ".agent/architecture/architecture.html",
        "Document Ingestion / Parse Gateway",
        "Tool Control Plane",
        "LangSmith-compatible Trace / Eval",
    ]
    for phrase in shared_phrases:
        if phrase not in docs_architecture:
            errors.append(f"docs/architecture/architecture.md missing sync phrase: {phrase}")
        if phrase not in agent_architecture:
            errors.append(f".agent/architecture/architecture.md missing sync phrase: {phrase}")

    for phrase in [
        "Current",
        "Target",
        "Document Ingestion",
        "Security / Governance",
        "zuno-security-enterprise-scenarios-v1",
        "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/",
    ]:
        if phrase not in docs_architecture:
            errors.append(f"docs/architecture/architecture.md missing architecture phrase: {phrase}")

    if docs_architecture != agent_architecture:
        errors.append(".agent/architecture/architecture.md must mirror docs/architecture/architecture.md exactly")

    return errors


def verify_architecture_html_sync() -> list[str]:
    errors: list[str] = []
    renderer = _load_render_architecture_module()
    rendered = renderer.build_html()
    html_path = REPO_ROOT / "docs" / "architecture" / "architecture.html"
    agent_html_path = REPO_ROOT / ".agent" / "architecture" / "architecture.html"
    if html_path.read_text(encoding="utf-8") != rendered:
        errors.append("docs/architecture/architecture.html is stale; run python tools/agent/render_architecture.py --write")
    if agent_html_path.read_text(encoding="utf-8") != rendered:
        errors.append(".agent/architecture/architecture.html is stale; run python tools/agent/render_architecture.py --write")

    architecture_source = _read("docs/architecture/architecture.md")
    for phrase in [
        "Zuno 架构总览",
        "python tools/agent/render_architecture.py --write",
        "architecture.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "Document Ingestion",
        "Tool Control Plane",
    ]:
        if phrase not in architecture_source:
            errors.append(f"docs/architecture/architecture.md missing phrase: {phrase}")

    return errors


def verify_architecture_view_contract() -> list[str]:
    errors: list[str] = []
    renderer = _load_render_architecture_module()
    expected_titles = [title for _, title, _ in ARCHITECTURE_VIEW_CONTRACT]
    if list(renderer.EXPECTED_DIAGRAMS) != expected_titles:
        errors.append("render_architecture.py EXPECTED_DIAGRAMS does not match architecture view contract")

    architecture_source = _read("docs/architecture/architecture.md")
    source_titles = [diagram.title for diagram in renderer.extract_diagrams(architecture_source)]
    if source_titles != expected_titles:
        errors.append(f"docs/architecture/architecture.md diagram order drifted: {source_titles}")

    html_page = _read("docs/architecture/architecture.html")
    agent_html_page = _read(".agent/architecture/architecture.html")
    if html_page != agent_html_page:
        errors.append(".agent/architecture/architecture.html must mirror docs/architecture/architecture.html exactly")
    for index, title, _theory in ARCHITECTURE_VIEW_CONTRACT:
        html_title = title.replace("&", "&amp;")
        if f"<h3>{index}. {html_title}</h3>" not in html_page:
            errors.append(f"docs/architecture/architecture.html missing rendered view heading: {index}. {title}")

    if html_page.count('class="diagram-section"') != 10:
        errors.append("docs/architecture/architecture.html must render exactly ten diagram sections")
    if html_page.count('<div class="mermaid">') != 10:
        errors.append("docs/architecture/architecture.html must render exactly ten Mermaid containers")
    if html_page.count("<summary>Mermaid source</summary>") != 10:
        errors.append("docs/architecture/architecture.html must expose Mermaid source for each diagram")
    for phrase in [
        "展开全屏查看",
        "diagram-open",
        "diagram-dialog",
        "securityLevel: \"strict\"",
        "useMaxWidth: true",
    ]:
        if phrase not in html_page:
            errors.append(f"docs/architecture/architecture.html missing visual safety phrase: {phrase}")

    return errors


def verify_no_retired_front_path_links() -> list[str]:
    errors: list[str] = []
    forbidden_paths = [
        "docs/architecture/current-architecture.md",
        "docs/architecture/target-architecture.md",
        "docs/architecture/roadmap.md",
        "docs/architecture/product-scenario-enterprise-kb.md",
        "docs/architecture/security-and-sandbox.md",
        "docs/architecture/deliverables.md",
        "docs/architecture/overall-architecture.md",
        ".agent/architecture/overall-architecture.md",
        ".agent/architecture/near-term/",
        ".agent/architecture/future/",
        ".agent/architecture/decisions/",
    ]
    scan_roots = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "docs",
        REPO_ROOT / ".agent",
    ]
    for root in scan_roots:
        paths = [root] if root.is_file() else sorted(root.rglob("*"))
        for path in paths:
            if not path.is_file() or path.suffix not in {".md", ".py", ".yaml", ".yml"}:
                continue
            relative_path = path.relative_to(REPO_ROOT).as_posix()
            if relative_path.startswith("docs/history/"):
                continue
            if relative_path.startswith(".agent/local/"):
                continue
            if relative_path.startswith(".agent/scripts/"):
                continue
            content = path.read_text(encoding="utf-8")
            for forbidden in forbidden_paths:
                if forbidden in content:
                    errors.append(f"{relative_path} references retired front path: {forbidden}")
    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(verify_front_path_shape())
    errors.extend(verify_entrypoint_text())
    errors.extend(verify_architecture_html_sync())
    errors.extend(verify_architecture_view_contract())
    errors.extend(verify_no_retired_front_path_links())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("documentation entrypoint verification failed.")
        return 1

    print("documentation entrypoint verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

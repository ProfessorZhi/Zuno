from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = REPO_ROOT / "docs/architecture/architecture.md"
VIEWS_PATH = REPO_ROOT / "docs/architecture/architecture-views.md"
HTML_PATH = REPO_ROOT / "docs/architecture/architecture.html"
AGENT_DESIGN_PATH = REPO_ROOT / ".agent/architecture/architecture.md"
AGENT_HTML_PATH = REPO_ROOT / ".agent/architecture/architecture.html"

# Backward-compatible alias used by older tests and helper scripts.
SOURCE_PATH = VIEWS_PATH
AGENT_SOURCE_PATH = AGENT_DESIGN_PATH

STALE_OUTPUTS = [
    REPO_ROOT / "docs/architecture/overview.html",
    REPO_ROOT / "docs/architecture.md",
    REPO_ROOT / "docs/architecture.html",
    REPO_ROOT / ".agent/architecture/blueprint.html",
    REPO_ROOT / "docs/architecture/overall-architecture.md",
    REPO_ROOT / ".agent/architecture/overall-architecture.md",
]

VIEW_GROUPS = [
    {
        "title": "一、4+1 View Model",
        "views": [
            "Logical View (4+1)",
            "Development View (4+1)",
            "Process View (4+1)",
            "Physical View (4+1)",
            "Scenarios View (4+1)",
        ],
    },
    {
        "title": "二、Views & Beyond",
        "views": [
            "Module View (Views & Beyond)",
            "Component-and-Connector View (Views & Beyond)",
            "Data View (Views & Beyond)",
            "Quality View (Views & Beyond)",
        ],
    },
    {
        "title": "三、Zuno Product Core",
        "views": ["Agentic GraphRAG Evidence and Agent Loop (Zuno)"],
    },
]

EXPECTED_VIEWS = [view for group in VIEW_GROUPS for view in group["views"]]
EXPECTED_DIAGRAMS = EXPECTED_VIEWS
MERMAID_MODULE_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"


def _section(content: str, title: str) -> str:
    marker = f"### {title}"
    start = content.find(marker)
    if start < 0:
        return ""
    candidates = [
        content.find(f"### {other}", start + len(marker))
        for other in EXPECTED_VIEWS
        if other != title and content.find(f"### {other}", start + len(marker)) >= 0
    ]
    end = min(candidates) if candidates else len(content)
    return content[start:end]


def validate_design(content: str) -> list[str]:
    errors: list[str] = []
    required_sections = [
        "# Zuno Target Architecture Atlas",
        "# 1. 项目定位：轻量实现，成熟设计",
        "# 2. 总体架构",
        "# 3. 完整 Agent 闭环",
        "# 4. 十一模块目标设计",
        "## 4.1 Product Surface",
        "## 4.2 Input",
        "## 4.3 Knowledge：Agentic GraphRAG",
        "## 4.4 Model Gateway",
        "## 4.5 Memory 与 Context 管理",
        "## 4.6 Agent Core / Planning & Control",
        "## 4.7 Capability",
        "## 4.8 Tool Runtime",
        "## 4.9 Security",
        "## 4.10 Observability & Eval",
        "## 4.11 Infrastructure",
        "# 5. 模块间核心 contract",
        "# 9. Target completion criteria",
        "# 10. Architecture Visual Atlas",
    ]
    for section in required_sections:
        if section not in content:
            errors.append(f"architecture.md missing text-first design section: {section}")

    required_terms = [
        "十一逻辑能力模块",
        "六个物理运行域",
        "Single Controller Agent",
        "TaskQueuePort",
        "RabbitMQAdapter",
        "LangSmithTraceSink",
        "Agentic GraphRAG",
        "EvidenceLedger",
        "ContextPack",
        "Plan-and-Execute",
        "ReAct",
        "Reflection",
        "Replan",
        "Reflexion",
        "Capability Registry",
        "MCP",
        "ToolCallIntent",
        "NormalizedToolObservation",
        "GateDecision",
        "Recall@K",
        "token",
        "cost",
        "implementation available",
        "measurement blocked",
        "quality not yet proven",
        "architecture-views.md",
    ]
    for term in required_terms:
        if term not in content:
            errors.append(f"architecture.md missing required design term: {term}")

    mermaid_count = content.count("```mermaid")
    if mermaid_count < 2:
        errors.append("architecture.md should retain a small number of supporting Mermaid diagrams")
    if mermaid_count > 8:
        errors.append("architecture.md must stay text-first; move detailed diagrams to architecture-views.md")

    if len(content) < 20000:
        errors.append("architecture.md is too short for the normative text-first target design")
    return errors


def validate_source(content: str) -> list[str]:
    """Validate the dedicated Mermaid atlas source.

    Kept under the historical name because repo guardrails import this function.
    """

    errors: list[str] = []
    for title in EXPECTED_VIEWS:
        section = _section(content, title)
        if not section:
            errors.append(f"missing canonical architecture view: {title}")
            continue
        if "#### Overall" not in section:
            errors.append(f"canonical view has no Overall diagram: {title}")
        if section.count("#### Local") < 2:
            errors.append(f"canonical view must have at least two Local diagrams: {title}")
        if "```mermaid" not in section:
            errors.append(f"canonical view has no Mermaid diagram: {title}")

    if content.count("```mermaid") < 30:
        errors.append("architecture visual source must contain at least 30 Mermaid diagrams")

    required_terms = [
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
        "Recall",
        "Token",
        "Cost",
    ]
    for term in required_terms:
        if term.lower() not in content.lower():
            errors.append(f"architecture-views.md missing required visual term: {term}")
    return errors


def validate_html(content: str) -> list[str]:
    errors: list[str] = []
    required = [
        "Zuno Target Architecture Atlas",
        '<script type="module">',
        'fetch("/docs/architecture/architecture-views.md"',
        MERMAID_MODULE_URL,
        'className = "mermaid"',
        "diagram-dialog",
        "Mermaid source",
        'diagram.subtitle.startsWith("Overall")',
        "${kind} Diagram",
        "阅读文字总架构",
    ]
    for marker in required:
        if marker not in content:
            errors.append(f"architecture.html missing native Mermaid marker: {marker}")
    for title in EXPECTED_VIEWS:
        if title not in content:
            errors.append(f"architecture.html missing canonical view title: {title}")
    if "offline-svg" in content or "offline-diagram" in content:
        errors.append("architecture.html must not use the retired simplified offline SVG renderer")
    return errors


def build_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def write_outputs() -> None:
    design = DESIGN_PATH.read_text(encoding="utf-8")
    views = VIEWS_PATH.read_text(encoding="utf-8")
    html = HTML_PATH.read_text(encoding="utf-8")
    errors = [*validate_design(design), *validate_source(views), *validate_html(html)]
    if errors:
        raise ValueError("\n".join(errors))
    AGENT_DESIGN_PATH.parent.mkdir(parents=True, exist_ok=True)
    AGENT_DESIGN_PATH.write_text(design, encoding="utf-8", newline="\n")
    AGENT_HTML_PATH.write_text(html, encoding="utf-8", newline="\n")


def check_outputs() -> list[str]:
    errors: list[str] = []
    design = DESIGN_PATH.read_text(encoding="utf-8")
    views = VIEWS_PATH.read_text(encoding="utf-8")
    html = HTML_PATH.read_text(encoding="utf-8")
    errors.extend(validate_design(design))
    errors.extend(validate_source(views))
    errors.extend(validate_html(html))

    if not AGENT_DESIGN_PATH.exists():
        errors.append(f"missing generated Markdown mirror: {AGENT_DESIGN_PATH.relative_to(REPO_ROOT)}")
    elif AGENT_DESIGN_PATH.read_text(encoding="utf-8") != design:
        errors.append(".agent/architecture/architecture.md is not synced with docs/architecture/architecture.md")

    if not AGENT_HTML_PATH.exists():
        errors.append(f"missing generated HTML mirror: {AGENT_HTML_PATH.relative_to(REPO_ROOT)}")
    elif AGENT_HTML_PATH.read_text(encoding="utf-8") != html:
        errors.append(".agent/architecture/architecture.html is not synced with docs/architecture/architecture.html")

    for path in STALE_OUTPUTS:
        if path.exists():
            errors.append(f"stale architecture output exists: {path.relative_to(REPO_ROOT)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the text-first Zuno target architecture and native Mermaid visual atlas."
    )
    parser.add_argument("--write", action="store_true", help="validate sources and sync Markdown/HTML mirrors")
    parser.add_argument("--check", action="store_true", help="check design, views, HTML, and mirrors")
    args = parser.parse_args()

    if args.write:
        write_outputs()
    if args.check:
        errors = check_outputs()
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("architecture render check passed.")
    if not args.write and not args.check:
        print(build_html())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

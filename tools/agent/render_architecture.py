from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPO_ROOT / "docs/architecture/architecture.md"
HTML_PATH = REPO_ROOT / "docs/architecture/architecture.html"
AGENT_SOURCE_PATH = REPO_ROOT / ".agent/architecture/architecture.md"
AGENT_HTML_PATH = REPO_ROOT / ".agent/architecture/architecture.html"

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

AGENT_POINTER = """# Zuno Target Architecture Atlas — Agent Entry

status: generated-entrypoint  
normative_source: `docs/architecture/architecture.md`  
visual_atlas: `docs/architecture/architecture.html`

本文件不再复制完整架构正文，避免两份大型 Mermaid 图谱产生内容漂移。

Agent、Codex 和自动化工具在进行架构审阅、实现计划或代码修改前，必须读取：

1. `docs/architecture/architecture.md`：目标架构唯一规范事实源；
2. `docs/architecture/architecture.html`：4+1、Views & Beyond 与 Zuno Product Core 的十类 Mermaid 图谱；
3. `docs/architecture/production-readiness.md`：当前真实实现、差距和测量状态。

更新流程：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
```

边界：

```text
architecture.md = Target
production-readiness.md = Current
implementation available / measurement blocked / quality not yet proven
```
"""


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


def validate_source(content: str) -> list[str]:
    errors: list[str] = []
    for title in EXPECTED_VIEWS:
        section = _section(content, title)
        if not section:
            errors.append(f"missing canonical architecture view: {title}")
            continue
        if "#### Overall" not in section:
            errors.append(f"canonical view has no Overall diagram: {title}")
        if "#### Local" not in section:
            errors.append(f"canonical view has no Local diagram: {title}")
        if "```mermaid" not in section:
            errors.append(f"canonical view has no Mermaid diagram: {title}")

    if content.count("```mermaid") < 30:
        errors.append("architecture atlas must contain at least 30 Mermaid diagrams")

    required_terms = [
        "十一逻辑能力模块",
        "六个物理运行域",
        "Agent Core / Planning & Control",
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
    for term in required_terms:
        if term not in content:
            errors.append(f"architecture atlas is missing required term: {term}")
    return errors


def validate_html(content: str) -> list[str]:
    errors: list[str] = []
    required = [
        "Zuno Target Architecture Atlas",
        '<script type="module">',
        'fetch("architecture.md"',
        MERMAID_MODULE_URL,
        'class="mermaid"',
        "diagram-dialog",
        "Mermaid source",
        "Overall Diagram",
        "Local Diagram",
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
    source = SOURCE_PATH.read_text(encoding="utf-8")
    html = HTML_PATH.read_text(encoding="utf-8")
    errors = [*validate_source(source), *validate_html(html)]
    if errors:
        raise ValueError("\n".join(errors))
    AGENT_SOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    AGENT_SOURCE_PATH.write_text(AGENT_POINTER, encoding="utf-8", newline="\n")
    AGENT_HTML_PATH.write_text(html, encoding="utf-8", newline="\n")


def check_outputs() -> list[str]:
    errors: list[str] = []
    source = SOURCE_PATH.read_text(encoding="utf-8")
    html = HTML_PATH.read_text(encoding="utf-8")
    errors.extend(validate_source(source))
    errors.extend(validate_html(html))

    if not AGENT_SOURCE_PATH.exists():
        errors.append(f"missing generated agent entrypoint: {AGENT_SOURCE_PATH.relative_to(REPO_ROOT)}")
    elif AGENT_SOURCE_PATH.read_text(encoding="utf-8") != AGENT_POINTER:
        errors.append(".agent/architecture/architecture.md is not the generated normative-source pointer")

    if not AGENT_HTML_PATH.exists():
        errors.append(f"missing generated HTML mirror: {AGENT_HTML_PATH.relative_to(REPO_ROOT)}")
    elif AGENT_HTML_PATH.read_text(encoding="utf-8") != html:
        errors.append(".agent/architecture/architecture.html is not synced with docs/architecture/architecture.html")

    for path in STALE_OUTPUTS:
        if path.exists():
            errors.append(f"stale architecture output exists: {path.relative_to(REPO_ROOT)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and sync the Zuno target architecture atlas.")
    parser.add_argument("--write", action="store_true", help="sync agent pointer and HTML mirror")
    parser.add_argument("--check", action="store_true", help="check source, native Mermaid HTML, and mirrors")
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

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPO_ROOT / "docs/architecture.md"
OUTPUT_PATH = REPO_ROOT / "docs/architecture.html"
STALE_OUTPUTS = [
    REPO_ROOT / "docs/architecture/architecture.html",
    REPO_ROOT / "docs/architecture/overview.html",
    REPO_ROOT / ".agent/architecture/blueprint.html",
]

EXPECTED_DIAGRAMS = [
    "Logical View",
    "Development View",
    "Process View",
    "Physical View",
    "Scenarios View",
    "V&B Logical View",
    "Component-and-Connector View",
    "V&B Deployment View",
    "Quality View",
    "Agent Loop View",
]

GROUPS = [
    (
        "一、4+1 View Model",
        "4+1 用 Logical、Development、Process、Physical、Scenarios 五个视图解释同一个系统。",
        [
            "Logical View",
            "Development View",
            "Process View",
            "Physical View",
            "Scenarios View",
        ],
    ),
    (
        "二、View & Beyond",
        "本页采用 Logical、Component-and-Connector、Deployment、Quality 四类工程视图。",
        [
            "V&B Logical View",
            "Component-and-Connector View",
            "V&B Deployment View",
            "Quality View",
        ],
    ),
    (
        "三、Agent Loop 专题图",
        "Agent Loop 是 Process View 的内部细化，但不等同于整个 Process View。",
        [
            "Agent Loop View",
        ],
    ),
]

VIEW_META = {
    "Logical View": (
        "4+1: Logical",
        "View & Beyond: Logical",
        "说明前端、API、Agent、Memory、Capability、Knowledge、Evidence、Platform 的职责分层。",
    ),
    "Development View": (
        "4+1: Development",
        "View & Beyond: Implementation",
        "说明 apps、backend、docs、.agent、tools、tests 如何组织。",
    ),
    "Process View": (
        "4+1: Process",
        "View & Beyond: C&C",
        "说明请求、服务、Agent runtime、外部能力和事件流如何运行。",
    ),
    "Physical View": (
        "4+1: Physical",
        "View & Beyond: Deployment",
        "说明本地优先部署、FastAPI、Web/Desktop、存储和外部 provider 的关系。",
    ),
    "Scenarios View": (
        "4+1: Scenarios / Process",
        "View & Beyond: Runtime Scenario",
        "说明一个 query 如何经过 Context、Mode Policy、Agentic RAG、Evidence 和 Trace。",
    ),
    "V&B Logical View": (
        "4+1: Logical",
        "View & Beyond: Logical",
        "说明 Agent Workspace 的领域子系统和核心概念。",
    ),
    "Component-and-Connector View": (
        "4+1: Logical / Process",
        "View & Beyond: Component-and-Connector",
        "说明 API、Agent、Memory、Tool、Retrieval、Evidence、Trace 的运行连接。",
    ),
    "V&B Deployment View": (
        "4+1: Physical",
        "View & Beyond: Deployment",
        "说明可替换 provider、存储、模型、搜索和 MCP 的部署关系。",
    ),
    "Quality View": (
        "4+1: Scenarios / Cross-cutting",
        "View & Beyond: Quality",
        "说明性能、可靠性、安全、可观测性、可修改性和评测如何落到机制。",
    ),
    "Agent Loop View": (
        "4+1: Logical / Process",
        "View & Beyond: C&C",
        "说明主控 Agent 的 Plan、Act、Observe、Reflect、Replan 循环。",
    ),
}

PALETTE = {
    "background": "#f7f8fb",
    "node": "#ffffff",
    "border": "#b8c2cc",
    "text": "#16202a",
    "line": "#52616f",
}


@dataclass(frozen=True)
class Diagram:
    title: str
    description: str
    analysis: list[str]
    mermaid: str


def _sections(content: str) -> dict[str, str]:
    matches = list(re.finditer(r"^### (?P<title>[^\n]+)\n", content, re.M))
    sections: dict[str, str] = {}
    seen: set[str] = set()
    duplicates: list[str] = []
    for index, match in enumerate(matches):
        title = match.group("title").strip()
        if title in seen:
            duplicates.append(title)
        seen.add(title)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        sections[title] = content[start:end]
    if duplicates:
        raise ValueError(f"duplicate Mermaid diagram sections: {duplicates}")
    return sections


def _extract_section_description(section_body: str, title: str) -> str:
    body_before_mermaid = section_body.split("```mermaid", maxsplit=1)[0]
    if body_before_mermaid == section_body:
        raise ValueError(f"missing Mermaid block for {title}")
    lines = [
        line.strip()
        for line in body_before_mermaid.strip().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    return " ".join(lines)


def _extract_analysis(section_body: str) -> list[str]:
    match = re.search(r"#### 分析\n(?P<body>.*?)(?:\n## |\n### |\Z)", section_body, re.S)
    if not match:
        return []
    analysis: list[str] = []
    for line in match.group("body").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            analysis.append(stripped[2:].strip())
    return analysis


def _verify_palette(title: str, mermaid: str) -> None:
    required = [
        f"fill:{PALETTE['node']}",
        f"stroke:{PALETTE['border']}",
        f"color:{PALETTE['text']}",
        f'"lineColor": "{PALETTE["line"]}"',
    ]
    missing = [phrase for phrase in required if phrase not in mermaid]
    if missing:
        raise ValueError(f"{title} Mermaid palette is incomplete: {missing}")


def _verify_render_safe(title: str, mermaid: str) -> None:
    unsafe = re.findall(r"\[[^\]\"].*?[+/&:：].*?\]", mermaid)
    if unsafe:
        raise ValueError(f"{title} has unquoted Mermaid labels that may fail in browser: {unsafe[:3]}")


def extract_diagrams(content: str) -> list[Diagram]:
    sections = _sections(content)
    missing = [title for title in EXPECTED_DIAGRAMS if title not in sections]
    if missing:
        raise ValueError(f"missing Mermaid diagram sections: {missing}")
    mermaid_block_count = len(re.findall(r"```mermaid\n", content))
    if mermaid_block_count != len(EXPECTED_DIAGRAMS):
        raise ValueError(
            f"expected {len(EXPECTED_DIAGRAMS)} Mermaid blocks, found {mermaid_block_count}"
        )
    unknown = [
        title
        for title, section_body in sections.items()
        if "```mermaid" in section_body and title not in EXPECTED_DIAGRAMS
    ]
    if unknown:
        raise ValueError(f"unknown Mermaid diagram sections: {unknown}")

    diagrams: list[Diagram] = []
    for title in EXPECTED_DIAGRAMS:
        section_body = sections[title]
        match = re.search(r"```mermaid\n(?P<code>.*?)\n```", section_body, re.S)
        if not match:
            raise ValueError(f"missing Mermaid block for {title}")
        mermaid = match.group("code").strip()
        _verify_palette(title, mermaid)
        _verify_render_safe(title, mermaid)
        diagrams.append(
            Diagram(
                title=title,
                description=_extract_section_description(section_body, title),
                analysis=_extract_analysis(section_body),
                mermaid=mermaid,
            )
        )
    return diagrams


def _render_diagram_card(diagram: Diagram, index: int) -> str:
    title = html.escape(diagram.title)
    description = html.escape(diagram.description)
    mermaid = html.escape(diagram.mermaid)
    four_plus, view_beyond, analysis = VIEW_META[diagram.title]
    bullets = "\n".join(
        f"          <li>{html.escape(item)}</li>" for item in (diagram.analysis or [analysis])
    )
    return f"""      <section class="diagram-section">
        <h3>{index}. {title}</h3>
        <p class="purpose">{description}</p>
        <dl class="meta">
          <div><dt>4+1</dt><dd>{html.escape(four_plus)}</dd></div>
          <div><dt>View &amp; Beyond</dt><dd>{html.escape(view_beyond)}</dd></div>
        </dl>
        <ul class="analysis">
{bullets}
        </ul>
        <div class="diagram-actions">
          <button type="button" class="diagram-open" data-diagram-title="{title}">展开全屏查看</button>
        </div>
        <figure class="diagram-frame">
          <div class="mermaid">
{mermaid}
          </div>
        </figure>
        <details>
          <summary>Mermaid source</summary>
          <pre><code>{mermaid}</code></pre>
        </details>
      </section>"""


def _render_diagrams_chapter(diagrams: list[Diagram]) -> str:
    diagram_map = {diagram.title: diagram for diagram in diagrams}
    html_sections: list[str] = []
    index = 1
    for heading, summary, titles in GROUPS:
        cards: list[str] = []
        for title in titles:
            cards.append(_render_diagram_card(diagram_map[title], index))
            index += 1
        html_sections.append(
            f"""    <section class="chapter">
      <h2>{html.escape(heading)}</h2>
      <p>{html.escape(summary)}</p>
{chr(10).join(cards)}
    </section>"""
        )
    return "\n".join(html_sections)


def render_html(diagrams: list[Diagram]) -> str:
    content = _render_diagrams_chapter(diagrams)
    palette_css = "\n".join(f"      --zuno-{name}: {value};" for name, value in PALETTE.items())
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Zuno Architecture Overview</title>
  <style>
    :root {{
{palette_css}
      color-scheme: light;
      font-family: Inter, "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
    }}
    body {{
      margin: 0;
      background: #ffffff;
      color: var(--zuno-text);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 52px 32px 70px;
    }}
    header {{
      margin-bottom: 30px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--zuno-border);
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 34px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 24px;
      line-height: 1.3;
      letter-spacing: 0;
    }}
    h3 {{
      margin: 0 0 8px;
      font-size: 18px;
      line-height: 1.35;
      letter-spacing: 0;
    }}
    p {{
      margin: 0 0 10px;
      line-height: 1.68;
      font-size: 15px;
    }}
    code {{
      font-family: "Cascadia Mono", Consolas, monospace;
      font-size: 0.92em;
    }}
    .sync {{
      color: #52616f;
      font-size: 14px;
    }}
    .purpose {{
      color: #25313d;
      font-size: 15px;
    }}
    .chapter {{
      margin-top: 34px;
    }}
    .view-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .view-grid article {{
      border: 1px solid var(--zuno-border);
      border-radius: 6px;
      padding: 14px;
      background: #ffffff;
    }}
    .diagram-section {{
      margin-top: 28px;
      padding-top: 24px;
      border-top: 1px solid #e3e7ec;
      break-inside: avoid;
    }}
    .meta {{
      display: grid;
      gap: 8px;
      margin: 12px 0 16px;
      padding: 12px 14px;
      border: 1px solid var(--zuno-border);
      border-radius: 6px;
      background: #f7f8fb;
      font-size: 14px;
    }}
    .meta div {{
      display: grid;
      grid-template-columns: 130px 1fr;
      gap: 10px;
    }}
    dt {{
      margin: 0;
      font-weight: 650;
    }}
    dd {{
      margin: 0;
      line-height: 1.55;
    }}
    .analysis {{
      margin: 10px 0 16px;
      padding-left: 20px;
      color: #25313d;
      font-size: 14px;
      line-height: 1.7;
    }}
    .analysis li {{
      margin: 4px 0;
    }}
    .diagram-frame {{
      margin: 16px auto 10px;
      box-sizing: border-box;
      width: 100%;
      padding: 14px;
      max-width: 100%;
      overflow: hidden;
      border: 1px solid var(--zuno-border);
      border-radius: 6px;
      background: #ffffff;
    }}
    .diagram-actions {{
      display: flex;
      justify-content: flex-end;
      margin: 6px 0 8px;
    }}
    .diagram-actions button,
    .diagram-dialog button {{
      border: 1px solid var(--zuno-border);
      border-radius: 6px;
      background: #ffffff;
      color: var(--zuno-text);
      cursor: pointer;
      font: inherit;
      font-size: 13px;
      line-height: 1.2;
      padding: 7px 12px;
    }}
    .diagram-actions button:hover,
    .diagram-dialog button:hover {{
      background: #f7f8fb;
    }}
    .mermaid {{
      width: 100%;
      min-height: 120px;
      display: flex;
      justify-content: center;
      text-align: center;
    }}
    .mermaid svg {{
      display: block;
      width: 100% !important;
      max-width: 100%;
      min-width: 0;
      height: auto !important;
    }}
    .diagram-dialog {{
      width: min(96vw, 1500px);
      height: min(92vh, 980px);
      padding: 0;
      border: 1px solid var(--zuno-border);
      border-radius: 8px;
      background: #ffffff;
      color: var(--zuno-text);
    }}
    .diagram-dialog::backdrop {{
      background: rgba(22, 32, 42, 0.42);
    }}
    .dialog-shell {{
      box-sizing: border-box;
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 12px;
      height: 100%;
      padding: 14px;
    }}
    .dialog-toolbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid #e3e7ec;
      padding-bottom: 10px;
    }}
    .dialog-title {{
      font-size: 16px;
      font-weight: 650;
    }}
    .dialog-canvas {{
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 0;
      overflow: hidden;
    }}
    .dialog-canvas svg {{
      width: auto !important;
      max-width: 100%;
      max-height: 100%;
      height: auto !important;
    }}
    details {{
      max-width: 100%;
      margin: 8px auto 0;
      font-size: 13px;
      color: #52616f;
    }}
    pre {{
      overflow-x: auto;
      padding: 14px;
      border-radius: 6px;
      background: #f7f8fb;
      border: 1px solid var(--zuno-border);
      color: var(--zuno-text);
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Zuno 架构总览 / Architecture Overview</h1>
      <p>Zuno 是本地优先的 Agent Workspace。本文用 4+1、View &amp; Beyond 和 Agent Loop 专题图说明目标架构。</p>
      <p class="sync">Source: <code>docs/architecture.md</code>. Generator: <code>tools/agent/render_architecture.py</code>. Output: <code>docs/architecture.html</code>.</p>
    </header>
{content}
    <dialog class="diagram-dialog" id="diagram-dialog">
      <div class="dialog-shell">
        <div class="dialog-toolbar">
          <div class="dialog-title" id="diagram-dialog-title">Diagram</div>
          <button type="button" id="diagram-dialog-close">关闭</button>
        </div>
        <div class="dialog-canvas" id="diagram-dialog-canvas"></div>
      </div>
    </dialog>
  </main>
  <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{
      startOnLoad: true,
      theme: "base",
      securityLevel: "strict",
      flowchart: {{
        useMaxWidth: true,
        htmlLabels: true,
        curve: "basis",
        padding: 10,
        nodeSpacing: 24,
        rankSpacing: 34
      }},
      themeVariables: {{
        background: "{PALETTE['background']}",
        mainBkg: "{PALETTE['node']}",
        primaryColor: "{PALETTE['node']}",
        primaryBorderColor: "{PALETTE['border']}",
        primaryTextColor: "{PALETTE['text']}",
        lineColor: "{PALETTE['line']}",
        textColor: "{PALETTE['text']}",
        fontFamily: "Inter, Segoe UI, Microsoft YaHei, Arial"
      }}
    }});
    const dialog = document.getElementById("diagram-dialog");
    const dialogTitle = document.getElementById("diagram-dialog-title");
    const dialogCanvas = document.getElementById("diagram-dialog-canvas");
    const closeButton = document.getElementById("diagram-dialog-close");

    function openDiagram(button) {{
      const section = button.closest(".diagram-section");
      const sourceSvg = section?.querySelector(".mermaid svg");
      if (!section || !sourceSvg || !dialog || !dialogCanvas || !dialogTitle) {{
        return;
      }}
      dialogTitle.textContent = button.dataset.diagramTitle || "Diagram";
      dialogCanvas.replaceChildren(sourceSvg.cloneNode(true));
      dialog.showModal();
    }}

    document.querySelectorAll(".diagram-open").forEach((button) => {{
      button.addEventListener("click", () => openDiagram(button));
    }});
    closeButton?.addEventListener("click", () => dialog?.close());
    dialog?.addEventListener("click", (event) => {{
      if (event.target === dialog) {{
        dialog.close();
      }}
    }});
  </script>
</body>
</html>
"""


def build_html() -> str:
    content = SOURCE_PATH.read_text(encoding="utf-8")
    diagrams = extract_diagrams(content)
    return render_html(diagrams)


def write_outputs() -> None:
    rendered = build_html()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT_PATH.relative_to(REPO_ROOT).as_posix()}")
    for stale_path in STALE_OUTPUTS:
        if stale_path.exists():
            stale_path.unlink()
            print(f"removed stale {stale_path.relative_to(REPO_ROOT).as_posix()}")


def check_outputs() -> int:
    rendered = build_html()
    errors: list[str] = []
    if not OUTPUT_PATH.exists():
        errors.append(f"missing generated output: {OUTPUT_PATH.relative_to(REPO_ROOT).as_posix()}")
    elif OUTPUT_PATH.read_text(encoding="utf-8") != rendered:
        errors.append(f"generated output is stale: {OUTPUT_PATH.relative_to(REPO_ROOT).as_posix()}")

    for stale_path in STALE_OUTPUTS:
        if stale_path.exists():
            errors.append(f"stale generated output still exists: {stale_path.relative_to(REPO_ROOT).as_posix()}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("architecture HTML output is in sync with docs/architecture.md")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render architecture Mermaid diagrams to lightweight HTML.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write generated HTML file")
    mode.add_argument("--check", action="store_true", help="verify generated HTML file is current")
    args = parser.parse_args(argv)

    if args.write:
        write_outputs()
        return 0
    return check_outputs()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

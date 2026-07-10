from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPO_ROOT / "docs/architecture/architecture.md"
AGENT_SOURCE_PATH = REPO_ROOT / ".agent/architecture/architecture.md"
OUTPUT_PATHS = [
    REPO_ROOT / "docs/architecture/architecture.html",
    REPO_ROOT / ".agent/architecture/architecture.html",
]
STALE_OUTPUTS = [
    REPO_ROOT / "docs/architecture/overview.html",
    REPO_ROOT / "docs/architecture.md",
    REPO_ROOT / "docs/architecture.html",
    REPO_ROOT / ".agent/architecture/blueprint.html",
    REPO_ROOT / "docs/architecture/overall-architecture.md",
    REPO_ROOT / ".agent/architecture/overall-architecture.md",
]

EXPECTED_DIAGRAMS = [
    "Lean System Overview",
    "Golden Path Runtime",
    "Agentic GraphRAG and Agent Loop",
    "Local Deployment and State",
]

GROUPS = [
    (
        "Lean Complete Product Architecture",
        "四张图从产品域、黄金链路、Agentic GraphRAG 循环和本地状态部署解释同一个近期目标。",
        EXPECTED_DIAGRAMS,
    )
]

VIEW_META = {
    "Lean System Overview": (
        "Six runtime domains",
        "展示 Product & API、Input & Knowledge、Agent Core、Capability & Tool、Governance & Observability、Local Infrastructure 的 owner 边界。",
    ),
    "Golden Path Runtime": (
        "End-to-end product path",
        "展示配置模型、创建 Workspace、上传、解析、索引、AgentChat、证据、引用、回答、trace、feedback 和恢复。",
    ),
    "Agentic GraphRAG and Agent Loop": (
        "Retrieval and control loop",
        "展示 standard / deep / agentic 的关系，以及 evidence、claim binding、reflection、replan 和 release gate。",
    ),
    "Local Deployment and State": (
        "Local durable runtime",
        "展示 Web、FastAPI、SQLite、本地对象存储、本地队列、本地索引、模型 provider 和 trace store。",
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
        match = re.search(r"```mermaid\n(?P<body>.*?)\n```", section_body, re.S)
        if not match:
            raise ValueError(f"missing Mermaid source for {title}")
        mermaid = match.group("body").strip()
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


def _render_diagram_card(index: int, diagram: Diagram) -> str:
    escaped_title = html.escape(diagram.title)
    escaped_description = html.escape(diagram.description)
    focus, purpose = VIEW_META[diagram.title]
    analysis_items = "\n".join(
        f"              <li>{html.escape(item)}</li>" for item in diagram.analysis
    )
    if not analysis_items:
        analysis_items = "              <li>此图暂无额外分析。</li>"
    escaped_source = html.escape(diagram.mermaid)
    return f"""
        <article class="diagram-section" data-title="{escaped_title}">
          <div class="diagram-heading">
            <div>
              <span class="diagram-kicker">Diagram {index}</span>
              <h3>{index}. {escaped_title}</h3>
              <p>{escaped_description}</p>
            </div>
            <button class="fullscreen-button" type="button" data-diagram-index="{index - 1}">展开全屏查看</button>
          </div>
          <dl class="diagram-meta">
            <div><dt>Focus</dt><dd>{html.escape(focus)}</dd></div>
            <div><dt>Purpose</dt><dd>{html.escape(purpose)}</dd></div>
          </dl>
          <div class="diagram-frame">
            <div class="mermaid">
{escaped_source}
            </div>
          </div>
          <div class="analysis">
            <h4>分析</h4>
            <ul>
{analysis_items}
            </ul>
          </div>
          <details>
            <summary>Mermaid source</summary>
            <pre><code>{escaped_source}</code></pre>
          </details>
        </article>
"""


def build_html() -> str:
    content = SOURCE_PATH.read_text(encoding="utf-8")
    diagrams = extract_diagrams(content)
    cards = []
    for group_title, group_description, group_diagrams in GROUPS:
        rendered = "\n".join(
            _render_diagram_card(EXPECTED_DIAGRAMS.index(title) + 1, diagrams[EXPECTED_DIAGRAMS.index(title)])
            for title in group_diagrams
        )
        cards.append(
            f"""
      <section class="diagram-group">
        <h2>{html.escape(group_title)}</h2>
        <p>{html.escape(group_description)}</p>
{rendered}
      </section>
"""
        )
    body = "\n".join(cards)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Zuno Lean Complete Product Architecture</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --paper: #ffffff;
      --ink: #16202a;
      --muted: #52616f;
      --line: #b8c2cc;
      --accent: #2f6db3;
      --soft: #eef6ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    header, main {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
    }}
    header {{
      padding: 40px 0 24px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(30px, 4vw, 52px);
      line-height: 1.08;
      letter-spacing: 0;
    }}
    h2 {{
      margin: 36px 0 10px;
      font-size: 24px;
      letter-spacing: 0;
    }}
    h3 {{
      margin: 4px 0 8px;
      font-size: 20px;
      letter-spacing: 0;
    }}
    p {{ color: var(--muted); }}
    .lede {{
      max-width: 880px;
      font-size: 18px;
    }}
    .source-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 18px;
    }}
    .source-links a {{
      border: 1px solid var(--line);
      background: var(--paper);
      color: var(--ink);
      text-decoration: none;
      padding: 8px 10px;
      border-radius: 6px;
      font-size: 14px;
    }}
    .diagram-group {{
      margin: 28px 0 44px;
    }}
    .diagram-section {{
      margin: 18px 0 28px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--paper);
    }}
    .diagram-heading {{
      display: flex;
      gap: 16px;
      align-items: flex-start;
      justify-content: space-between;
    }}
    .diagram-kicker {{
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .fullscreen-button {{
      flex: 0 0 auto;
      border: 1px solid var(--line);
      background: var(--soft);
      color: var(--ink);
      border-radius: 6px;
      padding: 8px 10px;
      cursor: pointer;
    }}
    .diagram-meta {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin: 12px 0;
    }}
    .diagram-meta div {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      min-width: 0;
    }}
    dt {{
      font-size: 12px;
      color: var(--muted);
      margin-bottom: 4px;
    }}
    dd {{ margin: 0; }}
    .diagram-frame {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      background: #fbfcfe;
    }}
    .mermaid {{
      min-width: 760px;
      display: flex;
      justify-content: center;
    }}
    .analysis {{
      margin-top: 14px;
      background: #fbfcfe;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
    }}
    .analysis h4 {{ margin: 0 0 8px; }}
    .analysis ul {{ margin: 0; padding-left: 20px; }}
    details {{
      margin-top: 12px;
    }}
    pre {{
      overflow-x: auto;
      background: #101820;
      color: #f5f7fb;
      border-radius: 6px;
      padding: 12px;
    }}
    dialog {{
      width: min(1200px, calc(100vw - 24px));
      height: min(900px, calc(100vh - 24px));
      border: 0;
      border-radius: 8px;
      padding: 0;
    }}
    dialog::backdrop {{
      background: rgba(13, 20, 28, 0.62);
    }}
    .dialog-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      border-bottom: 1px solid var(--line);
      background: var(--paper);
    }}
    .dialog-body {{
      height: calc(100% - 58px);
      overflow: auto;
      padding: 16px;
      background: var(--bg);
    }}
    .dialog-body .mermaid {{
      min-width: 980px;
    }}
    @media (max-width: 720px) {{
      header, main {{ width: min(100vw - 20px, 1180px); }}
      .diagram-heading {{ display: block; }}
      .fullscreen-button {{ margin-top: 10px; }}
      .diagram-meta {{ grid-template-columns: 1fr; }}
      .mermaid {{ min-width: 680px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Zuno Lean Complete Product Architecture</h1>
    <p class="lede">Zuno 是本地优先的 Agentic GraphRAG 产品。Markdown 是详细实施蓝图；本页是从四张 canonical Mermaid 图生成的展示摘要。</p>
    <nav class="source-links" aria-label="Source links">
      <a href="architecture.md">docs/architecture/architecture.md</a>
      <a href="../../.agent/architecture/architecture.md">.agent/architecture/architecture.md</a>
      <a href="../../tools/agent/render_architecture.py">tools/agent/render_architecture.py</a>
    </nav>
  </header>
  <main>
{body}
  </main>
  <dialog id="diagram-dialog" aria-label="Diagram fullscreen view">
    <div class="dialog-header">
      <strong id="dialog-title">Diagram</strong>
      <button id="dialog-close" type="button">关闭</button>
    </div>
    <div class="dialog-body">
      <div id="dialog-content"></div>
    </div>
  </dialog>
  <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{ startOnLoad: true, securityLevel: "strict", theme: "base" }});

    const dialog = document.getElementById("diagram-dialog");
    const dialogTitle = document.getElementById("dialog-title");
    const dialogContent = document.getElementById("dialog-content");
    const closeButton = document.getElementById("dialog-close");
    const sections = Array.from(document.querySelectorAll(".diagram-section"));

    document.querySelectorAll(".fullscreen-button").forEach((button) => {{
      button.addEventListener("click", () => {{
        const index = Number(button.dataset.diagramIndex);
        const section = sections[index];
        const title = section.dataset.title || "Diagram";
        const mermaidSource = section.querySelector("pre code").textContent;
        dialogTitle.textContent = title;
        dialogContent.innerHTML = `<div class="mermaid">${{mermaidSource}}</div>`;
        dialog.showModal();
        mermaid.run({{ nodes: [dialogContent.querySelector(".mermaid")] }});
      }});
    }});

    closeButton.addEventListener("click", () => dialog.close());
  </script>
</body>
</html>
"""


def write_outputs() -> None:
    source = SOURCE_PATH.read_bytes()
    AGENT_SOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    AGENT_SOURCE_PATH.write_bytes(source)
    html_output = build_html()
    for path in OUTPUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html_output, encoding="utf-8", newline="\n")


def check_outputs() -> list[str]:
    errors: list[str] = []
    expected_html = build_html()
    source = SOURCE_PATH.read_bytes()
    if not AGENT_SOURCE_PATH.exists():
        errors.append(f"missing generated mirror: {AGENT_SOURCE_PATH.relative_to(REPO_ROOT)}")
    elif AGENT_SOURCE_PATH.read_bytes() != source:
        errors.append(".agent/architecture/architecture.md is not synced with docs/architecture/architecture.md")
    for path in OUTPUT_PATHS:
        if not path.exists():
            errors.append(f"missing generated HTML: {path.relative_to(REPO_ROOT)}")
            continue
        if path.read_text(encoding="utf-8") != expected_html:
            errors.append(f"{path.relative_to(REPO_ROOT)} is not generated from current Markdown")
    for path in STALE_OUTPUTS:
        if path.exists():
            errors.append(f"stale architecture output exists: {path.relative_to(REPO_ROOT)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Zuno architecture HTML from Markdown.")
    parser.add_argument("--write", action="store_true", help="write generated mirror and HTML files")
    parser.add_argument("--check", action="store_true", help="check generated files are up to date")
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

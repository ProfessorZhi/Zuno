from __future__ import annotations

import argparse
import json
import sys
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
MERMAID_MODULE_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"


def validate_source(content: str) -> list[str]:
    errors: list[str] = []
    for title in EXPECTED_VIEWS:
        marker = f"### {title}"
        if marker not in content:
            errors.append(f"missing canonical architecture view: {title}")
            continue
        start = content.index(marker)
        later_starts = [
            content.find(f"### {other}", start + len(marker))
            for other in EXPECTED_VIEWS
            if content.find(f"### {other}", start + len(marker)) >= 0
        ]
        end = min(later_starts) if later_starts else len(content)
        section = content[start:end]
        if "```mermaid" not in section:
            errors.append(f"canonical view has no Mermaid diagram: {title}")
        if "#### Overall" not in section:
            errors.append(f"canonical view has no Overall diagram: {title}")
        if "#### Local" not in section:
            errors.append(f"canonical view has no Local diagram: {title}")
    if content.count("```mermaid") < 30:
        errors.append("architecture atlas must contain at least 30 Mermaid diagrams")
    required_contract_terms = [
        "RuntimeRequest",
        "ModelCallRequest",
        "ContextPack",
        "RetrievalPlan",
        "EvidenceBundle",
        "ToolCallIntent",
        "NormalizedToolObservation",
        "GroundedAnswer",
    ]
    for term in required_contract_terms:
        if term not in content:
            errors.append(f"architecture atlas is missing connector contract: {term}")
    return errors


def build_html() -> str:
    groups_json = json.dumps(VIEW_GROUPS, ensure_ascii=False)
    expected_json = json.dumps(EXPECTED_VIEWS, ensure_ascii=False)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Zuno Target Architecture Atlas</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f7fa;
      --paper: #ffffff;
      --ink: #16202a;
      --muted: #52616f;
      --line: #c8d1da;
      --accent: #2563a6;
      --accent-soft: #eaf3ff;
      --warning: #8c5a00;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    a {{ color: var(--accent); }}
    .layout {{
      display: grid;
      grid-template-columns: 300px minmax(0, 1fr);
      min-height: 100vh;
    }}
    aside {{
      position: sticky;
      top: 0;
      height: 100vh;
      overflow: auto;
      padding: 24px 18px;
      border-right: 1px solid var(--line);
      background: #f9fafc;
    }}
    aside h1 {{ margin: 0 0 8px; font-size: 22px; }}
    aside p {{ margin: 0 0 18px; color: var(--muted); font-size: 13px; }}
    nav h2 {{ margin: 20px 0 8px; font-size: 13px; color: var(--muted); }}
    nav a {{
      display: block;
      padding: 7px 9px;
      margin: 3px 0;
      border-radius: 6px;
      color: var(--ink);
      text-decoration: none;
      font-size: 13px;
    }}
    nav a:hover {{ background: var(--accent-soft); }}
    main {{ width: min(1480px, 100%); padding: 34px 34px 80px; }}
    .hero {{
      padding: 24px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--paper);
    }}
    .hero h1 {{ margin: 0 0 10px; font-size: clamp(30px, 4vw, 52px); line-height: 1.08; }}
    .hero p {{ max-width: 980px; color: var(--muted); }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
    .legend span {{ padding: 5px 8px; border: 1px solid var(--line); border-radius: 999px; background: #fff; font-size: 12px; }}
    .status {{ margin-top: 14px; color: var(--warning); font-weight: 650; }}
    .group {{ margin-top: 42px; }}
    .group > h2 {{ margin: 0 0 14px; font-size: 26px; }}
    .view {{
      margin: 22px 0 38px;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 12px;
      background: var(--paper);
      scroll-margin-top: 16px;
    }}
    .view > h3 {{ margin: 0 0 6px; font-size: 23px; }}
    .view-description {{ margin: 0 0 18px; color: var(--muted); }}
    .diagram-card {{
      margin: 18px 0;
      padding-top: 18px;
      border-top: 1px solid var(--line);
    }}
    .diagram-header {{ display: flex; justify-content: space-between; gap: 14px; align-items: flex-start; }}
    .diagram-header h4 {{ margin: 0 0 4px; font-size: 18px; }}
    .diagram-kind {{ display: inline-block; margin-bottom: 5px; color: var(--accent); font-size: 11px; font-weight: 750; text-transform: uppercase; }}
    button {{
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 7px 10px;
      background: var(--accent-soft);
      color: var(--ink);
      cursor: pointer;
      white-space: nowrap;
    }}
    .diagram-frame {{
      margin-top: 12px;
      padding: 18px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 9px;
      background: #fcfdff;
    }}
    .mermaid {{ min-width: 860px; text-align: center; }}
    details {{ margin-top: 10px; }}
    pre.source {{ overflow: auto; max-height: 420px; padding: 13px; border-radius: 8px; background: #101820; color: #f5f7fb; }}
    dialog {{ width: min(1500px, calc(100vw - 24px)); height: min(960px, calc(100vh - 24px)); border: 0; border-radius: 10px; padding: 0; }}
    dialog::backdrop {{ background: rgba(15, 23, 42, .72); }}
    .dialog-head {{ display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--line); }}
    .dialog-body {{ height: calc(100% - 58px); overflow: auto; padding: 20px; background: var(--bg); }}
    .dialog-body svg {{ min-width: 1200px; height: auto; }}
    .error {{ padding: 14px; border: 1px solid #c97979; border-radius: 8px; background: #fff2f2; color: #7b2020; }}
    @media (max-width: 900px) {{
      .layout {{ grid-template-columns: 1fr; }}
      aside {{ position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); }}
      main {{ padding: 20px 14px 60px; }}
      .diagram-header {{ display: block; }}
      .diagram-header button {{ margin-top: 8px; }}
    }}
  </style>
</head>
<body>
  <div class="layout">
    <aside>
      <h1>Zuno Architecture Atlas</h1>
      <p>4+1、Views & Beyond 与 Zuno Product Core。Markdown 是目标架构事实源，HTML 使用原生 Mermaid 渲染。</p>
      <nav id="toc"></nav>
      <p><a href="architecture.md">打开 Markdown 事实源</a></p>
    </aside>
    <main>
      <section class="hero">
        <h1>Zuno Target Architecture Atlas</h1>
        <p>十类 canonical views。每一类均包含一张 Overall 图和至少一张 Local 图；核心 connector 使用 typed contract 标注，Security 与 Observability 明确横切。</p>
        <div class="legend">
          <span>==&gt; command / control</span>
          <span>--&gt; data / result</span>
          <span>-. -&gt; governance / observation</span>
          <span>Target view; Current 见 production-readiness.md</span>
        </div>
        <div id="status" class="status">正在读取 architecture.md 并加载 Mermaid…</div>
      </section>
      <div id="atlas"></div>
    </main>
  </div>

  <dialog id="diagram-dialog">
    <div class="dialog-head">
      <strong id="dialog-title">Diagram</strong>
      <button id="dialog-close" type="button">关闭</button>
    </div>
    <div id="dialog-body" class="dialog-body"></div>
  </dialog>

  <script type="module">
    const groups = {groups_json};
    const expectedViews = {expected_json};
    const status = document.getElementById("status");
    const atlas = document.getElementById("atlas");
    const toc = document.getElementById("toc");

    const slugify = (value) => value
      .toLowerCase()
      .replace(/[^a-z0-9\u4e00-\u9fff]+/g, "-")
      .replace(/^-+|-+$/g, "");

    function sectionFor(markdown, title) {{
      const marker = `### ${{title}}`;
      const start = markdown.indexOf(marker);
      if (start < 0) throw new Error(`缺少 canonical view: ${{title}}`);
      const candidates = expectedViews
        .filter((other) => other !== title)
        .map((other) => markdown.indexOf(`### ${{other}}`, start + marker.length))
        .filter((index) => index >= 0);
      const end = candidates.length ? Math.min(...candidates) : markdown.length;
      return markdown.slice(start + marker.length, end);
    }}

    function parseView(markdown, title) {{
      const section = sectionFor(markdown, title);
      const firstLocal = section.search(/^#### /m);
      const description = (firstLocal >= 0 ? section.slice(0, firstLocal) : section)
        .trim()
        .split(/\n+/)
        .filter((line) => line && !line.startsWith("#"))
        .join(" ");
      const diagrams = [];
      const regex = /^#### (?<subtitle>[^\n]+)\n(?<between>[\s\S]*?)```mermaid\n(?<source>[\s\S]*?)\n```/gm;
      for (const match of section.matchAll(regex)) {{
        diagrams.push({{
          subtitle: match.groups.subtitle.trim(),
          source: match.groups.source.trim(),
        }});
      }}
      if (!diagrams.length) throw new Error(`视图没有 Mermaid 子图: ${{title}}`);
      return {{ title, description, diagrams }};
    }}

    function renderShell(views) {{
      const lookup = new Map(views.map((view) => [view.title, view]));
      groups.forEach((group) => {{
        const navTitle = document.createElement("h2");
        navTitle.textContent = group.title;
        toc.appendChild(navTitle);

        const groupSection = document.createElement("section");
        groupSection.className = "group";
        const groupHeading = document.createElement("h2");
        groupHeading.textContent = group.title;
        groupSection.appendChild(groupHeading);

        group.views.forEach((title) => {{
          const view = lookup.get(title);
          const id = slugify(title);
          const link = document.createElement("a");
          link.href = `#${{id}}`;
          link.textContent = title;
          toc.appendChild(link);

          const article = document.createElement("article");
          article.className = "view";
          article.id = id;
          article.innerHTML = `<h3>${{title}}</h3><p class="view-description">${{view.description}}</p>`;

          view.diagrams.forEach((diagram, index) => {{
            const card = document.createElement("section");
            card.className = "diagram-card";
            const kind = diagram.subtitle.startsWith("Overall") ? "Overall" : "Local";
            const escaped = diagram.source
              .replaceAll("&", "&amp;")
              .replaceAll("<", "&lt;")
              .replaceAll(">", "&gt;");
            card.innerHTML = `
              <div class="diagram-header">
                <div><span class="diagram-kind">${{kind}} Diagram</span><h4>${{diagram.subtitle}}</h4></div>
                <button type="button" class="fullscreen">全屏查看</button>
              </div>
              <div class="diagram-frame"><pre class="mermaid">${{escaped}}</pre></div>
              <details><summary>Mermaid source</summary><pre class="source"><code>${{escaped}}</code></pre></details>`;
            article.appendChild(card);
          }});
          groupSection.appendChild(article);
        }});
        atlas.appendChild(groupSection);
      }});
    }}

    function bindFullscreen() {{
      const dialog = document.getElementById("diagram-dialog");
      const body = document.getElementById("dialog-body");
      const title = document.getElementById("dialog-title");
      document.getElementById("dialog-close").addEventListener("click", () => dialog.close());
      document.querySelectorAll(".fullscreen").forEach((button) => {{
        button.addEventListener("click", () => {{
          const card = button.closest(".diagram-card");
          const svg = card.querySelector("svg");
          title.textContent = card.querySelector("h4").textContent;
          body.replaceChildren(svg.cloneNode(true));
          dialog.showModal();
        }});
      }});
    }}

    try {{
      if (location.protocol === "file:") {{
        throw new Error("请使用 HTTP 预览：python -m http.server 8000，然后打开 /docs/architecture/architecture.html");
      }}
      const response = await fetch("architecture.md", {{ cache: "no-store" }});
      if (!response.ok) throw new Error(`无法读取 architecture.md: HTTP ${{response.status}}`);
      const markdown = await response.text();
      const views = expectedViews.map((title) => parseView(markdown, title));
      renderShell(views);

      const {{ default: mermaid }} = await import("{MERMAID_MODULE_URL}");
      mermaid.initialize({{
        startOnLoad: false,
        securityLevel: "strict",
        theme: "base",
        flowchart: {{ htmlLabels: true, curve: "basis", useMaxWidth: false }},
        sequence: {{ useMaxWidth: false, wrap: true }},
      }});
      await mermaid.run({{ querySelector: ".mermaid" }});
      bindFullscreen();
      status.textContent = `已渲染 ${{views.length}} 类视图，共 ${{views.reduce((sum, view) => sum + view.diagrams.length, 0)}} 张 Mermaid 图。`;
    }} catch (error) {{
      status.textContent = "架构图加载失败。";
      atlas.innerHTML = `<div class="error"><strong>无法渲染 Architecture Atlas</strong><br/>${{error.message}}</div>`;
      console.error(error);
    }}
  </script>
</body>
</html>
"""


def write_outputs() -> None:
    content = SOURCE_PATH.read_text(encoding="utf-8")
    errors = validate_source(content)
    if errors:
        raise ValueError("\n".join(errors))
    AGENT_SOURCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    AGENT_SOURCE_PATH.write_text(content, encoding="utf-8", newline="\n")
    html_output = build_html()
    for path in OUTPUT_PATHS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html_output, encoding="utf-8", newline="\n")


def check_outputs() -> list[str]:
    errors: list[str] = []
    content = SOURCE_PATH.read_text(encoding="utf-8")
    errors.extend(validate_source(content))
    expected_html = build_html()
    if not AGENT_SOURCE_PATH.exists():
        errors.append(f"missing generated mirror: {AGENT_SOURCE_PATH.relative_to(REPO_ROOT)}")
    elif AGENT_SOURCE_PATH.read_text(encoding="utf-8") != content:
        errors.append(".agent/architecture/architecture.md is not synced with docs/architecture/architecture.md")
    for path in OUTPUT_PATHS:
        if not path.exists():
            errors.append(f"missing generated HTML: {path.relative_to(REPO_ROOT)}")
        elif path.read_text(encoding="utf-8") != expected_html:
            errors.append(f"{path.relative_to(REPO_ROOT)} is not generated from current renderer")
    for path in STALE_OUTPUTS:
        if path.exists():
            errors.append(f"stale architecture output exists: {path.relative_to(REPO_ROOT)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the Zuno target architecture atlas.")
    parser.add_argument("--write", action="store_true", help="sync mirrors and generated HTML")
    parser.add_argument("--check", action="store_true", help="check source and generated outputs")
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

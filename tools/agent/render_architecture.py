from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = REPO_ROOT / "docs/architecture/diagrams.md"
OUTPUTS = [
    REPO_ROOT / "docs/architecture/overview.html",
    REPO_ROOT / ".agent/architecture/blueprint.html",
]

EXPECTED_DIAGRAMS = [
    "Current Runtime",
    "Target Runtime",
    "Maintenance Workflow",
]

PALETTE = {
    "background": "#f8f8fb",
    "node": "#f6f3ff",
    "border": "#a99cff",
    "text": "#2c255f",
    "line": "#9b8cff",
}


@dataclass(frozen=True)
class Diagram:
    title: str
    description: str
    mermaid: str


def _sections(content: str) -> dict[str, str]:
    matches = list(re.finditer(r"^## (?P<title>[^\n]+)\n", content, re.M))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        sections[match.group("title").strip()] = content[start:end]
    return sections


def _extract_section_description(section_body: str, title: str) -> str:
    body_before_mermaid = section_body.split("```mermaid", maxsplit=1)[0]
    if body_before_mermaid == section_body:
        raise ValueError(f"missing Mermaid block for {title}")
    lines = [line.strip() for line in body_before_mermaid.strip().splitlines() if line.strip()]
    return " ".join(lines)


def _verify_palette(title: str, mermaid: str) -> None:
    required = [
        f"fill:{PALETTE['node']}",
        f"stroke:{PALETTE['border']}",
        f"color:{PALETTE['text']}",
        f"stroke:{PALETTE['line']}",
    ]
    missing = [phrase for phrase in required if phrase not in mermaid]
    if missing:
        raise ValueError(f"{title} Mermaid palette is incomplete: {missing}")


def extract_diagrams(content: str) -> list[Diagram]:
    sections = _sections(content)
    missing = [title for title in EXPECTED_DIAGRAMS if title not in sections]
    if missing:
        raise ValueError(f"missing Mermaid diagram sections: {missing}")

    diagrams: list[Diagram] = []
    for title in EXPECTED_DIAGRAMS:
        section_body = sections[title]
        match = re.search(r"```mermaid\n(?P<code>.*?)\n```", section_body, re.S)
        if not match:
            raise ValueError(f"missing Mermaid block for {title}")
        mermaid = match.group("code").strip()
        _verify_palette(title, mermaid)
        diagrams.append(
            Diagram(
                title=title,
                description=_extract_section_description(section_body, title),
                mermaid=mermaid,
            )
        )
    return diagrams


def _render_diagram_card(diagram: Diagram) -> str:
    title = html.escape(diagram.title)
    description = html.escape(diagram.description)
    mermaid = html.escape(diagram.mermaid)
    return f"""    <section>
      <h2>{title}</h2>
      <p>{description}</p>
      <div class="mermaid">
{mermaid}
      </div>
      <details>
        <summary>Mermaid source</summary>
        <pre><code>{mermaid}</code></pre>
      </details>
    </section>"""


def render_html(diagrams: list[Diagram]) -> str:
    diagram_cards = "\n".join(_render_diagram_card(diagram) for diagram in diagrams)
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
      font-family: Inter, "Segoe UI", Arial, sans-serif;
    }}
    body {{
      margin: 0;
      background: var(--zuno-background);
      color: var(--zuno-text);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 40px 24px 56px;
    }}
    header {{
      margin-bottom: 28px;
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 32px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    p {{
      margin: 0;
      line-height: 1.7;
    }}
    .sync {{
      margin-top: 12px;
      font-size: 14px;
    }}
    section {{
      margin-top: 24px;
      padding: 22px;
      border: 1px solid var(--zuno-border);
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.72);
    }}
    h2 {{
      margin: 0 0 8px;
      font-size: 20px;
      letter-spacing: 0;
    }}
    .mermaid {{
      margin-top: 18px;
      padding: 18px;
      overflow-x: auto;
      border: 1px solid var(--zuno-border);
      border-radius: 8px;
      background: #ffffff;
    }}
    details {{
      margin-top: 12px;
      font-size: 13px;
    }}
    pre {{
      overflow-x: auto;
      padding: 14px;
      border-radius: 8px;
      background: #ffffff;
      border: 1px solid var(--zuno-border);
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Zuno Architecture Overview</h1>
      <p>三张核心图分别说明当前真实调用链、近期目标 runtime 和维护工作流。Current 与 Target 分开展示，避免把目标状态写成当前事实。</p>
      <p class="sync">同步规则：Mermaid 源只维护在 <code>docs/architecture/diagrams.md</code>，本页由 <code>tools/agent/render_architecture.py</code> 生成。HTML 可用本地 <code>file://</code> 打开，图形渲染使用 CDN Mermaid runtime；离线时仍保留标题、说明和 Mermaid source。</p>
    </header>
{diagram_cards}
  </main>
  <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{
      theme: "base",
      securityLevel: "strict",
      themeVariables: {{
        background: "{PALETTE['background']}",
        mainBkg: "{PALETTE['node']}",
        primaryColor: "{PALETTE['node']}",
        primaryBorderColor: "{PALETTE['border']}",
        primaryTextColor: "{PALETTE['text']}",
        lineColor: "{PALETTE['line']}",
        textColor: "{PALETTE['text']}"
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
    for output_path in OUTPUTS:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {output_path.relative_to(REPO_ROOT).as_posix()}")


def check_outputs() -> int:
    rendered = build_html()
    errors: list[str] = []
    for output_path in OUTPUTS:
        if not output_path.exists():
            errors.append(f"missing generated output: {output_path.relative_to(REPO_ROOT).as_posix()}")
            continue
        current = output_path.read_text(encoding="utf-8")
        if current != rendered:
            errors.append(f"generated output is stale: {output_path.relative_to(REPO_ROOT).as_posix()}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("architecture HTML outputs are in sync with docs/architecture/diagrams.md")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render architecture Mermaid diagrams to lightweight HTML.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write generated HTML files")
    mode.add_argument("--check", action="store_true", help="verify generated HTML files are current")
    args = parser.parse_args(argv)

    if args.write:
        write_outputs()
        return 0
    return check_outputs()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

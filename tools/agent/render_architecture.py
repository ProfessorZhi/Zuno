from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = REPO_ROOT / "docs/architecture/architecture.md"
VIEWS_PATH = REPO_ROOT / "docs/architecture/architecture-views.md"
HTML_PATH = REPO_ROOT / "docs/architecture/architecture.html"
AGENT_DESIGN_PATH = REPO_ROOT / ".agent/architecture/architecture.md"
AGENT_VIEWS_PATH = REPO_ROOT / ".agent/architecture/architecture-views.md"
AGENT_HTML_PATH = REPO_ROOT / ".agent/architecture/architecture.html"

SOURCE_PATH = VIEWS_PATH
AGENT_SOURCE_PATH = AGENT_VIEWS_PATH

EXPECTED_VIEWS = ['Logical View (4+1)', 'Development View (4+1)', 'Process View (4+1)', 'Physical View (4+1)', 'Scenarios View (4+1)', 'Module View (Views & Beyond)', 'Component-and-Connector View (Views & Beyond)', 'Data View (Views & Beyond)', 'Quality View (Views & Beyond)', 'Agentic GraphRAG Evidence and Agent Loop (Zuno)']
EXPECTED_DIAGRAMS = EXPECTED_VIEWS
MODULE_DOCS = ['01-product-surface.md', '02-input-document-ingestion.md', '03-knowledge-agentic-graphrag.md', '04-model-gateway.md', '05-memory-context.md', '06-agent-core-planning-control.md', '07-capability-skill.md', '08-tool-runtime.md', '09-security.md', '10-observability-eval.md', '11-infrastructure.md']
CANONICAL_ARCHITECTURE_FILES = {"README.md", "architecture.md", "architecture-views.md", "architecture.html"}
MERMAID_MODULE_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"

STALE_OUTPUTS = [
    REPO_ROOT / "docs/architecture/overview.html",
    REPO_ROOT / "docs/architecture.md",
    REPO_ROOT / "docs/architecture.html",
    REPO_ROOT / ".agent/architecture/blueprint.html",
    REPO_ROOT / "docs/architecture/overall-architecture.md",
    REPO_ROOT / ".agent/architecture/overall-architecture.md",
]


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
        "# Zuno 总体 Target 架构",
        "# 1. 问题、目标与非目标",
        "# 2. 全局架构原则",
        "# 3. 十一个逻辑模块",
        "# 4. 全局事实所有权",
        "# 5. 在线 Agent 完整运行流程",
        "# 6. 文档摄取与 Knowledge 发布流程",
        "# 7. Agentic GraphRAG 与证据闭环",
        "# 8. Model、Capability 与 Memory 协作",
        "# 9. Tool Runtime 与外部效果",
        "# 10. Security、Audit 与 Information Flow",
        "# 11. 状态、并发、恢复与幂等",
        "# 12. 物理运行域与部署",
        "# 13. 跨模块 Contract",
        "# 14. 可观测性、评测与质量证明",
        "# 15. Program、测试与完成证据",
    ]
    for section in required_sections:
        if section not in content:
            errors.append(f"architecture.md missing integration section: {section}")

    required_terms = [
        "Single Controller",
        "AgentRunGraph",
        "Plan DAG",
        "StepExecutionGraph",
        "CrossModuleEnvelope",
        "PreparedToolAction",
        "EffectReconciliation",
        "EvidenceLedger",
        "ContextPackVersion",
        "EffectiveSecurityEpoch",
        "IndexWriteReceipt",
        "ServingWatermark",
        "RunOutcome",
        "implementation available",
        "quality proven",
        "production ready",
    ]
    for term in required_terms:
        if term not in content:
            errors.append(f"architecture.md missing required integration term: {term}")

    for module_doc in MODULE_DOCS:
        if f"docs/modules/{module_doc}" not in content:
            errors.append(f"architecture.md does not route to module document: {module_doc}")

    if content.count("```mermaid") < 3:
        errors.append("architecture.md must keep at least three integration Mermaid diagrams")
    if content.count("```mermaid") > 8:
        errors.append("architecture.md must remain text-first; detailed diagrams belong in architecture-views.md")
    if len(content) < 15000:
        errors.append("architecture.md is too short for the cross-module integration specification")
    return errors


def validate_source(content: str) -> list[str]:
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
        if section.count("```mermaid") < 3:
            errors.append(f"canonical view must have three Mermaid diagrams: {title}")

    if content.count("```mermaid") != 30:
        errors.append("architecture visual source must contain exactly 30 Mermaid diagrams")

    required_terms = [
        "RuntimeRequest",
        "ActionProposal",
        "PreparedToolAction",
        "EffectReceipt",
        "ContextPackVersion",
        "KnowledgeRetrievalGraph",
        "EvidenceLedger",
        "CrossModuleEnvelopeV1",
        "RabbitMQ",
        "PostgreSQL",
        "ReleaseGateEvaluation",
    ]
    for term in required_terms:
        if term.lower() not in content.lower():
            errors.append(f"architecture-views.md missing required visual term: {term}")
    return errors


def validate_html(content: str) -> list[str]:
    errors: list[str] = []
    required = [
        "Zuno Target Architecture",
        '<script type="module">',
        'fetch("./architecture-views.md")',
        MERMAID_MODULE_URL,
        "十一模块 + 总体集成架构",
        "../modules/README.md",
        "../status/production-readiness.md",
        "diagram-dialog",
        "Mermaid source",
    ]
    for marker in required:
        if marker not in content:
            errors.append(f"architecture.html missing marker: {marker}")
    for title in EXPECTED_VIEWS:
        if title not in content:
            errors.append(f"architecture.html missing canonical view title: {title}")
    return errors


def _directory_errors(root: Path) -> list[str]:
    files = {path.name for path in root.iterdir() if path.is_file()}
    dirs = [path.name for path in root.iterdir() if path.is_dir()]
    errors: list[str] = []
    if files != CANONICAL_ARCHITECTURE_FILES:
        errors.append(f"{root.relative_to(REPO_ROOT)} must contain exactly {sorted(CANONICAL_ARCHITECTURE_FILES)}, got {sorted(files)}")
    if dirs:
        errors.append(f"{root.relative_to(REPO_ROOT)} must not contain subdirectories: {dirs}")
    return errors


def write_outputs() -> None:
    design = DESIGN_PATH.read_text(encoding="utf-8")
    views = VIEWS_PATH.read_text(encoding="utf-8")
    html = HTML_PATH.read_text(encoding="utf-8")
    errors = [*validate_design(design), *validate_source(views), *validate_html(html)]
    if errors:
        raise ValueError("\n".join(errors))
    AGENT_DESIGN_PATH.parent.mkdir(parents=True, exist_ok=True)
    AGENT_DESIGN_PATH.write_text(design, encoding="utf-8", newline="\n")
    AGENT_VIEWS_PATH.write_text(views, encoding="utf-8", newline="\n")
    AGENT_HTML_PATH.write_text(html, encoding="utf-8", newline="\n")


def check_outputs() -> list[str]:
    errors: list[str] = []
    errors.extend(_directory_errors(REPO_ROOT / "docs/architecture"))
    errors.extend(_directory_errors(REPO_ROOT / ".agent/architecture"))

    design = DESIGN_PATH.read_text(encoding="utf-8")
    views = VIEWS_PATH.read_text(encoding="utf-8")
    html = HTML_PATH.read_text(encoding="utf-8")
    errors.extend(validate_design(design))
    errors.extend(validate_source(views))
    errors.extend(validate_html(html))

    for formal, mirror, label in [
        (DESIGN_PATH, AGENT_DESIGN_PATH, "architecture.md"),
        (VIEWS_PATH, AGENT_VIEWS_PATH, "architecture-views.md"),
        (HTML_PATH, AGENT_HTML_PATH, "architecture.html"),
    ]:
        if not mirror.exists():
            errors.append(f"missing Agent mirror: {mirror.relative_to(REPO_ROOT)}")
        elif formal.read_bytes() != mirror.read_bytes():
            errors.append(f"Agent mirror is not byte-identical: {label}")

    for path in STALE_OUTPUTS:
        if path.exists():
            errors.append(f"stale architecture output exists: {path.relative_to(REPO_ROOT)}")
    return errors


def build_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Zuno integration architecture, visual source, HTML and mirrors.")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
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

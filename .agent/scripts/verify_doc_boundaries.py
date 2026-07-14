from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_ROOT = "docs/history/architecture-surface-cleanup-2026-06-30"

CANONICAL_ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
    "architecture-views.md",
    "architecture.html",
}

MODULE_DOCS = [
    "01-product-surface.md",
    "02-input-document-ingestion.md",
    "03-knowledge-agentic-graphrag.md",
    "04-model-gateway.md",
    "05-memory-context.md",
    "06-agent-core-planning-control.md",
    "07-capability-skill.md",
    "08-tool-runtime.md",
    "09-security.md",
    "10-observability-eval.md",
    "11-infrastructure.md",
]

RETIRED_FRONT_PATHS = [
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/architecture/product-scenario-enterprise-kb.md",
    "docs/architecture/security-and-sandbox.md",
    "docs/architecture/deliverables.md",
    "docs/architecture/overall-architecture.md",
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
    ".agent/architecture/overall-architecture.md",
    ".agent/architecture/agent-core-runtime.md",
    ".agent/architecture/near-term",
    ".agent/architecture/future",
    ".agent/architecture/decisions",
]

RETIRED_MODULE_DOCS = [
    "04-model-gateway-contract-freeze.md",
    "04-model-gateway-operations-conformance.md",
    "10-observability-eval-rag-agent-evaluation.md",
    "11-infrastructure-data-services.md",
    "11-infrastructure-consistency-lifecycle.md",
]

REQUIRED_ARCHIVES = [
    f"{ARCHIVE_ROOT}/README.md",
    f"{ARCHIVE_ROOT}/docs-architecture/current-architecture.md",
    f"{ARCHIVE_ROOT}/docs-architecture/target-architecture.md",
    f"{ARCHIVE_ROOT}/docs-architecture/roadmap.md",
    f"{ARCHIVE_ROOT}/docs-architecture/product-scenario-enterprise-kb.md",
    f"{ARCHIVE_ROOT}/docs-architecture/security-and-sandbox.md",
    f"{ARCHIVE_ROOT}/docs-architecture/deliverables.md",
]

CANONICAL_VIEWS = [
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


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def verify_architecture_surface() -> list[str]:
    errors: list[str] = []
    for relative_root in ["docs/architecture", ".agent/architecture"]:
        root = REPO_ROOT / relative_root
        files = {path.name for path in root.iterdir() if path.is_file()}
        directories = [path.name for path in root.iterdir() if path.is_dir()]
        if files != CANONICAL_ARCHITECTURE_FILES:
            errors.append(
                f"{relative_root} must contain only {sorted(CANONICAL_ARCHITECTURE_FILES)}; got {sorted(files)}"
            )
        if directories:
            errors.append(f"{relative_root} must not contain subdirectories: {sorted(directories)}")

    for relative_path in RETIRED_FRONT_PATHS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"retired architecture front path still exists: {relative_path}")
    for relative_path in REQUIRED_ARCHIVES:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing architecture cleanup archive path: {relative_path}")

    formal_modules = sorted(path.name for path in (REPO_ROOT / "docs/modules").glob("[0-9][0-9]-*.md"))
    mirror_modules = sorted(path.name for path in (REPO_ROOT / ".agent/modules").glob("[0-9][0-9]-*.md"))
    if formal_modules != MODULE_DOCS:
        errors.append(f"formal module document set mismatch: {formal_modules}")
    if mirror_modules != MODULE_DOCS:
        errors.append(f"Agent module mirror set mismatch: {mirror_modules}")

    for name in RETIRED_MODULE_DOCS:
        if (REPO_ROOT / "docs/modules" / name).exists() or (REPO_ROOT / ".agent/modules" / name).exists():
            errors.append(f"retired split module document remains active: {name}")

    pairs = [
        ("docs/architecture/README.md", ".agent/architecture/README.md"),
        ("docs/architecture/architecture.md", ".agent/architecture/architecture.md"),
        ("docs/architecture/architecture-views.md", ".agent/architecture/architecture-views.md"),
        ("docs/architecture/architecture.html", ".agent/architecture/architecture.html"),
        *[(f"docs/modules/{name}", f".agent/modules/{name}") for name in MODULE_DOCS],
    ]
    for formal, mirror in pairs:
        if (REPO_ROOT / formal).read_bytes() != (REPO_ROOT / mirror).read_bytes():
            errors.append(f"mirror mismatch: {mirror} must match {formal}")
    return errors


def verify_architecture_markdown_contract() -> list[str]:
    errors: list[str] = []
    content = _read("docs/architecture/architecture.md")
    required_phrases = [
        "# Zuno 总体 Target 架构",
        "十一个逻辑模块",
        "六个物理运行域",
        "Single Controller",
        "AgentRunGraph",
        "Plan DAG",
        "StepExecutionGraph",
        "TaskContract",
        "FinalCandidate",
        "Publication",
        "EvidenceLedger",
        "PreparedToolAction",
        "EffectReconciliation",
        "docs/status/production-readiness.md",
        "docs/architecture/architecture-views.md",
        "docs/architecture/architecture.html",
    ]
    for phrase in required_phrases:
        if phrase not in content:
            errors.append(f"docs/architecture/architecture.md missing architecture contract phrase: {phrase}")
    for name in MODULE_DOCS:
        if f"docs/modules/{name}" not in content:
            errors.append(f"docs/architecture/architecture.md does not route module: {name}")

    mermaid_count = content.count("```mermaid")
    if not 3 <= mermaid_count <= 8:
        errors.append("docs/architecture/architecture.md must remain text-first with three to eight Mermaid diagrams")
    if len(content) < 15000:
        errors.append("docs/architecture/architecture.md is too short for the integration target design")
    return errors


def verify_architecture_views_contract() -> list[str]:
    errors: list[str] = []
    content = _read("docs/architecture/architecture-views.md")
    if content.count("```mermaid") != 30:
        errors.append("docs/architecture/architecture-views.md must keep exactly thirty Mermaid diagrams")
    for title in CANONICAL_VIEWS:
        marker = f"### {title}"
        if marker not in content:
            errors.append(f"docs/architecture/architecture-views.md missing canonical view: {title}")
            continue
        section_start = content.index(marker)
        later = [
            content.find(f"### {other}", section_start + len(marker))
            for other in CANONICAL_VIEWS
            if other != title and content.find(f"### {other}", section_start + len(marker)) >= 0
        ]
        section_end = min(later) if later else len(content)
        section = content[section_start:section_end]
        if "#### Overall" not in section:
            errors.append(f"canonical view missing Overall diagram: {title}")
        if section.count("#### Local") < 2:
            errors.append(f"canonical view needs at least two Local diagrams: {title}")
    return errors


def verify_architecture_html_contract() -> list[str]:
    errors: list[str] = []
    content = _read("docs/architecture/architecture.html")
    required = [
        "Zuno Target Architecture",
        '<script type="module">',
        'fetch("./architecture-views.md")',
        "mermaid@11",
        "../modules/README.md",
        "../status/production-readiness.md",
        "diagram-dialog",
        "Mermaid source",
    ]
    for phrase in required:
        if phrase not in content:
            errors.append(f"docs/architecture/architecture.html missing native Mermaid phrase: {phrase}")
    for title in CANONICAL_VIEWS:
        if title not in content:
            errors.append(f"docs/architecture/architecture.html missing canonical view title: {title}")
    if "offline-svg" in content or "offline-diagram" in content:
        errors.append("docs/architecture/architecture.html must not use retired simplified SVG rendering")
    return errors


def verify_future_only_terms() -> list[str]:
    errors: list[str] = []
    future_terms = [
        "Java",
        "microservice",
        "microservices",
        "微服务",
        "product-level multi-agent",
        "多 Agent runtime",
        "产品级多 Agent",
        "Coding Agent",
    ]
    allowed_context_markers = [
        "Future",
        "非目标",
        "不默认建设",
        "不作为",
        "不是当前",
        "不是近期",
        "不用微服务数量证明成熟度",
        "不默认引入",
        "Future Optional",
    ]
    for relative_path in ["README.md", "docs/architecture/architecture.md"]:
        lines = _read(relative_path).splitlines()
        for index, line in enumerate(lines, start=1):
            if not any(term in line for term in future_terms):
                continue
            window = "\n".join(lines[max(0, index - 12) : min(len(lines), index + 3)])
            if not any(marker in window for marker in allowed_context_markers):
                errors.append(
                    f"{relative_path}:{index} mentions future-only term outside explicit Future/not-Current context: {line.strip()}"
                )
    return errors


def verify_no_local_download_paths() -> list[str]:
    errors: list[str] = []
    for path in [*REPO_ROOT.glob("docs/**/*.md"), *REPO_ROOT.glob(".agent/**/*.md")]:
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if relative_path.startswith(".agent/local/"):
            continue
        if "C:\\Users\\Administrator\\Downloads" in path.read_text(encoding="utf-8"):
            errors.append(f"{relative_path} contains local Downloads path")
    return errors


def main() -> int:
    checks = [
        verify_architecture_surface,
        verify_architecture_markdown_contract,
        verify_architecture_views_contract,
        verify_architecture_html_contract,
        verify_future_only_terms,
        verify_no_local_download_paths,
    ]
    errors: list[str] = []
    for check in checks:
        errors.extend(check())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Doc boundary verification failed.")
        return 1
    print("Doc boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

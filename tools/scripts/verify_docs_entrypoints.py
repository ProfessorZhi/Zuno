from __future__ import annotations

import html
import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ARCHITECTURE_VIEW_CONTRACT = [
    (1, "Logical View (4+1)", "4+1 Logical"),
    (2, "Development View (4+1)", "4+1 Development"),
    (3, "Process View (4+1)", "4+1 Process"),
    (4, "Physical View (4+1)", "4+1 Physical"),
    (5, "Scenarios View (4+1)", "4+1 Scenarios"),
    (6, "Module View (Views & Beyond)", "V&B Module"),
    (7, "Component-and-Connector View (Views & Beyond)", "V&B Component-and-Connector"),
    (8, "Data View (Views & Beyond)", "V&B Data / Information"),
    (9, "Quality View (Views & Beyond)", "V&B Quality"),
    (10, "Agentic GraphRAG Evidence and Agent Loop (Zuno)", "Zuno Product Core"),
]

ACTIVE_DOCS_ARCHITECTURE_FILES = {
    "README.md",
    "architecture.md",
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

ACTIVE_AGENT_ARCHITECTURE_FILES = {
    "README.md",
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


def _current_phase_name(content: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("current_phase:"):
            return line.split(":", 1)[1].strip().strip("`")
    return None


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
        "docs/architecture/production-readiness.md",
        "docs/architecture/document-ingestion-foundation.md",
        "docs/architecture/agent-core-runtime.md",
        "docs/architecture/memory-and-context.md",
        "docs/architecture/capability-and-skill-layer.md",
        "docs/architecture/agentic-retrieval-planner.md",
        "docs/architecture/eval-observability-and-cost.md",
        "docs/architecture/input-layer-and-document-processing.md",
        "docs/architecture/knowledge-space-product-configuration.md",
        "docs/architecture/architecture.html",
        "docs/architecture/repo-ownership-matrix.md",
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
    docs_architecture = _read("docs/architecture/architecture.md")
    production_readiness = _read("docs/architecture/production-readiness.md")
    current_program = _read(".agent/programs/current.md")
    current_phase = _current_phase_name(current_program)
    if current_phase not in {
        "none",
        "PHASE01_truth-source-baseline-and-program-activation",
        "PHASE02_unified-runtime-contracts-and-state",
        "PHASE03_model-gateway-closure",
        "PHASE04_durable-store-trace-and-idempotency",
        "PHASE05_unified-langgraph-runtime-skeleton",
        "PHASE06_strategy-plan-and-react-step-execution",
        "PHASE07_tool-control-plane-and-approval-integration",
        "PHASE08_corrective-agentic-graphrag-and-evidence-ledger",
        "PHASE09_reflection-replan-grounded-synthesis",
        "PHASE10_four-layer-memory-and-reflexion-reuse",
        "PHASE11_product-api-sse-ui-and-recovery-cutover",
        "PHASE12_real-pdf-source-span-vertical-slice",
        "PHASE03_four-diagram-html-and-guardrails",
        "PHASE04_docs-sync-verification-and-closure",
    }:
        errors.append(f"unexpected current phase for docs verification: {current_phase}")

    readme_phrases = [
        "Lean Complete Agentic GraphRAG Product",
        "./docs/architecture/architecture.md",
        "./docs/architecture/architecture.html",
        "./docs/architecture/production-readiness.md",
        "./docs/evidence/public-demo.md",
        "implementation available",
        "measurement blocked",
        "quality not yet proven",
    ]
    for phrase in readme_phrases:
        if phrase not in readme:
            errors.append(f"README.md missing phrase: {phrase}")

    docs_index_phrases = [
        "Zuno 文档入口",
        "./architecture/architecture.md",
        "./architecture/architecture.html",
        "./architecture/production-readiness.md",
        "./history/README.md",
        "前台文档默认使用中文",
    ]
    for phrase in docs_index_phrases:
        if phrase not in docs_index:
            errors.append(f"docs/README.md missing phrase: {phrase}")

    architecture_index_phrases = [
        "架构文档",
        "architecture.md",
        "architecture.html",
        "production-readiness.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "python tools/agent/render_architecture.py --write",
    ]
    for phrase in architecture_index_phrases:
        if phrase not in architecture_index:
            errors.append(f"docs/architecture/README.md missing phrase: {phrase}")

    architecture_phrases = [
        "Zuno Lean Complete Product Architecture",
        "Lean Complete Agentic GraphRAG Product",
        "十一逻辑能力层",
        "六物理运行域",
        "Agent Core / Planning & Control",
        "Capability 是能力目录、选择器和权限策略",
        "Four-layer governed Memory",
        "Corrective Agentic GraphRAG",
        "EvidenceLedger",
        "Product & API",
        "Input & Knowledge",
        "Agent Core",
        "Capability & Tool",
        "Governance & Observability",
        "Local Infrastructure",
        "代码 Ownership Matrix",
        "配置化与禁止写死契约",
        "数据与状态模型",
        "Runtime 完成与质量完成",
        "Agentic Recall@5 >= standard_rag",
        "unavailable_due_to_missing_trace_fields",
        "Future Optional Extensions",
    ]
    for phrase in architecture_phrases:
        if phrase not in docs_architecture:
            errors.append(f"docs/architecture/architecture.md missing phrase: {phrase}")

    production_phrases = [
        "Short-term Closure Gap",
        "Measurement Blocked",
        "Future Optional",
        "Agentic GraphRAG fixed benchmark 跑通并达到 baseline gate",
        "所有真实模型调用统一进入 Model Runtime / Gateway",
        "统一 Agent Core 真实闭环",
        "EvidenceLedger",
        "Agent run trace 持久化并可查看",
    ]
    for phrase in production_phrases:
        if phrase not in production_readiness:
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
        "完整十类视图",
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
    expected_titles = [title for _index, title, _focus in ARCHITECTURE_VIEW_CONTRACT]
    if module.EXPECTED_DIAGRAMS != expected_titles:
        errors.append(
            "render_architecture.EXPECTED_DIAGRAMS drifted: "
            f"expected {expected_titles}, got {module.EXPECTED_DIAGRAMS}"
        )

    source = _read("docs/architecture/architecture.md")
    html_content = _read("docs/architecture/architecture.html")
    if source.count("```mermaid") < len(expected_titles):
        errors.append(f"architecture.md must contain at least {len(expected_titles)} Mermaid blocks")

    for index, title, focus in ARCHITECTURE_VIEW_CONTRACT:
        if f"### {title}" not in source:
            errors.append(f"architecture.md missing diagram heading: {title}")
        html_title = title.replace("&", "&amp;")
        if f"<h3>{index}. {html_title}</h3>" not in html_content:
            errors.append(f"architecture.html missing diagram title: {title}")
        if html.escape(focus) not in html_content:
            errors.append(f"architecture.html missing focus text: {focus}")

    if html_content.count('class="diagram-section') != len(expected_titles):
        errors.append("architecture.html must render exactly ten view categories")
    if html_content.count('class="diagram-card"') < len(expected_titles):
        errors.append("architecture.html must render at least one subdiagram card for each view category")
    if html_content.count('class="offline-svg"') < len(expected_titles):
        errors.append("architecture.html must render offline SVG diagrams")
    if html_content.count("<summary>Mermaid source</summary>") < len(expected_titles):
        errors.append("architecture.html must include source disclosure for each subdiagram")
    if "diagram-dialog" not in html_content:
        errors.append("architecture.html must preserve fullscreen dialog")
    if "https://" in html_content or "http://" in html_content or "cdn.jsdelivr" in html_content:
        errors.append("architecture.html must be offline and contain no external network URL")
    if "import mermaid" in html_content:
        errors.append("architecture.html must not depend on browser-side Mermaid runtime")
    return errors


def verify_architecture_mirrors() -> list[str]:
    errors: list[str] = []
    docs_md = (REPO_ROOT / "docs/architecture/architecture.md").read_bytes()
    agent_md = (REPO_ROOT / ".agent/architecture/architecture.md").read_bytes()
    if docs_md != agent_md:
        errors.append(".agent/architecture/architecture.md must match docs/architecture/architecture.md")

    docs_html = _read("docs/architecture/architecture.html")
    agent_html = _read(".agent/architecture/architecture.html")
    if docs_html != agent_html:
        errors.append(".agent/architecture/architecture.html must match docs/architecture/architecture.html")

    module = _load_render_architecture_module()
    if docs_html != module.build_html():
        errors.append("architecture.html is not generated from current Markdown")
    return errors


def verify_docs_map_has_unique_architecture_source_roles() -> list[str]:
    errors: list[str] = []
    content = _read(".agent/references/docs-map.md")
    formal_entries = content.split("正式人类入口：", 1)[1].split("Agent 工作流入口：", 1)[0]
    if formal_entries.count("`docs/architecture/architecture.md`") != 1:
        errors.append("docs-map must list architecture.md exactly once in formal entries")
    for phrase in [
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

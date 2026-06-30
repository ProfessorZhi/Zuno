from __future__ import annotations

import importlib.util
import re
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


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _require(name: str, content: str, phrases: list[str]) -> list[str]:
    return [f"{name} missing phrase: {phrase}" for phrase in phrases if phrase not in content]


def _load_render_architecture_module():
    module_path = REPO_ROOT / "tools" / "agent" / "render_architecture.py"
    spec = importlib.util.spec_from_file_location("render_architecture", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load tools/agent/render_architecture.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify_architecture_decision_boundaries() -> list[str]:
    errors: list[str] = []
    active_decision = REPO_ROOT / "docs/architecture/decisions/0001-domain-pack-binding.md"
    history_decision = REPO_ROOT / "docs/history/decisions/0001-domain-pack-binding.md"
    decisions_index = _read("docs/architecture/decisions/README.md")

    if active_decision.exists():
        errors.append("docs/architecture/decisions/0001-domain-pack-binding.md must stay archived")
    if not history_decision.exists():
        errors.append("docs/history/decisions/0001-domain-pack-binding.md is missing")
    if "0001-domain-pack-binding.md" in decisions_index:
        errors.append("superseded ADR 0001 must not be listed as active")
    return errors


def verify_active_docs_do_not_link_retired_paths() -> list[str]:
    forbidden_phrases = [
        "docs/architecture/phases/",
        "docs/architecture/plans/",
        "docs/architecture/programs/",
        "docs/architecture/audits/",
        "docs/architecture/specs/",
        "docs/architecture/history/",
        "docs/development/",
        "docs/prototypes/",
        "docs/ui-review/",
        "docs/ui-gallery/",
    ]

    errors: list[str] = []
    for path in sorted((REPO_ROOT / "docs").glob("**/*.md")):
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if relative_path.startswith("docs/history/"):
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in forbidden_phrases:
            if phrase in content:
                errors.append(f"{relative_path} links retired front-path text: {phrase}")
    return errors


def verify_front_path_shape() -> list[str]:
    forbidden_paths = [
        "docs/architecture/audits",
        "docs/architecture/specs",
        "docs/architecture/history",
        "docs/development",
        "docs/prototypes",
        "docs/ui-review",
        "docs/ui-gallery",
        "docs/reference/api.md",
        "docs/reference/core.md",
        "docs/reference/database.md",
        "docs/reference/service.md",
        "docs/reference/zuno.md",
    ]
    return [
        f"retired docs front-path still exists: {relative_path}"
        for relative_path in forbidden_paths
        if (REPO_ROOT / relative_path).exists()
    ]


def verify_architecture_html_sync() -> list[str]:
    errors: list[str] = []
    for relative_path in ["docs/architecture/architecture.md", "docs/architecture/architecture.html", "tools/agent/render_architecture.py"]:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing architecture diagram sync path: {relative_path}")
    if errors:
        return errors

    renderer = _load_render_architecture_module()
    rendered = renderer.build_html()
    html_path = REPO_ROOT / "docs" / "architecture" / "architecture.html"
    if html_path.read_text(encoding="utf-8") != rendered:
        errors.append("docs/architecture/architecture.html is stale; run python tools/agent/render_architecture.py --write")

    architecture_source = _read("docs/architecture/architecture.md")
    for phrase in [
        "Zuno 架构总览",
        "python tools/agent/render_architecture.py --write",
        "#f7f8fb",
        "#ffffff",
        "#b8c2cc",
        "#16202a",
        "#52616f",
        "Raw Event Log",
        "Memory Read Policy",
        "Memory Review Gate",
        "structured memory candidate",
        "write-manage-read",
        "Tool Control Plane",
        "Tool Manifest Registry",
        "Tool Policy Approval",
        "Result Normalizer",
    ]:
        if phrase not in architecture_source:
            errors.append(f"docs/architecture/architecture.md missing diagram sync phrase: {phrase}")

    for stale_path in [
        "docs/architecture.md",
        "docs/architecture.html",
        "docs/architecture/overview.html",
        ".agent/architecture/blueprint.html",
    ]:
        if (REPO_ROOT / stale_path).exists():
            errors.append(f"stale architecture HTML must not remain: {stale_path}")

    for relative_path in ["docs/architecture/architecture.html"]:
        path = REPO_ROOT / relative_path
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in [
            "docs/architecture/architecture.md",
            "tools/agent/render_architecture.py",
            "4+1 View Model",
            "Component-and-Connector View",
            "Deployment View",
            "Quality View",
            "Scenarios View",
            "Process View",
            "View &amp; Beyond",
            "V&amp;B Logical View",
            "V&amp;B Deployment View",
            "Agent Loop View",
            "#f7f8fb",
            "#ffffff",
            "#b8c2cc",
            "#16202a",
            "#52616f",
        ]:
            if phrase not in content:
                errors.append(f"{relative_path} missing architecture diagram phrase: {phrase}")
    return errors


def verify_overall_architecture_docs_sync() -> list[str]:
    errors: list[str] = []
    docs_overall = _read("docs/architecture/overall-architecture.md")
    agent_overall = _read(".agent/architecture/overall-architecture.md")

    shared_phrases = [
        "总架构文档",
        "本地优先的企业私有知识库与多功能 Agent 助手",
        "文字总架构文档",
        "架构 HTML",
        "docs/architecture/overall-architecture.md",
        ".agent/architecture/overall-architecture.md",
        "docs/architecture/architecture.md",
        "docs/architecture/architecture.html",
        "Document Ingestion / Parse Gateway",
        "Tool Control Plane",
        "LangSmith-compatible Trace / Eval",
    ]
    for phrase in shared_phrases:
        if phrase not in docs_overall:
            errors.append(f"docs/architecture/overall-architecture.md missing sync phrase: {phrase}")
        if phrase not in agent_overall:
            errors.append(f".agent/architecture/overall-architecture.md missing sync phrase: {phrase}")

    for phrase in [
        "current-architecture.md",
        "target-architecture.md",
        "security-and-sandbox.md",
        "product-scenario-enterprise-kb.md",
        "python tools/agent/render_architecture.py --write",
    ]:
        if phrase not in docs_overall:
            errors.append(f"docs/architecture/overall-architecture.md missing governance phrase: {phrase}")

    for phrase in [
        "不要在 `.agent/architecture/` 复制新的 HTML",
        "如果两者冲突，以 `docs/architecture/overall-architecture.md` 为准",
        "一致性锚点",
    ]:
        if phrase not in agent_overall:
            errors.append(f".agent/architecture/overall-architecture.md missing governance phrase: {phrase}")
    return errors


def verify_architecture_view_contract() -> list[str]:
    errors: list[str] = []
    renderer = _load_render_architecture_module()
    expected_titles = [title for _, title, _ in ARCHITECTURE_VIEW_CONTRACT]
    if list(renderer.EXPECTED_DIAGRAMS) != expected_titles:
        errors.append("render_architecture.py EXPECTED_DIAGRAMS does not match architecture view contract")
    if len(expected_titles) != 10 or len(set(expected_titles)) != 10:
        errors.append("architecture view contract must contain exactly ten unique view titles")

    architecture_source = _read("docs/architecture/architecture.md")
    try:
        source_titles = [diagram.title for diagram in renderer.extract_diagrams(architecture_source)]
    except Exception as exc:  # pragma: no cover - surfaced as verifier output
        errors.append(f"docs/architecture/architecture.md cannot be parsed by renderer: {exc}")
        source_titles = []
    if source_titles and source_titles != expected_titles:
        errors.append(f"docs/architecture/architecture.md diagram order drifted: {source_titles}")

    inventory = _read(".agent/references/diagram-inventory.md")
    deliverables = _read("docs/architecture/deliverables.md")
    target = _read("docs/architecture/target-architecture.md")
    architecture_index = _read("docs/architecture/README.md")
    html_page = _read("docs/architecture/architecture.html")

    for index, title, theory in ARCHITECTURE_VIEW_CONTRACT:
        inventory_row = f"| {index} | {title} | {theory} |"
        deliverables_row = f"| {index} | {title} | {theory} |"
        if inventory_row not in inventory:
            errors.append(f"diagram-inventory.md missing canonical row: {inventory_row}")
        if deliverables_row not in deliverables:
            errors.append(f"docs/architecture/deliverables.md missing canonical row: {deliverables_row}")
        if f"| {title} | {theory} |" not in target:
            errors.append(f"target-architecture.md missing canonical view/theory pair: {title} / {theory}")
        if f"{index}. `{title}`" not in architecture_index:
            errors.append(f"docs/architecture/README.md missing canonical ordered view: {index}. `{title}`")
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
        "overflow: hidden",
        "max-width: 100%",
        "展开全屏查看",
        "diagram-open",
        "diagram-dialog",
        "dialog-canvas",
        "securityLevel: \"strict\"",
        "useMaxWidth: true",
    ]:
        if phrase not in html_page:
            errors.append(f"docs/architecture/architecture.html missing visual safety phrase: {phrase}")

    forbidden_prefixed_titles = [
        "4+1 Logical View",
        "4+1 Development View",
        "4+1 Process View",
        "4+1 Physical View",
        "4+1 Scenarios View",
        "V&B Component-and-Connector View",
        "V&B Quality View",
    ]
    for relative_path in [
        "docs/architecture/deliverables.md",
        "docs/architecture/README.md",
        "docs/architecture/target-architecture.md",
    ]:
        content = _read(relative_path)
        for title in forbidden_prefixed_titles:
            if re.search(rf"`?{re.escape(title)}`?", content):
                errors.append(f"{relative_path} keeps non-canonical view title: {title}")

    return errors


def main() -> int:
    readme = _read("README.md")
    docs_index = _read("docs/README.md")
    architecture_index = _read("docs/architecture/README.md")
    overall = _read("docs/architecture/overall-architecture.md")
    deliverables = _read("docs/architecture/deliverables.md")
    roadmap = _read("docs/architecture/roadmap.md")
    target = _read("docs/architecture/target-architecture.md")
    product_scenario = _read("docs/architecture/product-scenario-enterprise-kb.md")
    security_sandbox = _read("docs/architecture/security-and-sandbox.md")
    architecture_source = _read("docs/architecture/architecture.md")
    evidence = _read("docs/evidence/public-demo.md")
    workflow = _read(".agent/references/workflow.md")
    agent_overall = _read(".agent/architecture/overall-architecture.md")
    agents = _read("AGENTS.md")

    errors: list[str] = []
    errors.extend(
        _require(
            "README.md",
            readme,
            [
                "./docs/architecture/current-architecture.md",
                "./docs/architecture/overall-architecture.md",
                "./docs/architecture/product-scenario-enterprise-kb.md",
                "./docs/architecture/target-architecture.md",
                "./docs/architecture/security-and-sandbox.md",
                "./docs/architecture/roadmap.md",
                "./docs/evidence/public-demo.md",
                "受限历史兼容",
                "企业私有知识库与多功能 Agent 助手",
                "普通 RAG 问答",
                "Security、Approval 和 Sandbox 是目标治理层",
                "src/backend/zuno",
                "Single Controller Agent 是目标架构角色",
                "当前实现主线是 `GeneralAgent` single loop",
                "Summary Compression",
                "ToolCard",
                "Native BM25",
                "RRF",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/README.md",
            docs_index,
            [
                "./architecture/current-architecture.md",
                "./architecture/overall-architecture.md",
                "./architecture/target-architecture.md",
                "./architecture/roadmap.md",
                "./architecture/deliverables.md",
                "./evidence/public-demo.md",
                "./history/README.md",
                "前台文档默认使用中文",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/architecture/README.md",
            architecture_index,
            [
                "current-architecture.md",
                "overall-architecture.md",
                "product-scenario-enterprise-kb.md",
                "target-architecture.md",
                "security-and-sandbox.md",
                "roadmap.md",
                "architecture.md",
                "architecture.html",
                "../evidence/public-demo.md",
                "docs/history/programs/official-graphrag-cleanup-v1/",
                "docs/history/programs/zuno-target-architecture-migration-v1/",
                "zuno-target-runtime-v2",
                "过时审计、旧规格、旧 phase、旧计划和旧 runbook",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/architecture/deliverables.md",
            deliverables,
            [
                "八大交付物",
                "十类架构视图",
                "根目录清洁期望",
                "absorbed reference programs / roadmap reference inputs",
                "Logical View",
                "V&B Logical View",
                "Agent Loop View",
                "Quality View",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/architecture/roadmap.md",
            roadmap,
            [
                "Phase 11A：已完成",
                "Phase 11B：已完成",
                "Phase 11C：active runtime cleanup 已完成",
                "Phase 12：已通过 target migration closure evidence 关闭",
                "受限历史兼容",
                "zuno-workflow-doc-system-v1",
                "zuno-target-architecture-refresh-v1",
                "zuno-repo-layout-cleanup-v1",
                "zuno-architecture-visuals-v1",
                "PHASE03 completed",
                "视觉 QA",
                "docs/architecture/architecture.md",
                "docs/architecture/deliverables.md",
                "docs/history/programs/zuno-target-architecture-migration-v1/",
                "docs/history/programs/official-graphrag-cleanup-v1/",
                "zuno-document-ingestion-v1",
                "zuno-security-enterprise-scenarios-v1",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/architecture/overall-architecture.md",
            overall,
            [
                "总架构文档",
                "当前架构事实",
                "目标架构分层",
                "主链路",
                "文档解析边界",
                "安全与评测",
                "实施落点",
                "文档一致性规则",
                "Document Ingestion / Parse Gateway",
                "Tool Control Plane",
                "LangSmith-compatible Trace / Eval",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/architecture/target-architecture.md",
            target,
            [
                "Summary Compression",
                "Structured Extraction",
                "Native BM25",
                "ToolCard",
                "RRF",
                "`auto` 是 router",
                "GraphRAG 实体抽取默认主路径是 LLM 抽取",
                "六个主层",
                "新增或重写的前台文档使用中文",
                "企业私有知识库与多功能 Agent 助手",
                "Policy Sandbox",
                "Network / Credential Sandbox",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/architecture/product-scenario-enterprise-kb.md",
            product_scenario,
            [
                "企业私有知识库与多功能 Agent 助手",
                "普通 RAG 问答",
                "企业内部文档",
                "简历和候选人资料",
                "Current",
                "Target",
                "Future",
                "zuno-document-ingestion-v1",
                "zuno-security-enterprise-scenarios-v1",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/architecture/security-and-sandbox.md",
            security_sandbox,
            [
                "Policy Sandbox",
                "Workspace Sandbox",
                "Execution Sandbox",
                "Network / Credential Sandbox",
                "不能声称已经有成熟沙箱系统",
                "ToolCard / MCP policy foundation",
                "Target",
                "Future",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/architecture/architecture.md",
            architecture_source,
            [
                "Logical View",
                "Development View",
                "Process View",
                "Physical View",
                "Scenarios View",
                "View & Beyond",
                "V&B Logical View",
                "V&B Deployment View",
                "Quality View",
                "Agent Loop View",
                "Component-and-Connector View",
                "```mermaid",
                "4+1 View Model",
                "Component-and-Connector View",
                "Deployment View",
                "Quality View",
                "Agentic RAG",
                "GraphRAG",
                "企业私有知识库与多功能 Agent 助手",
                "安全与沙箱目标架构",
                "总架构文档",
                "Domain Pack 只允许作为历史或兼容语境出现",
            ],
        )
    )
    errors.extend(
        _require(
            "docs/evidence/public-demo.md",
            evidence,
            [
                "../history/development/public-demo-evidence.md",
                "../history/development/public-demo-runbook.md",
                "../history/development/public-demo-acceptance.md",
            ],
        )
    )
    errors.extend(
        _require(
            ".agent/references/workflow.md",
            workflow,
            [
                "前台文档默认使用中文",
                "过时材料移动到 `docs/history/`",
                "旧 audit、旧 spec、旧 runbook、旧 UI 原型",
                "docs/architecture/overall-architecture.md",
                ".agent/architecture/overall-architecture.md",
            ],
        )
    )
    errors.extend(
        _require(
            ".agent/architecture/overall-architecture.md",
            agent_overall,
            [
                "Agent 侧总架构文档",
                "正式人类总架构文档",
                "Current / Target 快速边界",
                "根部总架构维护面",
                "与 HTML 图页的关系",
                "一致性锚点",
                "docs/architecture/overall-architecture.md",
                "docs/architecture/architecture.html",
            ],
        )
    )
    errors.extend(
        _require(
            "AGENTS.md",
            agents,
            [
                "这是仓库唯一的 Agent 入口",
                ".agent/references/task-routing.md",
                ".agent/references/workflow.md",
                ".agent/references/architecture-docs-map.md",
                ".agent/references/workflow-governance.md",
                ".agent/programs/",
                ".agent/architecture/",
                "Architecture Documentation Governance",
                "Agent Workflow Self-Maintenance",
                "前台文档默认中文",
                "docs/architecture/overall-architecture.md",
                ".agent/architecture/overall-architecture.md",
            ],
        )
    )

    errors.extend(verify_architecture_decision_boundaries())
    errors.extend(verify_active_docs_do_not_link_retired_paths())
    errors.extend(verify_front_path_shape())
    errors.extend(verify_architecture_html_sync())
    errors.extend(verify_overall_architecture_docs_sync())
    errors.extend(verify_architecture_view_contract())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("documentation entrypoint verification failed.")
        return 1

    print("documentation entrypoint verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

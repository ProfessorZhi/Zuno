from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _require(name: str, content: str, phrases: list[str]) -> list[str]:
    return [f"{name} missing phrase: {phrase}" for phrase in phrases if phrase not in content]


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
    for relative_path in ["docs/architecture.md", "docs/architecture.html", "tools/agent/render_architecture.py"]:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing architecture diagram sync path: {relative_path}")

    architecture_source = _read("docs/architecture.md")
    for phrase in [
        "Zuno 架构总览",
        "python tools/agent/render_architecture.py --write",
        "#f7f8fb",
        "#ffffff",
        "#b8c2cc",
        "#16202a",
        "#52616f",
    ]:
        if phrase not in architecture_source:
            errors.append(f"docs/architecture.md missing diagram sync phrase: {phrase}")

    for stale_path in [
        "docs/architecture/architecture.html",
        "docs/architecture/overview.html",
        ".agent/architecture/blueprint.html",
    ]:
        if (REPO_ROOT / stale_path).exists():
            errors.append(f"stale architecture HTML must not remain: {stale_path}")

    for relative_path in ["docs/architecture.html"]:
        path = REPO_ROOT / relative_path
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in [
            "docs/architecture.md",
            "tools/agent/render_architecture.py",
            "4+1 View Model",
            "Component-and-Connector View",
            "Deployment View",
            "Quality View",
            "Scenarios View",
            "Process View",
            "V&B Logical View",
            "V&B Deployment View",
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


def main() -> int:
    readme = _read("README.md")
    docs_index = _read("docs/README.md")
    architecture_index = _read("docs/architecture/README.md")
    deliverables = _read("docs/deliverables.md")
    roadmap = _read("docs/architecture/roadmap.md")
    target = _read("docs/architecture/target-architecture.md")
    architecture_source = _read("docs/architecture.md")
    evidence = _read("docs/evidence/public-demo.md")
    workflow = _read(".agent/references/workflow.md")
    agents = _read("AGENTS.md")

    errors: list[str] = []
    errors.extend(
        _require(
            "README.md",
            readme,
            [
                "./docs/architecture/current-architecture.md",
                "./docs/architecture/target-architecture.md",
                "./docs/architecture/roadmap.md",
                "./docs/evidence/public-demo.md",
                "受限历史兼容",
                "src/backend/zuno",
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
                "./architecture/target-architecture.md",
                "./architecture/roadmap.md",
                "./deliverables.md",
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
                "target-architecture.md",
                "roadmap.md",
                "../architecture.md",
                "../architecture.html",
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
            "docs/deliverables.md",
            deliverables,
            [
                "八大交付物",
                "十类架构视图",
                "根目录清洁期望",
                "4+1 Logical View",
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
                "docs/architecture.md",
                "docs/deliverables.md",
                "docs/history/programs/zuno-target-architecture-migration-v1/",
                "docs/history/programs/official-graphrag-cleanup-v1/",
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
            ],
        )
    )
    errors.extend(
        _require(
            "docs/architecture.md",
            architecture_source,
            [
                "Logical View",
                "Development View",
                "Process View",
                "Physical View",
                "Scenarios View",
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
            ],
        )
    )

    errors.extend(verify_architecture_decision_boundaries())
    errors.extend(verify_active_docs_do_not_link_retired_paths())
    errors.extend(verify_front_path_shape())
    errors.extend(verify_architecture_html_sync())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("documentation entrypoint verification failed.")
        return 1

    print("documentation entrypoint verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

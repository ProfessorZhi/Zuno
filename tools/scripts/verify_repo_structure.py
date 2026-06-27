from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


REQUIRED_PATHS = [
    "AGENTS.md",
    ".agent/README.md",
    ".agent/references/README.md",
    ".agent/references/task-routing.md",
    ".agent/references/workflow.md",
    ".agent/references/docs-map.md",
    ".agent/programs/current.md",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/phase-05-memory-engine.md",
    ".agent/programs/phase-06-capability-tool-retrieval.md",
    ".agent/programs/phase-07-graphrag-llm-entity-extraction.md",
    ".agent/programs/phase-08-langgraph-runtime.md",
    ".agent/programs/phase-09-product-trace-eval-closure.md",
    ".agent/programs/closure-checklist.md",
    ".agent/architecture/README.md",
    ".agent/architecture/future/README.md",
    ".agent/architecture/decisions/README.md",
    ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
    ".agent/architecture/near-term/01-target-runtime-architecture.md",
    ".agent/architecture/near-term/02-context-memory-architecture.md",
    ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
    ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
    ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
    ".agent/scripts/verify_agent_system.py",
    ".agent/scripts/verify_doc_boundaries.py",
    ".agent/scripts/verify_repo_hygiene.py",
    "apps/desktop",
    "apps/web",
    "apps/web/AGENTS.md",
    "docs/README.md",
    "docs/architecture/README.md",
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/architecture/decisions/README.md",
    "docs/evidence/README.md",
    "docs/evidence/public-demo.md",
    "docs/evidence/eval-baselines.md",
    "docs/reference/terminology.md",
    "docs/history/README.md",
    "docs/history/phases/README.md",
    "docs/history/plans/README.md",
    "docs/history/programs/README.md",
    "docs/history/programs/zuno-target-architecture-migration-v1/README.md",
    "docs/history/programs/zuno-target-runtime-v2/README.md",
    "docs/history/programs/official-graphrag-cleanup-v1/README.md",
    "docs/history/development/README.md",
    "docs/history/reference/migration.md",
    "docs/history/specs",
    "docs/history/audits",
    "examples/graphrag-projects/contract_review/settings.yaml",
    "examples/graphrag-projects/contract_review/schema.json",
    "examples/graphrag-projects/contract_review/retrieval_policy.yaml",
    "examples/graphrag-projects/contract_review/eval/eval_dataset.jsonl",
    "docs/history/domain-packs/root-contract-review/contract_review/pack.yaml",
    "docs/history/domain-packs/root-contract-review/contract_review/schema.json",
    "infra/db",
    "infra/docker",
    "src/backend/zuno",
    "src/backend/zuno/AGENTS.md",
    "src/backend/zuno/main.py",
    "tests",
    "tools",
    "tools/evals/zuno",
    "tools/evals/zuno/AGENTS.md",
]


FORBIDDEN_CURRENT_PATHS = [
    ".agent/skills",
    ".agent/workflows",
    "docs/architecture/history",
    "docs/architecture/audits",
    "docs/architecture/specs",
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
    "docs/development",
    "docs/prototypes",
    "docs/ui-review",
    "docs/ui-gallery",
    "docs/reference/api.md",
    "docs/reference/core.md",
    "docs/reference/database.md",
    "docs/reference/service.md",
    "docs/reference/zuno.md",
    ".agent/programs/context-memory-agent-runtime-v1",
    ".agent/programs/official-graphrag-cleanup-v1",
    ".agent/programs/zuno-target-runtime-v2",
    ".agent/programs/implementation-phases",
    "docs/superpowers",
    "src/frontend",
    "domain-packs",
    "tests/compat",
]


DOC_REQUIRED_PHRASES: dict[str, list[str]] = {
    "AGENTS.md": [
        "这是仓库唯一的 Agent 入口",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/programs/",
        ".agent/architecture/",
        "前台文档默认中文",
    ],
    ".agent/README.md": [
        "Agent 工作流库",
        "类似 skill 的任务路由",
        "新写或重写的 Agent 文档默认使用中文",
    ],
    "docs/README.md": [
        "./architecture/current-architecture.md",
        "./architecture/target-architecture.md",
        "./architecture/roadmap.md",
        "./evidence/public-demo.md",
        "./history/README.md",
        "前台文档默认使用中文",
    ],
    "docs/architecture/README.md": [
        "current-architecture.md",
        "target-architecture.md",
        "roadmap.md",
        "../evidence/public-demo.md",
        "docs/history/programs/official-graphrag-cleanup-v1/",
        "docs/history/programs/zuno-target-architecture-migration-v1/",
        "过时审计、旧规格、旧 phase、旧计划和旧 runbook",
    ],
    "docs/architecture/roadmap.md": [
        "Phase 11A：已完成",
        "Phase 11B：已完成",
        "Phase 11C：active runtime cleanup 已完成",
        "Phase 12：已通过 target migration closure evidence 关闭",
        "受限历史兼容",
        "Phase 05：记忆引擎",
        "Phase 09：产品边界、Trace 与 Eval 收口",
    ],
}


@dataclass
class VerificationResult:
    errors: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def _read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def verify_required_paths() -> list[str]:
    return [
        f"missing required path: {relative_path}"
        for relative_path in REQUIRED_PATHS
        if not (REPO_ROOT / relative_path).exists()
    ]


def verify_forbidden_current_paths() -> list[str]:
    return [
        f"retired current-path still exists: {relative_path}"
        for relative_path in FORBIDDEN_CURRENT_PATHS
        if (REPO_ROOT / relative_path).exists()
    ]


def verify_doc_phrases() -> list[str]:
    errors: list[str] = []
    for relative_path, phrases in DOC_REQUIRED_PHRASES.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing required doc: {relative_path}")
            continue
        content = _read_text(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing phrase: {phrase}")
    return errors


def verify_target_architecture_html() -> list[str]:
    errors: list[str] = []
    html_path = REPO_ROOT / ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html"
    if not html_path.exists():
        return ["missing canonical target architecture HTML"]
    html = html_path.read_text(encoding="utf-8")
    if "<html" not in html.lower() or "</html>" not in html.lower():
        errors.append("canonical target architecture HTML is not valid HTML")
    for phrase in [
        "Target / Proposed",
        "Native BM25",
        "RRF",
        "Summary Compression",
        "Structured Extraction",
        "ToolCard",
        "Phase 05",
        "Query Journey",
        "产品入口层",
        "RAG / GraphRAG 层",
    ]:
        if phrase not in html:
            errors.append(f"canonical target architecture HTML missing phrase: {phrase}")
    html_refs = [
        path
        for path in REPO_ROOT.glob(".agent/**/*.md")
        if "zuno-ideal-architecture-and-repo-layout.html" in path.read_text(encoding="utf-8")
    ]
    if len(html_refs) < 5:
        errors.append("target architecture HTML is under-referenced by Agent docs")
    return errors


def verify_active_v2_phase_plan() -> list[str]:
    roadmap_path = REPO_ROOT / ".agent/programs/implementation-roadmap.md"
    if not roadmap_path.exists():
        return ["missing active V2 implementation roadmap"]
    roadmap = roadmap_path.read_text(encoding="utf-8")
    errors = [
        f"active V2 roadmap missing phase plan: {phrase}"
        for phrase in [
            "Phase 05：记忆引擎",
            "Phase 06：能力与工具检索",
            "Phase 07：GraphRAG LLM 实体抽取与知识检索融合",
            "Phase 08：GeneralAgent LangGraph 运行时",
            "Phase 09：产品边界、Trace 与 Eval 收口",
            "所有 phase 文件平铺在 `.agent/programs/`",
        ]
        if phrase not in roadmap
    ]
    phase07_path = REPO_ROOT / ".agent/programs/phase-07-graphrag-llm-entity-extraction.md"
    if not phase07_path.exists():
        errors.append("missing active Phase 07 GraphRAG LLM extraction plan")
    else:
        phase07 = phase07_path.read_text(encoding="utf-8")
        for phrase in [
            "model_refs.entity_extraction_llm_id",
            "LLM 抽取是默认主路径",
            "规则/正则只辅助日期、金额、条款号",
        ]:
            if phrase not in phase07:
                errors.append(f"Phase 07 GraphRAG LLM extraction plan missing phrase: {phrase}")
    return errors


def run_verification() -> VerificationResult:
    return VerificationResult(
        errors=[
            *verify_required_paths(),
            *verify_forbidden_current_paths(),
            *verify_doc_phrases(),
            *verify_target_architecture_html(),
            *verify_active_v2_phase_plan(),
        ]
    )


def main() -> int:
    result = run_verification()
    if result.ok:
        print("Repository structure verification passed.")
        return 0

    for error in result.errors:
        print(f"ERROR: {error}")
    print("Repository structure verification failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

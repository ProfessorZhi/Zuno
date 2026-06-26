from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "AGENTS.md",
    ".agent",
    ".agent/README.md",
    ".agent/programs/current.md",
    "docs/architecture/history/programs/zuno-target-architecture-migration-v1",
    ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
    ".agent/architecture/near-term/19-repository-layout-and-module-boundaries.md",
    ".agent/scripts/verify_agent_system.py",
    ".agent/scripts/verify_doc_boundaries.py",
    ".agent/scripts/verify_repo_hygiene.py",
    ".agent/workflows/repo-hygiene.md",
    ".agent/skills/zuno-repo-hygiene/SKILL.md",
    "apps/desktop",
    "apps/web",
    "apps/web/AGENTS.md",
    "docs/README.md",
    "docs/architecture",
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/architecture/history",
    "docs/architecture/history/phases/README.md",
    "docs/architecture/history/plans/README.md",
    "docs/architecture/history/programs/README.md",
    "docs/architecture/history/programs/context-memory-agent-runtime-v1/README.md",
    "docs/architecture/history/programs/official-graphrag-cleanup-v1/README.md",
    "docs/architecture/history/development/README.md",
    "docs/architecture/history/reference/migration.md",
    "docs/development",
    "docs/evidence/README.md",
    "docs/evidence/public-demo.md",
    "docs/reference",
    "examples/graphrag-projects/contract_review/settings.yaml",
    "examples/graphrag-projects/contract_review/schema.json",
    "examples/graphrag-projects/contract_review/retrieval_policy.yaml",
    "examples/graphrag-projects/contract_review/prompts/extract_graph.md",
    "examples/graphrag-projects/contract_review/prompts/local_query.md",
    "examples/graphrag-projects/contract_review/prompts/report_template.md",
    "examples/graphrag-projects/contract_review/eval/eval_dataset.jsonl",
    "docs/architecture/history/domain-packs/root-contract-review/contract_review/pack.yaml",
    "docs/architecture/history/domain-packs/root-contract-review/contract_review/schema.json",
    "docs/architecture/history/domain-packs/root-contract-review/contract_review/retrieval_policy.yaml",
    "docs/architecture/history/domain-packs/root-contract-review/contract_review/extraction_prompt.md",
    "docs/architecture/history/domain-packs/root-contract-review/contract_review/answer_template.md",
    "docs/architecture/history/domain-packs/root-contract-review/contract_review/report_template.md",
    "docs/architecture/history/domain-packs/root-contract-review/contract_review/eval_dataset.jsonl",
    "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/capture_knowledge_product_ui_gallery.py",
    "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/check_knowledge_product_responsive.py",
    "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/check_settings_navigation_interaction.py",
    "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/preview_phase6_bundle_scope.py",
    "docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/verify_phase6_bundle_ready.py",
    "docs/architecture/history/specs/deep-graphrag-v1-runtime.md",
    "docs/architecture/history/specs/domain-pack-langgraph-graphrag-architecture.md",
    "docs/architecture/history/specs/domain-pack-builder.md",
    "docs/architecture/history/specs/knowledge-product-boundary.md",
    "infra/db",
    "infra/docker",
    "src/backend/zuno",
    "src/backend/zuno/AGENTS.md",
    "src/backend/zuno/main.py",
    "tests",
    "tools",
    "tools/evals/zuno",
    "tools/evals/zuno/AGENTS.md",
    "tools/launchers/windows",
]

FORBIDDEN_CURRENT_PATHS = [
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
    ".agent/programs/context-memory-agent-runtime-v1",
    ".agent/programs/official-graphrag-cleanup-v1",
    "docs/superpowers",
    "docs/prototypes/superpowers-legacy",
    "docs/ui-gallery/knowledge-product-refactor-deep-graphrag-v1",
    "src/frontend",
    "domain-packs",
    "tests/compat",
    "docs/development/history",
    "docs/reference/history",
]

DOC_REQUIRED_PHRASES: dict[str, list[str]] = {
    "README.md": [
        "## Default Reading Path",
        "./docs/architecture/current-architecture.md",
        "./docs/architecture/target-architecture.md",
        "./docs/architecture/roadmap.md",
        "./docs/evidence/public-demo.md",
        "Blocked Legacy",
        "uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860",
    ],
    "docs/README.md": [
        "./architecture/current-architecture.md",
        "./architecture/target-architecture.md",
        "./architecture/roadmap.md",
        "./evidence/public-demo.md",
        "./architecture/history/README.md",
    ],
    "docs/architecture/README.md": [
        "current-architecture.md",
        "target-architecture.md",
        "roadmap.md",
        "../evidence/public-demo.md",
        "docs/architecture/history/programs/official-graphrag-cleanup-v1/",
        "docs/architecture/history/programs/zuno-target-architecture-migration-v1/",
        "history/phases/",
    ],
    "docs/architecture/roadmap.md": [
        "Phase 11A: complete",
        "Phase 11B: complete",
        "Phase 11C: active runtime cleanup complete",
        "Phase 12: closed through the target migration closure evidence",
        "Blocked Legacy",
        "docs/architecture/history/programs/zuno-target-architecture-migration-v1/",
        "docs/architecture/history/programs/official-graphrag-cleanup-v1/",
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
    if not any(marker in html for marker in ["Target", "Proposed", "目标"]):
        errors.append("canonical target architecture HTML missing Target/Proposed marker")
    html_refs = [
        path for path in REPO_ROOT.glob(".agent/**/*.md")
        if "zuno-ideal-architecture-and-repo-layout.html" in path.read_text(encoding="utf-8")
    ]
    if len(html_refs) < 6:
        errors.append("target architecture HTML is under-referenced by Agent workflows")
    return errors


def verify_archived_reference_docs() -> list[str]:
    errors: list[str] = []
    if (REPO_ROOT / "docs" / "reference" / "migration.md").exists():
        errors.append("docs/reference/migration.md should be archived out of the front path")
    if not (REPO_ROOT / "docs" / "architecture" / "history" / "reference" / "migration.md").exists():
        errors.append("docs/architecture/history/reference/migration.md is missing")
    return errors


def run_verification() -> VerificationResult:
    errors = [
        *verify_required_paths(),
        *verify_forbidden_current_paths(),
        *verify_doc_phrases(),
        *verify_target_architecture_html(),
        *verify_archived_reference_docs(),
    ]
    return VerificationResult(errors=errors)


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

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
    ".agent/programs/official-graphrag-cleanup-v1",
    "apps/desktop",
    "apps/web",
    "docs/README.md",
    "docs/architecture",
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/architecture/history",
    "docs/architecture/history/phases/README.md",
    "docs/architecture/history/plans/README.md",
    "docs/development",
    "docs/evidence/README.md",
    "docs/evidence/public-demo.md",
    "docs/reference",
    "domain-packs",
    "infra/db",
    "infra/docker",
    "src/backend/zuno",
    "src/backend/zuno/main.py",
    "tests",
    "tests/compat",
    "tools",
    "tools/evals/zuno",
    "tools/launchers/windows",
]

FORBIDDEN_CURRENT_PATHS = [
    "docs/architecture/phases",
    "docs/architecture/plans",
    "docs/architecture/programs",
    "docs/superpowers",
    "docs/prototypes/superpowers-legacy",
    "docs/ui-gallery/knowledge-product-refactor-deep-graphrag-v1",
    "src/frontend",
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
        ".agent/programs/official-graphrag-cleanup-v1/",
        "history/phases/",
    ],
    "docs/architecture/roadmap.md": [
        "Phase 11 is Runtime Legacy Deletion.",
        "Blocked Legacy",
        ".agent/programs/official-graphrag-cleanup-v1/",
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


def verify_archived_reference_docs() -> list[str]:
    errors: list[str] = []
    if (REPO_ROOT / "docs" / "reference" / "migration.md").exists():
        errors.append("docs/reference/migration.md should be archived out of the front path")
    if not (REPO_ROOT / "docs" / "reference" / "history" / "migration.md").exists():
        errors.append("docs/reference/history/migration.md is missing")
    return errors


def run_verification() -> VerificationResult:
    errors = [
        *verify_required_paths(),
        *verify_forbidden_current_paths(),
        *verify_doc_phrases(),
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
